from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostDTO(BaseModel):
    id: int
    image_url: str
    caption: Optional[str]
    user_id: int
    username: str
    user_profile: Optional[str]
    created_at: datetime
    hidden_tag: bool

    class ConfigDict:
        from_attributes = True

class PostDetailResponse(BaseModel):
    message: Optional[str] = None
    post: PostDTO
    likes: dict
    comments: dict

class FeedResponse(BaseModel):
    message: str
    content: List[PostDTO]

class EditPayload(BaseModel):
    caption: str
    hidden_tag: bool

class FeedDetailResponse(BaseModel):
    message: str
    content: List[PostDetailResponse]

class PostLightDTO(BaseModel):
    id: int
    image_url: str
    caption: Optional[str]
    user_id: int
    username: str
    user_profile: Optional[str]
    created_at: datetime

    class ConfigDict:
        from_attributes = True
