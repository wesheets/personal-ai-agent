"""
SQLite Memory Database Module

This module provides SQLite-backed persistent storage for agent memories.
It replaces the in-memory memory_store array and JSON file storage with a
SQLite database that persists across deployments.
"""

import sqlite3
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
import logging

# Configure logging
logger = logging.getLogger("app.db.memory_db")

# Path for SQLite database file
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db")
DB_FILE = os.path.join(DB_DIR, "memory.db")
SCHEMA_FILE = os.path.join(DB_DIR, "memory_schema.sql")

# Path for memory.json file (for migration)
MEMORY_JSON_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory.json")

# Path for memory_store.json file (for migration)
MEMORY_STORE_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")

class MemoryDB:
    """SQLite database connection manager for memory storage"""
    
    def __init__(self):
        """Initialize the database connection and ensure schema exists"""
        self.conn = None
        self.ensure_db_directory()
        self.connect()
        self.init_schema()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(DB_DIR, exist_ok=True)
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(DB_FILE)
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Configure connection to return rows as dictionaries
            self.conn.row_factory = sqlite3.Row
            logger.info(f"✅ Connected to SQLite database at {DB_FILE}")
        except Exception as e:
            logger.error(f"❌ Error connecting to SQLite database: {str(e)}")
            raise
    
    def init_schema(self):
        """Initialize the database schema if it doesn't exist"""
        try:
            if not os.path.exists(SCHEMA_FILE):
                logger.error(f"❌ Schema file not found at {SCHEMA_FILE}")
                raise FileNotFoundError(f"Schema file not found at {SCHEMA_FILE}")
            
            with open(SCHEMA_FILE, 'r') as f:
                schema_sql = f.read()
            
            # Execute the schema SQL
            self.conn.executescript(schema_sql)
            self.conn.commit()
            logger.info("✅ Database schema initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing database schema: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")
    
    def write_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a memory to the database
        
        Args:
            memory: Dictionary containing memory data
            
        Returns:
            The memory with its memory_id
        """
        try:
            # Convert tags list to JSON string
            tags_json = json.dumps(memory.get("tags", []))
            
            # Convert agent_tone to JSON string if present
            agent_tone_json = json.dumps(memory.get("agent_tone")) if "agent_tone" in memory else None
            
            # Insert the memory into the database
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO memories (
                    memory_id, agent_id, memory_type, content, tags, timestamp,
                    project_id, status, task_type, task_id, memory_trace_id, agent_tone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory["memory_id"],
                memory["agent_id"],
                memory["type"],
                memory["content"],
                tags_json,
                memory["timestamp"],
                memory.get("project_id"),
                memory.get("status"),
                memory.get("task_type"),
                memory.get("task_id"),
                memory.get("memory_trace_id"),
                agent_tone_json
            ))
            self.conn.commit()
            logger.info(f"✅ Memory written to database: {memory['memory_id']}")
            return memory
        except Exception as e:
            logger.error(f"❌ Error writing memory to database: {str(e)}")
            self.conn.rollback()
            raise
    
    def read_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a memory from the database by its ID
        
        Args:
            memory_id: The ID of the memory to read
            
        Returns:
            The memory as a dictionary, or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM memory_view WHERE memory_id = ?
            """, (memory_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Convert row to dictionary
            memory = dict(row)
            
            # Parse tags from JSON string
            memory["tags"] = json.loads(memory["tags"])
            
            # Parse agent_tone from JSON string if present and not null
            if memory.get("agent_tone"):
                memory["agent_tone"] = json.loads(memory["agent_tone"])
            
            return memory
        except Exception as e:
            logger.error(f"❌ Error reading memory from database: {str(e)}")
            raise
    
    def read_memories(self, 
                     agent_id: Optional[str] = None,
                     memory_type: Optional[str] = None,
                     tag: Optional[str] = None,
                     limit: Optional[int] = 10,
                     since: Optional[str] = None,
                     project_id: Optional[str] = None,
                     task_id: Optional[str] = None,
                     thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Read memories from the database with flexible filtering
        
        Args:
            agent_id: Filter by agent ID
            memory_type: Filter by memory type
            tag: Filter by tag
            limit: Maximum number of memories to return
            since: ISO 8601 timestamp to filter memories after a specific time
            project_id: Filter by project ID
            task_id: Filter by task ID
            thread_id: Filter by thread ID
            
        Returns:
            List of memories as dictionaries
        """
        try:
            # Build the query dynamically based on provided filters
            query = "SELECT * FROM memory_view"
            params = []
            where_clauses = []
            
            # Add filter conditions
            if agent_id:
                where_clauses.append("agent_id = ?")
                params.append(agent_id)
            
            if memory_type:
                where_clauses.append("type = ?")
                params.append(memory_type)
            
            if since:
                where_clauses.append("timestamp > ?")
                params.append(since)
            
            if project_id:
                where_clauses.append("project_id = ?")
                params.append(project_id)
            
            if task_id:
                where_clauses.append("task_id = ?")
                params.append(task_id)
            
            if thread_id:
                where_clauses.append("memory_trace_id = ?")
                params.append(thread_id)
            
            # Combine where clauses
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add order by and limit
            query += " ORDER BY timestamp DESC"
            
            if limit and limit > 0:
                query += " LIMIT ?"
                params.append(limit)
            
            # Execute the query
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            memories = [dict(row) for row in rows]
            
            # Process each memory
            for memory in memories:
                # Parse tags from JSON string
                memory["tags"] = json.loads(memory["tags"])
                
                # Parse agent_tone from JSON string if present and not null
                if memory.get("agent_tone"):
                    memory["agent_tone"] = json.loads(memory["agent_tone"])
            
            # Additional filtering for tags (needs to be done after JSON parsing)
            if tag:
                memories = [m for m in memories if tag in m["tags"]]
            
            return memories
        except Exception as e:
            logger.error(f"❌ Error reading memories from database: {str(e)}")
            raise
    
    def migrate_from_json(self) -> int:
        """
        Migrate memories from JSON files to SQLite database
        
        Returns:
            Number of memories migrated
        """
        migrated_count = 0
        
        try:
            # Check if memory.json exists
            if os.path.exists(MEMORY_JSON_FILE):
                with open(MEMORY_JSON_FILE, 'r') as f:
                    memories = json.load(f)
                
                # Insert each memory into the database
                for memory in memories:
                    try:
                        self.write_memory(memory)
                        migrated_count += 1
                    except Exception as e:
                        logger.error(f"❌ Error migrating memory {memory.get('memory_id')}: {str(e)}")
                
                logger.info(f"✅ Migrated {migrated_count} memories from memory.json")
            
            # Check if memory_store.json exists
            elif os.path.exists(MEMORY_STORE_FILE):
                with open(MEMORY_STORE_FILE, 'r') as f:
                    memories = json.load(f)
                
                # Insert each memory into the database
                for memory in memories:
                    try:
                        self.write_memory(memory)
                        migrated_count += 1
                    except Exception as e:
                        logger.error(f"❌ Error migrating memory {memory.get('memory_id')}: {str(e)}")
                
                logger.info(f"✅ Migrated {migrated_count} memories from memory_store.json")
            
            else:
                logger.info("⚠️ No JSON files found for migration")
            
            return migrated_count
        except Exception as e:
            logger.error(f"❌ Error during migration: {str(e)}")
            self.conn.rollback()
            raise

# Create a singleton instance
memory_db = MemoryDB()

# Perform migration on module import
try:
    migrated_count = memory_db.migrate_from_json()
    if migrated_count > 0:
        logger.info(f"✅ Successfully migrated {migrated_count} memories to SQLite database")
except Exception as e:
    logger.error(f"❌ Migration failed: {str(e)}")
