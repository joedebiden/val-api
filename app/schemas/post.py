from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class PostResponse(BaseModel):
    id: UUID
    image_url: str
    caption: Optional[str]
    user_id: UUID
    username: str
    user_profile: Optional[str]
    created_at: datetime
    hidden_tag: bool

    class ConfigDict:
        from_attributes = True

class PostDetailResponse(BaseModel):
    message: Optional[str] = None
    post: PostResponse
    likes: dict
    comments: dict

class FeedResponse(BaseModel):
    message: str
    content: List[PostResponse]

class EditPayload(BaseModel):
    caption: str
    hidden_tag: bool

class FeedDetailResponse(BaseModel):
    message: str
    content: List[PostDetailResponse]
