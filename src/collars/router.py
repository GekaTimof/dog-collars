from fastapi import APIRouter, Depends
from src.users.models import UsersSessions, Users
import uuid
from src.database import DBSession
import src.collars.crud as crud
from typing import Annotated
from src.collars.models import Collars


def errors(func):
    def wrapper(*args, **kwargs):
       try:
           print("\n\n\n\n" + str("errrrrs") + "\n\n\n\n\n")
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

        try:
            access = DBSession.query(UsersSessions).filter_by(token=accessToken).limit(1).all()
            result = func(*args, **kwargs)
        except:
            raise Exception("accessToken not exist")
        return result

        #print( "\n\n\n\n" + str(not(access is None)) + "\n\n\n\n\n")

        #if access:
        #    result = func(*args, **kwargs)
       # else:
        #    raise Exception("accessToken not exist")

        #return result

    wrapper.__name__ = func.__name__
    return wrapper



router = APIRouter(prefix="/user/collars")

# добавляем новый ошейник в систему
#@errors
#@token_checker
@router.post("/new_collar")
def new_collar(token, mac):
    access = DBSession.query(UsersSessions).filter_by(token=token).one()
    is_admin = DBSession.query(Users).filter_by(id=access.id).one()
    is_admin = is_admin.is_superuser


    if (is_admin):
        crud.create_collar(DBSession, mac)
        return {'access': 'yes'}
    else:
        return {'access': 'no'}


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


