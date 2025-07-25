from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.utils import get_user_id_from_jwt, upload_picture_util, UPLOAD_FOLDER
from app.models.models import User
from app.core.database import get_db
from app.schemas.user import UserEditRequest, UserResponse, UserSearchResponse, UserSearchItem
import os

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=UserResponse)
def get_own_profile(
        user_id: str = Depends(get_user_id_from_jwt),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found")
    return user

@router.post("/edit", response_model=UserResponse)
def edit_profile(
        payload: UserEditRequest,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_user_id_from_jwt)
):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found")

    if payload.username and payload.username != user.username:
        if db.query(User).filter_by(username=payload.username).first():
            raise HTTPException(400, detail="Username already taken")
        user.username = payload.username

    if payload.email and payload.email != user.email:
        if db.query(User).filter_by(email=payload.email).first():
            raise HTTPException(400, detail="Email already in use")
        user.email = payload.email

    if payload.bio is not None:
        user.bio = payload.bio
    if payload.website is not None:
        user.website = payload.website
    if payload.gender is not None:
        user.gender = payload.gender

    try:
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=f"Error: {str(e)}")

@router.post("/upload-profile-picture")
async def upload_profile_picture(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_id: int = Depends(get_user_id_from_jwt)
):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found")

    picture = upload_picture_util(file)
    user.profile_picture = picture

    try:
        db.commit()
        return {
            "message": "File uploaded successfully",
            "file_url": f"/user/picture/{picture}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=f"Error: {str(e)}")

@router.get("/picture/{filename}")
def get_profile_picture(filename: str):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        raise HTTPException(404, detail="File not found")
    return FileResponse(path)

@router.get("/profile/{username}", response_model=UserResponse)
def get_profile_by_username(
        username: str,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_user_id_from_jwt)
):
    if not user_id:
        raise HTTPException(400, detail="You must be logged in")

    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(404, detail="User not found")
    return user

@router.get("/search/{username}", response_model=UserSearchResponse)
def search_users(username: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.username.ilike(f"%{username}%")).all()
    if not users:
        raise HTTPException(404, detail="No user found")

    return {
        "message": "Users found",
        "users": [
            UserSearchItem(username=u.username, profile_picture=u.profile_picture)
            for u in users
        ]
    }
