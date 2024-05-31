from fastapi import APIRouter, Depends
from src.users.models import UsersSessions, Users
import uuid
import src.collars.crud as crud
from typing import Annotated
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.collars import models, schemas
from src.users.schemas import User
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
from src.collars.crud import get_active_collar_by_mac
from src.collars.crud import get_deactivated_collar_by_mac
from src.collars.crud import get_active_collar_by_id
from src.collars.crud import get_deactivated_collar_by_id
from src.collars.crud import get_user_collars
from src.database import SessionLocal, DBSession
from functools import wraps
# для декораторов
from src.users.crud import get_baned_user_by_id, get_session_by_token, get_user_id, get_user_by_id


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/collars")


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
        user_by_id = get_user_by_id(db, user_id=user_id)
        if user_by_id.is_superuser == 0:
            raise HTTPException(status_code=400, detail="User is not superuser")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# проверка, cуществует ли ошейник (ищем по id)
def Collar_checker_by_id(func):
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


# добавляем новый ошейник в систему
@router.post("/new_collar")
@token_checker
@superuser_checker
def new_collar(new_collar: schemas.NewCollar, db: Session = Depends(get_db)):
    # проверяем, нет ли выключенного ошейника с таким mac адресом (если есть, включаем обратно)
    deactivated_collar = get_deactivated_collar_by_mac(db=db, mac=new_collar.mac)
    if deactivated_collar is not None:
        collar_id = deactivated_collar.id
        return crud.activate_collar(db=db, collar_id=collar_id)

    # проверяем нет ли рабочего ошейника с таким mac в системе
    active_collar = get_active_collar_by_mac(db=db, mac=new_collar.mac)
    if active_collar is not None:
        raise HTTPException(status_code=400, detail="Collar already exist")

    return crud.create_collar(db=db, mac=new_collar.mac)


# привязываем ошейник к пользователю
@router.post("/add_collars")
@token_checker
@Collar_checker_by_id
def add_collar(collar: schemas.Collar, db: Session = Depends(get_db)):
    # получаем id пользователя
    user_id = get_user_id(db=db, token=collar.token)

    # проверяем, что пользователь не связан с ошейником
    user_collars = get_user_collars(db=db, user_id=user_id)
    if user_collars is not None and collar.collar_id in user_collars["collars_id"]:
        raise HTTPException(status_code=400, detail="It is already user collar")

    return crud.add_me_collar(db=db, user_id=user_id, collar_id=collar.collar_id)


# отвязываем ошейник от пользователю
@router.post("/remove_collar")
@token_checker
@Collar_checker_by_id
def remove_my_collar(collar: schemas.Collar, db: Session = Depends(get_db)):
    # получаем id пользователя
    user_id = get_user_id(db=db, token=collar.token)

    # проверяем, привязан ли ошейник к пользователю
    user_collars = get_user_collars(db=db, user_id=user_id)
    if user_collars is None or collar.collar_id not in user_collars["collars_id"]:
        raise HTTPException(status_code=400, detail="It is not user collar")

    return crud.remove_collar(db=db, user_id=user_id, collar_id=collar.collar_id)


# выдаём пользователю список id его ошейников
@router.get("/get_my_collars")
@token_checker
def my_collars(user: Annotated[User, Depends()], db: Session = Depends(get_db)):
    # получаем id пользователя
    user_id = get_user_id(db=db, token=user.token)

    return get_user_collars(db=db, user_id=user_id)


# удаляем ошейник (меняем статус на is_active=0)
@router.post("/deactivate_collar")
@token_checker
@superuser_checker
def delete_collar(collar: schemas.Collar, db: Session = Depends(get_db)):
    # проверяем не находиться ли ошейник в деактивированном состоянии
    collar_by_id = get_deactivated_collar_by_id(db=db, id=collar.collar_id)
    if collar_by_id is not None:
        raise HTTPException(status_code=400, detail="Collar already deactivate")

    # проверяем, есть ли ошейник
    collar_by_id = get_active_collar_by_id(db=db, id=collar.collar_id)
    if collar_by_id is None:
        raise HTTPException(status_code=400, detail="Collar not exist")

    return crud.deactivate_collar(db, collar_id=collar.collar_id)


# Активируем выключенный ошейник (меняем статус на is_active=1)
@router.post("/activate_collar")
@token_checker
@superuser_checker
def delete_collar(collar: schemas.Collar, db: Session = Depends(get_db)):
    # проверяем не находиться ли ошейник в деактивированном состоянии
    collar_by_id = get_deactivated_collar_by_id(db=db, id=collar.collar_id)
    if collar_by_id is None:
        raise HTTPException(status_code=400, detail="Collar not deactivate collar")

    return crud.deactivate_collar(db, collar_id=collar.collar_id)


# добавляем кординаты присланные с ошейника
@router.post("/post_coordinates")
def delete_collar(cords: schemas.NewCoordinates, db: Session = Depends(get_db)):
    # проверяем, есть ли ошейник
    collar_by_mac = get_active_collar_by_mac(db=db, mac=cords.mac)
    if collar_by_mac is None:
        raise HTTPException(status_code=400, detail="Collar not exist")

    collar_id = collar_by_mac.id

    return crud.get_coordinates(db, cords=cords, collar_id=collar_id)


# даём последнюю кординату ошейника
@router.get("/get_last_coordinates")
@token_checker
@Collar_checker_by_id
def get_last_coordinates(collar: Annotated[schemas.Collar, Depends()], db: Session = Depends(get_db)):
    coordinates = crud.get_last_collars_coordinates(db=db, collar_id=collar.collar_id)

    # проверяем, что мы получили координаты
    if coordinates is None:
        raise HTTPException(status_code=400, detail="Collar have no coordinates")

    return coordinates


# выдаём всех владельцев ошейника
@router.get("/owners")
@token_checker
@Collar_checker_by_id
def owners(collar: Annotated[schemas.Collar, Depends()], db: Session = Depends(get_db)):
    return crud.collars_owners(db=db, collar_id=collar.collar_id)


# выдаём всё ощейники без владельцев
@router.get("/get_lonely_collars")
@token_checker
def get_lonely_collars(user: Annotated[User, Depends()], db: Session = Depends(get_db)):
    return crud.get_all_lonely_collars(db=db)


# выдаём список ваших заданий
@router.get("/get_my_tasks")
@token_checker
def get_my_tasks(user: Annotated[User, Depends()], db: Session = Depends(get_db)):
    user_id = get_user_id(db=db, token=user.token)
    return crud.get_user_tasks(db=db, user_id=user_id)

