import enum
import os

from sqlalchemy import (Column, Integer, MetaData, String, Table, DECIMAL, Text, Time, Enum,
                        create_engine, ForeignKey, DateTime)
from databases import Database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI)
metadata = MetaData()


class SeasonalityEnum(str, enum.Enum):
    all_season = "all_season"
    winter = "winter"
    summer = "summer"


attraction_has_tag = Table(
    'attraction_has_tag',
    metadata,
    Column('fk_attraction', Integer, ForeignKey('attraction.id_attraction')),
    Column('fk_tag', Integer, ForeignKey('attraction_tag.id_tag'))
)

attraction = Table(
    'attraction',
    metadata,
    Column('id_attraction', Integer, primary_key=True),
    Column('name', String(50), nullable=False),
    Column('description', Text, nullable=False),
    Column('seasonality', Enum(SeasonalityEnum), nullable=False),
    Column('latitude', DECIMAL(8, 6), nullable=False),
    Column('longitude', DECIMAL(9, 6), nullable=False),
    Column('contact_information', String(255)),
    Column('entrance_fee', DECIMAL(10, 2)),
    Column('opening_time', Time),
    Column('closing_time', Time),
    Column('rating', DECIMAL(2, 1)),
)

tag = Table(
    'attraction_tag',
    metadata,
    Column('id_tag', Integer, primary_key=True),
    Column('name', String(45), nullable=False),
)

photo = Table(
    'photo',
    metadata,
    Column('id_photo', Integer, primary_key=True),
    Column('url', String(255), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('fk_attraction', Integer, ForeignKey('attraction.id_attraction'))
)

database = Database(DATABASE_URI)
