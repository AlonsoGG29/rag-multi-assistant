import os
from openai import AzureOpenAI
from sqlalchemy.orm import Session
from ..models import Chunk
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_embedding(text):
    """Obtiene el embedding de un texto usando Azure OpenAI"""
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text], 
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    )
    return response.data[0].embedding

def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Divide el texto en chunks con sobreposición
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño de cada chunk
        overlap: Caracteres de sobreposición entre chunks
        
    Returns:
        Lista de chunks de texto
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks

def search_context(db: Session, assistant_id: int, query: str, limit: int = 4):
    """Busca contexto relevante para una consulta usando búsqueda de similitud de vectores"""
    query_vector = get_embedding(query)
    # Aplicamos el AISLAMIENTO CRÍTICO por assistant_id
    results = db.query(Chunk).filter(Chunk.assistant_id == assistant_id).order_by(
        Chunk.embedding.cosine_distance(query_vector)
    ).limit(limit).all()
    
    return "\n\n".join([r.content for r in results]) if results else ""
