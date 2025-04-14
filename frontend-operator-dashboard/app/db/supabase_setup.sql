-- This file contains SQL functions for Supabase to enable vector similarity search
-- Save this as a SQL migration in your Supabase project

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the agent_memories table if it doesn't exist
CREATE TABLE IF NOT EXISTS agent_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    priority BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index for vector similarity search
CREATE INDEX IF NOT EXISTS agent_memories_embedding_idx 
ON agent_memories 
USING ivfflat (embedding vector_cosine_ops);

-- Function to match memories by vector similarity
CREATE OR REPLACE FUNCTION match_memories(query_embedding VECTOR(1536), match_threshold FLOAT, match_count INT)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT,
    priority BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        agent_memories.id,
        agent_memories.content,
        agent_memories.metadata,
        1 - (agent_memories.embedding <=> query_embedding) AS similarity,
        agent_memories.priority,
        agent_memories.created_at
    FROM agent_memories
    WHERE 1 - (agent_memories.embedding <=> query_embedding) > match_threshold
    ORDER BY agent_memories.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to match only priority memories by vector similarity
CREATE OR REPLACE FUNCTION match_memories_priority(query_embedding VECTOR(1536), match_threshold FLOAT, match_count INT)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT,
    priority BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        agent_memories.id,
        agent_memories.content,
        agent_memories.metadata,
        1 - (agent_memories.embedding <=> query_embedding) AS similarity,
        agent_memories.priority,
        agent_memories.created_at
    FROM agent_memories
    WHERE 
        agent_memories.priority = TRUE AND
        1 - (agent_memories.embedding <=> query_embedding) > match_threshold
    ORDER BY agent_memories.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
