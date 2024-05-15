from sqlalchemy import (Integer, String, Boolean, Column)
from src.database import BaseDBModel, engine


# класс хранящий информацию об ошейниках
class Collars(BaseDBModel):   # string of users' table
    __tablename__ = "collars"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, unique=True, index=False)
    is_active = Column(Boolean)


# класс хранящий информацию о владельцах ошейников
class Owners(BaseDBModel):
    __tablename__ = "owners"

    user_id = Column(Integer, primary_key=True, unique=False, index=False)
    collar_id = Column(Integer, primary_key=True, unique=False, index=False)


# класс хранящий координаты расположения ошейников
class Coordinates(BaseDBModel):
    __tablename__ = "coordinates"

    Coordinates_id = Column(Integer, primary_key=True, unique=False, index=False)
    collar_id = Column(Integer, primary_key=False, unique=False, index=False)
    coordinates = Column(String, primary_key=False, unique=False, index=False)
    time = Column(String, primary_key=False, unique=False, index=False)


BaseDBModel.metadata.create_all(bind=engine)


