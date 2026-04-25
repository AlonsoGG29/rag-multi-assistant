# 🔴 DEBUGEO: ¿Por qué no se guarda la BD?

## 📋 Checklist Diagnóstico

### PASO 1: Verificar la Conexión a la BD
```bash
# Abre una terminal con psql
psql -U postgres

# Verifica que la BD existe y tiene tablas
\c rag_db
\dt

# Debería mostrar:
# - assistants
# - documents  
# - chunks
# - conversations (nuevo)
# - messages (nuevo)
```

Si `\dt` muestra las tablas → **conexión OK ✓**
Si no muestra nada → **SQL script no ejecutó ✗**

---

### PASO 2: Test Automático della BD
```bash
cd backend

# Ejecuta el script de test que crea un registro manualmente
python test_db.py
```

**Si ves:**
- ✅ `TEST PASSED - LA BD ESTÁ GUARDANDO` → El problema NO es la BD
- ❌ `TEST FAILED - NO SE GUARDARON` → El problema ES la BD

---

### PASO 3: Ver Logs del Backend (IMPORTANTE)

Reinicia el backend y fíjate EN LOS LOGS:

```bash
cd backend
python run.py
```

**Tendrás que buscar estos logs:**

#### Cuando intentas CARGAR un PDF:
```
=== INICIANDO CARGA DE DOCUMENTO ===
Asistente ID: 1
Archivo: mi_documento.pdf
✓ Asistente encontrado: MiAsistente
✓ Archivo leído: 45678 bytes
✓ Texto extraído: 12345 caracteres
Iniciando indexación del documento...
```

**Si ves esto y luego NADA → El proceso se está colgando/fallando silenciosamente**

---

### PASO 4: Verificar Logs de Embedding

El problema PROBABLEMENTE está en `get_embedding()` que llama a Azure OpenAI.

En los logs deberías ver:
```
Procesando chunk 0/25
Procesando chunk 1/25
...
```

Si NO ves esto → **LOS CHUNKS NO SE ESTÁN CREANDO**

---

### PASO 5: Test Manual del Endpoint

Usa un cliente HTTP (curl, Postman, etc) para probar:

#### Test 1: Crear un asistente
```bash
curl -X POST http://localhost:8000/assistants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Assistant",
    "instructions": "Eres un asistente de prueba"
  }'

# Anota el ID devuelto (ej: 1)
```

#### Test 2: Verificar estado de la BD
```bash
curl http://localhost:8000/debug/status

# Deberías ver:
{
  "assistants_count": 1,
  "documents_count": 0,
  "chunks_count": 0,
  ...
}
```

#### Test 3: Prueba manual de inserción (SIN embeddings)
```bash
curl -X POST "http://localhost:8000/debug/test-insert?assistant_id=1"

# Si ves "success: true" → BD FUNCIONA
# Si ves error → PROBLEMA EN LA BD
```

#### Test 4: Después de cargar un PDF
```bash
curl http://localhost:8000/debug/status

# Debería mostrar:
{
  "assistants_count": 1,
  "documents_count": 1,  ← DEBE CAMBIAR A 1
  "chunks_count": 25,     ← DEBE CAMBIAR A ~25
  ...
}
```

---

## 🔍 Diagnosis por Síntomas

### Síntoma: `/debug/status` muestra `documents_count: 0`

**Causa probable:**
1. ❌ El PDF está vacío
2. ❌ El error está siendo silenciado en `index_document()`
3. ❌ Los embeddings están fallando
4. ❌ El commit no se está haciendo

**Solución:**
- Ve al **backend/app/services/document.py**
- Busca donde dice `logger.error`
- Los logs te mostrarán exactamente dónde falla

### Síntoma: `/debug/test-insert` retorna error

**Causa:** La BD no está conectada correctamente

**Solución:**
1. Verifica `DATABASE_URL` en `.env`
2. Verifica que PostgreSQL está corriendo: `psql -U postgres`
3. Verifica que la BD `rag_db` existe

### Síntoma: Logs muestran embedding error

**Causa:** Azure OpenAI credentials inválidas

**Solución:**
- Ve a `.env`
- Verifica que tienes:
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
  - `AZURE_OPENAI_CHAT_DEPLOYMENT`

---

## 📝 Pasos de RESET COMPLETO (si nada funciona)

```bash
# 1. Limpiar BD
psql -U postgres -c "DROP DATABASE rag_db;"
psql -U postgres -c "CREATE DATABASE rag_db;"

# 2. Ejecutar script SQL
psql -U postgres -d rag_db -f sql/script.sql

# 3. Reiniciar backend
cd backend
python run.py

# 4. Probar
curl http://localhost:8000/debug/status
```

---

## 📊 Tabla de Referencia: Qué DEBE estar en la BD

| Tabla | Sin PDF | Con 1 PDF | Con Chat |
|-------|---------|-----------|----------|
| assistants | 1 | 1 | 1 |
| documents | 0 | 1 | 1 |
| chunks | 0 | ~25 | ~25 |
| conversations | 0 | 0 | 1+ |
| messages | 0 | 0 | 2+ |

---

## 🚨 Si Todo Falla

**Ejecuta esto terminal por terminal:**

```bash
# Terminal 1: Ver logs de PostgreSQL
# (diferente según tu sistema operativo)

# Terminal 2: Ver logs del backend con DEBUG
cd backend
LOGLEVEL=DEBUG python run.py

# Terminal 3: Ejecutar el test
cd backend
python test_db.py

# Terminal 4: Hacer una carga desde otra ventana
# (abrir navegador y cargar un PDF)
```

Copia toda la salida del terminal 2 (backend logs) cuando intentes cargar un PDF y pásalo.
