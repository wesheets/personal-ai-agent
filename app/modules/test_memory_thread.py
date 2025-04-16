# /app/modules/test_memory_thread.py

import unittest
import json
import sys
import os
from datetime import datetime
from fastapi.testclient import TestClient

# Add the parent directory to sys.path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the memory_thread module
from app.modules.memory_thread import router, clear_all_threads

# Create a test client
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestMemoryThread(unittest.TestCase):
    """
    Test cases for the memory_thread module.
    """
    
    def setUp(self):
        """Set up test environment by clearing all threads."""
        clear_all_threads()
    
    def test_add_memory_thread(self):
        """Test adding a memory entry to a thread."""
        # Create a test memory entry
        memory_entry = {
            "project_id": "test_project",
            "chain_id": "test_chain",
            "agent": "hal",
            "role": "thinker",
            "content": "Test content",
            "step_type": "task"
        }
        
        # Send POST request to add the memory entry
        response = client.post("/memory/thread", json=memory_entry)
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["status"], "added")
        self.assertEqual(response_data["thread_length"], 1)
        
        # Add another entry to the same thread
        memory_entry2 = {
            "project_id": "test_project",
            "chain_id": "test_chain",
            "agent": "nova",
            "role": "designer",
            "content": "Test UI design",
            "step_type": "ui"
        }
        
        # Send POST request to add the second memory entry
        response = client.post("/memory/thread", json=memory_entry2)
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["status"], "added")
        self.assertEqual(response_data["thread_length"], 2)
    
    def test_get_memory_thread(self):
        """Test retrieving a memory thread."""
        # Create and add test memory entries
        memory_entries = [
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "hal",
                "role": "thinker",
                "content": "Test content 1",
                "step_type": "task",
                "timestamp": "2025-04-14T15:00:00Z"
            },
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "ash",
                "role": "explainer",
                "content": "Test content 2",
                "step_type": "summary",
                "timestamp": "2025-04-14T15:05:00Z"
            }
        ]
        
        # Add entries to the thread
        for entry in memory_entries:
            client.post("/memory/thread", json=entry)
        
        # Send GET request to retrieve the thread
        response = client.get("/memory/thread/test_project/test_chain")
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        thread_data = response.json()
        self.assertEqual(len(thread_data), 2)
        self.assertEqual(thread_data[0]["content"], "Test content 1")
        self.assertEqual(thread_data[1]["content"], "Test content 2")
    
    def test_get_nonexistent_thread(self):
        """Test retrieving a thread that doesn't exist."""
        # Send GET request for a nonexistent thread
        response = client.get("/memory/thread/nonexistent/nonexistent")
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        thread_data = response.json()
        self.assertEqual(thread_data, [])
    
    def test_add_memory_thread_missing_fields(self):
        """Test adding a memory entry with missing required fields."""
        # Create an incomplete memory entry
        incomplete_entry = {
            "project_id": "test_project",
            "chain_id": "test_chain",
            "agent": "hal"
            # Missing role, content, and step_type
        }
        
        # Send POST request with incomplete entry
        response = client.post("/memory/thread", json=incomplete_entry)
        
        # Check response status code and error message
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field", response.json()["detail"])
    
    def test_add_memory_thread_invalid_agent(self):
        """Test adding a memory entry with an invalid agent value."""
        # Create a memory entry with invalid agent
        invalid_entry = {
            "project_id": "test_project",
            "chain_id": "test_chain",
            "agent": "invalid_agent",
            "role": "thinker",
            "content": "Test content",
            "step_type": "task"
        }
        
        # Send POST request with invalid entry
        response = client.post("/memory/thread", json=invalid_entry)
        
        # Check response status code and error message
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid agent value", response.json()["detail"])
    
    def test_add_memory_thread_invalid_step_type(self):
        """Test adding a memory entry with an invalid step_type value."""
        # Create a memory entry with invalid step_type
        invalid_entry = {
            "project_id": "test_project",
            "chain_id": "test_chain",
            "agent": "hal",
            "role": "thinker",
            "content": "Test content",
            "step_type": "invalid_step_type"
        }
        
        # Send POST request with invalid entry
        response = client.post("/memory/thread", json=invalid_entry)
        
        # Check response status code and error message
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid step_type value", response.json()["detail"])
    
    def test_add_memory_thread_with_timestamp(self):
        """Test adding a memory entry with a provided timestamp."""
        # Create a memory entry with timestamp
        memory_entry = {
            "project_id": "test_project",
            "chain_id": "test_chain",
            "agent": "hal",
            "role": "thinker",
            "content": "Test content",
            "step_type": "task",
            "timestamp": "2025-04-14T15:00:00Z"
        }
        
        # Send POST request to add the memory entry
        response = client.post("/memory/thread", json=memory_entry)
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Retrieve the thread and check the timestamp
        response = client.get("/memory/thread/test_project/test_chain")
        thread_data = response.json()
        self.assertEqual(thread_data[0]["timestamp"], "2025-04-14T15:00:00Z")
    
    def test_multiple_threads(self):
        """Test creating and retrieving multiple threads."""
        # Create entries for two different threads
        thread1_entry = {
            "project_id": "project1",
            "chain_id": "chain1",
            "agent": "hal",
            "role": "thinker",
            "content": "Thread 1 content",
            "step_type": "task"
        }
        
        thread2_entry = {
            "project_id": "project2",
            "chain_id": "chain2",
            "agent": "ash",
            "role": "explainer",
            "content": "Thread 2 content",
            "step_type": "summary"
        }
        
        # Add entries to their respective threads
        client.post("/memory/thread", json=thread1_entry)
        client.post("/memory/thread", json=thread2_entry)
        
        # Retrieve and check thread 1
        response1 = client.get("/memory/thread/project1/chain1")
        thread1_data = response1.json()
        self.assertEqual(len(thread1_data), 1)
        self.assertEqual(thread1_data[0]["content"], "Thread 1 content")
        
        # Retrieve and check thread 2
        response2 = client.get("/memory/thread/project2/chain2")
        thread2_data = response2.json()
        self.assertEqual(len(thread2_data), 1)
        self.assertEqual(thread2_data[0]["content"], "Thread 2 content")


if __name__ == "__main__":
    unittest.main()
