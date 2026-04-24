import os
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv
import logging

from . import models, schemas, database
from .services import assistant, rag, chat, document
from .utils import pdf_processor

load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

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

@app.put("/assistants/{asst_id}", response_model=schemas.AssistantResponse)
def update_assistant_endpoint(asst_id: int, data: schemas.AssistantCreate, db: Session = Depends(database.get_db)):
    asst = assistant.update_assistant(db, asst_id, data)
    if not asst:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")
    return asst

@app.delete("/assistants/{asst_id}")
def delete_assistant_endpoint(asst_id: int, db: Session = Depends(database.get_db)):
    asst = assistant.delete_assistant(db, asst_id)
    if not asst:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")
    return {"message": "Asistente eliminado exitosamente"}

@app.post("/assistants/{asst_id}/documents")
async def upload_document(asst_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """Sube y indexa un documento PDF para un asistente"""
    logger.info(f"=== INICIANDO CARGA DE DOCUMENTO ===")
    logger.info(f"Asistente ID: {asst_id}")
    logger.info(f"Archivo: {file.filename}")
    
    try:
        # Verificar que el asistente existe
        logger.info("Verificando que el asistente existe...")
        asst = db.query(models.Assistant).filter(models.Assistant.id == asst_id).first()
        if not asst:
            logger.error(f"Asistente {asst_id} no encontrado")
            return {"error": "Asistente no encontrado"}
        logger.info(f"✓ Asistente encontrado: {asst.name}")
        
        # Leer y procesar el archivo
        logger.info("Leyendo contenido del archivo...")
        content = await file.read()
        logger.info(f"✓ Archivo leído: {len(content)} bytes")
        
        logger.info("Extrayendo texto del PDF...")
        text = pdf_processor.extract_text(content)
        logger.info(f"✓ Texto extraído: {len(text)} caracteres")
        
        if not text or len(text.strip()) == 0:
            logger.error("El PDF no contiene texto")
            return {"error": "El PDF no contiene texto o no se pudo procesar"}
        
        # Indexar el documento
        logger.info("Iniciando indexación del documento...")
        result = document.index_document(db, asst_id, file.filename, text)
        
        logger.info(f"=== RESULTADO: {result} ===")
        return result
    except Exception as e:
        logger.error(f"ERROR al procesar documento: {str(e)}", exc_info=True)
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
        response_text = chat.generate_rag_response(
            db, 
            req.assistant_id, 
            req.message,
            session_id=req.session_id  # ← Añadido session_id
        )
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


# ==================== ENDPOINTS DE DEBUG ====================

@app.get("/debug/status")
def debug_status(db: Session = Depends(database.get_db)):
    """Muestra el estado actual de la BD"""
    assistants = db.query(models.Assistant).count()
    documents = db.query(models.Document).count()
    chunks = db.query(models.Chunk).count()
    conversations = db.query(models.Conversation).count()
    messages = db.query(models.Message).count()
    
    return {
        "assistants_count": assistants,
        "documents_count": documents,
        "chunks_count": chunks,
        "conversations_count": conversations,
        "messages_count": messages
    }

@app.get("/debug/assistants")
def debug_assistants(db: Session = Depends(database.get_db)):
    """Lista todos los asistentes y sus documentos"""
    assts = db.query(models.Assistant).all()
    result = []
    for asst in assts:
        docs = db.query(models.Document).filter(models.Document.assistant_id == asst.id).all()
        chunks_count = db.query(models.Chunk).filter(models.Chunk.assistant_id == asst.id).count()
        convs = db.query(models.Conversation).filter(models.Conversation.assistant_id == asst.id).count()
        result.append({
            "id": asst.id,
            "name": asst.name,
            "documents": len(docs),
            "chunks": chunks_count,
            "conversations": convs,
            "docs_detail": [{"id": d.id, "filename": d.filename} for d in docs]
        })
    return result

@app.get("/debug/conversations")
def debug_conversations(db: Session = Depends(database.get_db)):
    """Lista todas las conversaciones con sus mensajes"""
    convs = db.query(models.Conversation).all()
    result = []
    for conv in convs:
        msgs = db.query(models.Message).filter(models.Message.conversation_id == conv.id).all()
        result.append({
            "id": conv.id,
            "assistant_id": conv.assistant_id,
            "session_id": conv.session_id,
            "created_at": conv.created_at,
            "message_count": len(msgs),
            "messages": [{"role": msg.role, "content": msg.content[:100]} for msg in msgs]
        })
    return result

@app.get("/debug/conversations/{conv_id}")
def debug_conversation_detail(conv_id: int, db: Session = Depends(database.get_db)):
    """Obtiene el detalle completo de una conversación"""
    conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
    if not conv:
        return {"error": "Conversación no encontrada"}
    
    msgs = db.query(models.Message).filter(models.Message.conversation_id == conv_id).all()
    return {
        "id": conv.id,
        "assistant_id": conv.assistant_id,
        "session_id": conv.session_id,
        "created_at": conv.created_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in msgs
        ]
    }

@app.delete("/debug/clean-all")
def debug_clean_all(db: Session = Depends(database.get_db)):
    """🔴 CUIDADO: Elimina TODOS los datos de la BD exceptuando assistants"""
    try:
        # Eliminar en orden de dependencias
        db.query(models.Message).delete()
        db.query(models.Conversation).delete()
        db.query(models.Chunk).delete()
        db.query(models.Document).delete()
        db.commit()
        return {"message": "BD limpiada (documentos, chunks, conversaciones y mensajes eliminados)"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@app.post("/debug/test-insert")
def debug_test_insert(assistant_id: int, db: Session = Depends(database.get_db)):
    """🧪 TEST: Intenta insertar un documento sin embeddings para debugear"""
    logger.info("=== TEST INSERT INICIADO ===")
    
    try:
        # Verificar asistente
        asst = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
        if not asst:
            return {"error": f"Asistente {assistant_id} no encontrado"}
        logger.info(f"✓ Asistente {asst.name} encontrado")
        
        # 1. Crear documento
        logger.info("Creando documento...")
        doc = models.Document(
            assistant_id=assistant_id,
            filename="TEST_DOCUMENTO.txt"
        )
        db.add(doc)
        db.flush()
        logger.info(f"✓ Documento creado con ID: {doc.id}")
        
        # 2. Crear chunk sin embedding
        logger.info("Creando chunk sin embedding...")
        chunk = models.Chunk(
            assistant_id=assistant_id,
            document_id=doc.id,
            chunk_index=0,
            content="Este es un texto de prueba para testing",
            embedding=None  # SIN embedding
        )
        db.add(chunk)
        logger.info(f"✓ Chunk agregado (sin embedding aún)")
        
        # 3. Commit
        logger.info("Haciendo commit...")
        db.commit()
        logger.info("✓ Commit exitoso")
        
        # 4. Verificar
        logger.info("Verificando inserción...")
        docs = db.query(models.Document).filter(models.Document.assistant_id == assistant_id).all()
        chunks = db.query(models.Chunk).filter(models.Chunk.assistant_id == assistant_id).all()
        logger.info(f"✓ Verificación: {len(docs)} documentos, {len(chunks)} chunks")
        
        return {
            "success": True,
            "message": "TEST PASSED - La BD está funcionando correctamente",
            "documents": len(docs),
            "chunks": len(chunks)
        }
    except Exception as e:
        logger.error(f"TEST FAILED: {str(e)}", exc_info=True)
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
