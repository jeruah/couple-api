from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request, Response, WebSocket
from sqlmodel import Session, select
from app.database import get_db
import app.models as models
import app.auth as auth


def get_current_user(request: Request, response: Response, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access")

    if not token:
        raise credentials_exception

    try:
        token = token.replace("Bearer ", "")

        data = auth.decode_access_token(token)
        if data is None:
            raise credentials_exception

        user = db.exec(select(models.User).filter(models.User.email == data.get("sub"))).first()
        if user is None:
            raise credentials_exception

        return user
    except:
        response.delete_cookie("access")
        raise credentials_exception


async def get_current_user_ws(websocket: WebSocket, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.WS_1008_POLICY_VIOLATION,
        detail="Could not validate credentials",
    )

    token = websocket.cookies.get("access")

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise credentials_exception

    try:
        token = token.replace("Bearer ", "")

        data = auth.decode_access_token(token)
        if data is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise credentials_exception

        user = db.exec(select(models.User).filter(models.User.email == data.get("sub"))).first()
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise credentials_exception

        return user
    except:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise credentials_exception

