from fastapi import APIRouter, Depends
#from src.users.schemas import User, UserAuth
#from src.users.models import Users as db_user
import uuid
import json
from typing import Annotated
from src.database import SessionLocal, DBSession
from sqlalchemy.orm import Session
from src.community import models, schemas
from fastapi import HTTPException
from functools import wraps
import src.community.crud as crud
from src.community.schemas import NewCollarTask, Complaint, Respond, CompleteTask
from src.collars.crud import get_active_collar_by_id
from src.collars.schemas import Collar
# для декораторов
from src.users.crud import get_baned_user_by_id, get_session_by_token, get_user_id, get_user_by_id
from logger import get_logger

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/community")


# проверка существования токена
def token_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs[next(iter(kwargs))].token
        db: Session = DBSession()

        # проверяем правильный ли токен
        session_by_token = get_session_by_token(db=db, token=token)
        if session_by_token is None:
            raise HTTPException(status_code=400, detail="Wrong token")

        # получаем id пользователя
        user_id = get_user_id(db=db, token=token)
        # проверяем, не забанен ли пользователь токена
        baned_user_by_id = get_baned_user_by_id(db=db, user_id=user_id)
        if baned_user_by_id is not None:
            raise HTTPException(status_code=400, detail="Number is baned")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# проверка, есть ли у пользователя права супер пользователя
def superuser_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs[next(iter(kwargs))].token
        db: Session = DBSession()

        # получаем id пользователя
        user_id = get_user_id(db=db, token=token)

        # проверяем есть ли у пользователя права сурпер пользователя
        user_by_id = get_user_by_id(db=db, user_id=user_id)
        if user_by_id.is_superuser == 0:
            raise HTTPException(status_code=400, detail="User is not superuser")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# проверка, cуществует ли ошейник (ищем по id)
def collar_checker_by_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        collar_id = kwargs[next(iter(kwargs))].collar_id
        db: Session = DBSession()

        # проверяем, есть ли ошейник
        collar_by_id = get_active_collar_by_id(db=db, id=collar_id)
        if collar_by_id is None:
            raise HTTPException(status_code=400, detail="Collar not exist")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# проверка, cуществует ли задание (ищем по id)
def task_checker_by_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        collar_id = kwargs[next(iter(kwargs))].task_id
        db: Session = DBSession()

        # проверяем, что задание существует
        active_task_by_id = crud.get_active_task_by_id(db=db, task_id=task.task_id)
        if active_task_by_id is None:
            raise HTTPException(status_code=400, detail="Task not exist")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# отправление запроса на бан пользователя
@router.post("/add_complaint")
@token_checker
def add_complaint(complaint: Complaint, db: Session = Depends(get_db)):
    # проверяем существует ли тот, на кого направлена жалоба
    user_by_id = get_user_by_id(db=db, user_id=complaint.user_id)
    if user_by_id is None:
        raise HTTPException(status_code=400, detail="User to complaint not exist")

    return crud.add_user_complaint(db=db, complaint=complaint)


# отмечаем в бд, что мы ответили на жалобу
@router.post("/respond_complaint")
@token_checker
@superuser_checker
def respond_complaint(respond: Respond, db: Session = Depends(get_db)):
    # проверяем существует нужная жалоба
    complaint_id = crud.get_complaint_by_id(db=db, complaint_id=respond.complaint_id)
    if complaint_id is None:
        raise HTTPException(status_code=400, detail="Complaint not exist")

    return crud.respond_user_complaint(db=db, complaint_id=respond.complaint_id)


# добавляем задание для пользователей привязанных к ошейнику
@router.post("/add_task")
@token_checker
@superuser_checker
@collar_checker_by_id
def add_task(task: NewCollarTask, db: Session = Depends(get_db)):
    return crud.add_collar_task(db=db, task=task)


# получаем список задач для одного ошейника
@router.get("/collar_tasks")
@token_checker
@collar_checker_by_id
def collar_tasks(collar: Collar, db: Session = Depends(get_db)):
    return crud.get_collar_tasks(db=db, collar_id=collar.collar_id)


# пометка задания, как выполненого
@router.post("/complete_task")
@token_checker
@task_checker_by_id
def complete_task(task: CompleteTask, db: Session = Depends(get_db)):
    return crud.complete_collar_task(db=db, task_id=task.task_id)


