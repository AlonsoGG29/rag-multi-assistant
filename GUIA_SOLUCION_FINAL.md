# ✅ GUÍA FINAL: Solucionar el Problema de Persistencia en BD

## 🎯 Problema Identificado
El `index.html` estaba usando el endpoint incorrecto para cargar PDFs:
- ❌ Anterior: Usaba `/chat/document` (NO indexaba ni guardaba)
- ✅ Nuevo: Usa `/assistants/{id}/documents` (INDEXA y guarda chunks)

## 🚀 PASOS PARA SOLUCIONAR (URGENTE)

### PASO 1: Limpia la BD Completamente
```bash
# Conecta a PostgreSQL
psql -U postgres

# Dentro de psql:
DROP DATABASE rag_db;
CREATE DATABASE rag_db;
\c rag_db

# Ejecuta el script SQL
\i D:/CLASE/TAJAMAR/IA\ GENERATIVA/Trabajo/rag-multi-assistant/sql/script.sql

# Verifica que se crearon las tablas
\dt

# Debería mostrar:
#  assistants
#  documents
#  chunks
#  conversations
#  messages
```

### PASO 2: Reinicia el Backend
```bash
cd backend
python run.py
```

**⚠️ Mira los logs mientras reinicia**. Deberías ver algo como:
```
🚀 Iniciando servidor en 0.0.0.0:8000
...uvicorn running
```

### PASO 3: Crea un Asistente
1. Abre http://localhost:3000 (o donde esté tu frontend)
2. Clic en "+ Nuevo Asistente"
3. Nombre: "Test Assistant"
4. Instrucciones: "Eres un asistente de prueba inteligente"

### PASO 4: **CARGA UN PDF** - AHORA CON EL FLUJO CORRECTO
1. Clic en "📎 Adjuntar PDF"
2. Selecciona un PDF
3. **⏳ ESPERA A VER:**
   - `✅ filename.pdf: 25 chunks indexados` ← Éxito!
   - O `❌ Error: ...` ← Falló

**🔴 IMPORTANTE: Mira los LOGS del Backend mientras se carga**

Deberías ver:
```
=== INICIANDO CARGA DE DOCUMENTO ===
Asistente ID: 1
Archivo: mi_archivo.pdf
✓ Asistente encontrado: Test Assistant
✓ Archivo leído: 45678 bytes
✓ Texto extraído: 12345 caracteres
=== RESULTADO: {'success': True, 'document_id': 1, 'filename': '...', 'chunks_indexed': 25} ===
```

### PASO 5: Verifica que se guardó en la BD
```bash
# En otra terminal
curl http://localhost:8000/debug/status

# Deberías ver:
{
  "assistants_count": 1,
  "documents_count": 1,    ← DEBE SER 1 O MÁS
  "chunks_count": 25,      ← DEBE SER 25 O MÁS (chunks del PDF)
  "conversations_count": 0,
  "messages_count": 0
}
```

Si ves `documents_count: 0` → **Hay aún un problema**, ve al "DEBUGGING" abajo.

### PASO 6: Haz una Pregunta
1. Escribe una pregunta sobre el PDF
2. Clic "Enviar"

Deberías ver la respuesta basada en el contenido del PDF.

### PASO 7: Verifica Conversaciones
```bash
curl http://localhost:8000/debug/status

# Debería AUMENTAR:
{
  ...
  "conversations_count": 1,  ← DEBE CAMBIAR A 1
  "messages_count": 2        ← DEBE CAMBIAR A 2 (user + assistant)
}
```

---

## 🔍 SI SIGUE SIN FUNCIONAR

### Test 1: Verifica que la BD acepta datos
```bash
cd backend
python test_db.py
```

- Si ves `✅ TEST PASSED` → **La BD funciona**, el problema está en el código
- Si ves `❌ TEST FAILED` → **La BD no guarda**, problema de conexión

### Test 2: Prueba el endpoint de inserción manual
```bash
# Primero crea un asistente desde la UI (deberías tener ID 1)

curl -X POST "http://localhost:8000/debug/test-insert?assistant_id=1"

# Si ve "success: true" → El endpoint funciona
# Si ve error → Hay un problema en main.py
```

### Test 3: Revisa los LOGS DEL BACKEND en detalle

Cuando intentes cargar un PDF, copia TODO lo que salga en los logs del backend y pástalo.

Busca específicamente:
- ❌ `ERROR` o traceback de excepción
- ❌ Línea que dice `=== RESULTADO:` con `"error":`
- ✅ Línea que dice `=== RESULTADO:` con `"success": True`

---

## 📝 CAMBIOS QUE SE HICIERON

### `frontend/public/index.html`
- ✅ El upload de PDF ahora va a `/assistants/{id}/documents`
- ✅ El PDF se indexa INMEDIATAMENTE cuando lo subes
- ✅ Los mensajes normales van a `/chat`

### `backend/app/main.py`
- ✅ Endpoint `/assistants/{asst_id}/documents` ahora tiene LOGGING detallado
- ✅ Endpoint `/debug/test-insert` para debugear inserciones
- ✅ Endpoints de debug mejorados

### `backend/app/services/document.py`
- ✅ Logging completo en cada paso

### `backend/run.py`
- ✅ Configurado logging para ver qué está pasando

---

## 🎯 Flujo Esperado

```
┌─ Selecciona Asistente ─┐
│                         ↓
│                    (muestra chat)
│
├─ Clic "Adjuntar PDF" ─┬─→ PDF se carga a BD
│ (Selecciona archivo)  │   (crea Document + Chunks)
│                        │   ✅ Se guarda en BD
│                        ↓
├─ Escribe pregunta ────→ POST /chat
│                        │   ↓
│                        ├─ Busca chunks relevantes
│                        ├─ Llama a OpenAI
│                        ├─ Gets respuesta
│                        └─→ Guarda Conversation + Messages
│                            ✅ Se guarda en BD
```

---

## ⚠️ Puntos Críticos

1. **El PDF debe tener texto visible** (no PDF de imagen escaneada)
2. **Azure OpenAI credentials deben ser válidas** (para embeddings)
3. **PostgreSQL y vector extension deben estar activos**
4. **Los logs son TU MEJOR AMIGO** - lee todos los logs cuando algo falla

---

## 📊 Tabla de Verificación Final

| Acción | documents_count | chunks_count | Result |
|--------|-----------------|--------------|--------|
| Solo Asistente | 0 | 0 | ✅ Normal |
| Después de Upload | 1+ | 25+ | ✅ **ÉXITO** |
| Después de Chat | 1+ | 25+ | ✅ Conversaciones guardadas |

Si ves:
- ✅ `documents_count: 1+` después del upload → **FUNCIONA**
- ❌ `documents_count: 0` después del upload → **PROBLEMA**

---

## 🆘 Últimas Opciones

Si nada funciona después de todo esto:

1. **Elimina el backend completamente y clona de cero:**
   ```bash
   rm -rf backend
   git clone <repo> backend
   ```

2. **Usa SQLite en lugar de PostgreSQL** (para testing):
   - Cambia `DATABASE_URL` a `sqlite:///./test.db`
   - Reinicia el backend

3. **Activa logging a archivo:**
   ```bash
   cd backend
   LOGLEVEL=DEBUG python run.py > backend.log 2>&1
   ```
   Luego: `tail -f backend.log`

---

**Si sigues teniendo problemas después de esto, proporciona:**
1. Screenshot completo de los LOGS del backend cuando cargas un PDF
2. Resultado de `curl http://localhost:8000/debug/status`
3. Resultado de `python test_db.py`
