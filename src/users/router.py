from fastapi import APIRouter, Depends
import src.users.schemas as schemas
from src.users.models import Users as db_user
import uuid
import src.users.crud as crud
from src.users.crud import create_user_session
from typing import Annotated
from sqlalchemy.orm import Session
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from src.database import SessionLocal, DBSession
from src.users import models, schemas
from functools import wraps
from argon2 import PasswordHasher
# для декораторов
from src.users.crud import get_baned_user_by_id, get_session_by_token, get_user_id, get_user_by_id
from logger import get_logger, ColoredFormatter


userlogger = get_logger("user_loger")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/user")


# проверка существования токена
def token_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs[next(iter(kwargs))].token
        db: Session = DBSession()

        # проверяем правильный ли токен
        session_by_token = get_session_by_token(db=db, token=token)
        if session_by_token is None:
            raise HTTPException(status_code=400, detail="Wrong token")

        # получаем id пользователя
        user_id = get_user_id(db=db, token=token)
        # проверяем, не забанен ли пользователь токена
        baned_user_by_id = get_baned_user_by_id(db=db, user_id=user_id)
        if baned_user_by_id is not None:
            raise HTTPException(status_code=400, detail="Number is baned")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# проверка, есть ли у пользователя права супер пользователя
def superuser_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs[next(iter(kwargs))].token
        db: Session = DBSession()

        # получаем id пользователя
        user_id = get_user_id(db=db, token=token)

        # проверяем есть ли у пользователя права сурпер пользователя
        user_by_id = get_user_by_id(db=db, user_id=user_id)
        if user_by_id.is_superuser == 0:
            raise HTTPException(status_code=400, detail="User is not superuser")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!     Начало запросов     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# регистрация нового пользователя
@router.post("/register")
def new_user(user_new: schemas.NewUser, db: Session = Depends(get_db)):
    result = crud.get_user_by_number(db, user_new.number)
    # проверяем нет ли пользователя с таким номером в системе
    if result is not None:
        userlogger.warning("User " + str(PasswordHasher().hash(user_new.number)) + " is already exist")
        raise HTTPException(status_code=400, detail="Number already exist")

    userlogger.info("User " + str(PasswordHasher().hash(user_new.number)) + " succesfully registred")
    return crud.create_user(db=db, user=user_new)


# авторизация существующего пользователя по номеру и паролю
@router.post("/auth")
def user_auth(user: schemas.UserAuth, db: Session = Depends(get_db)):
    # проверяем не забанен ли порльзователь
    baned_user_by_id = crud.get_baned_user_by_number(db, user.number)
    if baned_user_by_id is not None:
        raise HTTPException(status_code=400, detail="Number is baned")

    # проверяем есть ли пользователя с таким номером в системе
    user_by_number = crud.get_user_by_number(db, user.number)
    if user_by_number is None:
        raise HTTPException(status_code=400, detail="Number not exist")

    # проверяем что проль подходи
    try:
        PasswordHasher().verify(user_by_number.hash_password, user.password)
    except:
        raise HTTPException(status_code=400, detail="wrong passwd")

    response = create_user_session(db, user_by_number.id)
    return {"access": "yes",
            "token": response.token}


# бан пользователя (ставим статус is_active=0)
@router.post("/ban")
@token_checker
@superuser_checker
def ban(user_to_ban: schemas.BanUser, db: Session = Depends(get_db)):
    # проверяемc что пользователь которого мы хотим забанить существует
    user_by_id = get_user_by_id(db=db, user_id=user_to_ban.user_id)
    if user_by_id is None:
        raise HTTPException(status_code=400, detail="User to ban not exist")

    return crud.user_ban(db=db, user_id=user_to_ban.user_id)

