# Fixes Aplicados - RAG Multi-Assistant

## 🔴 Problemas Encontrados

### 1. **Error de Schema en BD** (Problema Principal)
- **Síntoma**: `psycopg2.errors.UndefinedColumn: no existe la columna chunks.created_at`
- **Causa**: El script SQL original no incluía `created_at` en la tabla `chunks`
- **Solución**: ✅ Script.sql actualizado con la columna

### 2. **Frontend sin funcionalidad de carga de PDF**
- **Síntoma**: No se podían cargar documentos desde la UI
- **Causa**: El frontend solo tenía chat sin subida de archivos
- **Solución**: ✅ App.js mejorado con:
  - Botón de carga de PDF
  - Visualización de documentos
  - Mejor UX general

---

## 📋 Pasos a Seguir

### **PASO 1: Recrear las Tablas en PostgreSQL**

Ejecuta este script en tu cliente PostgreSQL (pgAdmin, psql, etc.):

```sql
-- 1. Eliminar tablas existentes (en orden de dependencias)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS assistants CASCADE;

-- 2. Ejecutar el script actualizado
-- Copia el contenido completo de: sql/script.sql
```

O ejecutalo directamente desde psql:
```bash
psql -U postgres -d nombre_bd -f sql/script.sql
```

### **PASO 2: Verificar el Backend**

```bash
cd backend
pip install -r requirements.txt
python run.py
```

El backend debe estar escuchando en `http://localhost:8000`

### **PASO 3: Verificar el Frontend**

```bash
cd frontend
npm install  # Si no está hecho
npm start
```

El frontend estará en `http://localhost:3000`

---

## ✅ Flujo de Uso Correcto

1. **Abre la app**: http://localhost:3000
2. **Crea/Selecciona un asistente**: Verás los existentes en la barra izquierda
3. **Carga un PDF**: Haz clic en "📥 Cargar PDF" y elige tu archivo
   - Verás un mensaje: ✅ Documento cargado: X chunks indexados
   - Los documentos aparecerán en la lista de "DOCUMENTOS"
4. **Haz preguntas**: Escribe tu pregunta y presiona "Enviar"
   - El asistente buscará información en los documentos cargados
   - Responderá basado en el contenido del PDF

---

## 🔧 Cambios Realizados

### `sql/script.sql`
```sql
-- Antes:
CREATE TABLE chunks (
  id SERIAL PRIMARY KEY,
  assistant_id INTEGER NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB
);

-- Después: (+ created_at)
CREATE TABLE chunks (
  id SERIAL PRIMARY KEY,
  assistant_id INTEGER NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT NOW(),  -- ← AÑADIDO
  metadata JSONB
);
```

### `frontend/src/App.js`
- ✅ Añadido estado para documentos, carga, y loading
- ✅ Función `handleFileUpload()` para cargar PDFs
- ✅ Función `fetchDocuments()` para listar documentos
- ✅ Sidebar mejorado con sección de documentos
- ✅ Indicador de carga ("⏳ Generando respuesta...")
- ✅ Mejor manejo de errores

---

## 🐛 Si Sigue Fallando

### Error: `UndefinedColumn`
→ Recrea las tablas ejecutando el script SQL nuevamente

### Error: `Connection refused localhost:8000`
→ Asegúrate de que el backend está corriendo: `python backend/run.py`

### Error: `Connection refused localhost:3000`
→ Inicia el frontend: `npm start` en la carpeta frontend

### Error: `DocumentNotFound` al cargar PDF
→ Verifica que el archivo existe en `backend/uploads/`

### Las preguntas tardan mucho
→ Esto es normal en la primera consulta (genera embeddings)
→ Las siguientes serán más rápidas

---

## 📚 Estructura de Datos

Después de cargar un documento, la BD debe tener:

```
assistants (1 registro)
├── documents (1 registro por PDF)
│   └── chunks (múltiples registros - uno por cada fragmento de texto)
├── conversations (1 por sesión de chat)
│   └── messages (uno por cada mensaje)
```

Ejemplo: Si subes un PDF de 10 páginas, generará ~20-30 chunks dependiendo del tamaño.

---

## ¿Preguntas?

Si algo no funciona, verifica:
1. ¿PostgreSQL está corriendo? → `psql -U postgres`
2. ¿Extension vector instalada? → `CREATE EXTENSION IF NOT EXISTS vector;`
3. ¿Backend tiene los keys de Azure OpenAI? → `.env`
4. ¿logs del backend muestran errores? → Copia el error exacto
