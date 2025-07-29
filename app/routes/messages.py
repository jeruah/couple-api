
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session, select
from typing import List, Dict
from app.database import get_db
import app.models as models
from app.schemas import MessageCreate, MessageResponse, ChatResponse, UserResponse
from app.utils.security import get_current_user, get_current_user_ws
from app.utils.concurrent import verify_album_access
from app import crud


messages_router = APIRouter(prefix="/chats", tags=["chat"])

class ConnectionManager:
    def __init__(self) -> None:
        self.connections: Dict[int, list[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.setdefault(chat_id, []).append(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket) -> None:
        if chat_id in self.connections:
            self.connections[chat_id].remove(websocket)
            if not self.connections[chat_id]:
                del self.connections[chat_id]

    async def broadcast(self, chat_id: int, message: dict) -> None:
        for connection in self.connections.get(chat_id, []):
            await connection.send_json(message)


manager = ConnectionManager()

@messages_router.post("/{image_id}", response_model=ChatResponse)
def create_chat(
    image_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image = db.get(models.Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    verify_album_access(image.album_id, db, current_user)

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

    image = db.get(models.Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    verify_album_access(image.album_id, db, current_user)

    if not chat:
        chat = models.Chat(image_id=image_id)
        db.add(chat)
        db.commit()
        db.refresh(chat)

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

    image = db.get(models.Image, chat.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    verify_album_access(image.album_id, db, current_user)

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

    image = db.get(models.Image, chat.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    verify_album_access(image.album_id, db, current_user)

    messages = db.exec(select(models.Message).where(models.Message.chat_id == chat_id)).all()
    return messages

@messages_router.websocket("/ws/{chat_id}")
async def chat_websocket(
    websocket: WebSocket,
    chat_id: int,
    db: Session = Depends(get_db),
):
    user = await get_current_user_ws(websocket, db)

    chat = db.get(models.Chat, chat_id)
    if not chat:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="Chat not found")

    image = db.get(models.Image, chat.image_id)
    if not image:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="Image not found")

    try:
        verify_album_access(image.album_id, db, user)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise

    await manager.connect(chat_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue
            message = crud.create_message(
                db,
                MessageCreate(chat_id=chat_id, content=content),
                sender_id=user.id,
            )
            await manager.broadcast(
                chat_id,
                {
                    "id": message.id,
                    "content": message.content,
                    "sent_at": message.sent_at.isoformat(),
                    "sender_id": message.sender_id,
                    "chat_id": message.chat_id,
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)

