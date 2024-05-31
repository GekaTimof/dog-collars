from sqlalchemy.orm import Session
import src.community.models as models
import src.community.schemas as schemas
from fastapi import HTTPException


# ищем неотвеченную жалобу по complaint_id в таблице Complaints
def get_complaint_by_id(db: Session, complaint_id: int):
    return db.query(models.Complaint).filter_by(complaint_id=complaint_id, is_answered=0).first()


def get_active_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter_by(task_id=task_id, is_completed=0).first()


# добавляем жалобу на пользователя
def add_user_complaint(db: Session, complaint: schemas.Complaint) -> models.Complaint:
    db_complain = models.Complaint(
        text=complaint.text,
        user_id=complaint.user_id
    )
    db.add(db_complain)
    db.commit()
    db.refresh(db_complain)
    return db_complain


# помечаем, что мы ответили на жалобу
def respond_user_complaint(db: Session, complaint_id: int):
    db_complaint = db.query(models.Complaint).filter_by(complaint_id=complaint_id).one()
    db_complaint.is_answered = 1
    db.commit()
    db.refresh(db_complaint)
    return {
        "operation": "respond complaint",
        "access": "True"
    }


# добавляем новое задание в базу данных
def add_collar_task(db: Session, task: schemas.NewCollarTask) -> models.Task:
    db_collar_task = models.Task(
        collar_id=task.collar_id,
        text=task.text,
        is_alert=task.is_alert
    )
    db.add(db_collar_task)
    db.commit()
    db.refresh(db_collar_task)
    return db_collar_task


# получаем список задач для одного ошейника
def get_collar_tasks(db: Session, collar_id: int):
    all_tasks = [x.task_id for x in db.query(models.Task).filter_by(is_completed=0, collar_id=collar_id).distinct()]
    return {"collar_id": collar_id,
            "task_id": all_tasks}


# получаем список срочных задач для одного ошейника
def get_alert_collar_tasks(db: Session, collar_id: int):
    all_tasks = [x.task_id for x in db.query(models.Task).filter_by(is_completed=1, collar_id=collar_id).distinct()]
    return {"collar_id": collar_id,
            "task_id": all_tasks}


# пометка задания, как выполненого
def complete_collar_task(db: Session, task_id: int):
    db_complete_task = db.query(models.Task).filter_by(task_id=task_id).one()
    db_complete_task.is_completed = 1
    db.commit()
    db.refresh(db_complete_task)
    return {
        "operation": "complete task",
        "access": "True"
    }

