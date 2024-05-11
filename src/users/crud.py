from sqlalchemy.orm import Session
import src.users.models as models
import src.users.schemas as schemas
from src.users.models import UsersSessions as user_session
import uuid


# ищем токен в таблице токенов
def get_user_by_token(db: Session, token: str):
    return db.query(models.UsersSessions).filter_by(token=token).first()


# ищем номер таблице номеров
def get_user_by_number(db: Session, number: str):
    return db.query(models.Users).filter_by(number=number).first()


# добавление новового пользователя в бд
def create_user(db: Session, user: schemas.User) -> models.Users:
    fake_hash_password = user.password[::-1]

    db_user = models.Users(
        name=user.nickname,
        number=user.number,
        hash_password=fake_hash_password,
        is_active=True,
        is_superuser=user.superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# создание сессии для юзера и выдача ему токена
def create_user_session(db: Session, id: int) -> models.UsersSessions:
    # ищем токен данного пользователя
    result = db.query(user_session).filter_by(id = id).one()

    # если токен уже существует, то вовращанм его
    if result.token:
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