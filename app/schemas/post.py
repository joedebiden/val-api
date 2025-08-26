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
    post: 'PostDTO'
    likes: list
    comments: list
    # avoid circular import issues
    # likes: List['LikeDTO']
    # comments: List['CommentDTO']
    @classmethod
    def create(cls, post, likes, comments):
        from app.schemas.like import LikeDTO
        from app.schemas.comment import CommentDTO
        return cls(
            post=post,
            likes=[LikeDTO.model_validate(l) for l in likes],
            comments=[CommentDTO.model_validate(c) for c in comments]
        )

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
