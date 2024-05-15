from fastapi import APIRouter, Depends
#from src.users.schemas import User, UserAuth
#from src.users.models import Users as db_user
import uuid
#from src.users.crud import create_user, create_user_session
from typing import Annotated
from src.database import SessionLocal
from sqlalchemy.orm import Session
from src.community import models, schemas
import src.community.crud as crud
from fastapi import HTTPException
from functools import wraps


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/user/community")

#@router.post("/add_task")
#def add_task(token, collar_id):



