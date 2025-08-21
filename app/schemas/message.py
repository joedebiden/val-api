from pydantic import BaseModel
from datetime import datetime


class MessageSent(BaseModel):
    content: str

class MessageUpdate(BaseModel):
    content: str

class MessageDTO(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool

    class Config:
        orm_mode = True

class MessageOut(BaseModel):
    detail: str
    message: MessageDTO

    class Config:
        orm_mode = True

class ConversationDTO(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime

class ConversationOut(BaseModel):
    conversation: ConversationDTO
    messages: list[MessageOut]
    detail: str

    class Config:
        orm_mode = True
