from pydantic import BaseModel

class collar(BaseModel):
    id: int
    mac: str
    is_active: bool

class NewCollar(BaseModel):
    number: str
    mac: str


# модель для получения коордитан
class NewCoordinates(BaseModel):
    mac: str
    coordinates: str
