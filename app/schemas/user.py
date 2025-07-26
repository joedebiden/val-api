from uuid import UUID

from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class UserEditRequest(BaseModel):
    username: Optional[constr(max_length=20)]
    email: Optional[EmailStr]
    bio: Optional[constr(max_length=100)]
    website: Optional[constr(max_length=32)]
    gender: Optional[constr(max_length=32)]

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    bio: Optional[str]
    website: Optional[str]
    gender: Optional[str]
    profile_picture: Optional[str]
    created_at: datetime

    class ConfigDict:
        from_attributes = True

class UserSearchItem(BaseModel):
    username: str
    profile_picture: Optional[str]

class UserSearchResponse(BaseModel):
    message: str
    users: List[UserSearchItem]
