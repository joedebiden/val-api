from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["messages"])

@router.put("/send/{username}")
def send_message(username):
    """send message to user and check if conv exist else create a new conversation"""
    pass

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
