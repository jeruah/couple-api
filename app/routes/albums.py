from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlmodel import Session, select,or_, and_

from app.database import get_db
import app.models as models
from app.schemas import UserResponse
from app.schemas import AlbumCreate, AlbumResponse

from app.routes.images import images_router, me_images_router

from app.utils.security import get_current_user


me_albums_router = APIRouter(prefix="/albums", tags=["albums"])

@me_albums_router.get("/", response_model=List[AlbumResponse])
def read_user_albums(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    albums = db.exec(select(models.Album).join(models.AlbumParticipant, isouter=True).where(
        or_(
            models.Album.owner_id == current_user.id,
            models.AlbumParticipant.user_id == current_user.id
        )
    ))
    return albums
@me_albums_router.post("/new_album")
def create_album(album: AlbumCreate, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    new_album = models.Album(title=album.title, owner_id=current_user.id)
    db.add(new_album)
    db.commit()
    db.refresh(new_album)
    return new_album

@me_albums_router.get("/{album_id}", response_model=AlbumResponse)
def read_album(album_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    album = db.get(models.Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    if album.owner_id != current_user.id:
        participant = db.exec(select(models.AlbumParticipant).where(
            and_(
                models.AlbumParticipant.user_id == current_user.id,
                models.AlbumParticipant.album_id == album_id
            )
        ))
        if not participant:
            raise HTTPException(status_code=403, detail="Album not found")

    return album

@me_albums_router.delete("/delete/{album_id}")
def delete_album(album_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    album = db.get(models.Album, album_id)
    if not current_user.id == album.owner_id:
        participant = db.exec(select(models.AlbumParticipant).where(
            and_(
                models.AlbumParticipant.user_id == current_user.id,
                models.Album == album_id
            )
        )).first()
        if not participant:
            raise HTTPException(status_code=401, detail="denied")

        db.delete(participant)
        db.commit()
        return {"message": "deleted for you"}


    db.delete(album)
    db.commit()
    return {"message": "Album deleted successfully"}

@me_albums_router.put("update/{album_id}")
def update_album(album_id: int, album_data: AlbumCreate, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    db_album = db.get(models.Album, album_id)
    if not current_user.id == db_album.owner_id:
        participant = db.exec(select(models.AlbumParticipant).where(
            and_(
                models.AlbumParticipant.user_id == current_user.id,
                models.Album == album_id
            )
        )).first()
        if not participant:
            raise HTTPException(status_code=401, detail="denied")

        db_album.title = album_data.title
        db.commit()
        db.refresh(db_album)
        return db_album

    db_album.title = album_data.title
    db.commit()
    db.refresh(db_album)
    return db_album

me_albums_router.include_router(images_router)
me_albums_router.include_router(me_images_router)
