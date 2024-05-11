from fastapi import APIRouter, Depends
from src.users.schemas import User, UserAuth
from src.users.models import Users as db_user
import uuid
import src.users.crud as crud
from src.users.crud import create_user_session
from src.database import DBSession
from typing import Annotated
from src.users.crud import get_user_by_number
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

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


router = APIRouter(prefix="/user")


# регистрация новово пользователя
@router.post("/register")
def new_user(user_new: User, db: Session = Depends(get_db)):
    # проверяем нет ли пользователя с таким номером в системе
    number_in_db = get_user_by_number(db, user_new.number)
    if number_in_db is not None:
        raise HTTPException(status_code=400, detail="Number already exist")

    return crud.create_user(db=db, user=user_new)


# авторизация существующего пользователя по номеру и паролю
@router.post("/auth")
def user_auth(user: Annotated[UserAuth, Depends()]):
    result = DBSession.query(db_user).filter_by(number=user.number).one()
    user_id = result.id
    if user.password[::-1] == result.hash_password:
        response = create_user_session(DBSession, user_id)
        return {"access": "yes",
                "token": response.token}
    else:
        return {"access": "no"}




