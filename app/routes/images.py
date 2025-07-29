from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from typing import List

from app.schemas import ImageCreate, ImageResponse
from app.schemas import UserResponse
from app.database import get_db
import app.models as models

from app.utils.security import get_current_user
from app.utils.concurrent import participation_controller, get_image, not_found_exception, existing_element_exception

images_router = APIRouter(prefix='/images', tags=["images"])
me_images_router = APIRouter(prefix='/{album_id}/images', tags=["me_images"])

@me_images_router.post("/create")
def create_image(album_id: int, image: ImageCreate, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    album, participant = participation_controller(album_id, db, current_user)

    if not album.owner_id == current_user.id and not participant:
        raise HTTPException(status_code=403, detail="Album not found")

    existing_image = get_image(album_id, image.id, db)

    existing_element_exception(existing_image, "Image already exists")

    new_image = models.Image(title=image.title, description=image.description, path=image.image_path, album_id=album_id)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


@me_images_router.get("/", response_model=List[ImageResponse])
def read_images(album_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    album, participant = participation_controller(album_id, db, current_user)

    if not album.owner_id == current_user.id and not participant:
        raise HTTPException(status_code=403, detail="Album not found")

    images = db.exec(select(models.Image).where(models.Image.album_id == album_id)).all()
    return images

@me_images_router.get("/{image_id}", response_model=ImageResponse)
def read_images_id(album_id:int, image_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):

    image = get_image(album_id, image_id, db)
    not_found_exception(image, "Image not found")

    album, participant = participation_controller(album_id, db, current_user)

    if not album.owner_id == current_user.id and not participant:
        raise HTTPException(status_code=403, detail="Album not found")

    return image

@me_images_router.delete("/{image_id}/delete")
def delete_image(album_id:int, image_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    image = get_image(album_id, image_id, db)

    not_found_exception(image, "Image not found")

    album, participant = participation_controller(album_id, db, current_user)

    if not album.owner_id == current_user.id and not participant:
        raise HTTPException(status_code=403, detail="Album not found")

    db.delete(image)
    db.commit()
    return {"message": "Image deleted"}

@me_images_router.put("/{image_id}/update")
def update_image(album_id:int, image_id: int, image: ImageCreate, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    image_db = get_image(album_id, image_id, db)

    not_found_exception(image_db, "Image not found")

    album, participant = participation_controller(album_id, db, current_user)

    if not album.owner_id == current_user.id and not participant:
        raise HTTPException(status_code=403, detail="Album not found")

    image_db.title = image.title
    image_db.description = image.description
    image_db.path = image.image_path
    db.add(image_db)
    db.commit()
    db.refresh(image_db)
    return image_db


