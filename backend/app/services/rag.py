import os
from openai import AzureOpenAI
from sqlalchemy.orm import Session
from ..models import Chunk

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def search_context(db: Session, assistant_id: int, query: str, limit: int = 4):
    query_vector = get_embedding(query)
    # Aquí aplicamos el AISLAMIENTO CRÍTICO por assistant_id
    results = db.query(Chunk).filter(Chunk.assistant_id == assistant_id).order_by(
        Chunk.embedding.cosine_distance(query_vector)
    ).limit(limit).all()
    
    return "\n\n".join([r.content for r in results])
