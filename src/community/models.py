from sqlalchemy import (Integer, String, Boolean, Column)
from src.database import BaseDBModel, engine


# класс хранящий информацию о задачах
class Tasks(BaseDBModel):
    __tablename__ = "tasks"

    task_id = Column(Integer, unique=True, primary_key=True, index=True)
    collar_id = Column(Integer, unique=False, primary_key=False, index=False)
    text = Column(String, unique=False, index=False)
    is_completed = Column(Boolean, unique=False,  default=False)
    is_alert = Column(Boolean, unique=False)


class BanRequests(BaseDBModel):
    __tablename__ = "requests"

    request_id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=False, index=False)
    user_id = Column(Integer, unique=False, primary_key=False, index=False)
    is_answered = Column(Boolean, unique=False,  default=False)


BaseDBModel.metadata.create_all(bind=engine)