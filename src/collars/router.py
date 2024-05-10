from fastapi import APIRouter, Depends
from src.users.models import UsersSessions, Users
import uuid
from src.database import DBSession
import src.collars.crud as crud
from typing import Annotated
#from src.collars.models import Collars
from sqlalchemy.orm import Session
from src.collars import models, schemas



def get_db():
    db = DBSessionLocal()
    try:
        yield db
    finally:
        db.close()

def errors(func):
    def wrapper(*args, **kwargs):
       try:
           result = func(*args, **kwargs)
           print(result)
       except Exception as err:
           response = {'error': str(err)}
           return response, 400
       return result
    wrapper.__name__ = func.__name__
    return wrapper

def token_checker(func):
    def wrapper(*args, **kwargs):
        accessToken = request.args.get('token')
        print(accessToken)
        try:
            access = DBSession.query(UsersSessions).filter_by(token=accessToken).count()
            if access > 0:
                result = func(*args, **kwargs)
            else:
                raise HTTPException("accessToken not exist")
        except:
            raise HTTPException("accessToken not exist")
        return result

    wrapper.__name__ = func.__name__
    return wrapper



router = APIRouter(prefix="/user/collars")

# добавляем новый ошейник в систему
#@errors
#@token_checker
@router.post("/new_collar") #response_model= schemas.NewCollar
def new_collar(mac, db: Session = get_db()):
    #access = DBSession.query(UsersSessions).filter_by(token=token).one()
    #is_admin = DBSession.query(Users).filter_by(id=access.id).one()
    #is_admin = is_admin.is_superuser

    #if (is_admin):
    #    crud.create_collar(DBSession, mac)
    #    return {'access': 'yes'}
    #else:
    #    return {'access': 'no'}
    crud.create_collar(db, mac=mac)
    return {'access': 'yes'}


@router.post("/add_collar")
def add_collar(collar_id, token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    user_id = access.id
    crud.add_me_collar(DBSession, user_id, collar_id)
    return {"access": "True"}

@router.post("/remove_collar")
def remove_my_collar(collar_id, token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    user_id = access.id
    crud.remove_collar(DBSession, user_id, collar_id)
    return {"access": "True"}

@router.get("/my_collars")
def my_collars(token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    user_id = access.id
    return crud.collar_group(DBSession, user_id)

@router.post("/unactivate_collar")
def delete_collar(collar_id, token):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    is_admin = DBSession.query(Users).filter_by(id=access.id).one()
    is_admin = is_admin.is_superuser

    if (is_admin):
        crud.unactivate_collar(DBSession, collar_id)
        return {'access': 'yes'}
    else:
        return {'access': 'no'}


