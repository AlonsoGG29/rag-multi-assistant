CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE assistants (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  instructions TEXT NOT NULL,
  description TEXT
);

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  assistant_id INTEGER NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  mime_type TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chunks (
  id SERIAL PRIMARY KEY,
  assistant_id INTEGER NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536), -- ajusta a dimensión del modelo
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  assistant_id INTEGER NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- 'user' | 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
