from datetime import datetime
from typing import List

from pydantic import BaseModel
from uuid import UUID

class CommentResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    user_id: UUID
    post_id: UUID

class CommentContent(BaseModel):
    content: str

class ListCommentContent(BaseModel):
    content: List[CommentResponse]
    count: int
