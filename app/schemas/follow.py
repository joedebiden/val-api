from pydantic import BaseModel

class FollowResponse(BaseModel):
    id: int
    follow_id: str
    followed_id: str
    created_at: str

class FollowUserOut(BaseModel):
    id: int
    username: str
    profile_picture: str | None
    followed_at: str
