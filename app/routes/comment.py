from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.utils import get_user_id_from_jwt
from app.models.models import Post, Comment
from app.schemas.comment import CommentResponse, CommentContent, ListCommentContent

router = APIRouter(prefix="/comment", tags=["Comments"])

"""Add a comment on a post"""
@router.put("/{post_id}", response_model=CommentResponse)
def comment(
        post_id: UUID,
        payload: CommentContent,
        db: Session = Depends(get_db),
        user_id: UUID = Depends(get_user_id_from_jwt)
):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    if len(payload.content) > 1000:
        raise HTTPException(status_code=400, detail="Comment too long")

    new_comment = Comment(content=payload.content, post_id=post.id, user_id=user_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentResponse(
        id=new_comment.id,
        content=new_comment.content,
        created_at=new_comment.created_at,
        post_id=new_comment.post_id,
        user_id=new_comment.user_id
    )

"""Delete a comment on a post"""
@router.delete("/delete/{comment_id}")
def delete_comment(
        comment_id: UUID,
        db: Session = Depends(get_db),
        user_id: UUID = Depends(get_user_id_from_jwt)
):
    comment = db.query(Comment).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    if str(comment.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete")
    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted",
        "comment_id": comment_id
    }

"""Get all comments in a post"""
@router.get("/{post_id}/contents")
def get_comment_post(
        post_id: UUID,
        db: Session = Depends(get_db),
        user_id: UUID = Depends(get_user_id_from_jwt)
):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    all_comments = db.query(Comment).filter_by(post_id=post.id).all()
    return ListCommentContent(
        content=[
            CommentResponse(
                id=c.id,
                content=c.content,
                created_at=c.created_at,
                user_id=c.user_id,
                post_id=c.post_id
            ) for c in all_comments
        ],
        count=len(all_comments)
    )

"""Get all comments of the current user"""
@router.get("/all")
def get_all_comments(
        user_id: UUID = Depends(get_user_id_from_jwt),
        db: Session = Depends(get_db)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    all_comments = db.query(Comment).filter_by(user_id=user_id).all()
    return ListCommentContent(
        content=[
            CommentResponse(
                id=c.id,
                content=c.content,
                created_at=c.created_at,
                user_id=c.user_id,
                post_id=c.post_id
            ) for c in all_comments
        ],
        count=len(all_comments)
    )
