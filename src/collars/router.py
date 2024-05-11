from fastapi import APIRouter, Depends
from src.users.models import UsersSessions, Users
import uuid
from src.database import DBSession
import src.collars.crud as crud
from typing import Annotated
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.collars import models, schemas
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.users.crud import get_user_by_token
from src.collars.crud import get_collar_by_mac


SQLALCHEMY_DATABASE_URL = "sqlite:///./collars.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/user/collars")


# добавляем новый ошейник в систему
@router.post("/new_collar")
def new_collar(token, mac, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    token_in_db = get_user_by_token(db, token)
    if token_in_db is None:
        raise HTTPException(status_code=400, detail="Wrong token")
    # проверяем нет ли уже такова mac в системе
    collar_in_db = get_collar_by_mac(db, mac)
    if collar_in_db is not None:
        raise HTTPException(status_code=400, detail="Collar already exist")

    return crud.create_collar(db=db, mac=mac)


@router.post("/add_collar")
def add_collar(collar_id, token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    user_id = access.id
    crud.add_me_collar(DBSession, user_id, collar_id)
    return {"access": "True"}

@router.post("/remove_collar")
def remove_my_collar(collar_id, token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    user_id = access.id
    crud.remove_collar(DBSession, user_id, collar_id)
    return {"access": "True"}

@router.get("/my_collars")
def my_collars(token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    user_id = access.id
    return crud.collar_group(DBSession, user_id)

@router.post("/unactivate_collar")
def delete_collar(collar_id, token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    is_admin = DBSession.query(Users).filter_by(id=access.id).one()
    is_admin = is_admin.is_superuser

    if (is_admin):
        crud.unactivate_collar(DBSession, collar_id)
        return {'access': 'yes'}
    else:
        return {'access': 'no'}


