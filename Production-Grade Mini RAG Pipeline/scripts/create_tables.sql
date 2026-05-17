CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_name TEXT,
    chunk_index INT,
    content TEXT,
    embedding VECTOR(1536)
);

CREATE INDEX idx_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);