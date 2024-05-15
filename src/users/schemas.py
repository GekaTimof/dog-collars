from pydantic import BaseModel
#   FastAPI objects


class User(BaseModel):
    number: str
    nickname: str
    password: str
    superuser: bool


class UserAuth(BaseModel):
    number: str
    password: str

