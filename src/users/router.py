from fastapi import APIRouter, Depends
from src.users.schemas import User, UserAuth
from src.users.models import Users as db_user
import uuid
import src.users.crud as crud
from src.users.crud import create_user_session
from typing import Annotated
from src.users.crud import get_user_by_number
from sqlalchemy.orm import Session
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from src.database import SessionLocal
from src.users import models, schemas
from functools import wraps


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/user")


# проверка что номер есть в системе
def number_exist_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        number = args[0][0]
        db: Session = Depends(get_db)

        # проверяем что номер существует
        result = get_user_by_number(db, number)
        if result is None:
            raise HTTPException(status_code=400, detail="Number not exist")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# регистрация новово пользователя
@router.post("/register")
def new_user(user_new: Annotated[User, Depends()], db: Session = Depends(get_db)):
    result = get_user_by_number(db, user_new.number)
    # проверяем нет ли пользователя с таким номером в системе
    if result is not None:
        raise HTTPException(status_code=400, detail="Number already exist")

    return crud.create_user(db=db, user=user_new)


# авторизация существующего пользователя по номеру и паролю
@router.post("/auth")
def user_auth(user: Annotated[UserAuth, Depends()], db: Session = Depends(get_db)):
    result = get_user_by_number(db, user.number)
    # проверяем есть ли пользователя с таким номером в системе
    if result is None:
        raise HTTPException(status_code=400, detail="Number not exist")

    fake_hash_password = user.password[::-1]
    # проверяем что проль подходи
    if fake_hash_password != result.hash_password:
        raise HTTPException(status_code=400, detail="wrong passwd")

    response = create_user_session(db, result.id)
    return {"access": "yes",
            "token": response.token}


# бан пользователя (ставим статус is_active=0)
#@router.post("/ban_user")
#def user_auth(user: Annotated[UserAuth, Depends()], db: Session = Depends(get_db)):
