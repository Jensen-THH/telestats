import telethon
from telethon.tl.types import Message, ReactionEmoji, ReactionCustomEmoji, PeerUser, PeerChannel, PeerChat, ReactionPaid
from app.telegram_client import client
from app.database import messages_collection
import datetime
import base64
from io import BytesIO
from app.utils.helper import convert_objectid
from pymongo.errors import PyMongoError
import logging
from datetime import timezone, timedelta
from typing import List
from fastapi import UploadFile
from telethon.errors import FloodWaitError, RPCError

VN_TZ = timezone(timedelta(hours=7))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_entity(chat_id: str, channel_id: int = None) -> tuple:
    if channel_id:
        try:
            entity = await client.get_entity(channel_id)
            logger.info(f"Fetching messages from channel ID: {channel_id}")
            return entity, f"https://t.me/c/{str(channel_id).replace('-100', '')}"
        except Exception as e:
            logger.error(f"Failed to get entity by channel_id {channel_id}: {e}")
            raise ValueError(f"Invalid channel_id: {e}")
    try:
        entity = await client.get_entity(chat_id)
        logger.info(f"Fetching messages from chat ID: {chat_id}")
        username = getattr(entity, 'username', None)
        return entity, f"https://t.me/{username}" if username else f"https://t.me/c/{chat_id}"
    except Exception as e:
        logger.error(f"Failed to get entity by chat_id {chat_id}: {e}")
        raise ValueError(f"Invalid chat_id: {e}")

async def get_sender_info(message, fetch_username: bool, from_user: str) -> tuple:
    user_name, user_id = None, None
    if fetch_username and message.from_id:
        try:
            sender = await message.get_sender()
            user_name = sender.username or str(message.from_id.user_id) if sender else str(message.from_id.user_id)
            user_id = message.from_id.user_id if hasattr(message.from_id, 'user_id') else None
        except Exception as e:
            logger.warning(f"Error fetching sender for message {message.id}: {e}")
            if isinstance(message.from_id, PeerUser):
                user_id = message.from_id.user_id
                user_name = str(user_id)
            elif isinstance(message.from_id, PeerChannel):
                user_id = message.from_id.channel_id
                user_name = f"Channel_{user_id}"
            elif isinstance(message.from_id, PeerChat):
                user_id = message.from_id.chat_id
                user_name = f"Chat_{user_id}"
    else:
        if isinstance(message.from_id, PeerUser):
            user_id = message.from_id.user_id
        elif isinstance(message.from_id, PeerChannel):
            user_id = message.from_id.channel_id
        elif isinstance(message.from_id, PeerChat):
            user_id = message.from_id.chat_id
        user_name = from_user if from_user else (str(user_id) if user_id else None)
    return user_name, user_id

def process_reactions(message) -> dict:
    reactions = {}
    if message.reactions and message.reactions.results:
        for reaction in message.reactions.results:
            if isinstance(reaction.reaction, ReactionEmoji):
                key = reaction.reaction.emoticon
            elif isinstance(reaction.reaction, ReactionCustomEmoji):
                key = f"CustomEmoji_{reaction.reaction.document_id}"
            elif isinstance(reaction.reaction, ReactionPaid):
                key = "PaidReaction"
            else:
                key = str(reaction.reaction)
            reactions[key] = reaction.count
    return reactions

async def process_media(message, img_flag: bool) -> tuple:
    content = message.text.strip() if message.text else ""
    media_base64 = None
    if message.media and img_flag:
        content += " [Hình ảnh/Tệp đính kèm]"
        try:
            file = await client.download_media(message, BytesIO())
            if file:
                media_base64 = base64.b64encode(file.getvalue()).decode("utf-8")
        except Exception as e:
            logger.warning(f"Error downloading media: {e}")
    return content, media_base64

async def fetch_messages(chat_id: str, offset_date: datetime, end_date: datetime, keyword: str,
                         limit: int, img_flag: bool, topic_id: int, fetch_username: bool, 
                         from_user: str, channel_id: int = None) -> dict:
    messages = []
    offset_date_utc = offset_date.astimezone(timezone.utc) if offset_date else None
    end_date_utc = end_date.astimezone(timezone.utc) if end_date else None

    try:
        async with client:
            entity, link_prefix = await get_entity(chat_id, channel_id)
            async for message in client.iter_messages(
                entity=entity,
                limit=limit,
                offset_date=offset_date_utc,
                search=keyword or None,
                from_user=from_user,
                reply_to=topic_id,
                wait_time=1 if limit > 3000 else None
            ):
                if end_date_utc and message.date < end_date_utc:
                    break

                user_name, user_id = await get_sender_info(message, fetch_username, from_user)
                reactions = process_reactions(message)
                total_reactions = (message.views or 0) + sum(reactions.values())
                content, media_base64 = await process_media(message, img_flag)
                message_date_vn = message.date.astimezone(VN_TZ)

                msg_data = {
                    "message_id": message.id,
                    "chat_id": chat_id if not channel_id else None,
                    "channel_id": channel_id if channel_id else None,
                    "date": message.date.isoformat(),
                    "date_vn": message_date_vn.isoformat(),
                    "text": content,
                    "views": message.views,
                    "reactions": reactions or None,
                    "total_reactions": total_reactions,
                    "message_link": f"{link_prefix}/{message.id}",
                    "media_base64": media_base64,
                    "user_name": user_name,
                    "user_id": user_id,
                    "reply_to_msg_id": message.reply_to.reply_to_msg_id if message.reply_to else None,
                    "reply_to_top_id": message.reply_to.reply_to_top_id if message.reply_to else None,
                    "forum_topic": message.reply_to.forum_topic if message.reply_to else None,
                }
                messages.append(msg_data)

            if messages:
                try:
                    messages_collection.insert_many(messages)
                except PyMongoError as e:
                    logger.error(f"Error saving to MongoDB: {e}")

            return {"status": "success", "data": convert_objectid(messages)}

    except ValueError as e:
        return {"error": str(e).split(":")[0], "details": str(e)}
    except telethon.errors.FloodWaitError as e:
        logger.error(f"Flood wait: {e.seconds} seconds")
        return {"error": "Flood wait", "details": f"Wait {e.seconds} seconds"}
    except telethon.errors.RPCError as e:
        logger.error(f"Telegram API error: {e}")
        return {"error": "Telegram API error", "details": str(e)}
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        return {"error": "Unknown error", "details": str(e)}
    
async def get_all_channels():
    channels = []
    try:
        async with client:
            async for dialog in client.iter_dialogs(archived=False):
                # if dialog.is_channel:
                    entity = dialog.entity
                    channel_info = {
                        "id": dialog.id,
                        "title": dialog.title,
                        "username": getattr(entity, 'username', None) or "None",
                        "members": getattr(entity, 'participants_count', "Unknown"),
                        "access_hash": getattr(entity, 'access_hash', None),
                        "is_public": bool(getattr(entity, 'username', None))
                    }
                    channels.append(channel_info)

        return {"status": "success", "data": channels} if channels else {"status": "success", "data": [], "message": "No channels found"}

    except Exception as e:
        logger.error(f"Error fetching channels: {e}")
        return {"status": "error", "details": str(e)}
    
async def send_message_to_telegram(recipient: str, text: str, files: List[UploadFile] = None):
    try:
        async with client:
            if files:
                media = []
                for f in files:
                    file_bytes = await f.read()
                    bio = BytesIO(file_bytes)
                    bio.name = f.filename
                    media.append(bio)
                await client.send_file(recipient, media, caption=text, grouped=True)
            else:
                await client.send_message(recipient, text)
            return {"status": "success", "message": "Message sent successfully"}
    except FloodWaitError as e:
        return {"status": "error", "message": f"Flood wait: Please wait {e.seconds} seconds"}
    except RPCError as e:
        return {"status": "error", "message": f"Telegram API error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}