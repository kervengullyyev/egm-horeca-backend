from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import Message
from ..schemas import MessageCreate, MessageResponse, MessageUpdate

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Create a new message from contact form"""
    try:
        # Create new message
        db_message = Message(
            name=message.name,
            email=message.email,
            subject=message.subject or f"Contact from {message.name}",
            message=message.message,
            status="unread"
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        return db_message
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )

@router.get("/", response_model=List[MessageResponse])
def get_messages(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """Get all messages with optional filtering"""
    query = db.query(Message)
    
    if status_filter:
        query = query.filter(Message.status == status_filter)
    
    messages = query.offset(skip).limit(limit).order_by(Message.created_at.desc()).all()
    return messages

@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific message by ID"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return message

@router.put("/{message_id}", response_model=MessageResponse)
def update_message(message_id: int, message_update: MessageUpdate, db: Session = Depends(get_db)):
    """Update message status (e.g., mark as read, replied)"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    try:
        db_message.status = message_update.status
        db_message.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_message)
        
        return db_message
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update message: {str(e)}"
        )

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a message"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    try:
        db.delete(db_message)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )
