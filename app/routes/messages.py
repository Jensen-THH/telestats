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
        start_date: datetime = Query(None),
        end_date: datetime = Query(None),
        keyword: str = Query(None),
        limit: int = Query(100, gt=0, le=1000),
        img_flag: bool = Query(False),
        topic_id: int = Query(None),
        username_filter: str = Query(None),
):
    # Xử lý timezone của start_date
    if start_date:
        if start_date.tzinfo is None:
            start_date = vietnam_tz.localize(start_date)  # Gán timezone VN nếu chưa có
        start_date = start_date.astimezone(timezone.utc)  # Chuyển sang UTC

    # Xử lý timezone của end_date
    if end_date:
        if end_date.tzinfo is None:
            end_date = vietnam_tz.localize(end_date)  # Gán timezone VN nếu chưa có
        end_date = end_date.astimezone(timezone.utc)  # Chuyển sang UTC

    result = await fetch_messages(chat_id, start_date, end_date, keyword, limit, img_flag, topic_id, username_filter)

    return result
