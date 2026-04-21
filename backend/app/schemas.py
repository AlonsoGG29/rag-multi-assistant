from pydantic import BaseModel
from typing import Optional, List

# Esquemas para Asistente
class AssistantBase(BaseModel):
    name: str
    instructions: str
    description: Optional[str] = None

class AssistantCreate(AssistantBase):
    pass

class AssistantResponse(AssistantBase):
    id: int
    class Config:
        from_attributes = True

# Esquemas para Chat
class ChatRequest(BaseModel):
    assistant_id: int
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    response: str
