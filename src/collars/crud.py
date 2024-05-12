from sqlalchemy.orm import Session
import src.collars.models as models
import src.collars.schemas as schemas


# ищем mac работающего ошейника в таблице Collars
def get_deactivated_collar_by_mac(db: Session, mac: str):
    return db.query(models.Collars).filter_by(mac=mac, is_active=0).first()


# ищем mac не работающего ошейника в таблице Collars
def get_active_collar_by_mac(db: Session, mac: int):
    return db.query(models.Collars).filter_by(mac=mac, is_active=1).first()


# ищем id работающего ошейника в таблице Collars
def get_active_collar_by_id(db: Session, id: int):
    return db.query(models.Collars).filter_by(id=id, is_active=1).first()


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


#
def collar_group(db: Session, user_id: int):
    db_pets = [x.collar_id for x in db.query(models.Owners).filter_by(user_id=user_id).distinct()]
    is_active = []
    for i in db_pets:
        collar_n = db.query(models.Collars).filter_by(id=i).one()
        if (collar_n.is_active == True):
            is_active.append(i)
    return {"owner_id": user_id,
            "collars_id": is_active}


def deactivate_collar(db: Session, collar_id: int):
    db_collar_active = db.query(models.Collars).filter_by(id=collar_id).one()
    db_collar_active.is_active = 0
    db.commit()
    db.refresh(db_collar_active)
    return {
        "operation": "deactivate collar",
        "access": "True"
    }


def activate_collar(db: Session, collar_id: int):
    db_collar_active = db.query(models.Collars).filter_by(id=collar_id).one()
    db_collar_active.is_active = 1
    db.commit()
    db.refresh(db_collar_active)
    return {
        "operation": "activate collar",
        "access": "True"
    }