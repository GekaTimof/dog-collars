from fastapi import APIRouter, Depends
from src.users.models import UsersSessions, Users
import uuid
import src.collars.crud as crud
from typing import Annotated
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.collars import models, schemas
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
from src.users.crud import get_session_by_token
from src.users.crud import get_user_by_id
from src.collars.crud import get_active_collar_by_mac
from src.collars.crud import get_deactivated_collar_by_mac
from src.collars.crud import get_active_collar_by_id
from src.collars.crud import get_deactivated_collar_by_id
from src.collars.crud import get_user_collars
from src.database import SessionLocal
from functools import wraps


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/user/collars")


def token_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs.get('token')
        db: Session = Depends(get_db)

        # проверяем правильный ли токен
        session_by_token = get_session_by_token(db=db, token=token)
        if session_by_token is None:
            raise HTTPException(status_code=400, detail="Wrong token")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper



# добавляем новый ошейник в систему
@router.post("/new_collar")
@token_checker
def new_collar(token: str, mac: str, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db, token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # проверяем есть ли у пользователя права сурпер пользователя
    user_by_id = get_user_by_id(db, session_by_token.id)
    if user_by_id.is_superuser == 0:
        raise HTTPException(status_code=400, detail="User is not superuser")

    # проверяем, нет ли выключенного ошейника с таким mac адресом (если есть, включаем обратно)
    deactivated_collar = get_deactivated_collar_by_mac(db=db, mac=mac)
    if deactivated_collar is not None:
        collar_id = deactivated_collar.id
        return crud.activate_collar(db=db, collar_id=collar_id)

    # проверяем нет ли рабочего ошейника с таким mac в системе
    active_collar = get_active_collar_by_mac(db, mac)
    if active_collar is not None:
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
    collar_by_id = get_active_collar_by_id(db=db, id=collar_id)
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

    # проверяем, есть ли ошейник
    collar_by_id = get_active_collar_by_id(db=db, id=collar_id)
    if collar_by_id is None:
        raise HTTPException(status_code=400, detail="Collar not exist")

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


# удаляем ошейник (меняем статус на is_active=0)
@router.post("/deactivate_collar")
def delete_collar(token: str, collar_id: int, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db, token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # проверяем есть ли у пользователя права сурпер пользователя
    user_by_id = get_user_by_id(db, session_by_token.id)
    if user_by_id.is_superuser == 0:
        raise HTTPException(status_code=400, detail="User is not superuser")

    # проверяем не находиться ли ошейник в деактивированном состоянии
    collar_by_id = get_deactivated_collar_by_id(db=db, id=collar_id)
    if collar_by_id is not None:
        raise HTTPException(status_code=400, detail="Collar already deactivate")

    # проверяем, есть ли ошейник
    collar_by_id = get_active_collar_by_id(db=db, id=collar_id)
    if collar_by_id is None:
        raise HTTPException(status_code=400, detail="Collar not exist")

    return crud.deactivate_collar(db, collar_id=collar_id)


# Активируем выключенный ошейник (меняем статус на is_active=1)
@router.post("/activate_collar")
def delete_collar(token: str, collar_id: int, db: Session = Depends(get_db)):
    # проверяем правильный ли токен
    session_by_token = get_session_by_token(db, token)
    if session_by_token is None:
        raise HTTPException(status_code=400, detail="Wrong token")

    # проверяем есть ли у пользователя права сурпер пользователя
    user_by_id = get_user_by_id(db, session_by_token.id)
    if user_by_id.is_superuser == 0:
        raise HTTPException(status_code=400, detail="User is not superuser")

    # проверяем не находиться ли ошейник в деактивированном состоянии
    collar_by_id = get_deactivated_collar_by_id(db=db, id=collar_id)
    if collar_by_id is None:
        raise HTTPException(status_code=400, detail="Collar not deactivate collar")

    return crud.deactivate_collar(db, collar_id=collar_id)


# добавляем кординаты присланные с ошейника
@router.post("/get_coordinates")
def delete_collar(cords: Annotated[schemas.NewCoordinates, Depends()], db: Session = Depends(get_db)):
    # проверяем, есть ли ошейник
    collar_by_mac = get_active_collar_by_mac(db=db, mac=cords.mac)
    if collar_by_mac is None:
        raise HTTPException(status_code=400, detail="Collar not exist")

    collar_id = collar_by_mac.id

    return crud.get_coordinates(db, cords=cords, collar_id=collar_id)


