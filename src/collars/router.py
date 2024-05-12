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
from src.users.crud import get_session_by_token
from src.users.crud import get_user_by_id
from src.collars.crud import get_collar_by_mac
from src.collars.crud import get_collar_by_id
from src.collars.crud import get_user_collars


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


def token_checker(func):
    def wrapper(*args, **kwargs):
        token = request.args.get('token')
        db: Session = Depends(get_db)

        # проверяем правильный ли токен
        result = get_user_by_token(db, token)
        if result is None:
            raise HTTPException(status_code=400, detail="Wrong token")

        return result

    wrapper.__name__ = func.__name__
    return wrapper


# добавляем новый ошейник в систему
@router.post("/new_collar")
def new_collar(token: str, mac: str, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db, token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # проверяем есть ли у пользователя права сурпер пользователя
    user_by_id = get_user_by_id(db, session_by_token.id)
    if user_by_id.is_superuser == 0:
        raise HTTPException(status_code=400, detail="User is not superuser")

    # проверяем нет ли уже такова mac в системе
    collar_by_mac = get_collar_by_mac(db, mac)
    if collar_by_mac is not None:
        raise HTTPException(status_code=400, detail="Collar already exist")

    return crud.create_collar(db=db, mac=mac)


# привязываем ошейник к пользователю
@router.post("/add_collar")
def add_collar(token: str, collar_id: int, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db=db, token=token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # получаем id пользователя
    user_id = session_by_token.id

    # проверяем, есть ли ошейник
    collar_by_id = get_collar_by_id(db=db, id=collar_id)
    if collar_by_id is None:
        raise HTTPException(status_code=400, detail="Collar not exist")

    # проверяем, что пользователь не связан с ошейником
    user_collars = get_user_collars(db=db, user_id=user_id)
    if user_collars is not None and collar_id in user_collars["collars_id"]:
        raise HTTPException(status_code=400, detail="It is already user collar")

    return crud.add_me_collar(db=db, user_id=user_id, collar_id=collar_id)


# отвязываем ошейник от пользователю
@router.post("/remove_collar")
def remove_my_collar(token: str, collar_id: int, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db=db, token=token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # получаем id пользователя
    user_id = session_by_token.id

    # проверяем, привязан ли ошейник к пользователю
    user_collars = get_user_collars(db=db, user_id=user_id)
    if user_collars is None or collar_id not in user_collars["collars_id"]:
        raise HTTPException(status_code=400, detail="It is not user collar")

    return crud.remove_collar(db=db, user_id=user_id, collar_id=collar_id)


# выдаём пользователю список id его ошейников
@router.get("/my_collars")
def my_collars(token, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db=db, token=token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # получаем id пользователя
    user_id = session_by_token.id

    return get_user_collars(db=db, user_id=user_id)



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


