import asyncio
import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.utils import jwt_user_id, ConnectionManager
from app.models.models import Conversation, User, Message
from app.schemas.message import MessageSent, MessageOut, MessageUpdate, ConversationOut, ConversationDTO, MessageDTO
from app.schemas.user import UserLightDTO

router = APIRouter(prefix="/message", tags=["messages"])
manager = ConnectionManager()

@router.post("/send/{username}", response_model=MessageOut)
async def send_message(
        payload: MessageSent,
        username: str,
        db: Session = Depends(get_db),
        current_user: int = Depends(jwt_user_id)
):
    """send message to user and check if conv exist else create a new conversation"""
    other_user = db.query(User).filter_by(username=username).first()
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

    if other_user.id in manager.active_connections:
        # send notification to the other user if connected
        asyncio.create_task(manager.send_personal_message(
            {
                "event": "new_message",
                "conversation_id": conversation.id,
                "message": {
                    "id": new_message.id,
                    "sender_id": new_message.sender_id,
                    "content": new_message.content,
                    "created_at": new_message.created_at.isoformat(),
                    "is_read": new_message.is_read
                }
            },
            other_user.id
        ))

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
    db.refresh(conversation)

    return ConversationOut(
        conversation=ConversationDTO.model_validate(conversation, from_attributes=True),
        messages=[MessageDTO.model_validate(m, from_attributes=True) for m in conversation.messages],
        detail="success",
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


""" Maybe a good features ?
@router.delete("/{conversation_id}")
def delete_conversation(conversation_id):
    # delete conversation and all this message
"""

@router.websocket("/ws/{user_id}")
async def websocket_endpoint_chat(
        user_id: int,
        websocket: WebSocket
):
    """websocket endpoint for chat"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message({"message: ": data}, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        print(f"WebSocket disconnected for user {user_id}: {e}")
