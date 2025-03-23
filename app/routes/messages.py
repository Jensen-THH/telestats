from typing import Any
from fastapi import APIRouter, Body, Query
from datetime import datetime, timezone
import pytz
from app.services.telegram_service import fetch_messages
from app.services.message_service import get_messages_from_db
from app.services.message_service import delete_messages_by_id
from app.services.telegram_service import get_all_channels
from app.services.message_service import delete_messages_by_ids
from typing import Optional
from typing import List
from fastapi import APIRouter, Form, UploadFile, File
from app.services.telegram_service import send_message_to_telegram
router = APIRouter()

# Định nghĩa múi giờ Việt Nam (UTC+7)
vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")

@router.get("/get_messages/")
async def get_messages(
        chat_id: str = Query(None),
        offset_date: datetime = Query(None),
        end_date: datetime = Query(None),
        keyword: str = Query(None),
        limit: int = Query(100, gt=0, le=1000),
        img_flag: bool = Query(False),
        topic_id: int = Query(None),
        fetch_username: bool = Query(False),
        from_user: str = Query(None),
        channel_id: int = Query(None)
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

    result = await fetch_messages(chat_id, offset_date, end_date, keyword, limit, img_flag, topic_id, fetch_username, from_user, channel_id)

    return result

@router.post("/get_messages_db/")
async def get_messages_db(payload: Any = Body(None)):
    filterQuery = payload.get("filterQuery")
    sort_by = payload.get("sort_by")
    limit = payload.get("limit")
    page = payload.get("page")
    perPage = payload.get("perPage")
    result = await get_messages_from_db(filterQuery, sort_by, limit, page, perPage)
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

@router.post("/messages_db/")
async def get_messages_db(request: Any = Body(None)):
    return await get_messages_from_db(
        page=request.get("page"),
        perPage=request.get("perPage"),
        filterQuery=request.get("filterQuery"),
        sort_by=request.get("sort_by"),
        limit=request.get("limit"),
    )

@router.get("/get_channels/")
async def get_channels():
    return await get_all_channels()

@router.post("/send_message/", summary="Send a message to a Telegram recipient")
async def send_message(
    recipient: str = Form(..., description="The recipient's username, phone number, or ID (e.g., @username, +1234567890, or chat ID)"),
    text: str = Form("", description="The text of the message (can include links, emojis, etc.)"),
    files: List[UploadFile] = File(None, description="Optional files to send (e.g., images, videos)")
):
    """
    Send a message to a Telegram channel, group, or user.
    - Supports text, images, videos, links, and emojis.
    - If files are provided, they are sent as an album with the text as the caption.
    """
    result = await send_message_to_telegram(recipient, text, files)
    return result