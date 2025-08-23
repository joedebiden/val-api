from datetime import datetime
from typing import List

from pydantic import BaseModel

class CommentDTO(BaseModel):
    id: int
    content: str
    created_at: datetime
    user_id: int
    post_id: int

class CommentContent(BaseModel):
    content: str # mandatory for the payload

class ListCommentContent(BaseModel):
    contents: List[CommentDTO]
    count: int
