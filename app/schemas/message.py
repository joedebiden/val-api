from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    #receiver_id: int
    content: str

class MessageUpdate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool

    class Config:
        orm_mode = True

class ConversationOut(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    messages: list[MessageOut]

    class Config:
        orm_mode = True
