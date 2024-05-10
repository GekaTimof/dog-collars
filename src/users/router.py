from fastapi import APIRouter, Depends
from src.users.schemas import User, UserAuth
from src.users.models import Users as db_user
import uuid
from src.users.crud import create_user, create_user_session
from src.database import DBSession
from typing import Annotated

router = APIRouter(prefix="/user")


# регистрация новово пользователя
@router.post("/register")
def new_user(user_new: Annotated[User, Depends()]):
    create_user(DBSession, user_new)
    return {"user": user_new}


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




