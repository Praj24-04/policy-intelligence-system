-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add new columns to the policies table
ALTER TABLE policies ADD COLUMN IF NOT EXISTS embedding vector(768);
ALTER TABLE policies ADD COLUMN IF NOT EXISTS cluster_id integer;
ALTER TABLE policies ADD COLUMN IF NOT EXISTS cluster_confidence double precision;
ALTER TABLE policies ADD COLUMN IF NOT EXISTS embedding_model varchar(255);
ALTER TABLE policies ADD COLUMN IF NOT EXISTS last_embedded_at timestamp with time zone;

-- Create ivfflat index for cosine similarity search
CREATE INDEX IF NOT EXISTS policies_embedding_cosine_idx ON policies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
