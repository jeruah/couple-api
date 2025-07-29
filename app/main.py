from fastapi import FastAPI, Depends
from sqlmodel import Session

from app.database import get_db, init_db
import app.models as models

import app.routes.users as users_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/testdb")
def test_db(db: Session = Depends(get_db)):
    try:
        test_album = models.Album(title="Test Album", owner_id=1)
        db.add(test_album)
        db.commit()
        db.refresh(test_album)

        album = db.query(models.Album).filter(models.Album.title == "Test Album").first()
        return {"message": "Database is working"}
    except Exception as e:
        return {"message": f"Database error: {e}"}

@app.get("/initdb")
def start():
    init_db()
    return {"message": "Database initialized"}

app.include_router(users_router.auth_router)
app.include_router(users_router.me_router)
