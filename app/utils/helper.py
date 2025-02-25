from bson import ObjectId

def convert_objectid(document):
    """Chuyển đổi ObjectId thành string trong MongoDB document"""
    if isinstance(document, list):
        return [{**doc, "_id": str(doc["_id"])} for doc in document]
    if isinstance(document, dict):
        document["_id"] = str(document["_id"])
        return document
    return document
