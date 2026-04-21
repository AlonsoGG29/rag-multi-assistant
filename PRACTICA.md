# Práctica: Aplicación Full-Stack de Asistentes RAG (multi-asistente)

## Contexto (caso real)

Una empresa nos ha contactado para desarrollar un **producto interno** con IA generativa.

Necesitan una aplicación **full-stack** que permita crear **asistentes personalizados** y chatear con ellos aplicando **RAG (Retrieval-Augmented Generation)**.

Este documento describe el **core** que la empresa exige: requisitos mínimos obligatorios. El stack, la arquitectura y el diseño quedan a elección del equipo, siempre que se cumpla lo siguiente.

La idea clave es esta:

- Se pueden crear **varios asistentes**.
- Cada asistente tiene **sus propias instrucciones** (cómo debe comportarse).
- Cada asistente tiene **sus propios documentos de referencia**.
- Cuando chateas con un asistente, **solo puede responder usando la información de SUS documentos** (aislamiento total entre asistentes).
- El chat debe **persistir** (historial/memoria conversacional).

---

## Funcionalidades core (obligatorias)

Tu aplicación **DEBE** implementar estas funcionalidades. El formato, el stack y el diseño son **totalmente libres**, pero estas capacidades tienen que existir y funcionar.

### 1) Gestión de asistentes

Debe existir un módulo para gestionar asistentes:

- Crear asistente
- Listar asistentes
- Editar asistente
- Eliminar asistente

Cada asistente debe tener, como mínimo:

- `nombre`
- `instrucciones` (prompt del sistema / reglas del asistente)
- (Opcional) `descripción`

### 2) Documentos por asistente

Debe ser posible asociar documentos a un asistente (no a “la app” en general):

- Subir documentos a un asistente
- Ver el listado de documentos de un asistente
- Eliminar documentos de un asistente

Formatos: PDF, DOCX, PPTX, TXT/Markdown y otros que quieras. Si aceptas imágenes, deberás extraer texto (OCR) o especificar claramente qué se soporta.

### 3) Ingesta, chunking y vectorización (por asistente)

Cuando se sube un documento a un asistente, tu sistema debe:

- Extraer el texto
- Dividirlo en fragmentos (chunking)
- Generar embeddings de cada fragmento
- Almacenar fragmentos + metadata + embeddings en un sistema de búsqueda/vectorial

Requisito crítico: **aislamiento por asistente**.

- Cada asistente debe tener su propio “espacio” de recuperación (índice/colección/namespace/filtro) para garantizar que **nunca** se recuperen documentos de otro asistente.

### 4) Chat con RAG por asistente (aislado)

Debe existir un chat en el que el usuario:

- Seleccione un asistente
- Envíe mensajes
- Reciba respuestas generadas por un LLM

Para cada mensaje, el flujo mínimo debe ser:

1. Recuperar contexto **solo** de los documentos del asistente seleccionado
2. Construir el prompt con:
   - Instrucciones del asistente
   - Historial de la conversación (si aplica)
   - Contexto recuperado
3. Generar la respuesta

Además:

- Las respuestas deben ser **fundamentadas** en los documentos del asistente.
- Deben incluir **citas** (referencias a los documentos/fragmentos usados).
- Si el asistente **no encuentra evidencia suficiente** en sus documentos, debe responder explícitamente que no puede contestar con la información disponible (sin inventar).

### 5) Persistencia del chat (memoria conversacional)

El chat debe mantener y persistir el contexto:

- Guardar historial de conversación
- Poder reanudar una conversación (por asistente)
- Permitir limpiar/iniciar una conversación nueva

La persistencia puede ser por usuario autenticado o por sesión (a elección), pero debe quedar claro y funcionar.

### 6) Aplicación full-stack

La aplicación debe tener:

- **Frontend**: interfaz para gestionar asistentes, documentos y el chat.
- **Backend**: API/servicio que implemente la gestión de asistentes, la ingesta/indexado y el chat con RAG.

---

## Libertad total para ampliar

Una vez cumplas el core, puedes ampliar la práctica con lo que quieras (features extra, mejoras de UX, autenticación, multi-usuario, permisos, streaming, herramientas, etc.). El objetivo es que la aplicación cumpla las funcionalidades core y que el resto sea totalmente a tu criterio.

---

## Entregables

Tu entrega debe incluir:

### 1) Repositorio de GitHub

Un repositorio público de GitHub con el **código fuente completo** y una estructura clara (por ejemplo, separación de `frontend/` y `backend/`, o el enfoque que elijas).

Debe incluir:

- Código completo y ejecutable
- `.gitignore` apropiado
- Gestión de dependencias (`package.json`, `requirements.txt`, `pyproject.toml`, etc.)
- Variables de entorno documentadas con un `.env.example` (sin credenciales reales)

### 2) README técnico

El README debe explicar la aplicación a nivel técnico, incluyendo como mínimo:

- Descripción del producto (qué problema resuelve y qué hace)
- Stack tecnológico utilizado
- **Arquitectura implementada** (diagrama y/o explicación clara)
- **Decisiones de diseño** (técnicas y de producto/UX) relevantes (por qué ese enfoque)
- Guía de ejecución local paso a paso (frontend + backend)
- Cómo se cumple el core:
  - cómo garantizas el **aislamiento por asistente** en el retrieval
  - cómo implementas la **persistencia del chat/memoria**
  - cómo gestionas las **citas** y el comportamiento de “no inventar”

### 3) Vídeo demo (3–5 minutos)

El vídeo debe mostrar de forma clara:

- Creación de al menos **2 asistentes** con instrucciones distintas
- Subida de documentos distintos a cada asistente
- Chat con cada asistente demostrando que responde con **sus** documentos (sin contaminación entre asistentes)
- Persistencia del historial (continuar conversación / recargar)
- Ejemplo de citas/fuentes en las respuestas

## Presentaciones
Se escogerá a 5 alumnos al azar para que presenten su proyecto (+ voluntarios). Preparad la presentación de la demo y el producto para el día de la presentación, porque no sabremos los alumnos que exponen hasta el día de las exposiciones.
