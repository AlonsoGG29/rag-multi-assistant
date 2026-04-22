"""Servicio para indexar documentos en la base de datos"""
from sqlalchemy.orm import Session
from .. import models
from .rag import get_embedding, split_text

def index_document(db: Session, assistant_id: int, filename: str, document_text: str):
    """
    Indexa un documento en la BD asociado a un asistente.
    
    Args:
        db: Session de SQLAlchemy
        assistant_id: ID del asistente propietario del documento
        filename: Nombre del archivo
        document_text: Texto completo del documento
        
    Returns:
        Diccionario con información sobre la indexación
    """
    try:
        # 1. Crear registro de documento
        doc = models.Document(
            assistant_id=assistant_id,
            filename=filename
        )
        db.add(doc)
        db.flush()  # Obtener el ID del documento sin hacer commit
        
        # 2. Dividir en chunks
        chunks = split_text(document_text)
        
        if not chunks:
            return {"error": "El documento está vacío"}
        
        # 3. Generar embeddings y guardar chunks
        chunk_count = 0
        for i, chunk_text in enumerate(chunks):
            try:
                vector = get_embedding(chunk_text)
                chunk = models.Chunk(
                    assistant_id=assistant_id,
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=vector
                )
                db.add(chunk)
                chunk_count += 1
            except Exception as e:
                print(f"Error al procesar chunk {i}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "document_id": doc.id,
            "filename": filename,
            "chunks_indexed": chunk_count
        }
    
    except Exception as e:
        db.rollback()
        return {
            "error": str(e)
        }
