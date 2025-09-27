import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.config import fast_mqtt
from app.core.database import get_db
from app.core.utils import jwt_user_id
from app.models.models import Conversation, User, Message
from app.schemas.message import MessageSent, MessageOut, MessageUpdate, ConversationOut, ConversationDTO, MessageDTO
from app.schemas.user import UserLightDTO

router = APIRouter(prefix="/message", tags=["messages"])

@router.post("/send/{user_id}", response_model=MessageDTO)
async def send_message(
        payload: MessageSent,
        user_id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """send message to user and check if conv exist else create a new conversation"""
    other_user = db.query(User).filter_by(id=user_id).first()
    if other_user.id == current_user:
        raise HTTPException(status_code=400, detail="You cannot talk to yourself")

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

    topic = f"chat/{conversation.id}/messages"
    fast_mqtt.publish(topic, new_message.content)

    return MessageDTO(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        sender=UserLightDTO(
            id=new_message.sender_id,
            username=new_message.sender.username,
            profile_picture=new_message.sender.profile_picture
        ),
        content=new_message.content,
        created_at=new_message.created_at,
        updated_at=new_message.updated_at,
        is_read=new_message.is_read
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
        if msg.sender != current_user and not msg.is_read:
            msg.is_read = True
    db.commit()
    db.refresh(conversation)

    message_sorted = sorted(conversation.messages, key=lambda m: m.created_at, reverse=False)

    return ConversationOut(
        conversation=ConversationDTO.model_validate(conversation, from_attributes=True),
        messages=[
            MessageDTO(
                id=m.id,
                conversation_id=m.conversation_id,
                sender=UserLightDTO(
                    id=m.sender.id,
                    username=m.sender.username,
                    profile_picture=m.sender.profile_picture
                ),
                content=m.content,
                created_at=m.created_at,
                updated_at=m.updated_at,
                is_read=m.is_read
            )
            for m in message_sorted
        ],
        detail="success"
    )

@router.get("/conversations", response_model=List[ConversationDTO])
def get_user_conversations(
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """display all the conversations of the current user"""
    conversations = (
        db.query(Conversation)
            .options(
                joinedload(Conversation.user1),
                joinedload(Conversation.user2)
            )
            .filter(
                (Conversation.user1_id == current_user) |
                (Conversation.user2_id == current_user)
        ).all()
    )

    if not conversations:
        return []

    conversations_dto = []
    for conv in conversations:
        conversations_dto.append(
            ConversationDTO(
                id=conv.id,
                user1=UserLightDTO(
                    id=conv.user1.id,
                    username=conv.user1.username,
                    profile_picture=conv.user1.profile_picture,
                ),
                user2=UserLightDTO(
                    id=conv.user2.id,
                    username=conv.user2.username,
                    profile_picture=conv.user2.profile_picture,
                ),
                created_at=conv.created_at,
            )
        )
    return conversations_dto
