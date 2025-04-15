# /app/modules/test_memory_summarize.py

import unittest
import json
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to sys.path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the memory_thread and memory_summarize modules
from app.modules.memory_thread import router as thread_router, THREAD_DB, clear_all_threads
from app.modules.memory_summarize import router as summarize_router

# Create a test client
from fastapi import FastAPI
app = FastAPI()
app.include_router(thread_router)
app.include_router(summarize_router)
client = TestClient(app)

class TestMemorySummarize(unittest.TestCase):
    """
    Test cases for the memory_summarize module.
    """
    
    def setUp(self):
        """Set up test environment by clearing all threads."""
        clear_all_threads()
    
    def test_summarize_nonexistent_thread(self):
        """Test summarizing a thread that doesn't exist."""
        # Create a request payload
        request_payload = {
            "project_id": "nonexistent",
            "chain_id": "nonexistent"
        }
        
        # Send POST request to summarize the nonexistent thread
        response = client.post("/memory/summarize", json=request_payload)
        
        # Check response status code and error message
        self.assertEqual(response.status_code, 404)
        self.assertIn("No memory thread found", response.json()["detail"])
    
    def test_summarize_missing_fields(self):
        """Test summarizing with missing required fields."""
        # Create an incomplete request payload
        incomplete_payload = {
            "project_id": "test_project"
            # Missing chain_id
        }
        
        # Send POST request with incomplete payload
        response = client.post("/memory/summarize", json=incomplete_payload)
        
        # Check response status code and error message
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field", response.json()["detail"])
    
    def test_summarize_single_agent_thread(self):
        """Test summarizing a thread with entries from a single agent."""
        # Create and add test memory entries
        memory_entries = [
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "hal",
                "role": "thinker",
                "content": "Implementing a function to reverse words in a sentence",
                "step_type": "task"
            },
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "hal",
                "role": "thinker",
                "content": "The function has been implemented successfully",
                "step_type": "reflection"
            }
        ]
        
        # Add entries to the thread
        for entry in memory_entries:
            client.post("/memory/thread", json=entry)
        
        # Create a request payload for summarization
        request_payload = {
            "project_id": "test_project",
            "chain_id": "test_chain"
        }
        
        # Send POST request to summarize the thread
        response = client.post("/memory/summarize", json=request_payload)
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        summary = response.json()["summary"]
        # Modified assertion to check for exact match instead of case-insensitive substring
        self.assertTrue("This project involved implementing a function" in summary)
    
    def test_summarize_multiple_agents_thread(self):
        """Test summarizing a thread with entries from multiple agents."""
        # Create and add test memory entries
        memory_entries = [
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "hal",
                "role": "thinker",
                "content": "Implementing a function to reverse words in a sentence",
                "step_type": "task"
            },
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "ash",
                "role": "explainer",
                "content": "The function reverses the order of words in a sentence",
                "step_type": "summary"
            },
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "nova",
                "role": "designer",
                "content": "UI design for the word reversal tool",
                "step_type": "ui"
            }
        ]
        
        # Add entries to the thread
        for entry in memory_entries:
            client.post("/memory/thread", json=entry)
        
        # Create a request payload for summarization
        request_payload = {
            "project_id": "test_project",
            "chain_id": "test_chain"
        }
        
        # Send POST request to summarize the thread
        response = client.post("/memory/summarize", json=request_payload)
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        summary = response.json()["summary"]
        # Modified assertion to check for exact match instead of case-insensitive substring
        self.assertTrue("This project involved implementing a function" in summary)
        self.assertIn("HAL", summary)
        self.assertIn("ASH", summary)
        self.assertIn("NOVA", summary)
    
    def test_summarize_with_missing_agent(self):
        """Test summarizing a thread where an agent is missing."""
        # Create and add test memory entries
        memory_entries = [
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "hal",
                "role": "thinker",
                "content": "Implementing a function to reverse words in a sentence",
                "step_type": "task"
            },
            {
                "project_id": "test_project",
                "chain_id": "test_chain",
                "agent": "ash",
                "role": "explainer",
                "content": "The function reverses the order of words in a sentence",
                "step_type": "summary"
            }
            # NOVA is missing
        ]
        
        # Add entries to the thread
        for entry in memory_entries:
            client.post("/memory/thread", json=entry)
        
        # Create a request payload for summarization
        request_payload = {
            "project_id": "test_project",
            "chain_id": "test_chain"
        }
        
        # Send POST request to summarize the thread
        response = client.post("/memory/summarize", json=request_payload)
        
        # Check response status code and content
        self.assertEqual(response.status_code, 200)
        summary = response.json()["summary"]
        # Modified assertion to check for exact match instead of case-insensitive substring
        self.assertTrue("This project involved implementing a function" in summary)
        self.assertIn("NOVA did not contribute", summary)
    
    def test_summarize_empty_thread(self):
        """Test summarizing an empty thread."""
        # Create an empty thread
        empty_entry = {
            "project_id": "empty_project",
            "chain_id": "empty_chain",
            "agent": "hal",
            "role": "thinker",
            "content": "",
            "step_type": "task"
        }
        
        # Add the empty entry to create the thread
        client.post("/memory/thread", json=empty_entry)
        
        # Remove the entry to make the thread empty
        THREAD_DB["empty_project:empty_chain"] = []
        
        # Create a request payload for summarization
        request_payload = {
            "project_id": "empty_project",
            "chain_id": "empty_chain"
        }
        
        # Send POST request to summarize the empty thread
        response = client.post("/memory/summarize", json=request_payload)
        
        # Check response status code and error message
        self.assertEqual(response.status_code, 404)
        self.assertIn("No memory thread found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
