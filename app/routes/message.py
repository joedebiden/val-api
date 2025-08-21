import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.utils import jwt_user_id
from app.models.models import Conversation, User, Message
from app.schemas.message import MessageSent, MessageOut, MessageUpdate, ConversationOut, ConversationDTO, MessageDTO

router = APIRouter(prefix="/message", tags=["messages"])

@router.post("/send/{username}", response_model=MessageOut)
def send_message(
        payload: MessageSent,
        username: str,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """send message to user and check if conv exist else create a new conversation"""
    other_user = db.query(User).filter_by(username=username).first()

    conversation = db.query(Conversation).filter(
        ((Conversation.user1_id == current_user) & (Conversation.user2_id == other_user.id)) |
        ((Conversation.user2_id == current_user) & (Conversation.user1_id == other_user.id))
    ).first()
    if not conversation:
        conversation = Conversation(user1_id=current_user, user2_id=other_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    new_message = Message(
        conversation_id=conversation.id,
        sender_id=current_user,
        content=payload.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return MessageOut(
        detail="success",
        message=MessageDTO.model_validate(new_message, from_attributes=True) # avoid warning from IDE & prevent error from SQLAlchemy orm
    )



@router.delete("/{message_id}")
def delete_message(
        message_id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """delete own message"""
    message = db.query(Message).filter_by(id=message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender_id != current_user:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(message)
    db.commit()
    return {
        "detail": "Message deleted with success",
        "message_id_deleted": message_id
    }

@router.patch("/{message_id}", response_model=MessageOut)
def update_message(
        payload: MessageUpdate,
        message_id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """update message content"""
    message = db.query(Message).filter_by(id=message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender_id != current_user:
        raise HTTPException(status_code=403, detail="Not allowed")

    message.content = payload.content
    message.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(message)

    return MessageOut(
        detail="success",
        message=MessageDTO.model_validate(message, from_attributes=True) # same comment as l:44
    )

@router.get("/conversation/{conversation_id}/content", response_model=ConversationOut)
def get_conversation_content(
        conversation_id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """get content of a conversation with user"""
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user not in [conversation.user1_id, conversation.user2_id]:
        raise HTTPException(status_code=403, detail="Not authorized to view this conversation")

    # display read message
    for msg in conversation.messages:
        if msg.sender_id != current_user and not msg.is_read:
            msg.is_read = True
    db.commit()

    return ConversationOut(
        conversation=conversation,
        messages=conversation.messages,
        detail="success",
    )

@router.get("/conversations", response_model=List[ConversationDTO])
def get_user_conversations(
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """display all the conversations of the current user"""
    conversations = db.query(Conversation).filter(
        (Conversation.user1_id == current_user) | (Conversation.user2_id == current_user)
    ).all()
    if not conversations:
        return []

    return conversations




@router.delete("/{conversation_id}")
def delete_conversation(conversation_id):
    """delete conversation"""
    pass
