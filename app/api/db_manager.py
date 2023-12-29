from datetime import datetime
from typing import List

from sqlalchemy import select

from app.api.db import database, attraction_has_tag, attraction, tag, photo
from app.api.models import AttractionIn, PhotoIn


async def get_tags():
    result = await database.fetch_all(query=tag.select().order_by(tag.c.name))

    return [row['name'] for row in result]


async def add_tag(tag_name: str):
    query = tag.insert().values(tag_name)
    return await database.execute(query=query)


async def get_attraction_tags(id_attraction):
    query = select(tag).join(attraction_has_tag, tag.c.id_tag == attraction_has_tag.c.fk_tag).where(
        attraction_has_tag.c.fk_attraction == id_attraction)

    result = await database.fetch_all(query)

    return [row['name'] for row in result]


async def get_attraction(id):
    query = attraction.select(attraction.c.id_attraction == id)
    return await database.fetch_one(query=query)


async def add_attraction(payload: AttractionIn):
    data = payload.dict()
    tags = data.pop('tags')

    query = attraction.insert().values(**data)

    new_attraction = await database.execute(query=query)

    if payload.tags:
        await add_tags_to_attraction(tags, new_attraction)

    return new_attraction


async def update_attraction(id: int, payload: AttractionIn):
    data = payload.dict()
    tags = data.pop('tags')

    query = (attraction
             .update()
             .where(attraction.c.id_attraction == id)
             .values(**data)
             )

    await database.execute(query=query)

    if tags:
        await remove_tags_from_attraction(id)
        await add_tags_to_attraction(tags, id)


async def delete_attraction(id: int):
    query = (attraction
             .delete()
             .where(attraction.c.id_attraction == id)
             )
    await remove_tags_from_attraction(id)
    await remove_photo(id)
    await database.execute(query=query)


async def add_photo(id_attraction: int, payload: PhotoIn):
    query = photo.insert().values(**payload.dict(), fk_attraction=id_attraction, created_at=datetime.utcnow())

    return await database.execute(query=query)


async def get_photo(id_photo: int):
    return await database.fetch_one(query=photo.select(photo.c.id_photo == id_photo))


async def get_attraction_photos(id_attraction: int):
    query = photo.select(photo.c.fk_attraction == id_attraction)
    return await database.fetch_all(query=query)


async def add_tags_to_attraction(tags: List[str], attraction_id: int):
    for name in tags:
        name = name.lower()

        tag_id = await database.fetch_one(query=tag.select(tag.c.name == name))

        if not tag_id:
            tag_id = await database.execute(query=tag.insert().values(name=name))
        else:
            tag_id = tag_id[0]

        add_attraction_tag_query = attraction_has_tag.insert().values(
            fk_tag=tag_id, fk_attraction=attraction_id)

        await database.execute(query=add_attraction_tag_query)


async def remove_tags_from_attraction(attraction_id: int):
    await database.execute(query=attraction_has_tag.delete(attraction_has_tag.c.fk_attraction == attraction_id))


async def remove_attraction_photo(attraction_id: int):
    await database.execute(query=photo.delete(photo.c.fk_attraction == attraction_id))


async def remove_photo(photo_id: int):
    await database.execute(query=photo.delete(photo.c.id_photo == photo_id))
