from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.schemas.user import UserLightDTO


class CommentDTO(BaseModel):
    id: int
    content: str
    created_at: datetime
    post_id: int
    user: UserLightDTO

class CommentContent(BaseModel):
    content: str # mandatory for the payload

class ListCommentContent(BaseModel):
    contents: List[CommentDTO]
    count: int
