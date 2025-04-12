-- SQLite schema update to add goal_id column to memories table

-- Add goal_id column to memories table
ALTER TABLE memories ADD COLUMN goal_id TEXT;

-- Create index for goal_id for efficient querying
CREATE INDEX IF NOT EXISTS idx_memories_goal_id ON memories(goal_id);

-- Update memory_view to include goal_id
DROP VIEW IF EXISTS memory_view;
CREATE VIEW memory_view AS
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
    goal_id,
    agent_tone,
    created_at
FROM memories;

-- Update schema version
UPDATE metadata SET value = '1.1' WHERE key = 'schema_version';
INSERT OR REPLACE INTO metadata (key, value) VALUES ('updated_at', CURRENT_TIMESTAMP);
INSERT OR REPLACE INTO metadata (key, value) VALUES ('update_description', 'Added goal_id column to memories table');
