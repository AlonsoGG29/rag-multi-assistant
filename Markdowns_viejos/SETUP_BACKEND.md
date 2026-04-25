# Instrucciones para ejecutar el Backend

## 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

## 2. Configurar variables de entorno

El archivo `.env` ya está configurado con:
- **AZURE_OPENAI_API_KEY**: Tu clave de API de Azure OpenAI
- **AZURE_OPENAI_ENDPOINT**: Tu endpoint de Azure OpenAI
- **AZURE_OPENAI_CHAT_DEPLOYMENT**: gpt4omini (o el modelo que uses)
- **AZURE_OPENAI_EMBEDDING_DEPLOYMENT**: text-embedding3-small
- **DATABASE_URL**: Conexión a PostgreSQL

⚠️ **IMPORTANTE**: Asegúrate de que PostgreSQL esté corriendo en tu máquina local.

## 3. Crear la base de datos (si no existe)

```bash
# En PowerShell o terminal
psql -U postgres -c "CREATE DATABASE rag_db;"
```

O si usas una herramienta gráfica como pgAdmin, crea la base de datos manualmente.

## 4. Ejecutar el servidor

```bash
# Desde la carpeta backend
python run.py
```

O alternativamente:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El servidor estará disponible en: **http://localhost:8000**

## 5. Verificar que el backend está corriendo

Abre tu navegador y ve a:
- `http://localhost:8000/assistants` - Debe devolver una lista vacía `[]`

## 6. Ejecutar el frontend

En otra terminal:

```bash
cd frontend
# Si tienes Node.js instalado, puedes usar:
npm install
npm start

# O simplemente abre frontend/public/index.html en tu navegador
```

## Solución de problemas

### Error: "Error al conectar con el servidor: failed to fetch"
- Asegúrate de que el backend está corriendo en http://localhost:8000
- Verifica que CORS está configurado (ya está en main.py)
- Abre la consola del navegador (F12) para ver errores más detallados

### Error de conexión a base de datos
- Verifica que PostgreSQL está corriendo
- Verifica que la DATABASE_URL en .env es correcta
- Crea la base de datos si no existe

### Error de Azure OpenAI
- Verifica que tu API_KEY y ENDPOINT son correctos en el archivo .env
- Verifica que los nombres de despliegue (gpt4omini, text-embedding3-small) existen en tu instancia de Azure
