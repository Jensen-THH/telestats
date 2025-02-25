import telethon
from telethon.tl.types import Message
from app.telegram_client import client
from app.database import messages_collection
import datetime
import base64
from io import BytesIO
from app.utils.helper import convert_objectid
from pymongo.errors import PyMongoError
import logging
from datetime import timezone, timedelta

# Định nghĩa múi giờ UTC+7
VN_TZ = timezone(timedelta(hours=7))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_messages(chat_id: str, start_date: datetime.datetime, end_date: datetime.datetime, keyword: str,
                         limit: int, img_flag: bool, topic_id: int, username_filter: str = None):
    messages = []

    try:
        async with client:
            async for message in client.iter_messages(
                    chat_id,
                    limit=limit,
                    reply_to=topic_id,
                    from_user=username_filter,
                    offset_date=start_date,  # Truy vấn với UTC
            ):
                try:
                    # Dừng nếu tin nhắn quá cũ hơn end_date_utc
                    # if start_date and message.date > start_date:
                    #     break

                    # Kiểm tra keyword
                    if keyword and keyword.lower() not in (message.text or "").lower():
                        continue

                    # Lấy thông tin người gửi
                    username = "Unknown"
                    try:
                        sender = await message.get_sender()
                        if sender and sender.username:
                            username = sender.username
                    except Exception as e:
                        logger.warning(f"Lỗi khi lấy sender: {e}")

                    # Xử lý reactions
                    reactions = {}
                    if message.reactions:
                        for reaction in message.reactions.results:
                            if isinstance(reaction.reaction, telethon.tl.types.ReactionEmoji):
                                key = reaction.reaction.emoticon
                            elif isinstance(reaction.reaction, telethon.tl.types.ReactionCustomEmoji):
                                key = f"CustomEmoji_{reaction.reaction.document_id}"
                            else:
                                key = "Unknown"
                            reactions[key] = reaction.count

                    total_reactions = (message.views or 0) + sum(reactions.values()) if reactions else (message.views or 0)

                    # Xử lý nội dung tin nhắn
                    content = message.text if message.text else ""
                    media_base64 = None

                    if message.media and img_flag:
                        content += " [Hình ảnh/Tệp đính kèm]"
                        try:
                            file = await client.download_media(message, BytesIO())
                            if file:
                                media_base64 = base64.b64encode(file.getvalue()).decode("utf-8")
                        except Exception as e:
                            logger.warning(f"Lỗi khi tải media: {e}")

                    # Chuyển message.date về UTC+7
                    message_date_vn = message.date.astimezone(VN_TZ)

                    # Dữ liệu tin nhắn
                    msg_data = {
                        "message_id": message.id,
                        "chat_id": chat_id,
                        "date":message.date.isoformat(),
                        "date_vn": message_date_vn.isoformat(),  # Lưu datetime theo UTC+7
                        "text": content.strip(),
                        "views": message.views,
                        "reactions": reactions if reactions else None,
                        "total_reactions": total_reactions,
                        "message_link": f"https://t.me/{chat_id}/{message.id}",
                        "media_base64": media_base64,
                        "user_name": username,
                    }

                    messages.append(msg_data)

                    # Lưu vào MongoDB
                    try:
                        messages_collection.insert_one(msg_data)
                    except PyMongoError as e:
                        logger.error(f"Lỗi khi lưu vào MongoDB: {e}")

                except Exception as e:
                    logger.error(f"Lỗi xử lý tin nhắn {message.id} trong {chat_id}: {e}")

        return {"status":"success", "data": convert_objectid(messages) }

    except telethon.errors.RPCError as e:
        logger.error(f"Lỗi từ Telegram API: {e}")
        return {"error": "Lỗi từ Telegram API", "details": str(e)}
    except Exception as e:
        logger.error(f"Lỗi không xác định: {e}")
        return {"error": "Lỗi không xác định", "details": str(e)}
