from datetime import datetime

from pydantic import BaseModel

class FollowResponse(BaseModel):
    id: int
    follow_id: int
    followed_id: int
    created_at: datetime

class FollowUserOut(BaseModel):
    id: int
    username: str
    profile_picture: str | None
    followed_at: str
