# 🛠️ Registro de Problemas y Soluciones

Este documento detalla los desafíos técnicos enfrentados durante el desarrollo del sistema RAG Multi-Asistente, desde errores de sintaxis hasta fallos de arquitectura y base de datos.

### 1. Error de Conexión y CORS
- **Problema:** Errores de "Failed to fetch" al intentar comunicar el frontend (puerto 3000) con el backend (puerto 8000).
- **Causa:** La política de intercambio de recursos de origen cruzado (CORS) no estaba permitiendo las peticiones desde el entorno de desarrollo de React.
- **Solución:** Se configuró el middleware de CORS en `main.py` para permitir peticiones desde `http://localhost:3000`.

### 2. Conflictos de Sintaxis y Renderizado (Frontend)
- **Problema:** Errores masivos en `App.js` (líneas 568-614) con mensajes como "JSX expressions must have one parent element" e interferencias visuales de texto plano sobre la interfaz.
- **Causa:** Se mezcló código de Tailwind CSS/HTML plano fuera del componente principal de React y después del `export default`, lo que provocó que el navegador interpretara el código como texto.
- **Solución:** Se realizó una limpieza profunda del archivo `App.js`, eliminando el código redundante y centralizando toda la lógica visual en componentes de **Material UI** debidamente anidados.

### 3. Error de Columna Inexistente en Chunks
- **Problema:** Error crítico `psycopg2.errors.UndefinedColumn: no existe la columna chunks.created_at` al intentar indexar documentos.
- **Causa:** El script de creación de la base de datos no coincidía con el modelo definido en SQLAlchemy, faltando columnas de auditoría necesarias para el ordenamiento.
- **Solución:** Se actualizó `script.sql` para incluir todas las columnas faltantes y se procedió a recrear las tablas mediante un "Reset" de la base de datos.

### 4. Fallo de Persistencia en Conversaciones
- **Problema:** El historial de chat se borraba al refrescar el navegador y el backend no registraba los mensajes.
- **Causa:** Faltaban los modelos de `Conversation` y `Message` en el backend, y el frontend no generaba un identificador de sesión único.
- **Solución:** Se implementó la librería `uuid` en el frontend para generar un `session_id` persistente y se crearon las tablas correspondientes en PostgreSQL para vincular mensajes a asistentes y sesiones.

### 5. Uso de Endpoints Incorrectos para RAG
- **Problema:** Los documentos se subían pero el asistente no podía responder basándose en ellos (RAG fallido).
- **Causa:** El frontend llamaba al endpoint `/chat/document` (que no indexaba) en lugar de `/assistants/{id}/documents`.
- **Solución:** Se corrigió la llamada en el componente de carga para asegurar que el documento pase por el proceso de generación de embeddings y almacenamiento en la tabla de vectores `chunks`.

### 6. Desbordamiento de Git (10,000+ Cambios)
- **Problema:** Visual Studio Code mostraba miles de cambios pendientes, imposibilitando un "Push" limpio al repositorio.
- **Causa:** Ausencia de un archivo `.gitignore`, lo que provocaba que Git intentara rastrear la carpeta `node_modules` y los entornos virtuales de Python.
- **Solución:** Creación de un archivo `.gitignore` robusto que excluye dependencias, archivos de caché (`__pycache__`) y variables de entorno sensibles (`.env`).

### 7. Agotamiento de Cuota / Errores de API
- **Problema:** Respuestas vacías del asistente o errores 429 en los logs del backend.
- **Causa:** Credenciales de Azure OpenAI incorrectas o superación del límite de tokens por minuto (TPM).
- **Solución:** Validación de variables de entorno en el archivo `.env` y ajuste de los modelos de despliegue a `gpt-4o-mini` para optimizar el consumo.