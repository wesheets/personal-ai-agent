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
import threading
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

# Thread-local storage for database connections
local = threading.local()

class MemoryDB:
    """SQLite database connection manager for memory storage"""
    
    def __init__(self):
        """Initialize the database and ensure schema exists"""
        self.ensure_db_directory()
        # Initialize the schema using a temporary connection
        temp_conn = self._get_connection()
        self._init_schema(temp_conn)
        temp_conn.close()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(DB_DIR, exist_ok=True)
    
    def _get_connection(self):
        """Get a thread-local database connection"""
        if not hasattr(local, 'conn') or local.conn is None:
            try:
                local.conn = sqlite3.connect(DB_FILE)
                # Enable foreign keys
                local.conn.execute("PRAGMA foreign_keys = ON")
                # Configure connection to return rows as dictionaries
                local.conn.row_factory = sqlite3.Row
                logger.info(f"✅ Connected to SQLite database at {DB_FILE} in thread {threading.get_ident()}")
                print(f"🔌 [DB] Connected to SQLite database at {DB_FILE} in thread {threading.get_ident()}")
            except Exception as e:
                error_msg = f"❌ Error connecting to SQLite database: {str(e)}"
                logger.error(error_msg)
                print(f"❌ [DB] {error_msg}")
                raise
        else:
            # Verify connection is still valid
            try:
                # Simple query to check if connection is still open
                local.conn.execute("SELECT 1").fetchone()
            except sqlite3.ProgrammingError as e:
                if "closed database" in str(e):
                    # Connection was closed, create a new one
                    logger.warning(f"⚠️ Found closed database connection in thread {threading.get_ident()}, reconnecting...")
                    print(f"⚠️ [DB] Found closed database connection, reconnecting...")
                    local.conn = sqlite3.connect(DB_FILE)
                    # Enable foreign keys
                    local.conn.execute("PRAGMA foreign_keys = ON")
                    # Configure connection to return rows as dictionaries
                    local.conn.row_factory = sqlite3.Row
                    logger.info(f"✅ Reconnected to SQLite database at {DB_FILE} in thread {threading.get_ident()}")
                    print(f"🔌 [DB] Reconnected to SQLite database at {DB_FILE} in thread {threading.get_ident()}")
                else:
                    # Some other SQLite error
                    raise
            except Exception as e:
                # Some other error
                error_msg = f"❌ Error verifying database connection: {str(e)}"
                logger.error(error_msg)
                print(f"❌ [DB] {error_msg}")
                raise
                
        return local.conn
    
    def _init_schema(self, conn):
        """Initialize the database schema if it doesn't exist"""
        try:
            if not os.path.exists(SCHEMA_FILE):
                error_msg = f"Schema file not found at {SCHEMA_FILE}"
                logger.error(f"❌ {error_msg}")
                print(f"❌ [DB] {error_msg}")
                raise FileNotFoundError(error_msg)
            
            with open(SCHEMA_FILE, 'r') as f:
                schema_sql = f.read()
            
            # Execute the schema SQL
            conn.executescript(schema_sql)
            conn.commit()
            logger.info("✅ Database schema initialized")
            print(f"🏗️ [DB] Database schema initialized successfully")
        except Exception as e:
            error_msg = f"Error initializing database schema: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"❌ [DB] {error_msg}")
            raise
    
    def close(self):
        """Close the thread-local database connection"""
        if hasattr(local, 'conn') and local.conn:
            local.conn.close()
            local.conn = None
            logger.info(f"✅ Database connection closed in thread {threading.get_ident()}")
    
    def write_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a memory to the database
        
        Args:
            memory: Dictionary containing memory data
            
        Returns:
            The memory with its memory_id
        """
        conn = self._get_connection()
        try:
            # Convert tags list to JSON string
            tags_json = json.dumps(memory.get("tags", []))
            
            # Convert agent_tone to JSON string if present
            agent_tone_json = json.dumps(memory.get("agent_tone")) if "agent_tone" in memory else None
            
            # Convert metadata to JSON string if present
            metadata_json = json.dumps(memory.get("metadata")) if "metadata" in memory else None
            
            # Insert the memory into the database
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (
                    memory_id, agent_id, memory_type, content, tags, timestamp,
                    project_id, status, task_type, task_id, memory_trace_id, agent_tone, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                agent_tone_json,
                metadata_json
            ))
            conn.commit()
            logger.info(f"✅ Memory written to database: {memory['memory_id']} in thread {threading.get_ident()}")
            print(f"💾 [DB] Memory written to database: {memory['memory_id']} (agent: {memory['agent_id']}, type: {memory['type']})")
            
            # VERIFICATION: Verify the memory was actually written by reading it back
            try:
                verification = self.read_memory_by_id(memory["memory_id"])
                if verification:
                    logger.info(f"✅ VERIFIED: Memory {memory['memory_id']} successfully persisted and retrievable")
                    print(f"✅ [DB] VERIFIED: Memory {memory['memory_id']} successfully persisted and retrievable")
                else:
                    logger.warning(f"⚠️ VERIFICATION FAILED: Memory {memory['memory_id']} not found after write!")
                    print(f"⚠️ [DB] VERIFICATION FAILED: Memory {memory['memory_id']} not found after write!")
            except Exception as e:
                logger.error(f"❌ VERIFICATION ERROR: Failed to verify memory {memory['memory_id']}: {str(e)}")
                print(f"❌ [DB] VERIFICATION ERROR: Failed to verify memory {memory['memory_id']}: {str(e)}")
            
            # VERIFICATION: Test read_memories to ensure it's also retrievable that way
            try:
                recent_memories = self.read_memories(limit=5)
                found = any(m.get("memory_id") == memory["memory_id"] for m in recent_memories)
                if found:
                    logger.info(f"✅ VERIFIED: Memory {memory['memory_id']} found in recent memories list")
                    print(f"✅ [DB] VERIFIED: Memory {memory['memory_id']} found in recent memories list")
                else:
                    logger.warning(f"⚠️ VERIFICATION FAILED: Memory {memory['memory_id']} not found in recent memories!")
                    print(f"⚠️ [DB] VERIFICATION FAILED: Memory {memory['memory_id']} not found in recent memories!")
            except Exception as e:
                logger.error(f"❌ VERIFICATION ERROR: Failed to check recent memories: {str(e)}")
                print(f"❌ [DB] VERIFICATION ERROR: Failed to check recent memories: {str(e)}")
            
            return memory
        except Exception as e:
            error_msg = f"Error writing memory to database: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"❌ [DB] {error_msg} (memory_id: {memory.get('memory_id', 'unknown')})")
            conn.rollback()
            raise
    
    def read_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a memory from the database by its ID
        
        Args:
            memory_id: The ID of the memory to read
            
        Returns:
            The memory as a dictionary, or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM memory_view WHERE memory_id = ?
            """, (memory_id,))
            row = cursor.fetchone()
            
            if not row:
                print(f"🔍 [DB] Memory not found in database: {memory_id}")
                return None
            
            # Convert row to dictionary
            memory = dict(row)
            
            # Parse tags from JSON string
            memory["tags"] = json.loads(memory["tags"])
            
            # Parse agent_tone from JSON string if present and not null
            if memory.get("agent_tone"):
                memory["agent_tone"] = json.loads(memory["agent_tone"])
            
            # Parse metadata from JSON string if present and not null
            if memory.get("metadata"):
                memory["metadata"] = json.loads(memory["metadata"])
            
            print(f"📖 [DB] Memory retrieved from database: {memory_id} (agent: {memory.get('agent_id')}, type: {memory.get('type')})")
            return memory
        except Exception as e:
            error_msg = f"Error reading memory from database: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"❌ [DB] {error_msg} (memory_id: {memory_id})")
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
        conn = self._get_connection()
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
            
            # Log the query being executed
            filter_desc = ", ".join([f"{k}={v}" for k, v in {
                "agent_id": agent_id,
                "memory_type": memory_type,
                "since": since,
                "project_id": project_id,
                "task_id": task_id,
                "thread_id": thread_id,
                "limit": limit
            }.items() if v is not None])
            print(f"🔍 [DB] Querying memories with filters: {filter_desc}")
            
            # Execute the query
            cursor = conn.cursor()
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
                
                # Parse metadata from JSON string if present and not null
                if memory.get("metadata"):
                    memory["metadata"] = json.loads(memory["metadata"])
            
            # Additional filtering for tags (needs to be done after JSON parsing)
            if tag:
                memories = [m for m in memories if tag in m["tags"]]
            
            print(f"📚 [DB] Retrieved {len(memories)} memories from database")
            return memories
        except Exception as e:
            error_msg = f"Error reading memories from database: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"❌ [DB] {error_msg} (filters: {filter_desc if 'filter_desc' in locals() else 'unknown'})")
            raise
    
    def migrate_from_json(self) -> int:
        """
        Migrate memories from JSON files to SQLite database
        
        Returns:
            Number of memories migrated
        """
        conn = self._get_connection()
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
            conn.rollback()
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
