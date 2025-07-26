from pydantic import BaseModel
from datetime import datetime

from uuid import UUID


class LikeResponse(BaseModel):
    like_id: UUID
    post_id: UUID
    user_id: UUID
    created_at: datetime

class LikeRemovedResponse(BaseModel):
    like_id_removed: UUID
    post_id_attached: UUID
    user_id_from_like: UUID

class LikedPost(BaseModel):
    post_id: UUID
    liked_at: datetime

class UserLikeInfo(BaseModel):
    id: UUID
    username: str
    profile_picture: str | None = None

class PostLikesResponse(BaseModel):
    post_id: UUID
    likes_count: int
    users: list[UserLikeInfo]
