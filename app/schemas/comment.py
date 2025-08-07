from datetime import datetime
from typing import List

from pydantic import BaseModel

class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user_id: int
    post_id: int

class CommentContent(BaseModel):
    content: str

class ListCommentContent(BaseModel):
    content: List[CommentResponse]
    count: int
