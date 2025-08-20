from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.utils import jwt_user_id
from app.models.models import Conversation, User, Message
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["messages"])

@router.put("/send/{username}", response_model=MessageOut)
def send_message(
        payload: MessageCreate,
        username: str,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """send message to user and check if conv exist else create a new conversation"""
    other_user = db.query(User).filter_by(username=username).first()

    conversation = db.query(Conversation).filter(
        ((Conversation.user1_id == current_user) & (Conversation.user2_id == other_user.id)) |
        ((Conversation.user2_id == current_user) & (Conversation.user1_id == other_user.id))
    )
    if not conversation:
        conversation = Conversation(user1_id=current_user, user2_id=other_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    message = Message(
        content=payload.content,
        sender_id=current_user,
        conversation_id=conversation.id,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.delete("/{message_id}")
def delete_message(message_id):
    """delete message"""
    pass

@router.patch("/{message_id}")
def update_message(message_id):
    """update message content"""
    pass

@router.get("/{conversation_id}/content")
def get_conversation_content(conversation_id):
    """get content of a conversation with user"""
    pass

@router.get("/conversations")
def get_user_conversations():
    """display all the conversations of the current user"""

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id):
    """delete conversation"""
    pass
