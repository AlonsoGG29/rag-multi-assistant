from sqlalchemy import Column, Integer, TEXT, TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from .database import Base
import datetime

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

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    assistant_id = Column(Integer, ForeignKey("assistants.id", ondelete="CASCADE"))
    content = Column(TEXT, nullable=False)
    embedding = Column(Vector(1536)) # Dimensión para text-embedding-3-small
