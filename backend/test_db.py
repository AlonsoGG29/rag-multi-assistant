#!/usr/bin/env python
"""
Script de TEST para verificar que la BD está guardando datos correctamente
Ejecutar: python test_db.py
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/rag_db")

print(f"🔗 Conectando a: {DATABASE_URL}")

# Crear engine y session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("\n" + "="*60)
    print("TEST 1: Verificar que las tablas existen")
    print("="*60)
    
    # Verificar que podemos crear las tablas
    models.Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas/verificadas")
    
    print("\n" + "="*60)
    print("TEST 2: Contar registros actuales")
    print("="*60)
    
    asst_count = db.query(models.Assistant).count()
    doc_count = db.query(models.Document).count()
    chunk_count = db.query(models.Chunk).count()
    conv_count = db.query(models.Conversation).count()
    msg_count = db.query(models.Message).count()
    
    print(f"Assistants: {asst_count}")
    print(f"Documents: {doc_count}")
    print(f"Chunks: {chunk_count}")
    print(f"Conversations: {conv_count}")
    print(f"Messages: {msg_count}")
    
    if asst_count == 0:
        print("\n⚠️  No hay asistentes. Crea uno primero desde la UI.")
        db.close()
        exit(0)
    
    asst_id = db.query(models.Assistant).first().id
    print(f"\n🤖 Usando asistente ID: {asst_id}")
    
    print("\n" + "="*60)
    print("TEST 3: Crear documento MANUALMENTE")
    print("="*60)
    
    # Crear documento
    doc = models.Document(
        assistant_id=asst_id,
        filename="TEST_MANUAL.pdf"
    )
    db.add(doc)
    db.flush()
    print(f"✓ Documento creado con ID: {doc.id}")
    
    # Crear chunk SIN embedding (para aislar el problema)
    chunk = models.Chunk(
        assistant_id=asst_id,
        document_id=doc.id,
        chunk_index=0,
        content="Este es un texto de prueba. Lorem ipsum dolor sit amet.",
        embedding=None  # SIN embedding para evitar errores de Azure OpenAI
    )
    db.add(chunk)
    print(f"✓ Chunk creado sin embedding")
    
    # Hacer commit
    db.commit()
    print(f"✓ Commit exitoso")
    
    print("\n" + "="*60)
    print("TEST 4: Verificar que se guardó")
    print("="*60)
    
    docs = db.query(models.Document).filter(
        models.Document.assistant_id == asst_id
    ).all()
    chunks = db.query(models.Chunk).filter(
        models.Chunk.assistant_id == asst_id
    ).all()
    
    print(f"✓ Documentos para asistente {asst_id}: {len(docs)}")
    print(f"✓ Chunks para asistente {asst_id}: {len(chunks)}")
    
    if len(docs) > 0 and len(chunks) > 0:
        print("\n✅ TEST PASSED - LA BD ESTÁ GUARDANDO CORRECTAMENTE")
    else:
        print("\n❌ TEST FAILED - NO SE GUARDARON LOS DATOS")
    
    print("\n" + "="*60)
    print("TEST 5: Crear CONVERSACIÓN y MENSAJE")
    print("="*60)
    
    conv = models.Conversation(
        assistant_id=asst_id,
        session_id="test_session_123"
    )
    db.add(conv)
    db.flush()
    print(f"✓ Conversación creada con ID: {conv.id}")
    
    msg_user = models.Message(
        conversation_id=conv.id,
        role="user",
        content="Hola, ¿cómo estás?"
    )
    db.add(msg_user)
    
    msg_assistant = models.Message(
        conversation_id=conv.id,
        role="assistant",
        content="Hola, estoy bien. ¿Y tú?"
    )
    db.add(msg_assistant)
    
    db.commit()
    print(f"✓ Mensajes creados y guardados")
    
    convs = db.query(models.Conversation).filter(
        models.Conversation.assistant_id == asst_id
    ).all()
    msgs = db.query(models.Message).filter(
        models.Message.conversation_id == conv.id
    ).all()
    
    print(f"✓ Conversaciones: {len(convs)}")
    print(f"✓ Mensajes en conversación: {len(msgs)}")
    
    if len(convs) > 0 and len(msgs) >= 2:
        print("\n✅ CONVERSACIONES Y MENSAJES OK")
    else:
        print("\n❌ PROBLEMA CON CONVERSACIONES/MENSAJES")
    
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    final_doc_count = db.query(models.Document).count()
    final_chunk_count = db.query(models.Chunk).count()
    final_conv_count = db.query(models.Conversation).count()
    final_msg_count = db.query(models.Message).count()
    
    print(f"Documentos totales: {final_doc_count}")
    print(f"Chunks totales: {final_chunk_count}")
    print(f"Conversaciones totales: {final_conv_count}")
    print(f"Mensajes totales: {final_msg_count}")
    
    if final_doc_count > 0 and final_chunk_count > 0:
        print("\n✅ TODO FUNCIONA - LA BD ESTÁ GUARDANDO CORRECTAMENTE")
    else:
        print("\n❌ PROBLEMA: NO SE ESTÁN GUARDANDO DOCUMENTOS/CHUNKS")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
    print("\nConexión cerrada.")
