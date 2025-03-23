from app.database import messages_collection
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.utils.helper import convert_objectid

async def get_messages_from_db22(filterQuery=None, sort_by=None, limit=None, page=0, perPage=10):
    try:
        query = filterQuery or {}
        cursor = messages_collection.find(query).skip(perPage * page).limit(perPage)

        if sort_by:
            cursor = cursor.sort(sort_by)

        if limit:
            cursor = cursor.limit(limit)

        messages = [{**msg, "_id": str(msg["_id"])} for msg in cursor]
        total = messages_collection.count_documents(query)
        total_page = total // perPage + 1
        return {"status": "success", "data": messages, "total": total, "total_page": total_page}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def delete_messages_by_id(message_id: str):
    try:
        message_id = ObjectId(message_id)
        result = messages_collection.delete_one({"_id": message_id})
        return {"status": "success", "data": result.deleted_count}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
async def delete_messages_by_ids(message_ids: list):
    try:
        message_ids = [ObjectId(id) for id in message_ids]
        result = messages_collection.delete_many({"_id": {"$in": message_ids}})
        return {"status": "success", "data": result.deleted_count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def get_messages_from_db(
    page=0,
    perPage=10,
    filterQuery=None,
    sort_by=None,
    limit=None,
):
    try:
        query = filterQuery or {}
        cursor = messages_collection.find(query).skip(perPage * page).limit(perPage)

        if sort_by:
            sort_direction = -1 if sort_by.startswith("-") else 1
            sort_field = sort_by[1:] if sort_by.startswith("-") else sort_by
            cursor = cursor.sort(sort_field, sort_direction)

        if limit:
            cursor = cursor.limit(limit)

        messages = [{**msg, "_id": str(msg["_id"])} for msg in cursor]
        total = messages_collection.count_documents(query)
        total_page = total // perPage + 1 if total > 0 else 1
        
        return {
            "status": "success",
            "data": messages,
            "total": total,
            "total_page": total_page
        }
    except PyMongoError as e:
        return {"status": "error", "message": f"MongoDB error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
