from app.database import messages_collection
# from bson import ObjectId

from bson import ObjectId

from app.utils.helper import convert_objectid
def save_message(message_data):
    try:
        result = messages_collection.insert_many(message_data)
        print(f"✅ Đã chèn {len(result.inserted_ids)} documents vào MongoDB.")
        message_data = convert_objectid(message_data)
        return {"status": "success", "data": message_data}  
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return {"status": "error", "message": str(e)}
def get_messages_from_db(filter_query=None, sort_by=None, limit=None):
    try:
        query = filter_query or {}
        cursor = messages_collection.find(query)

        if sort_by:
            cursor = cursor.sort(sort_by)

        if limit:
            cursor = cursor.limit(limit)

        messages = [{**msg, "_id": str(msg["_id"])} for msg in cursor]
        return {"status": "success", "data": messages}
    except Exception as e:
        return {"status": "error", "message": str(e)}

