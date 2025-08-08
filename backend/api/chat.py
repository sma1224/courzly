from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from database.connection import get_db, get_redis
from models import ChatMessage
from middleware.auth import get_current_user
from chat.manager import ConnectionManager

router = APIRouter()

class ChatMessageRequest(BaseModel):
    message: str
    message_type: str = "text"
    metadata: dict = {}

class ChatMessageResponse(BaseModel):
    id: str
    workflow_id: str
    user_id: Optional[str]
    message: str
    message_type: str
    metadata: dict
    created_at: str
    is_ai: bool

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int

@router.post("/{workflow_id}/message", response_model=ChatMessageResponse)
async def send_chat_message(
    workflow_id: str,
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send a chat message in a workflow"""
    message_id = str(uuid.uuid4())
    
    # Save message to database
    chat_message = ChatMessage(
        id=message_id,
        workflow_id=workflow_id,
        user_id=current_user.id,
        message=request.message,
        message_type=request.message_type,
        metadata=request.metadata
    )
    
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    # Broadcast to WebSocket connections
    manager = ConnectionManager()
    await manager.broadcast_message(workflow_id, {
        "id": chat_message.id,
        "user_id": chat_message.user_id,
        "message": chat_message.message,
        "message_type": chat_message.message_type,
        "metadata": chat_message.metadata,
        "created_at": chat_message.created_at.isoformat(),
        "is_ai": False
    })
    
    # Trigger AI response if needed
    if request.message_type == "user_query":
        await trigger_ai_response(workflow_id, request.message, db)
    
    return ChatMessageResponse(
        id=chat_message.id,
        workflow_id=chat_message.workflow_id,
        user_id=chat_message.user_id,
        message=chat_message.message,
        message_type=chat_message.message_type,
        metadata=chat_message.metadata,
        created_at=chat_message.created_at.isoformat(),
        is_ai=False
    )

@router.get("/{workflow_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    workflow_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get chat history for a workflow"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.workflow_id == workflow_id
    ).order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
    
    total_count = db.query(ChatMessage).filter(
        ChatMessage.workflow_id == workflow_id
    ).count()
    
    message_responses = []
    for msg in reversed(messages):  # Reverse to show chronological order
        message_responses.append(ChatMessageResponse(
            id=msg.id,
            workflow_id=msg.workflow_id,
            user_id=msg.user_id,
            message=msg.message,
            message_type=msg.message_type,
            metadata=msg.metadata,
            created_at=msg.created_at.isoformat(),
            is_ai=msg.user_id is None
        ))
    
    return ChatHistoryResponse(
        messages=message_responses,
        total_count=total_count
    )

@router.delete("/{workflow_id}/messages/{message_id}")
async def delete_chat_message(
    workflow_id: str,
    message_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a chat message"""
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.workflow_id == workflow_id,
        ChatMessage.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    db.delete(message)
    db.commit()
    
    # Broadcast deletion to WebSocket connections
    manager = ConnectionManager()
    await manager.broadcast_message(workflow_id, {
        "type": "message_deleted",
        "message_id": message_id
    })
    
    return {"message": "Message deleted successfully"}

@router.post("/{workflow_id}/typing")
async def send_typing_indicator(
    workflow_id: str,
    is_typing: bool,
    current_user = Depends(get_current_user)
):
    """Send typing indicator to other users"""
    manager = ConnectionManager()
    await manager.broadcast_message(workflow_id, {
        "type": "typing_indicator",
        "user_id": current_user.id,
        "is_typing": is_typing,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"message": "Typing indicator sent"}

@router.get("/{workflow_id}/participants")
async def get_chat_participants(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of chat participants"""
    # Get unique user IDs from chat messages
    participants = db.query(ChatMessage.user_id).filter(
        ChatMessage.workflow_id == workflow_id,
        ChatMessage.user_id.isnot(None)
    ).distinct().all()
    
    # Get active WebSocket connections
    manager = ConnectionManager()
    active_users = manager.get_active_users(workflow_id)
    
    return {
        "participants": [p[0] for p in participants if p[0]],
        "active_users": active_users,
        "total_participants": len(participants)
    }

async def trigger_ai_response(workflow_id: str, user_message: str, db: Session):
    """Trigger AI response to user message"""
    from workflows.ai_chat import generate_ai_response
    
    try:
        # Generate AI response
        ai_response = await generate_ai_response(workflow_id, user_message)
        
        # Save AI message
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            user_id=None,  # AI message
            message=ai_response,
            message_type="ai_response",
            metadata={"triggered_by": user_message}
        )
        
        db.add(ai_message)
        db.commit()
        
        # Broadcast AI response
        manager = ConnectionManager()
        await manager.broadcast_message(workflow_id, {
            "id": ai_message.id,
            "user_id": None,
            "message": ai_message.message,
            "message_type": ai_message.message_type,
            "metadata": ai_message.metadata,
            "created_at": ai_message.created_at.isoformat(),
            "is_ai": True
        })
        
    except Exception as e:
        print(f"Error generating AI response: {e}")
        # Could send error message to chat