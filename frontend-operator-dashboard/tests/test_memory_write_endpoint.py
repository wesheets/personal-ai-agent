"""
Test script for the /memory/write endpoint.

This script tests the functionality of the /memory/write endpoint, which allows
direct writing of structured memories with metadata and scope support.
"""

import unittest
import requests
import json
import os
import sys
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the memory module for direct testing
from app.api.modules.memory import write_memory, memory_store
from app.db.memory_db import memory_db

class TestMemoryWriteEndpoint(unittest.TestCase):
    """Test cases for the /memory/write endpoint."""
    
    def setUp(self):
        """Set up test environment."""
        # Base URL for API requests
        self.base_url = "http://localhost:8000"
        
        # Test data
        self.test_agent_id = "test_agent"
        self.test_user_id = "test_user_001"
        self.test_memory_type = "test_memory"
        self.test_content = "This is a test memory for the /memory/write endpoint"
        self.test_project_id = "test_project"
        self.test_task_id = f"TASK_{uuid.uuid4().hex[:8]}"
        
        # Generate a unique memory_trace_id for this test run
        self.test_memory_trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        
        # Test metadata
        self.test_metadata = {
            "task_id": self.test_task_id,
            "project_id": self.test_project_id,
            "result": "success",
            "test_run": datetime.utcnow().isoformat()
        }
    
    def test_direct_write_memory_with_metadata(self):
        """Test the write_memory function directly with metadata."""
        # Call the write_memory function directly
        memory = write_memory(
            agent_id=self.test_agent_id,
            type=self.test_memory_type,
            content=self.test_content,
            tags=["test", "direct"],
            project_id=self.test_project_id,
            task_id=self.test_task_id,
            metadata=self.test_metadata
        )
        
        # Verify the memory was created with the correct data
        self.assertIsNotNone(memory)
        self.assertIsNotNone(memory.get("memory_id"))
        self.assertEqual(memory.get("agent_id"), self.test_agent_id)
        self.assertEqual(memory.get("type"), self.test_memory_type)
        self.assertEqual(memory.get("content"), self.test_content)
        self.assertEqual(memory.get("project_id"), self.test_project_id)
        self.assertEqual(memory.get("task_id"), self.test_task_id)
        
        # Verify metadata was stored correctly
        self.assertIsNotNone(memory.get("metadata"))
        self.assertEqual(memory.get("metadata").get("task_id"), self.test_task_id)
        self.assertEqual(memory.get("metadata").get("project_id"), self.test_project_id)
        self.assertEqual(memory.get("metadata").get("result"), "success")
        
        # Store the memory_id for later retrieval test
        self.memory_id = memory.get("memory_id")
        
        print(f"✅ Successfully created memory with ID: {self.memory_id}")
    
    def test_memory_retrieval_by_id(self):
        """Test retrieving the memory by ID from the database."""
        # First create a memory to retrieve
        memory = write_memory(
            agent_id=self.test_agent_id,
            type=self.test_memory_type,
            content=f"Retrieval test memory at {datetime.utcnow().isoformat()}",
            tags=["test", "retrieval"],
            project_id=self.test_project_id,
            task_id=self.test_task_id,
            metadata=self.test_metadata
        )
        
        memory_id = memory.get("memory_id")
        
        # Retrieve the memory from the database
        retrieved_memory = memory_db.read_memory_by_id(memory_id)
        
        # Verify the memory was retrieved correctly
        self.assertIsNotNone(retrieved_memory)
        self.assertEqual(retrieved_memory.get("memory_id"), memory_id)
        self.assertEqual(retrieved_memory.get("agent_id"), self.test_agent_id)
        self.assertEqual(retrieved_memory.get("type"), self.test_memory_type)
        self.assertEqual(retrieved_memory.get("project_id"), self.test_project_id)
        
        # Verify metadata was retrieved correctly
        self.assertIsNotNone(retrieved_memory.get("metadata"))
        self.assertEqual(retrieved_memory.get("metadata").get("task_id"), self.test_task_id)
        self.assertEqual(retrieved_memory.get("metadata").get("project_id"), self.test_project_id)
        self.assertEqual(retrieved_memory.get("metadata").get("result"), "success")
        
        print(f"✅ Successfully retrieved memory with ID: {memory_id}")
    
    def test_memory_with_user_scope(self):
        """Test creating a memory with user scope."""
        # Create a memory with user_id for scoping
        memory = write_memory(
            agent_id=self.test_agent_id,
            type=self.test_memory_type,
            content=f"User-scoped memory test at {datetime.utcnow().isoformat()}",
            tags=[f"user:{self.test_user_id}"],
            project_id=self.test_project_id,
            task_id=self.test_task_id,
            metadata={
                "user_id": self.test_user_id,
                "task_id": self.test_task_id,
                "project_id": self.test_project_id
            }
        )
        
        memory_id = memory.get("memory_id")
        
        # Verify the memory was created with the correct user scope
        self.assertIsNotNone(memory)
        self.assertIn(f"user:{self.test_user_id}", memory.get("tags", []))
        
        # Retrieve memories with user scope filter
        memories = memory_db.read_memories(
            agent_id=self.test_agent_id,
            tag=f"user:{self.test_user_id}",
            limit=10
        )
        
        # Verify at least one memory was found with the user scope
        self.assertGreater(len(memories), 0)
        
        # Verify the retrieved memory has the correct user scope
        found = False
        for mem in memories:
            if mem.get("memory_id") == memory_id:
                found = True
                self.assertIn(f"user:{self.test_user_id}", mem.get("tags", []))
                break
        
        self.assertTrue(found, f"Memory with ID {memory_id} not found in user-scoped results")
        
        print(f"✅ Successfully created and retrieved user-scoped memory")
    
    def test_memory_with_session_and_trace(self):
        """Test creating a memory with session_id and memory_trace_id."""
        # Create a unique session_id for this test
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create a memory with session_id and memory_trace_id
        memory = write_memory(
            agent_id=self.test_agent_id,
            type=self.test_memory_type,
            content=f"Session and trace test at {datetime.utcnow().isoformat()}",
            tags=["test", "session", "trace"],
            project_id=self.test_project_id,
            task_id=self.test_task_id,
            memory_trace_id=self.test_memory_trace_id,
            metadata={
                "session_id": session_id,
                "memory_trace_id": self.test_memory_trace_id
            }
        )
        
        memory_id = memory.get("memory_id")
        
        # Verify the memory was created with the correct session and trace data
        self.assertIsNotNone(memory)
        self.assertEqual(memory.get("memory_trace_id"), self.test_memory_trace_id)
        self.assertEqual(memory.get("metadata").get("session_id"), session_id)
        
        print(f"✅ Successfully created memory with session and trace IDs")

if __name__ == "__main__":
    unittest.main()
