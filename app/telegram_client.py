import datetime

from fastapi import Query
from telethon import TelegramClient
from app.config import TELEGRAM_API_ID, TELEGRAM_API_HASH, SESSION_NAME
client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)

async def start_client():
    await client.start()

async def stop_client():
    await client.disconnect()


