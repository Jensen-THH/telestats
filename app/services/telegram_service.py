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

VN_TZ = timezone(timedelta(hours=7))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_messages(chat_id: str, offset_date: datetime.datetime, end_date: datetime.datetime, keyword: str,
                         limit: int, img_flag: bool, topic_id: int, fetch_username: bool, from_user: str):
    messages = []

    offset_date_utc = offset_date.astimezone(timezone.utc) if offset_date else None
    end_date_utc = end_date.astimezone(timezone.utc) if end_date else None

    try:
        async with client:
            search_query = keyword if keyword else None
            wait_time = 1 if limit > 3000 else None

            async for message in client.iter_messages(
                    entity=chat_id,
                    limit=limit,
                    offset_date=offset_date_utc,
                    search=search_query,
                    from_user=from_user,
                    reply_to=topic_id,
                    wait_time=wait_time
            ):
                if end_date_utc and message.date < end_date_utc:
                    break

                user_name = None
                user_id = None
                if fetch_username and message.from_id:
                    try:
                        sender = await message.get_sender()
                        user_name = sender.username or str(message.from_id.user_id) if sender else str(message.from_id.user_id)
                    except Exception as e:
                        logger.warning(f"Lỗi khi lấy sender cho message {message.id}: {e}")
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

                total_reactions = (message.views or 0) + sum(reactions.values())
                content = message.text.strip() if message.text else ""
                media_base64 = None
                if message.media and img_flag:
                    content += " [Hình ảnh/Tệp đính kèm]"
                    try:
                        file = await client.download_media(message, BytesIO())
                        if file:
                            media_base64 = base64.b64encode(file.getvalue()).decode("utf-8")
                    except Exception as e:
                        logger.warning(f"Lỗi khi tải media: {e}")

                message_date_vn = message.date.astimezone(VN_TZ)
                msg_data = {
                    "message_id": message.id,
                    "chat_id": chat_id,
                    "date": message.date.isoformat(),
                    "date_vn": message_date_vn.isoformat(),
                    "text": content,
                    "views": message.views,
                    "reactions": reactions or None,
                    "total_reactions": total_reactions,
                    "message_link": f"https://t.me/{chat_id}/{message.id}",
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
                logger.error(f"Lỗi khi lưu vào MongoDB: {e}")

        return {"status": "success", "data": convert_objectid(messages)}

    except telethon.errors.FloodWaitError as e:
        logger.error(f"Flood wait: {e.seconds} giây")
        return {"error": "Flood wait", "details": f"Chờ {e.seconds} giây"}
    except telethon.errors.RPCError as e:
        logger.error(f"Lỗi từ Telegram API: {e}")
        return {"error": "Lỗi từ Telegram API", "details": str(e)}
    except Exception as e:
        logger.error(f"Lỗi không xác định: {e}")
        return {"error": "Lỗi không xác định", "details": str(e)}