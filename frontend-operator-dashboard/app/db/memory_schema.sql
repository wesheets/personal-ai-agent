-- SQLite schema for memory storage
-- This schema replaces the in-memory memory_store array and JSON file storage
-- with a persistent SQLite database

-- Memory table to store all memory entries
CREATE TABLE IF NOT EXISTS memories (
    memory_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT NOT NULL,  -- Stored as JSON array
    timestamp TEXT NOT NULL,  -- ISO 8601 format
    project_id TEXT,
    status TEXT,
    task_type TEXT,
    task_id TEXT,
    memory_trace_id TEXT,
    agent_tone TEXT,  -- Stored as JSON object
    metadata TEXT,    -- Stored as JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_memories_agent_id ON memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_memories_memory_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_project_id ON memories(project_id);
CREATE INDEX IF NOT EXISTS idx_memories_task_id ON memories(task_id);
CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);

-- Create a view for easier querying with common filters
CREATE VIEW IF NOT EXISTS memory_view AS
SELECT 
    memory_id,
    agent_id,
    memory_type AS type,
    content,
    tags,
    timestamp,
    project_id,
    status,
    task_type,
    task_id,
    memory_trace_id,
    agent_tone,
    created_at
FROM memories;

-- Metadata table for database information
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Insert initial metadata
INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '1.0');
INSERT OR REPLACE INTO metadata (key, value) VALUES ('created_at', CURRENT_TIMESTAMP);
