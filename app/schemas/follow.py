from pydantic import BaseModel

class FollowResponse(BaseModel):
    id: str
    follow_id: str
    followed_id: str
    created_at: str

class FollowUserOut(BaseModel):
    id: str
    username: str
    profile_picture: str | None
    followed_at: str
