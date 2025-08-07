from pydantic import BaseModel
from datetime import datetime


class LikeResponse(BaseModel):
    like_id: int
    post_id: int
    user_id: int
    created_at: datetime

class LikeRemovedResponse(BaseModel):
    like_id_removed: int
    post_id_attached: int
    user_id_from_like: int

class LikedPost(BaseModel):
    post_id: int
    liked_at: datetime

class UserLikeInfo(BaseModel):
    id: int
    username: str
    profile_picture: str | None = None

class PostLikesResponse(BaseModel):
    post_id: int
    likes_count: int
    users: list[UserLikeInfo]
