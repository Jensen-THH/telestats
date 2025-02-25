from pydantic import BaseModel
from typing import List, Optional

class MessageSchema(BaseModel):
    message_id: int
    text: str
    views: Optional[int] = 0
    reactions: Optional[List[str]] = []
    comments: Optional[int] = 0
    date: str
