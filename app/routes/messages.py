from fastapi import APIRouter, Query
from datetime import datetime, timezone
import pytz
from app.services.telegram_service import fetch_messages

router = APIRouter()

# Định nghĩa múi giờ Việt Nam (UTC+7)
vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")

@router.get("/get_messages/")
async def get_messages(
        chat_id: str,
        offset_date: datetime = Query(None),
        end_date: datetime = Query(None),
        keyword: str = Query(None),
        limit: int = Query(100, gt=0, le=1000),
        img_flag: bool = Query(False),
        topic_id: int = Query(None),
        fetch_username: bool = Query(False),
        from_user: str = Query(None),
):
    # Xử lý timezone
    if offset_date:
        if offset_date.tzinfo is None:
            offset_date = vietnam_tz.localize(offset_date)  
        offset_date = offset_date.astimezone(timezone.utc)  # Chuyển sang UTC

    if end_date:
        if end_date.tzinfo is None:
            end_date = vietnam_tz.localize(end_date)
        end_date = end_date.astimezone(timezone.utc)  # Chuyển sang UTC

    result = await fetch_messages(chat_id, offset_date, end_date, keyword, limit, img_flag, topic_id, fetch_username, from_user)

    return result
