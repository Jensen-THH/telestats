import os
from dotenv import load_dotenv
from pymongo import MongoClient
from app.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["telegram_stats"]
messages_collection = db["messages"]
print(MONGO_URI)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
try:
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Connection failed:", e)
# # Kiểm tra kết nối
if __name__ == "__main__":
    print("✅ Kết nối MongoDB thành công!")