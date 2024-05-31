import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import BaseDBModel, engine, DBSession
import src.users.models as user_models
from src.users.crud import create_user
from argon2 import PasswordHasher


@pytest.fixture(scope="session", autouse=True)
def setup_dp():
    BaseDBModel.metadata.drop_all(engine)
    BaseDBModel.metadata.create_all(engine)
    #тут по-хорошему надо все махинации с тестированием проводить на тестовой базе

@pytest.fixture(scope="session", autouse=True)
def started_users():

    #создаем двух тестовых пользователей: админа и обычного
    db_user1 = user_models.Users(
        name="Anna",
        number="89657123459",
        hash_password=PasswordHasher().hash("890"),
        is_active=1,
        is_superuser=False
    )

    db_user2 = user_models.Users(
        name="Dima",
        number="88003457826",
        hash_password=PasswordHasher().hash("dima"),
        is_active=1,
        is_superuser=True
    )

    #создаем две тестовые сессии
    db_user_session1 = user_models.UsersSessions(
        id=2,  #Dima
        token="token2"
    )
    db_user_session2 = user_models.UsersSessions(
        id=1,  #Anna
        token="token1"
    )

    DBSession.add(db_user1)
    DBSession.add(db_user2)
    DBSession.add(db_user_session1)
    DBSession.add(db_user_session2)
    DBSession.commit()
    DBSession.refresh(db_user1)
    DBSession.refresh(db_user2)
    DBSession.refresh(db_user_session1)
    DBSession.refresh(db_user_session2)


client = TestClient(app)
