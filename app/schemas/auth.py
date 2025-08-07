from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=20)
    email: EmailStr
    password: constr(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    token: str


class AuthResponse(BaseModel):
    token: str
    user_id: int
    username: str
    profile_picture: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
