from pydantic import BaseModel


# схема для ошейников
class Collar(BaseModel):
    token: str
    collar_id: int


# схема для регистрации ошейника
class NewCollar(BaseModel):
    token: str
    mac: str


# схема для получения коордитан
class NewCoordinates(BaseModel):
    mac: str
    coordinates: str
