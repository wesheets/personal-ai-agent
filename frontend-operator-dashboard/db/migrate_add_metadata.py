"""
Database Migration Script to Add Metadata Column

This script adds the metadata column to the existing memories table
in the SQLite database to support structured metadata for feedback
and reflection logs.
"""

import sqlite3
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path for SQLite database file
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "memory.db")

def migrate_database():
    """Add metadata column to memories table"""
    try:
        # Check if database file exists
        if not os.path.exists(DB_FILE):
            logger.error(f"❌ Database file not found at {DB_FILE}")
            print(f"❌ Database file not found at {DB_FILE}")
            return False
        
        # Connect to the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if metadata column already exists
        cursor.execute("PRAGMA table_info(memories)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "metadata" in column_names:
            logger.info("✅ Metadata column already exists in memories table")
            print("✅ Metadata column already exists in memories table")
            conn.close()
            return True
        
        # Add metadata column to memories table
        logger.info("🔄 Adding metadata column to memories table...")
        print("🔄 Adding metadata column to memories table...")
        
        cursor.execute("ALTER TABLE memories ADD COLUMN metadata TEXT")
        
        # Update memory_view to include metadata column
        logger.info("🔄 Updating memory_view to include metadata column...")
        print("🔄 Updating memory_view to include metadata column...")
        
        # Drop the existing view
        cursor.execute("DROP VIEW IF EXISTS memory_view")
        
        # Recreate the view with metadata column
        cursor.execute("""
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
            agent_tone,
            metadata,
            created_at
        FROM memories
        """)
        
        # Update schema version in metadata table
        cursor.execute("UPDATE metadata SET value = '1.1' WHERE key = 'schema_version'")
        
        # Commit changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(memories)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "metadata" in column_names:
            logger.info("✅ Migration successful: metadata column added to memories table")
            print("✅ Migration successful: metadata column added to memories table")
            conn.close()
            return True
        else:
            logger.error("❌ Migration failed: metadata column not found after migration")
            print("❌ Migration failed: metadata column not found after migration")
            conn.close()
            return False
        
    except Exception as e:
        logger.error(f"❌ Migration error: {str(e)}")
        print(f"❌ Migration error: {str(e)}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Database migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database migration failed")
        sys.exit(1)
