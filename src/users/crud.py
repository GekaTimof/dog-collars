from sqlalchemy.orm import Session
import src.users.models as models
import src.users.schemas as schemas
from src.users.models import UsersSessions
import uuid
from argon2 import PasswordHasher


# ищем токен в таблице UsersSessions
def get_session_by_token(db: Session, token: str):
    return db.query(models.UsersSessions).filter_by(token=token).first()


# получаем id пользователя
def get_user_id(db: Session, token: str):
    result = get_session_by_token(db, token).id
    return result


# ищем рабочего пользователя по id
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.Users).filter_by(id=user_id, is_active=1).first()


# ищем забаненого пользователя по id
def get_baned_user_by_id(db: Session, user_id: int):
    return db.query(models.Users).filter_by(id=user_id, is_active=0).first()


# ищем номер рабочего пользователя в таблице Users
def get_user_by_number(db: Session, number: str):
    return db.query(models.Users).filter_by(number=number, is_active=1).first()


# ищем номер забаненого пользователя в таблице Users
def get_baned_user_by_number(db: Session, number: str):
    return db.query(models.Users).filter_by(number=number, is_active=0).first()


# добавление новового пользователя в бд
def create_user(db: Session, user: schemas.NewUser) -> models.Users:
    # хэшируем пароль пользователя
    hash_password = PasswordHasher().hash(user.password)

    db_user = models.Users(
        name=user.nickname,
        number=user.number,
        hash_password=hash_password,
        is_active=1,
        is_superuser=user.superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# создание сессии для юзера и выдача ему токена
def create_user_session(db: Session, id: int) -> models.UsersSessions:
    # ищем токен данного пользователя
    result = db.query(UsersSessions).filter_by(id=id).first()
    # если токен уже существует, то вовращанм его
    if result is not None:
        db_user_session = models.UsersSessions(
            id=id,
            token=result.token
        )
    # если токена нет создаем его
    else:
        db_user_session = models.UsersSessions(
            id=id,
            token=str(uuid.uuid4())
        )

        db.add(db_user_session)
        db.commit()
        db.refresh(db_user_session)
    return db_user_session


# бан пользователя (ставим статус is_active=0)
def user_ban(db: Session, user_id: int):
    db_user_bun = db.query(models.Users).filter_by(id=user_id).one()
    db_user_bun.is_active = 0
    db.commit()
    db.refresh(db_user_bun)
    return {
        "operation": "ban user",
        "access": "True"
    }
