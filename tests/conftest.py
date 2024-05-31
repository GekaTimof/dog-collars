import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import BaseDBModel, engine, DBSession
import src.users.models as user_models


@pytest.fixture(scope="session", autouse=True)
def setup_dp():
    BaseDBModel.metadata.drop_all(engine)
    BaseDBModel.metadata.create_all(engine)
    #тут по-хорошему надо все махинации с тестированием проводить на тестовой базе

@pytest.fixture(scope="session", autouse=True)
def started_users():
    db_user1 = user_models.Users(
        name="Anna",
        number="89657123459",
        hash_password="098",
        is_active=1,
        is_superuser=False
    )
    db_user2 = user_models.Users(
        name="Dima",
        number="88003457826",
        hash_password="Dima666",
        is_active=1,
        is_superuser=True
    )
    db_user_session = user_models.UsersSessions(
        id=2,  #Dima
        token="56a2a257-173f-4ba7-bbf4-fd35f1498f15"
    )

    DBSession.add(db_user1)
    DBSession.add(db_user2)
    DBSession.add(db_user_session)
    DBSession.commit()
    DBSession.refresh(db_user1)
    DBSession.refresh(db_user2)
    DBSession.refresh(db_user_session)


client = TestClient(app)
