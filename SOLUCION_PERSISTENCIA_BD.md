# Solución de Persistencia en BD - RAG Multi-Assistant

## 🔍 Problemas Identificados

### 1. **Modelos Faltantes**
- ❌ No existían modelos `Conversation` y `Message` en `models.py`
- ❌ El backend no guardaba historial de conversaciones
- ❌ Los mensajes desaparecían al recargar la página

### 2. **Sin Lógica de Guardado en Chat**
- ❌ El servicio `chat.py` generaba respuestas pero nunca las guardaba
- ❌ Las conversaciones no se creaban
- ❌ Los mensajes no se persistían

### 3. **Sin Logging para Debug**
- ❌ Imposible saber qué estaba fallando
- ❌ Los errores se capturaban silenciosamente

---

## ✅ Soluciones Implementadas

### 1. **Agregados Modelos Faltantes** (`models.py`)
```python
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
```

### 2. **Mejorado Servicio de Chat** (`services/chat.py`)
- ✅ Agregado LogginG global
- ✅ Función `get_or_create_conversation()` - crea/obtiene conversaciones
- ✅ Función `save_message()` - persiste mensajes en BD
- ✅ Modificada `generate_rag_response()` para guardar:
  - Conversación (auto-crear si no existe)
  - Mensaje del usuario
  - Mensaje de respuesta del asistente

### 3. **Mejorado Servicio de Documentos** (`services/document.py`)
- ✅ Agregado LogginG completo
- ✅ Mejor traceo de chunks siendo procesados
- ✅ Mensajes de error más descriptivos

### 4. **Actualizado Endpoint Chat** (`main.py`)
- ✅ Ahora acepta y pasa `session_id`
- ✅ Las conversaciones se agrupan por `session_id`

### 5. **Agregados Endpoints de Debug** (`main.py`)
```
GET /debug/status           → Cuenta total de registros
GET /debug/assistants       → Lista asistentes con details
GET /debug/conversations    → Lista conversaciones + mensajes
GET /debug/conversations/{id} → Detalle completo de una conversación
DELETE /debug/clean-all     → Limpia BD (cuidado!)
```

### 6. **Mejorado Frontend** (`App.js`)
- ✅ Genera `session_id` único al iniciar (usa `uuid`)
- ✅ Envía `session_id` con cada mensaje
- ✅ Mantiene historial de mensajes en sesión

### 7. **Mejorado Script de Inicio** (`run.py`)
- ✅ Configurado Logging para debugear

---

## 🚀 Paso a Paso: Cómo Usar

### **Paso 1: Instalar dependencia uuid en Frontend**
```bash
cd frontend
npm install uuid
```

### **Paso 2: Recrear Tablas en PostgreSQL**
```sql
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS assistants CASCADE;
```

Luego ejecuta el script SQL actualizado (que ya tiene `created_at` en chunks).

### **Paso 3: Reiniciar Backend**
```bash
cd backend
python run.py
```

Verifica que inicie correctamente y veas los logs.

### **Paso 4: Iniciar Frontend**
```bash
cd frontend
npm start
```

---

## 🔧 Flujo Completo

### Cuando creas un asistente:
```
Frontend → Backend POST /assistants → Se guarda Assistant
```

### Cuando subes un PDF:
```
Frontend → Backend POST /assistants/{id}/documents
  → index_document() crea Document
  → Por cada chunk: create Chunk con embedding
  → TODO se guarda en BD ✅
```

### Cuando envías un mensaje:
```
Frontend (con session_id) → Backend POST /chat
  → get_or_create_conversation() crea/obtiene Conversation
  → save_message() guarda mensaje del USER
  → generate_response() llama Azure OpenAI
  → save_message() guarda respuesta ASSISTANT
  → TODO persiste en BD ✅
```

---

## 🧪 Cómo Verificar que Funciona

### Desde el navegador (debug endpoints):
```
http://localhost:8000/debug/status
http://localhost:8000/debug/assistants
http://localhost:8000/debug/conversations
```

### Respuesta esperada de `/debug/status`:
```json
{
  "assistants_count": 1,
  "documents_count": 1,
  "chunks_count": 25,
  "conversations_count": 1,
  "messages_count": 4
}
```

Si ves números > 0 en todos, ¡TODO está guardando! ✅

---

## ⚠️ Si Sigue Fallando

### Error: `uuid not found`
→ `npm install uuid` en frontend

### Error: `Conversation model does not exist`
→ Elimina la BD y recrea las tablas

### Error: `psycopg2.errors.UndefinedColumn`
→ Verifica que `script.sql` tiene `created_at` en chunks

### Logs no muestran Debug
→ Asegúrate de ejecutar `python run.py` (no `uvicorn app.main:app`)

---

## 📊 Estructura de Datos Actualizada

```
assistants
├── documents
│   └── chunks (con embeddings)
├── conversations (uno por session_id)
│   └── messages (user/assistant)
```

Cada conversación es independiente por `session_id`, así múltiples chats con el mismo asistente no se mezclan.
