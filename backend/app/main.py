import os
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv

from . import models, schemas, database
from .services import assistant, rag, chat
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
    # 1. Guardar temporalmente y extraer texto
    content = await file.read()
    text = pdf_processor.extract_text(content) # Lógica sencilla con PyPDF
    
    # 2. Generar chunks y embeddings
    chunks = rag.split_text(text)
    for i, chunk_text in enumerate(chunks):
        vector = rag.get_embedding(chunk_text)
        new_chunk = models.Chunk(
            assistant_id=asst_id,
            content=chunk_text,
            embedding=vector
        )
        db.add(new_chunk)
    
    db.commit()
    return {"message": "Documento indexado con éxito"}

@app.post("/chat", response_model=schemas.ChatResponse)
def chat_endpoint(req: schemas.ChatRequest, db: Session = Depends(database.get_db)):
    response_text = chat.generate_rag_response(db, req.assistant_id, req.message)
    return {"response": response_text}
