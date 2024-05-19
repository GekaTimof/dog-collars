from pydantic import BaseModel


# схема для запросов на бан пользователя
class Complaint(BaseModel):
    token: str
    user_id: int
    text: str


# схеиа для ответа на жалобы
class Respond(BaseModel):
    token: str
    complaint_id: int


# схема для добавления нового задания
class NewCollarTask(BaseModel):
    token: str
    collar_id: int
    text: str
    is_alert: bool


# схема для выполнения задания
class CompleteTask(BaseModel):
    token: str
    task_id: int

