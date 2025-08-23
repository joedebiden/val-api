from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.utils import jwt_user_id
from app.models.models import Post, Like, User
from app.schemas.like import LikeDTO, PostLikesResponse, LikedPostsByUser
from app.schemas.post import PostLightDTO
from app.schemas.user import UserLightDTO

router = APIRouter(prefix="/like", tags=["Likes"])


@router.post("/{post_id}", response_model=LikeDTO)
def like_post(
        post_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Like a post"""
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if db.query(Like).filter_by(post_id=post_id, user_id=user_id).first():
        raise HTTPException(status_code=400, detail="You have already liked this post")

    new_like = Like(post_id=post_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return LikeDTO(
        id=new_like.id,
        post_id=new_like.post_id,
        user_id=new_like.user_id,
        created_at=new_like.created_at
    )


@router.delete("/{post_id}", response_model=LikeDTO)
def unlike_post(
        post_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Unlike a post"""
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_to_dl = db.query(Like).filter_by(post_id=post_id, user_id=user_id).first()
    if not like_to_dl:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like_to_dl)
    db.commit()

    return LikeDTO(
            id=like_to_dl.id,
            post_id=like_to_dl.post_id,
            user_id=like_to_dl.user_id,
            created_at=like_to_dl.created_at
        )


@router.get("/liked-posts/{user_id}", response_model=LikedPostsByUser)
def get_liked_posts_by_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Fetch all the liked posts of an user"""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    liked_posts = (
        db.query(Post)
        .join(Like, Post.id == Like.post_id)
        .filter(Like.user_id == user_id)
        .options(joinedload(Post.author)) # alternative to lazy='joined'
        .all()
    )

    return LikedPostsByUser(
        user_id=user_id,
        liked_posts=[PostLightDTO(
            id=p.id, image_url=p.image_url,
            caption=p.caption, user_id=p.user_id,
            username=p.author.username, user_profile=p.author.profile_picture,
            created_at=p.created_at, hidden_tag=p.hidden_tag
        ) for p in liked_posts],
        count=len(liked_posts)
    )


@router.get("/get-likes/{post_id}", response_model=PostLikesResponse)
def get_post_likes(
        post_id: int,
        db: Session = Depends(get_db)
):
    """Fetch all the likes and users of a post"""
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
    return PostLikesResponse(
        post_id=post_id,
        likes_count=likes_count,
        users=[
            UserLightDTO(
                id=user.id,
                username=user.username,
                profile_picture=user.profile_picture
            ) for user in users
        ]
    )

