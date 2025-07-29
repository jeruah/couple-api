from sqlmodel import Session, select
from models import User, Message, Chat, Album
from schemas import UserCreate, MessageCreate, ChatCreate, AlbumCreate
from datetime import datetime, timezone
from typing import List, Optional

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)

def create_message(db: Session, message: MessageCreate) -> Message:
    db_message = Message(chat_id=message.chat_id, sender_id=message.sender_id, content=message.content, sent_at=datetime.now(timezone.utc))
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, chat_id: int) -> List[Message]:
    statement = select(Message).where(Message.chat_id == chat_id)
    return db.exec(statement).all()

def create_chat(db: Session, chat: ChatCreate) -> Chat:
    db_chat = Chat(image_id=chat.album_id, created_at=datetime.now(timezone.utc))
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chat(db: Session, chat_id: int, image_id: int) -> Optional[Chat]:
    statement = select(Chat).where((Chat.id == chat_id) & (Chat.image_id == image_id))
    return db.exec(statement).first()

def create_album(db: Session, album: AlbumCreate, owner_id: int) -> Album:
    db_album = Album(title=album.title, owner_id=owner_id)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

def get_album(db: Session, album_id: int) -> Optional[Album]:
    return db.get(Album, album_id)