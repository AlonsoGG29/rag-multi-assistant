from sqlalchemy import Column, Integer, TEXT, TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from .database import Base
import datetime
from datetime import datetime as dt

class Assistant(Base):
    __tablename__ = "assistants"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    instructions = Column(TEXT, nullable=False)
    description = Column(TEXT)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    assistant_id = Column(Integer, ForeignKey("assistants.id", ondelete="CASCADE"))
    filename = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=dt.utcnow)

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    assistant_id = Column(Integer, ForeignKey("assistants.id", ondelete="CASCADE"))
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    chunk_index = Column(Integer)
    content = Column(TEXT, nullable=False)
    embedding = Column(Vector(1536)) # Dimensión para text-embedding-3-small
    created_at = Column(TIMESTAMP, default=dt.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    assistant_id = Column(Integer, ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=dt.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # 'user' | 'assistant'
    content = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP, default=dt.utcnow)
