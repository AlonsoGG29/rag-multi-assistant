import os
from openai import AzureOpenAI
from sqlalchemy.orm import Session
from .rag import search_context
from .. import models

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_rag_response(db: Session, assistant_id: int, user_message: str):
    # 1. Obtener datos del asistente
    assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    
    # 2. Búsqueda de contexto (AISLAMIENTO)
    context = search_context(db, assistant_id, user_message)
    
    # 3. Prompt del Sistema (Reglas de Oro)
    system_prompt = f"""
    Eres el siguiente asistente: {assistant.name}
    Instrucciones de comportamiento: {assistant.instructions}
    
    REGLAS CRÍTICAS:
    1. Responde usando ÚNICAMENTE este contexto: {context}
    2. Si el contexto no contiene la respuesta, di: "Lo siento, no tengo información suficiente en mis documentos".
    3. Cita tus fuentes al final de la frase usando el nombre del documento si está disponible.
    4. NO inventes información fuera del contexto.
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
