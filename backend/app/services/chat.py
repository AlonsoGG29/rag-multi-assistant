import os
from openai import AzureOpenAI
from sqlalchemy.orm import Session
from .rag import search_context, get_embedding, split_text
from .. import models

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_rag_response(db: Session, assistant_id: int, user_message: str):
    """Genera respuesta usando RAG con documentos previamente indexados"""
    try:
        # 1. Obtener datos del asistente
        assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
        if not assistant:
            return "Error: Asistente no encontrado"
        
        # 2. Búsqueda de contexto (AISLAMIENTO)
        context = search_context(db, assistant_id, user_message)
        
        if not context:
            context = "No hay documentos disponibles para este asistente."
        
        # 3. Prompt del Sistema (Reglas de Oro)
        system_prompt = f"""
        Eres el siguiente asistente: {assistant.name}
        Instrucciones de comportamiento: {assistant.instructions}
        
        REGLAS CRÍTICAS:
        1. Responde usando ÚNICAMENTE este contexto disponible.
        2. Si el contexto no contiene la respuesta, di: "Lo siento, no tengo información suficiente en mis documentos".
        3. NO inventes información fuera del contexto.
        
        CONTEXTO DISPONIBLE:
        {context}
        """

        # 4. Llamada al LLM (GPT-4o-mini es la opción económica)
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

def generate_response_from_document(assistant_id: int, user_message: str, document_text: str):
    """Genera respuesta basada únicamente en el contenido de un documento"""
    try:
        # 1. Dividir documento en chunks
        chunks = split_text(document_text)
        
        if not chunks:
            return "El documento está vacío o no se pudo procesar."
        
        # 2. Crear contexto a partir de los chunks más relevantes
        query_vector = get_embedding(user_message)
        
        # Buscar chunks relevantes usando similitud del coseno
        scored_chunks = []
        for chunk in chunks:
            chunk_vector = get_embedding(chunk)
            # Calcular similitud del coseno
            similarity = cosine_similarity(query_vector, chunk_vector)
            scored_chunks.append((chunk, similarity))
        
        # Ordenar y obtener los top chunks
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        context = "\n\n".join([chunk[0] for chunk in scored_chunks[:4]])
        
        # 3. Generar prompt
        system_prompt = f"""Eres un asistente que responde preguntas sobre documentos.

REGLAS CRÍTICAS:
1. Responde ÚNICAMENTE basado en este contenido del documento:

{context}

2. Si el documento no contiene la información, di: "Lo siento, el documento no contiene información sobre eso".
3. NO inventas información.
4. Cita el documento cuando sea relevante."""

        # 4. Llamada al LLM
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar documento: {str(e)}"

def cosine_similarity(a, b):
    """Calcula similitud del coseno entre dos vectores"""
    import numpy as np
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
