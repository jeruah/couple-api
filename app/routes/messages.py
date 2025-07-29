from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_db
import app.models as models
from app.schemas import MessageCreate, MessageResponse, ChatResponse, UserResponse
from app.utils.security import get_current_user

messages_router = APIRouter(prefix="/chats", tags=["chat"])


@messages_router.post("/{image_id}", response_model=ChatResponse)
def create_chat(
    image_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image = db.get(models.Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    chat = db.exec(select(models.Chat).where(models.Chat.image_id == image_id)).first()
    if chat:
        return chat

    chat = models.Chat(image_id=image_id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@messages_router.get("/{image_id}", response_model=ChatResponse)
def get_chat(
    image_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.exec(select(models.Chat).where(models.Chat.image_id == image_id)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@messages_router.post("/{chat_id}/messages", response_model=MessageResponse)
def create_message(
    chat_id: int,
    message: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.get(models.Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message = models.Message(content=message.content, chat_id=chat_id, sender_id=current_user.id)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@messages_router.get("/{chat_id}/messages", response_model=List[MessageResponse])
def read_messages(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.get(models.Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = db.exec(select(models.Message).where(models.Message.chat_id == chat_id)).all()
    return messages
