from sqlalchemy import Integer, String, Boolean, Column
from src.database import BaseDBModel, engine


# таблица, которая хранит данные о пользователях
class Users(BaseDBModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False, index=False)
    number = Column(String, unique=True, index=False)
    hash_password = Column(String, unique=False, index=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


# таблица, которая хранит данные о сессиях
class UsersSessions(BaseDBModel):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=False)


BaseDBModel.metadata.create_all(bind=engine)
