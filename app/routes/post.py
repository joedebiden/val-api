from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.utils import get_user_id_from_jwt, upload_picture_util
from app.models.models import Post, User, Follow, Like, Comment
from app.core.database import get_db
from app.schemas.post import PostResponse, PostDetailResponse, FeedResponse, EditPayload, FeedDetailResponse
from sqlalchemy import func

router = APIRouter(prefix="/post", tags=["post"])

"""
Upload a post with picture and description
"""
@router.post("/upload", response_model=PostResponse)
async def upload_post(
        caption: Optional[str] = None,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_id: str = Depends(get_user_id_from_jwt)
):
    if not user_id:
        raise HTTPException(401, "Not authorized")
    filename = upload_picture_util(file)
    new_post = Post(image_url=filename, caption=caption, user_id=user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    user = db.get(User, user_id)
    return PostResponse(
        id=new_post.id, image_url=new_post.image_url,
        caption=new_post.caption, user_id=str(user_id),
        username=user.username, user_profile=user.profile_picture,
        created_at=new_post.created_at, hidden_tag=new_post.hidden_tag
    )


"""
Feed post management. As a reminder, the feed is the page that gathers
all recent posts, so it's just a huge fetch of the all most recent
posts, and on the frontend if the person scrolls to the eighth one, it triggers another request
"""
@router.get("/feed/global", response_model=FeedResponse) # TODO: Pagination fetch
def global_feed(db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    if not user_id:
        raise HTTPException(401, "Not authorized")
    posts = db.query(Post).filter_by(hidden_tag=False).order_by(Post.created_at.desc()).all()
    content = []
    for p in posts:
        u = db.get(User, p.user_id)
        content.append(PostResponse(
            id=p.id, image_url=p.image_url, caption=p.caption,
            user_id=p.user_id, username=u.username,
            user_profile=u.profile_picture,
            created_at=p.created_at, hidden_tag=p.hidden_tag
        ))
    return FeedResponse(message="Feed loaded", content=content)

"""
Delete a post
"""
@router.delete("/delete/{post_id}")
def delete_post(post_id: UUID, db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    p = db.get(Post, post_id)
    if not p:
        raise HTTPException(404, "Post not found")
    if str(p.user_id) != user_id:
        raise HTTPException(403, "Unauthorized to delete")
    db.delete(p)
    db.commit()
    return {"message": "Post deleted successfully"}

"""
Edit a post : caption and tag
"""
@router.post("/edit/{post_id}", response_model=PostResponse)
def edit_post(post_id: UUID, payload: EditPayload, db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    p = db.get(Post, post_id)
    if not p:
        raise HTTPException(404, "Post not found")
    if str(p.user_id) != user_id:
        raise HTTPException(403, "Unauthorized to edit")
    caption = payload.caption
    hidden = payload.hidden_tag
    if caption and len(caption) > 200:
        raise HTTPException(400, "Caption too long")
    if caption is not None:
        p.caption = caption
    if hidden is not None:
        p.hidden_tag = hidden
    db.commit()
    db.refresh(p)
    user = db.get(User, p.user_id)
    return PostResponse(
        id=str(p.id),
        image_url=p.image_url,
        caption=p.caption,
        user_id=str(p.user_id),
        username=user.username,
        user_profile=user.profile_picture,
        created_at=p.created_at,
        hidden_tag=p.hidden_tag
    )

"""
Feed of the home page, fetch all content of followed users of the current user
and do not display the content that are hidden
"""
@router.get("/feed", response_model=FeedResponse) # TODO: Pagination fetch
def personal_feed(db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    if not user_id:
        raise HTTPException(401, "Not authorized")
    followed = db.query(Follow.followed_id).filter(Follow.follower_id == user_id).subquery()
    posts = db.query(Post).filter(Post.user_id.in_(followed.select()), Post.hidden_tag==False).order_by(Post.created_at.desc()).all()
    content = []
    for p in posts:
        u = db.get(User, p.user_id)
        content.append(PostResponse(
            id=p.id, image_url=p.image_url, caption=p.caption,
            user_id=p.user_id, username=u.username, user_profile=u.profile_picture,
            created_at=p.created_at, hidden_tag=p.hidden_tag
        ))
    return FeedResponse(message="Feed loaded", content=content)

"""
Retrieve posts from a specific user (e.g., user profile). 
Get all posts including hidden ones if it's the concerned 
user (token jwt = user_id), otherwise only display the user's public posts.
"""
@router.get("/feed/{username}", response_model=FeedDetailResponse) # TODO: Pagination fetch
def user_feed(
        username: str,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_user_id_from_jwt)
):
    target = db.query(User).filter_by(username=username).first()
    if not target:
        raise HTTPException(404, "User not found")
    posts = db.query(Post).filter(Post.user_id == target.id)
    if str(target.id) != user_id:
        posts = posts.filter_by(hidden_tag=False)
    posts = posts.order_by(Post.created_at.desc()).all()
    content = []
    for p in posts:
        u = db.get(User, p.user_id)

        likes_count = db.query(func.count(Like.id)).filter(Like.post_id == p.id).scalar()
        comments_count = db.query(func.count(Comment.id)).filter(Comment.post_id == p.id).scalar()

        content.append(PostDetailResponse(
            post=PostResponse(
                id=p.id,
                image_url=p.image_url,
                caption=p.caption,
                user_id=p.user_id,
                username=u.username,
                user_profile=u.profile_picture,
                created_at=p.created_at,
                hidden_tag=p.hidden_tag,
            ),
            likes={"count": likes_count},
            comments={"count": comments_count},
        ))

    return FeedDetailResponse(
        message="Posts found",
        content=content
    )


"""
Return all the post info with post_id in param
"""
@router.get("/{post_id}", response_model=PostDetailResponse)
def show_post(post_id: UUID, db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    user = db.get(User, post.user_id)
    likes_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    comments_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post_id).scalar()
    likes_list = [{'like_id': l.id} for l in db.query(Like).filter_by(post_id=post_id)]
    comment_list = [{'comment_id': c.id} for c in db.query(Comment).filter_by(post_id=post_id)]

    return PostDetailResponse(
        message="Post found",
        post=PostResponse(
            id=post.id,
            image_url=post.image_url,
            caption=post.caption,
            user_id=post.user_id,
            username=user.username,
            user_profile=user.profile_picture,
            created_at=post.created_at,
            hidden_tag=post.hidden_tag,
        ),
        likes={'likes_count': likes_count, 'likes_list': likes_list},
        comments={'comments_count': comments_count, 'comments': comment_list}
    )
