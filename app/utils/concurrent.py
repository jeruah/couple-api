from fastapi import HTTPException
from sqlmodel import and_, select, Session

import app.models as models
from app.schemas import UserResponse

def participation_controller(album_id: int, db: Session, current_user: UserResponse):
    album = db.exec(select(models.Album).where(models.Album.id == album_id)).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    participant = db.exec(select(models.AlbumParticipant).where(
        and_(
            models.AlbumParticipant.user_id == current_user.id,
            models.AlbumParticipant.album_id == album.id
        )
    )).first()
    return album, participant

def verify_album_access(album_id: int, db: Session, current_user: UserResponse):
    """Return the album if the user is the owner or a participant.

    Raises a 403 error if the user has no permissions.
    """
    album, participant = participation_controller(album_id, db, current_user)
    if album.owner_id != current_user.id and not participant:
        raise HTTPException(status_code=403, detail="Album not found")
    return album

def get_image(album_id: int, image_id: int, db: Session):
    image = db.exec(select(models.Image).where(
        and_(
            models.Image.id == image_id,
            models.Image.album_id == album_id
        )
    )).first()

    return image

def not_found_exception(element: any, detail: str):
    if not element:
        raise HTTPException(status_code=404, detail=detail)

def existing_element_exception(element: any, detail: str):
    if element:
        raise HTTPException(status_code=400, detail=detail)
