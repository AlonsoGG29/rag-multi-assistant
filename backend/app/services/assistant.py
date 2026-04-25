from sqlalchemy.orm import Session
from .. import models, schemas

def create_assistant(db: Session, assistant: schemas.AssistantCreate):
    assistant_data = assistant.dict()
    
    # Si no hay instrucciones, asignar una por defecto
    if not assistant_data.get("instructions"):
        assistant_data["instructions"] = f"Eres un asistente experto llamado {assistant_data['name']}. Ayuda a los usuarios respondiendo preguntas basadas en los documentos que se te proporcionen."
    
    db_assistant = models.Assistant(**assistant_data)
    db.add(db_assistant)
    commit_db(db)
    return db_assistant

def get_assistants(db: Session):
    return db.query(models.Assistant).all()

def update_assistant(db: Session, assistant_id: int, assistant_update: schemas.AssistantCreate):
    assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    if assistant:
        for key, value in assistant_update.dict(exclude_unset=True).items():
            setattr(assistant, key, value)
        commit_db(db)
    return assistant

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
