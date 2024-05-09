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

BaseDBModel.metadata.create_all(bind=engine)


