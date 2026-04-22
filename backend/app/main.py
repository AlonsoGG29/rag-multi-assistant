import os
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv

from . import models, schemas, database
from .services import assistant, rag, chat, document
from .utils import pdf_processor

load_dotenv()

app = FastAPI(title="RAG Multi-Asistente API")

# Configuración de CORS para que el Frontend pueda comunicarse con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar (si no existen)
models.Base.metadata.create_all(bind=database.engine)

@app.get("/assistants", response_model=List[schemas.AssistantResponse])
def list_assistants(db: Session = Depends(database.get_db)):
    return assistant.get_assistants(db)

@app.post("/assistants", response_model=schemas.AssistantResponse)
def create_assistant(data: schemas.AssistantCreate, db: Session = Depends(database.get_db)):
    return assistant.create_assistant(db, data)

@app.post("/assistants/{asst_id}/documents")
async def upload_document(asst_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """Sube y indexa un documento PDF para un asistente"""
    try:
        # Verificar que el asistente existe
        asst = db.query(models.Assistant).filter(models.Assistant.id == asst_id).first()
        if not asst:
            return {"error": "Asistente no encontrado"}
        
        # Leer y procesar el archivo
        content = await file.read()
        text = pdf_processor.extract_text(content)
        
        # Indexar el documento
        result = document.index_document(db, asst_id, file.filename, text)
        
        return result
    except Exception as e:
        return {"error": f"Error al procesar documento: {str(e)}"}

@app.get("/assistants/{asst_id}/documents")
def get_documents(asst_id: int, db: Session = Depends(database.get_db)):
    """Obtiene los documentos indexados de un asistente"""
    docs = db.query(models.Document).filter(
        models.Document.assistant_id == asst_id
    ).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "created_at": doc.created_at
        }
        for doc in docs
    ]

@app.post("/chat", response_model=schemas.ChatResponse)
def chat_endpoint(req: schemas.ChatRequest, db: Session = Depends(database.get_db)):
    try:
        response_text = chat.generate_rag_response(db, req.assistant_id, req.message)
        return {"response": response_text}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.post("/chat/document", response_model=schemas.ChatResponse)
async def chat_with_document(
    assistant_id: int = Form(...), 
    message: str = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    """
    Chat con un documento específico.
    El asistente solo responde basado en el contenido del PDF cargado.
    """
    try:
        # 1. Leer el contenido del archivo
        content = await file.read()
        
        # 2. Extraer texto del PDF
        document_text = pdf_processor.extract_text(content)
        
        # 3. Generar respuesta basada solo en este documento
        response_text = chat.generate_response_from_document(
            assistant_id, 
            message, 
            document_text
        )
        
        return {"response": response_text}
    except Exception as e:
        return {"response": f"Error al procesar documento: {str(e)}"}
