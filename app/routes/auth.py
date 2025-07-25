from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.utils import decode_jwt
from app.models.models import User
from app.core.config import settings
from app.schemas.auth import RegisterRequest, LoginRequest, TokenRequest, AuthResponse, MessageResponse
from passlib.hash import argon2
import jwt
import datetime


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username
    email = data.email
    password = data.password

    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(status_code=400, detail="username or email already exists.")

    try:
        hashed_password = argon2.hash(password)
        new_user = User(username=username, email=str(email), password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        return {"message": "account created successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"an error occurred: {str(e)}")

@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter_by(username=data.username).first()
    if user and argon2.verify(data.password, user.password_hash):
        token = jwt.encode({
            "id": str(user.id),
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        }, settings.SECRET_KEY, algorithm="HS256")

        return {
            "token": token,
            "user_id": str(user.id),
            "username": data.username,
            "profile_picture": user.profile_picture
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/token")
def token(data: TokenRequest):
    user_data = decode_jwt(data.token)
    if user_data:
        return {"valid": True}
    raise HTTPException(status_code=401, detail="Invalid token")
