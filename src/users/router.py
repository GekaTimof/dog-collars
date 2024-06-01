from fastapi import APIRouter, Depends
import src.users.schemas as schemas
from src.users.models import Users as db_user
import src.users.crud as crud
from src.users.crud import create_user_session
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.database import SessionLocal, DBSession
from src.users import schemas
from functools import wraps
from argon2 import PasswordHasher
from logger import get_logger
# для декораторов
from src.users.crud import get_baned_user_by_id, get_session_by_token, get_user_id, get_user_by_id
from src.function import get_arg_from_request



userlogger = get_logger("user_loger")

def get_db():
    userlogger.debug("open db")
    db = SessionLocal()
    try:
        yield db
    finally:
        userlogger.debug("close db")
        db.close()


router = APIRouter(prefix="/user")


# проверка существования токена
def token_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # получаем токен
        token = get_arg_from_request(kwargs=kwargs, arg='token')
        # создаём сессию
        db: Session = DBSession()

        # проверяем правильный ли токен
        session_by_token = get_session_by_token(db=db, token=token)
        if session_by_token is None:
            userlogger.warning("Problems with token")
            raise HTTPException(status_code=400, detail="Wrong token")

        # получаем id пользователя
        user_id = get_user_id(db=db, token=token)
        # проверяем, не забанен ли пользователь токена
        baned_user_by_id = get_baned_user_by_id(db=db, user_id=user_id)
        if baned_user_by_id is not None:
            userlogger.error("Number is banned")
            raise HTTPException(status_code=400, detail="Number is baned")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# проверка, есть ли у пользователя права супер пользователя
def superuser_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # получаем токен
        token = get_arg_from_request(kwargs=kwargs, arg='token')
        # создаём сессию
        db: Session = DBSession()

        # получаем id пользователя
        user_id = get_user_id(db=db, token=token)

        # проверяем есть ли у пользователя права сурпер пользователя
        user_by_id = get_user_by_id(db=db, user_id=user_id)
        if user_by_id.is_superuser == 0:
            userlogger.error("User is not admin")
            raise HTTPException(status_code=400, detail="User is not superuser")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# регистрация нового пользователя
@router.post("/register")
def new_user(user_new: schemas.NewUser, db: Session = Depends(get_db)):
    # проверяем что номер введён правильно
    if not(user_new.number.isdigit()):
        userlogger.error("User " + str(PasswordHasher().hash(user_new.number)[-20:]) + " is incorrect number")
        raise HTTPException(status_code=400, detail="Incorrect number")

    # проверяем нет ли пользователя с таким номером в системе
    result = crud.get_user_by_number(db, user_new.number)
    if result is not None:
        userlogger.warning("User " + str(PasswordHasher().hash(user_new.number)[-20:]) + " is already exist")
        raise HTTPException(status_code=400, detail="Number already exist")

    userlogger.info("User " + str(PasswordHasher().hash(user_new.number)[-20:]) + " succesfully registred")
    return crud.create_user(db=db, user=user_new)


# авторизация существующего пользователя по номеру и паролю
@router.post("/auth")
def user_auth(user: schemas.UserAuth, db: Session = Depends(get_db)):
    # проверяем не забанен ли порльзователь
    baned_user_by_id = crud.get_baned_user_by_number(db, user.number)
    if baned_user_by_id is not None:
        userlogger.error("User " + str(PasswordHasher().hash(user.number)[-20:]) + " is banned")
        raise HTTPException(status_code=400, detail="Number is baned")

    # проверяем есть ли пользователя с таким номером в системе
    user_by_number = crud.get_user_by_number(db, user.number)
    if user_by_number is None:
        userlogger.warning("User " + str(PasswordHasher().hash(user.number)[-20:]) + " not exist")
        raise HTTPException(status_code=400, detail="Number not exist")

    userlogger.info("User " + str(PasswordHasher().hash(user.number)[-20:]) + " was auth")

    # проверяем что проль подходи
    try:
        PasswordHasher().verify(user_by_number.hash_password, user.password)
    except:
        userlogger.warning("User " + str(PasswordHasher().hash(user.number)[-20:]) + " gives wrong password")
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

