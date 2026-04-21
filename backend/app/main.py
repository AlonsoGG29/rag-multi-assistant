# Aqui deberán ir los endpoints siguientes:

# POST /assistants: Guarda en la tabla "assistants"

# POST /assistants/{id}/documents 
#   -Recibe el archivo (UploadFile).
#   -Usa PyPDF para leerlo.
#   -Llama a rag.get_embedding.
#   -Guarda en chunks con el assistant_id de la URL.

# POST /chat:
#   -Recibe assistant_id y el message.
#   -Llama a rag.search_context(db, assistant_id, message).
#   -Crea el prompt final enviando al LLM las instructions del asistente + el contexto recuperado.
