"""
Test cases for memory thread logging and summarization endpoint fixes.

This module contains tests to verify:
1. Memory thread logging in agent_runner.py
2. Memory summarization endpoint with optional agent_id
"""

import unittest
import json
import uuid
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.modules.memory_thread import THREAD_DB, clear_all_threads
from app.modules.agent_runner import log_memory_thread, run_agent

# Create test client
client = TestClient(app)

class TestMemoryThreadLogging(unittest.TestCase):
    """Test cases for memory thread logging functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Clear all threads before each test
        clear_all_threads()
        
        # Generate unique project_id and chain_id for each test
        self.project_id = f"test_project_{uuid.uuid4().hex[:8]}"
        self.chain_id = f"test_chain_{uuid.uuid4().hex[:8]}"
    
    def test_log_memory_thread_hal(self):
        """Test logging memory thread for HAL agent."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Log memory thread for HAL agent
            loop.run_until_complete(log_memory_thread(
                project_id=self.project_id,
                chain_id=self.chain_id,
                agent="hal",
                role="thinker",
                step_type="task",
                content="Test HAL task content"
            ))
            
            # Verify thread was created
            thread_key = f"{self.project_id}:{self.chain_id}"
            self.assertIn(thread_key, THREAD_DB)
            
            # Verify entry was added
            self.assertEqual(len(THREAD_DB[thread_key]), 1)
            
            # Verify entry content
            entry = THREAD_DB[thread_key][0]
            self.assertEqual(entry["agent"], "hal")
            self.assertEqual(entry["role"], "thinker")
            self.assertEqual(entry["step_type"], "task")
            self.assertEqual(entry["content"], "Test HAL task content")
        finally:
            loop.close()
    
    def test_log_memory_thread_ash(self):
        """Test logging memory thread for ASH agent."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Log memory thread for ASH agent
            loop.run_until_complete(log_memory_thread(
                project_id=self.project_id,
                chain_id=self.chain_id,
                agent="ash",
                role="explainer",
                step_type="summary",
                content="Test ASH summary content"
            ))
            
            # Verify thread was created
            thread_key = f"{self.project_id}:{self.chain_id}"
            self.assertIn(thread_key, THREAD_DB)
            
            # Verify entry was added
            self.assertEqual(len(THREAD_DB[thread_key]), 1)
            
            # Verify entry content
            entry = THREAD_DB[thread_key][0]
            self.assertEqual(entry["agent"], "ash")
            self.assertEqual(entry["role"], "explainer")
            self.assertEqual(entry["step_type"], "summary")
            self.assertEqual(entry["content"], "Test ASH summary content")
        finally:
            loop.close()
    
    def test_log_memory_thread_nova(self):
        """Test logging memory thread for NOVA agent."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Log memory thread for NOVA agent
            loop.run_until_complete(log_memory_thread(
                project_id=self.project_id,
                chain_id=self.chain_id,
                agent="nova",
                role="designer",
                step_type="ui",
                content="Test NOVA UI content"
            ))
            
            # Verify thread was created
            thread_key = f"{self.project_id}:{self.chain_id}"
            self.assertIn(thread_key, THREAD_DB)
            
            # Verify entry was added
            self.assertEqual(len(THREAD_DB[thread_key]), 1)
            
            # Verify entry content
            entry = THREAD_DB[thread_key][0]
            self.assertEqual(entry["agent"], "nova")
            self.assertEqual(entry["role"], "designer")
            self.assertEqual(entry["step_type"], "ui")
            self.assertEqual(entry["content"], "Test NOVA UI content")
        finally:
            loop.close()
    
    def test_run_agent_logs_memory(self):
        """Test that run_agent logs memory thread entries."""
        # Mock messages
        messages = [
            {"role": "user", "content": "Test message"}
        ]
        
        # Run agent with specified project_id and chain_id
        result = run_agent(
            agent_id="hal",
            messages=messages,
            project_id=self.project_id,
            chain_id=self.chain_id
        )
        
        # Verify thread was created
        thread_key = f"{self.project_id}:{self.chain_id}"
        self.assertIn(thread_key, THREAD_DB)
        
        # Verify entry was added (may be more than one if there are error logs)
        self.assertGreaterEqual(len(THREAD_DB[thread_key]), 1)
        
        # Verify at least one entry has the correct agent
        has_hal_entry = False
        for entry in THREAD_DB[thread_key]:
            if entry["agent"] == "hal":
                has_hal_entry = True
                break
        
        self.assertTrue(has_hal_entry)

class TestMemorySummarizeEndpoint(unittest.TestCase):
    """Test cases for memory summarize endpoint."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Clear all threads before each test
        clear_all_threads()
        
        # Generate unique project_id and chain_id for each test
        self.project_id = f"test_project_{uuid.uuid4().hex[:8]}"
        self.chain_id = f"test_chain_{uuid.uuid4().hex[:8]}"
        
        # Add test entries to thread
        self.thread_key = f"{self.project_id}:{self.chain_id}"
        THREAD_DB[self.thread_key] = [
            {
                "project_id": self.project_id,
                "chain_id": self.chain_id,
                "agent": "hal",
                "role": "thinker",
                "step_type": "task",
                "content": "HAL task content",
                "timestamp": "2025-04-15T01:00:00Z"
            },
            {
                "project_id": self.project_id,
                "chain_id": self.chain_id,
                "agent": "ash",
                "role": "explainer",
                "step_type": "summary",
                "content": "ASH summary content",
                "timestamp": "2025-04-15T01:01:00Z"
            },
            {
                "project_id": self.project_id,
                "chain_id": self.chain_id,
                "agent": "nova",
                "role": "designer",
                "step_type": "ui",
                "content": "NOVA UI content",
                "timestamp": "2025-04-15T01:02:00Z"
            }
        ]
    
    def test_summarize_with_agent_id(self):
        """Test summarize endpoint with agent_id provided."""
        # Create request with agent_id
        request_data = {
            "project_id": self.project_id,
            "chain_id": self.chain_id,
            "agent_id": "test_agent"
        }
        
        # Call summarize endpoint
        response = client.post("/memory/summarize", json=request_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = response.json()
        
        # Verify agent_id is included in response
        self.assertEqual(response_data["agent_id"], "test_agent")
        
        # Verify summary is generated
        self.assertIn("summary", response_data)
        self.assertIsInstance(response_data["summary"], str)
        self.assertGreater(len(response_data["summary"]), 0)
    
    def test_summarize_without_agent_id(self):
        """Test summarize endpoint without agent_id (should use default)."""
        # Create request without agent_id
        request_data = {
            "project_id": self.project_id,
            "chain_id": self.chain_id
        }
        
        # Call summarize endpoint
        response = client.post("/memory/summarize", json=request_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = response.json()
        
        # Verify default agent_id is used
        self.assertEqual(response_data["agent_id"], "orchestrator")
        
        # Verify summary is generated
        self.assertIn("summary", response_data)
        self.assertIsInstance(response_data["summary"], str)
        self.assertGreater(len(response_data["summary"]), 0)
    
    def test_summarize_nonexistent_thread(self):
        """Test summarize endpoint with nonexistent thread."""
        # Create request with nonexistent thread
        request_data = {
            "project_id": "nonexistent_project",
            "chain_id": "nonexistent_chain"
        }
        
        # Call summarize endpoint
        response = client.post("/memory/summarize", json=request_data)
        
        # Verify response (should be 404)
        self.assertEqual(response.status_code, 404)
        
        # Parse response
        response_data = response.json()
        
        # Verify error detail
        self.assertIn("detail", response_data)
        self.assertIn("No memory thread found", response_data["detail"])

if __name__ == "__main__":
    unittest.main()
