import uuid
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.api.db_manager import add_photo, get_photo
from app.api.gcs import upload_to_gcs, delete_blob, google_url, bucket_name
from app.api.models import AttractionOut, AttractionIn, Tag, PhotoIn, PhotoOut
from app.api import db_manager

attraction = APIRouter()


@attraction.get('/{id}/', response_model=AttractionOut)
async def get_attraction(id: int):
    attraction = await db_manager.get_attraction(id)
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")
    tags = await db_manager.get_attraction_tags(id_attraction=id)

    photos = []
    for row in await db_manager.get_attraction_photos(id_attraction=id):
        photos.append(
            PhotoOut(id_photo=row['id_photo'],
                     created_at=row['created_at'],
                     url=f"{google_url}{bucket_name}/photo/{row['url']}")
        )

    attraction_object = AttractionOut(**attraction, tags=tags, photos=photos)
    return attraction_object


@attraction.post('/', status_code=201)
async def create_attraction(payload: AttractionIn):
    attraction_id = await db_manager.add_attraction(payload)

    return {"id_attraction": attraction_id,
            "detail": f"Attraction {attraction_id} created!"}


@attraction.put('/{id}/', status_code=201)
async def update_attraction(id: int, payload: AttractionIn):
    attraction = await db_manager.get_attraction(id)

    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")
    await db_manager.update_attraction(id, payload)
    return {"detail": f"Attraction {id} updated!"}


@attraction.delete('/{id}/', response_model=None)
async def delete_attraction(id: int):
    attraction = await db_manager.get_attraction(id)
    if not attraction:
        raise HTTPException(status_code=404, detail="Movie not found")

    photos = await db_manager.get_attraction_photos(id_attraction=id)

    for photo in photos:
        await delete_blob(photo['url'])

    await db_manager.delete_attraction(id)
    return {"detail": f"Attraction {id} deleted!"}


@attraction.get('/tags', response_model=List[str])
async def get_tags():
    tags = await db_manager.get_tags()
    if not tags:
        raise HTTPException(status_code=404, detail="Tags not exists")

    return tags


@attraction.post('/{id}/photos', response_model=List[PhotoOut])
async def add_attraction_photos(id: int, files: List[UploadFile] = File(...)):
    if not await db_manager.get_attraction(id):
        raise HTTPException(status_code=404, detail="Attraction not found")
    photos = []
    for file in files:
        file.filename = f"{uuid.uuid4()}.jpg"

        public_url = await upload_to_gcs(file)

        photo_id = await add_photo(id, PhotoIn(url=public_url))

        if photo_id:
            photo = await get_photo(photo_id)
            photos.append(PhotoOut(id_photo=photo['id_photo'], created_at=photo['created_at'],
                                   url=f"{google_url}{bucket_name}/photo/{photo['url']}"))
    return photos


@attraction.delete('/photos/{id_photo}')
async def delete_photo(id_photo: int):
    photo = await db_manager.get_photo(id_photo)
    if photo:
        try:
            await delete_blob(photo['url'])
        except Exception as e:
            print(e)
        try:
            await db_manager.remove_photo(id_photo)
        except Exception as e:
            print(e)
        return {'detail': "Photo deleted!"}
    else:
        return {'detail': "Photo not found!"}
