from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.utils import jwt_user_id
from app.models.models import Post, Comment, User
from app.schemas.comment import CommentDTO, CommentContent, ListCommentContent
from app.schemas.user import UserLightDTO

router = APIRouter(prefix="/comment", tags=["Comments"])


@router.post("/{post_id}", response_model=CommentDTO)
def comment(
        post_id: int,
        payload: CommentContent,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Add a comment on a post : params post_id"""
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    if len(payload.content) > 500:
        raise HTTPException(status_code=400, detail="Comment too long")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_comment = Comment(
        content=payload.content,
        post_id=post.id,
        user_id=user_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentDTO(
        id=new_comment.id, content=new_comment.content,
        created_at=new_comment.created_at, post_id=new_comment.post_id,
        user=UserLightDTO(
            id=user_id,
            username=user.username,
            profile_picture=user.profile_picture
        )
    )

@router.delete("/{comment_id}")
def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Delete a comment on a post : params comment_id"""
    comment = db.query(Comment).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete")
    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted",
        "comment_id": CommentDTO(
            id=comment.id, content=comment.content,
            created_at=comment.created_at, post_id=comment.post_id,
            user=UserLightDTO(
                id=comment.user_id,
                username=db.get(User, comment.user_id).username,
                profile_picture=db.get(User, comment.user_id).profile_picture
            )
        )
    }


@router.get("/{post_id}", response_model=ListCommentContent)
def get_comment_post(
        post_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Get all comments in a post"""
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to see comments")

    all_comments = db.query(Comment).filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    return ListCommentContent(
        contents=[
            CommentDTO(
                id=c.id, content=c.content,
                created_at=c.created_at,
                user=UserLightDTO(
                    id=c.user_id,
                    username=db.get(User, c.user_id).username,
                    profile_picture=db.get(User, c.user_id).profile_picture
                ),
                post_id=c.post_id
            ) for c in all_comments
        ],
        count=len(all_comments)
    )

@router.patch("/{comment_id}", response_model=CommentDTO)
def update_comment(
        payload: CommentContent,
        comment_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Edit a comment, only by its author"""
    commentary = db.query(Comment).filter_by(id=comment_id).first()
    if not commentary:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    if commentary.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to edit")
    if len(payload.content) > 500:
        raise HTTPException(status_code=400, detail="Comment too long")
    commentary.content = payload.content
    db.commit()
    db.refresh(commentary)
    return CommentDTO(
        id=commentary.id, content=commentary.content,
        created_at=commentary.created_at, post_id=commentary.post_id,
        user=UserLightDTO(
            id=user_id,
            username=db.get(User, user_id).username,
            profile_picture=db.get(User, user_id).profile_picture
        )
    )


@router.get("/current/all")
def get_all_comments(
        user_id: int = Depends(jwt_user_id),
        db: Session = Depends(get_db)
):
    """Get all comments of the current user"""
    if not user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to see comments")
    all_comments = db.query(Comment).filter_by(user_id=user_id).all()
    return ListCommentContent(
        contents=[
            CommentDTO(
                id=c.id, content=c.content,
                created_at=c.created_at, user=UserLightDTO(
                    id=c.user_id,
                    username=db.get(User, c.user_id).username,
                    profile_picture=db.get(User, c.user_id).profile_picture
                ),
                post_id=c.post_id
            ) for c in all_comments
        ],
        count=len(all_comments)
    )
