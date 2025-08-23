from pydantic import BaseModel
from datetime import datetime

from app.schemas.post import PostLightDTO
from app.schemas.user import UserLightDTO


class LikeDTO(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

class LikedPost(BaseModel):
    post_id: int
    liked_at: datetime

class PostLikesResponse(BaseModel):
    post_id: int
    likes_count: int
    users: list[UserLightDTO]

class LikedPostsByUser(BaseModel):
    user_id: int
    liked_posts: list[PostLightDTO]
    count: int
