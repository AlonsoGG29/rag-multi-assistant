from sqlalchemy.orm import Session
from .. import models, schemas

def create_assistant(db: Session, assistant: schemas.AssistantCreate):
    db_assistant = models.Assistant(**assistant.dict())
    db.add(db_assistant)
    commit_db(db)
    return db_assistant

def get_assistants(db: Session):
    return db.query(models.Assistant).all()

def delete_assistant(db: Session, assistant_id: int):
    assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    if assistant:
        db.delete(assistant)
        commit_db(db)
    return assistant

def commit_db(db: Session):
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
