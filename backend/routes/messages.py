# Messages Routes
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..models.message import MessageModel
from ..models.user import UserModel
import logging

router = APIRouter(prefix="/api/messages", tags=["messages"])
logger = logging.getLogger(__name__)

class SendMessageRequest(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    product_id: Optional[str] = None

@router.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    partner_ids = MessageModel.get_conversation_partners(user_id)
    conversations = []
    
    for partner_id in partner_ids:
        partner = UserModel.get_by_id(partner_id)
        if partner:
            unread_count = MessageModel.get_unread_count(user_id, partner_id)
            conversations.append({
                "partner_id": partner_id,
                "partner_username": partner.get('username'),
                "unread_count": unread_count
            })
    
    return conversations

@router.get("/conversation/{user_id}/{partner_id}")
async def get_conversation(user_id: str, partner_id: str):
    MessageModel.mark_as_read(user_id, partner_id)
    
    messages = MessageModel.get_conversation(user_id, partner_id)
    partner = UserModel.get_by_id(partner_id)
    
    return {
        "partner": {
            "id": partner_id,
            "username": partner.get('username') if partner else None
        },
        "messages": messages
    }

@router.post("/send")
async def send_message(request: SendMessageRequest):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    receiver = UserModel.get_by_id(request.receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    msg_id = MessageModel.send_message(
        sender_id=request.sender_id,
        receiver_id=request.receiver_id,
        content=request.content,
        product_id=request.product_id
    )
    
    logger.info(f"Message sent from {request.sender_id} to {request.receiver_id}")
    return {"success": True, "message_id": msg_id}

@router.get("/unread/{user_id}")
async def get_unread_count(user_id: str):
    count = MessageModel.get_unread_count(user_id)
    return {"unread_count": count}

@router.post("/mark-read/{user_id}/{sender_id}")
async def mark_messages_read(user_id: str, sender_id: str):
    MessageModel.mark_as_read(user_id, sender_id)
    return {"success": True}
