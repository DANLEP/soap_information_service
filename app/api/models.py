import datetime

from pydantic import BaseModel
from typing import List, Optional

from app.api.db import SeasonalityEnum


class Tag(BaseModel):
    id_tag: int
    name: str


class PhotoIn(BaseModel):
    url: str


class PhotoOut(PhotoIn):
    id_photo: int
    created_at: datetime.datetime


class AttractionIn(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    seasonality: SeasonalityEnum
    contact_information: Optional[str]
    entrance_fee: Optional[float]
    opening_time: Optional[datetime.time]
    closing_time: Optional[datetime.time]
    tags: Optional[List[str]]


class AttractionOut(AttractionIn):
    id_attraction: int
    rating: Optional[float]
    photos: Optional[List[PhotoOut]]
