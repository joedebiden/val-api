from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session

from app.core.utils import jwt_user_id, upload_picture_util
from app.models.models import Post, User, Follow, Like, Comment
from app.core.database import get_db
from app.schemas.comment import CommentDTO
from app.schemas.like import LikeDTO
from app.schemas.post import PostDTO, PostDetailResponse, FeedResponse, EditPayload, FeedDetailResponse
from sqlalchemy import func

router = APIRouter(prefix="/post", tags=["post"])


@router.post("/upload", response_model=PostDTO)
async def upload_post(
        caption: Optional[str] = Form(None),
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Upload a post with picture and description"""
    if not user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to post")
    filename = upload_picture_util(file)
    new_post = Post(image_url=filename, caption=caption, user_id=user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    user = db.get(User, user_id)
    return PostDTO(
        id=new_post.id, image_url=new_post.image_url,
        caption=new_post.caption, user_id=user_id,
        username=user.username, user_profile=user.profile_picture,
        created_at=new_post.created_at, hidden_tag=new_post.hidden_tag
    )



@router.get("/feed/global", response_model=FeedResponse)
def global_feed(
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """ Feed post management. As a reminder, the feed is the page that gathers
        all recent posts, so it's just a huge fetch of the all most recent
        posts, and on the frontend if the person scrolls to the eighth one, it triggers another request"""
    if not user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to post")
    posts = db.query(Post).filter_by(hidden_tag=False).order_by(Post.created_at.desc()).all()
    content = []
    for p in posts:
        u = db.get(User, p.user_id)
        content.append(PostDTO(
            id=p.id, image_url=p.image_url,
            caption=p.caption, user_id=p.user_id,
            username=u.username, user_profile=u.profile_picture,
            created_at=p.created_at, hidden_tag=p.hidden_tag
        ))
    return FeedResponse(
        message="Feed loaded",
        content=content)

@router.delete("/delete/{post_id}")
def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Delete a post that you own"""
    p = db.get(Post, post_id)
    if not p:
        raise HTTPException(404, "Post not found")
    if p.user_id != user_id:
        raise HTTPException(403, "Unauthorized to delete")
    db.delete(p)
    db.commit()
    return {"message": "Post deleted successfully"}

@router.post("/edit/{post_id}", response_model=PostDTO)
def edit_post(
        post_id: int,
        payload: EditPayload,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Edit a post: caption and tag that you own only"""
    p = db.get(Post, post_id)
    if not p:
        raise HTTPException(404, "Post not found")
    if p.user_id != user_id:
        raise HTTPException(403, "Unauthorized to edit")
    caption = payload.caption
    hidden = payload.hidden_tag
    if caption and len(caption) > 500:
        raise HTTPException(400, "Caption too long")
    if caption is not None:
        p.caption = caption
    if hidden is not None:
        p.hidden_tag = hidden
    db.commit()
    db.refresh(p)
    user = db.get(User, p.user_id)
    return PostDTO(
        id=p.id, image_url=p.image_url,
        caption=p.caption, user_id=p.user_id,
        username=user.username, user_profile=user.profile_picture,
        created_at=p.created_at, hidden_tag=p.hidden_tag
    )


@router.get("/feed", response_model=FeedResponse)
def personal_feed(
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Feed of the home page, fetch all content of followed users of the current user and do not display the content that are hidden"""
    if not user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to post")
    followed = db.query(Follow.followed_id).filter(Follow.follower_id == user_id).subquery()
    posts = db.query(Post).filter(Post.user_id.in_(followed.select()), Post.hidden_tag==False).order_by(Post.created_at.desc()).all()
    content = []
    for p in posts:
        u = db.get(User, p.user_id)
        content.append(PostDTO(
            id=p.id, image_url=p.image_url,
            caption=p.caption, user_id=p.user_id,
            username=u.username, user_profile=u.profile_picture,
            created_at=p.created_at, hidden_tag=p.hidden_tag
        ))
    return FeedResponse(message="Feed loaded", content=content)


@router.get("/feed/{username}", response_model=FeedDetailResponse)
def user_feed(
        username: str,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """ Retrieve posts from a specific user (e.g., user profile).
        Get all posts including hidden ones if it's the concerned
        user (token jwt = user_id), otherwise only display the user's public posts."""
    target = db.query(User).filter_by(username=username).first()
    if not target:
        raise HTTPException(status_code=403, detail="You are not allowed to post")
    posts = db.query(Post).filter(Post.user_id == target.id)
    if target.id != user_id:
        posts = posts.filter_by(hidden_tag=False)
    posts = posts.order_by(Post.created_at.desc()).all()
    content = []
    for p in posts:
        u = db.get(User, p.user_id)

        content.append(PostDetailResponse(
            post=PostDTO(
                id=p.id, image_url=p.image_url,
                caption=p.caption, user_id=p.user_id,
                username=u.username, user_profile=u.profile_picture,
                created_at=p.created_at, hidden_tag=p.hidden_tag,
            ),
            likes=[LikeDTO(
                id=l.id,
                post_id=l.post_id,
                user_id=l.user_id,
                created_at=l.created_at
            ) for l in db.query(Like).filter_by(post_id=p.id) ],
            comments=[CommentDTO(
                id=c.id,
                post_id=c.post_id,
                user_id=c.user_id,
                content=c.content,
                created_at=c.created_at
            ) for c in db.query(Comment).filter_by(post_id=p.id
            )],
        ))
    return FeedDetailResponse(
        message="Posts found",
        content=content
    )



@router.get("/{post_id}", response_model=PostDetailResponse)
def show_post(
        post_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Return all the post info with post_id in param"""
    if not user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to see the post")
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    user = db.get(User, post.user_id)

    return PostDetailResponse(
        message="Post found",
        post=PostDTO(
            id=post.id, image_url=post.image_url,
            caption=post.caption, user_id=post.user_id,
            username=user.username, user_profile=user.profile_picture,
            created_at=post.created_at, hidden_tag=post.hidden_tag,
        ),
        likes=[LikeDTO(
            id=l.id,
            post_id=l.post_id,
            user_id=l.user_id,
            created_at=l.created_at
        ) for l in db.query(Like).filter_by(post_id=post_id)],
        comments=[CommentDTO(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            content=c.content,
            created_at=c.created_at
        ) for c in db.query(Comment).filter_by(post_id=post_id)]
    )
