from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(UserBase):
    username: Optional[str] = None
    password: str

class AlbumBase(BaseModel):
    title: str

class AlbumCreate(AlbumBase):
    pass
class AlbumResponse(AlbumBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class ImageBase(BaseModel):
    title: str
    description: Optional[str] = None

class ImageCreate(ImageBase):
    image_path: str

class ImageResponse(ImageBase):
    id: int
    album_id: int

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    chat_id: int  # 📌 Ahora pertenece a un chat, no a un álbum

class MessageResponse(MessageBase):
    id: int
    sent_at: datetime
    sender_id: int
    chat_id: int  # 📌 Referencia al chat, no al álbum

    class Config:
        from_attributes = True

# 📌 Nuevo modelo de chat
class ChatBase(BaseModel):
    album_id: int  # El chat sigue ligado a un álbum
    created_at: datetime

class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    id: int
    album_id: int
    created_at: datetime
    messages: List["MessageResponse"]

    class Config:
        from_attributes = True
