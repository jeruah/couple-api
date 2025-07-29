from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

class User(SQLModel, table=True):

    __tablename__ = "users"

    id: int = Field(primary_key=True, index=True, nullable=False)
    email: str = Field(index=True, nullable=False)
    username: str = Field(index=True, nullable=False)
    password: str = Field(nullable=False)

    albums: list["Album"] = Relationship(back_populates="owner")
    messages: list["Message"] = Relationship(back_populates="sender")
    albums_participation: list["AlbumParticipant"] = Relationship(back_populates="user")

class Album(SQLModel, table=True):

    __tablename__ = "albums"

    id: int = Field(primary_key=True, index=True)
    title: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: int = Field(foreign_key="users.id", nullable=False)

    owner: "User" = Relationship(back_populates="albums")
    images: list["Image"] = Relationship(back_populates="album", sa_relationship_kwargs={"cascade": "all, delete"})
    participants: list["AlbumParticipant"] = Relationship(back_populates="album")

class Image(SQLModel, table=True):

    __tablename__ = "images"

    id: int = Field(primary_key=True, index=True)
    title: str = Field(index=True, nullable=False)
    description: str = Field(nullable=True)
    path: str = Field(nullable=False)
    album_id: int = Field(foreign_key="albums.id", nullable=False)

    chat: "Chat" = Relationship(back_populates="image", sa_relationship_kwargs={"cascade": "all, delete"})
    album: "Album" = Relationship(back_populates="images")

class Chat(SQLModel, table=True):

    __tablename__ = "chats"

    id: int = Field(primary_key=True, index=True)
    image_id: int = Field(foreign_key="images.id", nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    image: "Image" = Relationship(back_populates="chat")
    messages: list["Message"] = Relationship(back_populates="chat")

class Message(SQLModel, table=True):

    __tablename__ = "messages"

    id: int = Field(primary_key=True, index=True)
    content: str = Field(nullable=False)
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sender_id: int = Field(foreign_key="users.id", nullable=False)
    chat_id: int = Field(foreign_key="chats.id", nullable=False)

    sender: "User" = Relationship(back_populates="messages")
    chat: "Chat" = Relationship(back_populates="messages")

class AlbumParticipant(SQLModel, table=True):

    __tablename__ = "album_participants"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    album_id: int = Field(foreign_key="albums.id", primary_key=True)

    user: "User" = Relationship(back_populates="albums_participation")
    album: "Album" = Relationship(back_populates="participants")