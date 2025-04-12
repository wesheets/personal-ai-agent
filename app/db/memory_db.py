"""
Memory Database Module

This module provides a SQLite-based persistent storage for agent memories.
It replaces the previous in-memory array and JSON file storage with a
robust database solution that supports efficient querying and filtering.

The module implements a singleton pattern to ensure consistent database
access across the application.
"""

import os
import json
import sqlite3
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger("app.db.memory_db")

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db")
DB_FILE = os.path.join(DB_DIR, "memory.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "memory_schema.sql")

# Log absolute database path for debugging
logger.info(f"💾 DB PATH: {os.path.abspath(DB_FILE)}")
print(f"💾 [DB] Absolute database path: {os.path.abspath(DB_FILE)}")

# Thread-local storage for database connections
thread_local = threading.local()

class MemoryDB:
    """
    SQLite-based persistent storage for agent memories.
    
    This class provides methods for writing, reading, and querying memories
    with support for filtering by various criteria.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        Create a new MemoryDB instance or return the existing singleton instance.
        
        Returns:
            MemoryDB: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryDB, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """
        Initialize the MemoryDB instance.
        
        This method is called when a new instance is created, but the actual
        initialization is only performed once due to the singleton pattern.
        """
        if self._initialized:
            return
            
        # Create database directory if it doesn't exist
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
            
        # Store the database path as an instance attribute
        self.db_path = DB_FILE
            
        # Initialize database
        self._init_db()
        
        # Set initialized flag
        self._initialized = True
        
        # Log initialization with absolute path
        logger.info(f"✅ MemoryDB initialized with database file: {os.path.abspath(self.db_path)}")
        print(f"🧠 [INIT] MemoryDB initialized with database file: {os.path.abspath(self.db_path)}")
    
    def get_path(self):
        """
        Get the absolute path to the database file.
        
        Returns:
            str: Absolute path to the database file
        """
        return os.path.abspath(self.db_path)
    
    def _init_db(self):
        """
        Initialize the database by creating tables and indexes if they don't exist.
        """
        try:
            # Get a database connection
            conn = self._get_connection()
            
            # Check if schema file exists
            if not os.path.exists(SCHEMA_FILE):
                logger.error(f"❌ Schema file not found: {SCHEMA_FILE}")
                raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")
            
            # Read schema file
            with open(SCHEMA_FILE, 'r') as f:
                schema = f.read()
            
            # Execute schema
            conn.executescript(schema)
            conn.commit()
            
            # Log success
            logger.info(f"✅ Database initialized with schema from {SCHEMA_FILE}")
            print(f"🧠 [INIT] Database initialized with schema from {SCHEMA_FILE}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database: {str(e)}")
            print(f"❌ [INIT] Error initializing database: {str(e)}")
            raise
    
    def _get_connection(self):
        """
        Get a database connection for the current thread.
        
        Returns:
            sqlite3.Connection: A database connection
        """
        # Check if connection exists for current thread
        if not hasattr(thread_local, "connection") or thread_local.connection is None:
            # Create a new connection
            try:
                # Log the absolute path when creating a new connection
                logger.info(f"💾 DB PATH: Creating connection to {self.get_path()}")
                
                thread_local.connection = sqlite3.connect(self.db_path)
                thread_local.connection.row_factory = sqlite3.Row
                logger.info(f"✅ New database connection created in thread {threading.get_ident()}")
                print(f"🧠 [DB] New database connection created in thread {threading.get_ident()}")
            except Exception as e:
                logger.error(f"❌ Error creating database connection: {str(e)}")
                print(f"❌ [DB] Error creating database connection: {str(e)}")
                raise
        
        return thread_local.connection
    
    def close(self):
        """
        Close the database connection for the current thread.
        """
        if hasattr(thread_local, "connection") and thread_local.connection is not None:
            try:
                thread_local.connection.close()
                thread_local.connection = None
                logger.info(f"✅ Database connection closed in thread {threading.get_ident()}")
                print(f"🧠 [DB] Database connection closed in thread {threading.get_ident()}")
            except Exception as e:
                logger.error(f"❌ Error closing database connection: {str(e)}")
                print(f"❌ [DB] Error closing database connection: {str(e)}")
    
    def write_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a memory to the database.
        
        Args:
            memory: A dictionary containing the memory data
            
        Returns:
            The memory with any additional fields added by the database
        """
        try:
            # Get a database connection
            conn = self._get_connection()
            
            # Log the database path for this write operation
            logger.info(f"💾 DB PATH: Writing to {self.get_path()}")
            
            # Prepare memory for database
            memory_db = memory.copy()
            
            # Convert tags to JSON if it's a list
            if "tags" in memory_db and isinstance(memory_db["tags"], list):
                memory_db["tags"] = json.dumps(memory_db["tags"])
            
            # Convert agent_tone to JSON if it's a dict
            if "agent_tone" in memory_db and isinstance(memory_db["agent_tone"], dict):
                memory_db["agent_tone"] = json.dumps(memory_db["agent_tone"])
            
            # Convert metadata to JSON if it's a dict
            if "metadata" in memory_db and isinstance(memory_db["metadata"], dict):
                memory_db["metadata"] = json.dumps(memory_db["metadata"])
            
            # Extract goal_id from metadata if not provided at top level
            if "goal_id" not in memory_db and "metadata" in memory_db:
                metadata = memory_db["metadata"]
                if isinstance(metadata, str):
                    try:
                        metadata_dict = json.loads(metadata)
                        if "goal_id" in metadata_dict:
                            memory_db["goal_id"] = metadata_dict["goal_id"]
                            logger.info(f"🎯 Extracted goal_id from metadata: {metadata_dict['goal_id']} for memory {memory_db['memory_id']}")
                    except:
                        pass
                elif isinstance(metadata, dict) and "goal_id" in metadata:
                    memory_db["goal_id"] = metadata["goal_id"]
                    logger.info(f"🎯 Extracted goal_id from metadata: {metadata['goal_id']} for memory {memory_db['memory_id']}")
            
            # Prepare SQL
            columns = ", ".join(memory_db.keys())
            placeholders = ", ".join(["?"] * len(memory_db))
            values = list(memory_db.values())
            
            # Execute SQL
            cursor = conn.cursor()
            cursor.execute(f"INSERT OR REPLACE INTO memories ({columns}) VALUES ({placeholders})", values)
            
            # Explicitly commit the transaction
            conn.commit()
            logger.info(f"✅ Transaction committed for memory {memory_db['memory_id']}")
            
            # Log success
            logger.info(f"✅ Memory written to database: {memory_db['memory_id']} in thread {threading.get_ident()}")
            print(f"💾 [DB] Memory written to database: {memory_db['memory_id']} (agent: {memory_db['agent_id']}, type: {memory_db['type'] if 'type' in memory_db else memory_db.get('memory_type')})")
            
            # Verify memory was written by immediately reading it back
            retrieved_memory = self.read_memory_by_id(memory_db["memory_id"])
            if retrieved_memory:
                logger.info(f"✅ VERIFIED: Memory {memory_db['memory_id']} successfully persisted and retrievable")
                print(f"✅ [DB] VERIFIED: Memory {memory_db['memory_id']} successfully persisted and retrievable")
            else:
                logger.warning(f"⚠️ VERIFICATION FAILED: Memory {memory_db['memory_id']} not found after write")
                print(f"⚠️ [DB] VERIFICATION FAILED: Memory {memory_db['memory_id']} not found after write")
            
            # Check connection status
            try:
                cursor.execute("SELECT 1")
                logger.info(f"✅ CONNECTION STATUS: Database connection is OPEN in thread {threading.get_ident()}")
                print(f"✅ [DB] CONNECTION STATUS: Database connection is OPEN in thread {threading.get_ident()}")
            except sqlite3.ProgrammingError:
                logger.warning(f"⚠️ CONNECTION STATUS: Database connection is CLOSED in thread {threading.get_ident()}")
                print(f"⚠️ [DB] CONNECTION STATUS: Database connection is CLOSED in thread {threading.get_ident()}")
            
            # Additional verification: read recent memories to confirm the write is visible
            recent_memories = self.read_memories(limit=10)
            logger.info(f"✅ VISIBILITY CHECK: Found {len(recent_memories)} recent memories after write")
            
            # Check if our memory is in the recent memories
            memory_found = False
            for m in recent_memories:
                if m.get("memory_id") == memory_db["memory_id"]:
                    memory_found = True
                    logger.info(f"✅ VISIBILITY CONFIRMED: Memory {memory_db['memory_id']} found in recent memories list")
                    break
            
            if not memory_found:
                logger.warning(f"⚠️ VISIBILITY ISSUE: Memory {memory_db['memory_id']} not found in recent memories list")
            
            # Return the memory
            return memory
            
        except Exception as e:
            logger.error(f"❌ Error writing memory: {str(e)}")
            print(f"❌ [DB] Error writing memory: {str(e)}")
            
            # Try to rollback if possible
            try:
                conn.rollback()
                logger.info("✅ Transaction rolled back")
                print("✅ [DB] Transaction rolled back")
            except:
                pass
                
            raise
    
    def read_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a memory from the database by its ID.
        
        Args:
            memory_id: The ID of the memory to read
            
        Returns:
            The memory if found, None otherwise
        """
        try:
            # Get a database connection
            conn = self._get_connection()
            
            # Log the database path for this read operation
            logger.info(f"💾 DB PATH: Reading from {self.get_path()}")
            
            # Execute SQL
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id,))
            row = cursor.fetchone()
            
            # Return None if not found
            if not row:
                return None
            
            # Convert row to dict
            memory = dict(row)
            
            # Parse JSON fields
            if "tags" in memory and memory["tags"]:
                try:
                    memory["tags"] = json.loads(memory["tags"])
                except:
                    pass
            
            if "agent_tone" in memory and memory["agent_tone"]:
                try:
                    memory["agent_tone"] = json.loads(memory["agent_tone"])
                except:
                    pass
            
            if "metadata" in memory and memory["metadata"]:
                try:
                    memory["metadata"] = json.loads(memory["metadata"])
                except:
                    pass
            
            # Log success
            print(f"📖 [DB] Memory retrieved from database: {memory_id} (agent: {memory['agent_id']}, type: {memory['memory_type']})")
            
            # Return the memory
            return memory
            
        except Exception as e:
            logger.error(f"❌ Error reading memory by ID: {str(e)}")
            print(f"❌ [DB] Error reading memory by ID: {str(e)}")
            raise
    
    def read_memories(self, agent_id: Optional[str] = None, memory_type: Optional[str] = None,
                     since: Optional[str] = None, project_id: Optional[str] = None,
                     task_id: Optional[str] = None, thread_id: Optional[str] = None,
                     goal_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read memories from the database with optional filtering.
        
        Args:
            agent_id: Filter by agent ID
            memory_type: Filter by memory type
            since: Filter by timestamp (ISO 8601 format)
            project_id: Filter by project ID
            task_id: Filter by task ID
            thread_id: Filter by thread ID (memory_trace_id)
            goal_id: Filter by goal ID
            limit: Maximum number of memories to return
            
        Returns:
            A list of memories matching the filters
        """
        try:
            # Get a database connection
            conn = self._get_connection()
            
            # Log the database path for this read operation
            logger.info(f"💾 DB PATH: Reading from {self.get_path()}")
            
            # Build SQL query
            sql = "SELECT * FROM memory_view"
            params = []
            where_clauses = []
            
            # Add filters
            if agent_id:
                where_clauses.append("agent_id = ?")
                params.append(agent_id)
            
            if memory_type:
                where_clauses.append("type = ?")
                params.append(memory_type)
            
            if since:
                where_clauses.append("timestamp >= ?")
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
                
            if goal_id:
                where_clauses.append("goal_id = ?")
                params.append(goal_id)
            
            # Add WHERE clause if filters are present
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY clause
            sql += " ORDER BY timestamp DESC"
            
            # Add LIMIT clause if limit is provided
            if limit:
                sql += f" LIMIT {limit}"
            
            # Execute SQL
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert rows to dicts and parse JSON fields
            memories = []
            for row in rows:
                memory = dict(row)
                
                # Parse JSON fields
                if "tags" in memory and memory["tags"]:
                    try:
                        memory["tags"] = json.loads(memory["tags"])
                    except:
                        pass
                
                if "agent_tone" in memory and memory["agent_tone"]:
                    try:
                        memory["agent_tone"] = json.loads(memory["agent_tone"])
                    except:
                        pass
                
                if "metadata" in memory and memory["metadata"]:
                    try:
                        memory["metadata"] = json.loads(memory["metadata"])
                    except:
                        pass
                
                memories.append(memory)
            
            # Log success
            logger.info(f"📚 [DB] Retrieved {len(memories)} memories from database")
            print(f"📚 [DB] Retrieved {len(memories)} memories from database")
            
            # Return the memories
            return memories
            
        except Exception as e:
            logger.error(f"❌ Error reading memories: {str(e)}")
            print(f"❌ [DB] Error reading memories: {str(e)}")
            raise
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from the database.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if the memory was deleted, False otherwise
        """
        try:
            # Get a database connection
            conn = self._get_connection()
            
            # Execute SQL
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
            
            # Commit the transaction
            conn.commit()
            
            # Check if a row was deleted
            if cursor.rowcount > 0:
                logger.info(f"✅ Memory deleted from database: {memory_id}")
                print(f"🗑️ [DB] Memory deleted from database: {memory_id}")
                return True
            else:
                logger.warning(f"⚠️ Memory not found for deletion: {memory_id}")
                print(f"⚠️ [DB] Memory not found for deletion: {memory_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting memory: {str(e)}")
            print(f"❌ [DB] Error deleting memory: {str(e)}")
            
            # Try to rollback if possible
            try:
                conn.rollback()
            except:
                pass
                
            raise
    
    def delete_memories(self, agent_id: Optional[str] = None, memory_type: Optional[str] = None,
                       project_id: Optional[str] = None, task_id: Optional[str] = None,
                       thread_id: Optional[str] = None, goal_id: Optional[str] = None) -> int:
        """
        Delete memories from the database with optional filtering.
        
        Args:
            agent_id: Filter by agent ID
            memory_type: Filter by memory type
            project_id: Filter by project ID
            task_id: Filter by task ID
            thread_id: Filter by thread ID (memory_trace_id)
            goal_id: Filter by goal ID
            
        Returns:
            The number of memories deleted
        """
        try:
            # Get a database connection
            conn = self._get_connection()
            
            # Build SQL query
            sql = "DELETE FROM memories"
            params = []
            where_clauses = []
            
            # Add filters
            if agent_id:
                where_clauses.append("agent_id = ?")
                params.append(agent_id)
            
            if memory_type:
                where_clauses.append("memory_type = ?")
                params.append(memory_type)
            
            if project_id:
                where_clauses.append("project_id = ?")
                params.append(project_id)
            
            if task_id:
                where_clauses.append("task_id = ?")
                params.append(task_id)
            
            if thread_id:
                where_clauses.append("memory_trace_id = ?")
                params.append(thread_id)
                
            if goal_id:
                where_clauses.append("goal_id = ?")
                params.append(goal_id)
            
            # Add WHERE clause if filters are present
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            else:
                # Prevent accidental deletion of all memories
                logger.error("❌ Attempted to delete all memories without filters")
                print("❌ [DB] Attempted to delete all memories without filters")
                return 0
            
            # Execute SQL
            cursor = conn.cursor()
            cursor.execute(sql, params)
            
            # Commit the transaction
            conn.commit()
            
            # Get the number of deleted rows
            deleted_count = cursor.rowcount
            
            # Log success
            logger.info(f"✅ Deleted {deleted_count} memories from database")
            print(f"🗑️ [DB] Deleted {deleted_count} memories from database")
            
            # Return the number of deleted rows
            return deleted_count
                
        except Exception as e:
            logger.error(f"❌ Error deleting memories: {str(e)}")
            print(f"❌ [DB] Error deleting memories: {str(e)}")
            
            # Try to rollback if possible
            try:
                conn.rollback()
            except:
                pass
                
            raise

# Create a singleton instance
memory_db = MemoryDB()
