from sqlalchemy.orm import Session
import src.collars.models as models
import src.collars.schemas as schemas
import datetime
from src.users.crud import get_user_by_id
from src.community.crud import get_collar_tasks

# ищем mac работающего ошейника в таблице Collars
def get_active_collar_by_mac(db: Session, mac: int):
    return db.query(models.Collars).filter_by(mac=mac, is_active=1).first()


# ищем mac не работающего ошейника в таблице Collars
def get_deactivated_collar_by_mac(db: Session, mac: str):
    return db.query(models.Collars).filter_by(mac=mac, is_active=0).first()


# ищем id работающего ошейника в таблице Collars
def get_active_collar_by_id(db: Session, id: int):
    return db.query(models.Collars).filter_by(id=id, is_active=1).first()


# ищем id не работающего ошейника в таблице Collars
def get_deactivated_collar_by_id(db: Session, id: int):
    return db.query(models.Collars).filter_by(id=id, is_active=0).first()


# получить все ошейники пользователя
def get_user_collars(db: Session, user_id: int):
    db_pets = [x.collar_id for x in db.query(models.Owners).filter_by(user_id=user_id).distinct()]
    is_active = []
    for collar_id in db_pets:
        collar = db.query(models.Collars).filter_by(id=collar_id).first()
        if (collar.is_active == 1):
            is_active.append(collar_id)
    return {"owner_id": user_id,
            "collars_id": is_active}


# создаем новый ошейник
def create_collar(db: Session, mac: str) -> models.Collars:
    db_collar = models.Collars(
        mac=mac,
        is_active=True
    )
    db.add(db_collar)
    db.commit()
    db.refresh(db_collar)
    return db_collar


# привязываем ошейник к пользователю
def add_me_collar(db: Session, user_id: int, collar_id: int) -> models.Owners:
    db_collar_user = models.Owners(
        user_id=user_id,
        collar_id=collar_id
    )
    db.add(db_collar_user)
    db.commit()
    db.refresh(db_collar_user)
    return db_collar_user


# отвязываем ошейник от пользователю
def remove_collar(db: Session, user_id: int, collar_id: int):
    db_collar_user = db.query(models.Owners).filter_by(user_id=user_id, collar_id=collar_id).one()
    db.delete(db_collar_user)
    db.commit()
    return {"access": "True"}


# выдаёт список ошейников которые привязаны к пользователю
def collar_group(db: Session, user_id: int):
    db_pets = [x.collar_id for x in db.query(models.Owners).filter_by(user_id=user_id).distinct()]
    is_active = []
    for i in db_pets:
        collar_n = db.query(models.Collars).filter_by(id=i).one()
        if (collar_n.is_active == True):
            is_active.append(i)
    return {"owner_id": user_id,
            "collars_id": is_active}


# выключаем ошейник (он прерстает использоваться и считается несуществующим)
def deactivate_collar(db: Session, collar_id: int):
    db_collar_active = db.query(models.Collars).filter_by(id=collar_id).one()
    db_collar_active.is_active = 0
    db.commit()
    db.refresh(db_collar_active)
    return {
        "operation": "deactivate collar",
        "access": "True"
    }


# включаем ошейник
def activate_collar(db: Session, collar_id: int):
    db_collar_active = db.query(models.Collars).filter_by(id=collar_id).one()
    db_collar_active.is_active = 1
    db.commit()
    db.refresh(db_collar_active)
    return {
        "operation": "activate collar",
        "access": "True"
    }


# добавляем кординаты, полученные от ошейника, в базу данных
def get_coordinates(db: Session, cords: schemas.NewCoordinates, collar_id: int):
    db_collar_cords = models.Coordinates(
        collar_id=collar_id,
        coordinates=cords.coordinates,
        time=datetime.datetime.now()
    )
    db.add(db_collar_cords)
    db.commit()
    db.refresh(db_collar_cords)
    return db_collar_cords


def collars_owners(db: Session, collar_id: int):
    db_owners = [x.user_id for x in db.query(models.Owners).filter_by(collar_id=collar_id).distinct()]

    is_active = []
    for user_id in db_owners:
        user_by_id = get_user_by_id(db=db, user_id=user_id)
        if user_by_id is not None:
            is_active.append(user_id)

    return {"collar_id": collar_id,
            "owners_id": is_active}


def get_last_collars_coordinates(db: Session, collar_id: int):
    return db.query(models.Coordinates).filter_by(collar_id=collar_id, is_active=1).order_by(models.Coordinates.time.desc()).first()


def get_all_lonely_collars(db: Session):
    all_collars = [x.id for x in db.query(models.Collars).filter_by(is_active=1).distinct()]
    all_collars_with_owner = [x.collar_id for x in db.query(models.Owners).distinct()]

    lonely_collars = []
    for collar_id in all_collars:
        if collar_id not in all_collars_with_owner:
            lonely_collars.append(collar_id)

    return lonely_collars


def get_user_tasks(db: Session, user_id: int):
    user_collars = get_user_collars(db=db, user_id=user_id)['collars_id']

    all_tasks = []
    for collar_id in user_collars:
        all_tasks += get_collar_tasks(db=db, collar_id=collar_id)['task_id']

    return all_tasks









