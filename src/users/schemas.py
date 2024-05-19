from pydantic import BaseModel
#   FastAPI objects


# схема для существующего пользователя
class User(BaseModel):
    token: str


# схема для создания нового пользователя
class NewUser(BaseModel):
    number: str
    nickname: str
    password: str
    superuser: bool


# схема для авторизации пользователя
class UserAuth(BaseModel):
    number: str
    password: str


#
class BanUser(BaseModel):
    token: str
    user_id: int


