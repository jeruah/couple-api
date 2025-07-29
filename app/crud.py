from sqlmodel import Session, select
import app.models as models
from app.schemas import UserCreate, MessageCreate, ChatCreate, AlbumCreate
from datetime import datetime, timezone
from typing import List, Optional

def create_user(db: Session, user: UserCreate) -> models.User:
    db_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.get(models.User, user_id)

def create_message(db: Session, message: MessageCreate, sender_id: int) -> models.Message:
    db_message = models.Message(
        chat_id=message.chat_id,
        sender_id=sender_id,
        content=message.content,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, chat_id: int) -> List[models.Message]:
    statement = select(models.Message).where(models.Message.chat_id == chat_id)
    return db.exec(statement).all()

def create_chat(db: Session, chat: ChatCreate) -> models.Chat:
    db_chat = models.Chat(image_id=chat.image_id, created_at=datetime.now(timezone.utc))
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chat(db: Session, chat_id: int, image_id: int) -> Optional[models.Chat]:
    statement = select(models.Chat).where((models.Chat.id == chat_id) & (models.Chat.image_id == image_id))
    return db.exec(statement).first()

def create_album(db: Session, album: AlbumCreate, owner_id: int) -> models.Album:
    db_album = models.Album(title=album.title, owner_id=owner_id)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

def get_album(db: Session, album_id: int) -> Optional[models.Album]:
    return db.get(models.Album, album_id)
