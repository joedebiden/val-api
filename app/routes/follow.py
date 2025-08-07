from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.utils import jwt_user_id
from app.models.models import User, Follow
from app.schemas.follow import FollowResponse, FollowUserOut

router = APIRouter(prefix="/follow", tags=["Follow"])


@router.put("/{username}", response_model=FollowResponse)
def follow_user(
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id),
        username=str
):
    """Follow an user"""
    other_user = db.query(User).filter_by(username=username).first()

    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    if other_user.id == user_id:
        raise HTTPException(status_code=400, detail="You can't follow yourself")

    already_following = db.query(Follow).filter_by(follower_id=user_id, followed_id=other_user.id).first()
    if already_following:
        raise HTTPException(status_code=400, detail="Already following")

    new_follow = Follow(follower_id=user_id, followed_id=other_user.id)
    db.add(new_follow)
    db.commit()
    db.refresh(new_follow)

    return {
        "id": new_follow.id,
        "follow_id": new_follow.follower_id,
        "followed_id": new_follow.followed_id,
        "created_at": new_follow.created_at.now()
    }


@router.put("/unfollow/{username}")
def unfollow_user(
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id),
        username=str
):
    """Unfollow an user"""
    other_user = db.query(User).filter_by(username=username).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    follow_entry = db.query(Follow).filter_by(follower_id=user_id, followed_id=other_user.id).first()
    if not follow_entry:
        raise HTTPException(status_code=404, detail="Follow query not found")

    db.delete(follow_entry)
    db.commit()
    return {
        "message": "Unfollowed successfully",
        "users": {
            "ex-follower-id": follow_entry.follower_id,
            "ex-followed-id": follow_entry.followed_id,
        }
    }


@router.get("/get-follow/{username}", response_model=dict)
def get_user_followers(
        username: str,
        db: Session = Depends(get_db)
):
    """Fetch all the followers of someone"""
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    followers = db.query(User.id, User.username, User.profile_picture, Follow.created_at) \
        .join(Follow, User.id == Follow.follower_id) \
        .filter(Follow.followed_id == user.id) \
        .order_by(Follow.created_at.desc()) \
        .all()

    result = [
        FollowUserOut(
            id=f.id,
            username=f.username,
            profile_picture=f.profile_picture,
            followed_at=f.created_at.isoformat()
        )
        for f in followers
    ]

    return {"followers": result, "count": len(result)}

@router.get("/get-followed/{username}", response_model=dict)
def get_user_followed(
        username: str,
        db: Session = Depends(get_db)
):
    """Fetch all the followed people of someone"""
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    followed_users = (db.query(User.id, User.username, User.profile_picture, Follow.created_at)
                      .join(Follow, User.id == Follow.followed_id)
                      .filter(Follow.follower_id == user.id)
                      .order_by(Follow.created_at.desc()).all())
    result = [
        FollowUserOut(
            id=f.id,
            username=f.username,
            profile_picture=f.profile_picture,
            followed_at=f.created_at.isoformat()
        )
        for f in followed_users
    ]

    return {"followed": result, "count": len(result)}

@router.delete("/remove-follower/{username}")
def remove_follower(
        username: str,
        db: Session = Depends(get_db),
        user_id: int = Depends(jwt_user_id)
):
    """Remove a person from his list of follower"""
    other_user = db.query(User).filter_by(username=username).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    follow_entry = db.query(Follow).filter_by(follower_id=other_user.id, followed_id=user_id).first()
    if not follow_entry:
        raise HTTPException(status_code=404, detail="No relationship found")

    db.delete(follow_entry)
    db.commit()
    return {
        "message": "Follower removed successfully",
        "users": {
            "ex-follower-id": follow_entry.follower_id,
            "ex-followed-id": follow_entry.followed_id,
        }
    }
