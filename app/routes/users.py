from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from datetime import timedelta

from app.database import get_db
import app.models as models
from app.schemas import UserCreate, UserLogin, UserResponse

from app.auth import hash_password, verify_password, create_access_token
from app.utils.security import get_current_user

from app.routes.albums import me_albums_router

auth_router = APIRouter(prefix="/auth", tags=["auth"])
me_router = APIRouter(prefix="/me", tags=["me"])

@auth_router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """register a new user"""
    if db.exec(select(models.User).filter(models.User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = models.User(email=user.email, username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/login")
def login(user_log: UserLogin, response: Response, db: Session = Depends(get_db)):
    """login a user"""
    user = db.exec(select(models.User).filter(models.User.email == user_log.email)).first()
    if not user or not verify_password(user_log.password, user.password):
        raise HTTPException(status_code=404, detail="Invalid credentials")

    """generate token"""
    access_token = create_access_token(data={"sub": user_log.email}, expires_delta=timedelta(minutes=30))

    """use cookie"""
    response.set_cookie(
        key="access",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="strict",
        secure=False,  # change to True in production
    )

    return {"message": "Login successful"}

@auth_router.get("/logout")
def logout(response: Response):
    response.delete_cookie(key="access")
    return {"message": "Logout successful"}

@me_router.get("/", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@me_router.delete("/delete")
def delete_me(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"message": "bye, bye"}

@me_router.put("/update")
def update_me(user: UserCreate, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.email = user.email
    current_user.username = user.username
    current_user.password = hash_password(user.password)
    db.commit()
    return current_user
me_router.include_router(me_albums_router)




