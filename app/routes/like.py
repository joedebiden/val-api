from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.utils import get_user_id_from_jwt
from app.models.models import Post, Like, User
from app.schemas.like import LikeResponse, PostLikesResponse, LikedPost, LikeRemovedResponse

router = APIRouter(prefix="/like", tags=["Likes"])

"""Like a post"""
@router.put("/{post_id}", response_model=LikeResponse)
def like_post(post_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if db.query(Like).filter_by(post_id=post_id, user_id=user_id).first():
        raise HTTPException(status_code=400, detail="You have already liked this post")

    new_like = Like(post_id=post_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return {
        "like_id": str(new_like.id),
        "post_id": str(post_id),
        "user_id": str(user_id),
        "created_at": new_like.created_at
    }

"""Unlike a post"""
@router.delete("/{post_id}/unlike", response_model=LikeRemovedResponse)
def unlike_post(post_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_to_dl = db.query(Like).filter_by(post_id=post_id, user_id=user_id).first()
    if not like_to_dl:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like_to_dl)
    db.commit()

    return {
        "like_id_removed": str(like_to_dl.id),
        "post_id_attached": str(post_id),
        "user_id_from_like": str(user_id)
    }

"""Fetch all the liked posts of an user"""
@router.get("/liked-posts/{user_id}", response_model=list[LikedPost])
def get_liked_posts_by_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    liked_posts = (
        db.query(Post, Like.created_at)
        .join(Like, Post.id == Like.post_id)
        .filter(Like.user_id == user_id)
        .all()
    )

    return [
        {"post_id": str(post.id), "liked_at": created_at}
        for post, created_at in liked_posts
    ]

"""Fetch all the likes and users of a post"""
@router.get("/get-likes/{post_id}", response_model=PostLikesResponse)
def get_post_likes(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes_count = db.query(Like).filter(Like.post_id == post_id).count()

    users = (
        db.query(User.id, User.username, User.profile_picture)
        .join(Like, User.id == Like.user_id)
        .filter(Like.post_id == post_id)
        .all()
    )

    return {
        "post_id": str(post_id),
        "likes_count": likes_count,
        "users": [
            {
                "id": str(user.id),
                "username": user.username,
                "profile_picture": user.profile_picture
            } for user in users
        ]
    }
