from typing import Any
from fastapi import APIRouter, Body, Query
from datetime import datetime, timezone
import pytz
from app.services.telegram_service import fetch_messages
from app.services.message_service import get_messages_from_db
from app.services.message_service import delete_messages_by_id
from app.services.message_service import delete_messages_by_ids

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

@router.post("/get_messages_db/")
async def get_messages_db(payload: Any = Body(None)):
    filter_query = payload.get("filter_query")
    sort_by = payload.get("sort_by")
    limit = payload.get("limit")
    page = payload.get("page")
    perPage = payload.get("perPage")
    result = await get_messages_from_db(filter_query, sort_by, limit, page, perPage)
    return result

@router.delete("/delete_messages/{message_id}")
async def delete_messages(message_id: str):
    result = await delete_messages_by_id(message_id)
    return result

@router.post("/delete_many_messages/")
async def delete_many_messages(payload: Any = Body(None)):
    message_ids = payload.get("message_ids")
    result = await delete_messages_by_ids(message_ids)
    return result

