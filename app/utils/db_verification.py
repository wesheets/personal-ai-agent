"""
Database Verification Utilities

This module provides utilities for verifying database operations
and logging detailed information about database connections and queries.
"""

import logging
import time
import os
import json
import sqlite3
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger("app.utils.db_verification")

class DBVerifier:
    """Utility class for verifying database operations and connections"""
    
    @staticmethod
    def verify_write_operation(memory_id: str, db_instance, in_memory_store: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Verify that a memory was successfully written to both the database and in_memory_store
        
        Args:
            memory_id: The ID of the memory to verify
            db_instance: The database instance to use for verification
            in_memory_store: The in-memory store to check
            
        Returns:
            Dictionary with verification results
        """
        results = {
            "db_verification": False,
            "in_memory_store_verification": False,
            "overall_success": False
        }
        
        # Verify in database
        try:
            db_memory = db_instance.read_memory_by_id(memory_id)
            if db_memory and db_memory.get("memory_id") == memory_id:
                results["db_verification"] = True
                logger.info(f"✅ DB VERIFICATION: Memory {memory_id} found in database")
                print(f"✅ [VERIFY] Memory {memory_id} found in database")
            else:
                logger.warning(f"⚠️ DB VERIFICATION FAILED: Memory {memory_id} not found in database")
                print(f"⚠️ [VERIFY] Memory {memory_id} not found in database")
        except Exception as e:
            logger.error(f"❌ DB VERIFICATION ERROR: {str(e)}")
            print(f"❌ [VERIFY] DB verification error: {str(e)}")
        
        # Verify in in_memory_store
        try:
            memory_store_found = any(m.get("memory_id") == memory_id for m in in_memory_store)
            if memory_store_found:
                results["in_memory_store_verification"] = True
                logger.info(f"✅ IN_MEMORY_STORE VERIFICATION: Memory {memory_id} found in in_memory_store")
                print(f"✅ [VERIFY] Memory {memory_id} found in in_memory_store")
            else:
                logger.warning(f"⚠️ IN_MEMORY_STORE VERIFICATION FAILED: Memory {memory_id} not found in in_memory_store")
                print(f"⚠️ [VERIFY] Memory {memory_id} not found in in_memory_store")
        except Exception as e:
            logger.error(f"❌ IN_MEMORY_STORE VERIFICATION ERROR: {str(e)}")
            print(f"❌ [VERIFY] In-memory store verification error: {str(e)}")
        
        # Overall success
        results["overall_success"] = results["db_verification"] and results["in_memory_store_verification"]
        
        return results
    
    @staticmethod
    def verify_db_connection(db_instance) -> Dict[str, Any]:
        """
        Verify database connection is working properly
        
        Args:
            db_instance: The database instance to verify
            
        Returns:
            Dictionary with verification results
        """
        results = {
            "connection_open": False,
            "query_execution": False,
            "db_file_exists": False,
            "db_file_path": None,
            "overall_success": False
        }
        
        # Check if DB file exists
        try:
            from app.db.memory_db import DB_FILE
            results["db_file_path"] = DB_FILE
            if os.path.exists(DB_FILE):
                results["db_file_exists"] = True
                logger.info(f"✅ DB FILE VERIFICATION: Database file exists at {DB_FILE}")
                print(f"✅ [VERIFY] Database file exists at {DB_FILE}")
                
                # Get file size
                file_size = os.path.getsize(DB_FILE)
                results["db_file_size"] = file_size
                logger.info(f"✅ DB FILE SIZE: {file_size} bytes")
                print(f"✅ [VERIFY] Database file size: {file_size} bytes")
            else:
                logger.warning(f"⚠️ DB FILE VERIFICATION FAILED: Database file not found at {DB_FILE}")
                print(f"⚠️ [VERIFY] Database file not found at {DB_FILE}")
        except Exception as e:
            logger.error(f"❌ DB FILE VERIFICATION ERROR: {str(e)}")
            print(f"❌ [VERIFY] DB file verification error: {str(e)}")
        
        # Verify connection is open
        try:
            # Get a connection
            conn = db_instance._get_connection()
            
            # Test with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result and result[0] == 1:
                results["connection_open"] = True
                results["query_execution"] = True
                logger.info(f"✅ DB CONNECTION VERIFICATION: Connection is open and query executed successfully")
                print(f"✅ [VERIFY] Database connection is open and query executed successfully")
            else:
                logger.warning(f"⚠️ DB CONNECTION VERIFICATION FAILED: Query did not return expected result")
                print(f"⚠️ [VERIFY] Database query did not return expected result")
        except Exception as e:
            logger.error(f"❌ DB CONNECTION VERIFICATION ERROR: {str(e)}")
            print(f"❌ [VERIFY] DB connection verification error: {str(e)}")
        
        # Overall success
        results["overall_success"] = results["connection_open"] and results["query_execution"] and results["db_file_exists"]
        
        return results
    
    @staticmethod
    def verify_memory_thread_retrieval(db_instance, goal_id: str) -> Dict[str, Any]:
        """
        Verify that memories can be retrieved by goal_id
        
        Args:
            db_instance: The database instance to use for verification
            goal_id: The goal ID to search for
            
        Returns:
            Dictionary with verification results
        """
        results = {
            "direct_query_success": False,
            "direct_query_count": 0,
            "metadata_query_success": False,
            "metadata_query_count": 0,
            "overall_success": False
        }
        
        # Try direct SQL query to check if memories with this goal_id exist
        try:
            conn = db_instance._get_connection()
            cursor = conn.cursor()
            
            # Check for top-level goal_id (this would require a schema change or custom query)
            # For now, we'll check in the metadata JSON
            cursor.execute("""
                SELECT COUNT(*) FROM memories 
                WHERE json_extract(metadata, '$.goal_id') = ?
            """, (goal_id,))
            
            count = cursor.fetchone()[0]
            results["metadata_query_count"] = count
            
            if count > 0:
                results["metadata_query_success"] = True
                logger.info(f"✅ GOAL_ID METADATA QUERY: Found {count} memories with goal_id={goal_id} in metadata")
                print(f"✅ [VERIFY] Found {count} memories with goal_id={goal_id} in metadata")
            else:
                logger.warning(f"⚠️ GOAL_ID METADATA QUERY: No memories found with goal_id={goal_id} in metadata")
                print(f"⚠️ [VERIFY] No memories found with goal_id={goal_id} in metadata")
            
            # Overall success - if we found memories with either method
            results["overall_success"] = results["metadata_query_success"]
            
        except Exception as e:
            logger.error(f"❌ GOAL_ID QUERY ERROR: {str(e)}")
            print(f"❌ [VERIFY] Goal ID query error: {str(e)}")
        
        return results
    
    @staticmethod
    def log_db_stats(db_instance) -> Dict[str, Any]:
        """
        Log database statistics
        
        Args:
            db_instance: The database instance to use
            
        Returns:
            Dictionary with database statistics
        """
        stats = {
            "total_memories": 0,
            "memory_types": {},
            "agent_counts": {},
            "recent_memories": []
        }
        
        try:
            conn = db_instance._get_connection()
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM memories")
            stats["total_memories"] = cursor.fetchone()[0]
            
            # Get counts by memory type
            cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
            for row in cursor.fetchall():
                stats["memory_types"][row[0]] = row[1]
            
            # Get counts by agent
            cursor.execute("SELECT agent_id, COUNT(*) FROM memories GROUP BY agent_id")
            for row in cursor.fetchall():
                stats["agent_counts"][row[0]] = row[1]
            
            # Get 5 most recent memories
            cursor.execute("SELECT memory_id, agent_id, memory_type, timestamp FROM memories ORDER BY timestamp DESC LIMIT 5")
            for row in cursor.fetchall():
                stats["recent_memories"].append({
                    "memory_id": row[0],
                    "agent_id": row[1],
                    "type": row[2],
                    "timestamp": row[3]
                })
            
            # Log the statistics
            logger.info(f"📊 DB STATS: {stats['total_memories']} total memories")
            logger.info(f"📊 DB STATS: Memory types: {stats['memory_types']}")
            logger.info(f"📊 DB STATS: Agent counts: {stats['agent_counts']}")
            logger.info(f"📊 DB STATS: Recent memories: {[m['memory_id'] for m in stats['recent_memories']]}")
            
            print(f"📊 [STATS] Database contains {stats['total_memories']} total memories")
            print(f"📊 [STATS] Memory types: {stats['memory_types']}")
            print(f"📊 [STATS] Agent counts: {stats['agent_counts']}")
            print(f"📊 [STATS] Recent memories: {[m['memory_id'] for m in stats['recent_memories']]}")
            
        except Exception as e:
            logger.error(f"❌ DB STATS ERROR: {str(e)}")
            print(f"❌ [STATS] Error getting database statistics: {str(e)}")
        
        return stats
