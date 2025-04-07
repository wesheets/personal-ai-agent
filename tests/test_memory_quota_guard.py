#!/usr/bin/env python3
"""
Test script for memory API quota guard functionality.

This script tests the memory API quota guard by simulating OpenAI API quota exhaustion
and verifying that the system gracefully handles the error and returns fallback responses.
"""

import os
import sys
import json
import logging
import unittest
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
from app.core.memory_api_quota_guard import MemoryQuotaGuard, get_quota_guard
from app.core.vector_memory import VectorMemorySystem
from openai.types.error import RateLimitError, APIError

class TestMemoryQuotaGuard(unittest.TestCase):
    """Test cases for the memory quota guard functionality."""

    def setUp(self):
        """Set up test environment."""
        self.quota_guard = MemoryQuotaGuard()
    
    def test_get_embedding_safe_success(self):
        """Test successful embedding generation."""
        # Mock the OpenAI client response
        mock_embedding = [0.1, 0.2, 0.3]
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        
        with patch.object(self.quota_guard.client.embeddings, 'create', return_value=mock_response):
            embedding, warning = self.quota_guard.get_embedding_safe("test text")
            
            self.assertEqual(embedding, mock_embedding)
            self.assertIsNone(warning)
    
    def test_get_embedding_safe_rate_limit(self):
        """Test handling of rate limit errors."""
        # Mock a rate limit error
        rate_limit_error = RateLimitError(
            message="You exceeded your current quota",
            type="insufficient_quota",
            code="rate_limit_exceeded",
            param=None,
            status_code=429
        )
        
        with patch.object(self.quota_guard.client.embeddings, 'create', side_effect=rate_limit_error):
            embedding, warning = self.quota_guard.get_embedding_safe("test text")
            
            self.assertIsNone(embedding)
            self.assertIsNotNone(warning)
            self.assertIn("quota exceeded", warning)
    
    def test_get_embedding_safe_api_error(self):
        """Test handling of general API errors."""
        # Mock an API error
        api_error = APIError(
            message="The server had an error processing your request",
            type="server_error",
            code="server_error",
            param=None,
            status_code=500
        )
        
        with patch.object(self.quota_guard.client.embeddings, 'create', side_effect=api_error):
            embedding, warning = self.quota_guard.get_embedding_safe("test text")
            
            self.assertIsNone(embedding)
            self.assertIsNotNone(warning)
            self.assertIn("API error", warning)
    
    def test_get_fallback_memories(self):
        """Test generation of fallback memories."""
        fallback_memories = self.quota_guard.get_fallback_memories(3)
        
        self.assertIsInstance(fallback_memories, list)
        self.assertLessEqual(len(fallback_memories), 3)
        self.assertGreater(len(fallback_memories), 0)
        
        # Check that the fallback memory has the required fields
        memory = fallback_memories[0]
        self.assertIn("id", memory)
        self.assertIn("content", memory)
        self.assertIn("metadata", memory)
        self.assertIn("similarity", memory)
        self.assertIn("priority", memory)
        self.assertIn("created_at", memory)
        
        # Check that the content mentions the system limitation
        self.assertIn("limited", memory["content"].lower())

class TestVectorMemorySystem(unittest.TestCase):
    """Test cases for the vector memory system with quota guard integration."""
    
    @patch('app.core.vector_memory.create_client')
    def setUp(self, mock_create_client):
        """Set up test environment with mocked Supabase client."""
        # Mock the Supabase client
        self.mock_supabase = MagicMock()
        mock_create_client.return_value = self.mock_supabase
        
        # Create a VectorMemorySystem instance
        self.vector_memory = VectorMemorySystem()
        
        # Mock the table and RPC methods
        self.mock_table = MagicMock()
        self.mock_supabase.table.return_value = self.mock_table
        self.mock_supabase.rpc = MagicMock()
    
    @patch('app.core.vector_memory.get_quota_guard')
    async def test_search_memories_with_quota_error(self, mock_get_quota_guard):
        """Test search_memories handles quota errors gracefully."""
        # Mock the quota guard
        mock_quota_guard = MagicMock()
        mock_get_quota_guard.return_value = mock_quota_guard
        
        # Set up the mock to return None for embedding and a warning
        mock_quota_guard.get_embedding_safe.return_value = (None, "OpenAI quota exceeded")
        
        # Set up fallback memories
        fallback_memories = [{"id": "test", "content": "Test memory"}]
        mock_quota_guard.get_fallback_memories.return_value = fallback_memories
        
        # Call search_memories
        memories, warning = await self.vector_memory.search_memories("test query")
        
        # Verify that fallback memories are returned with a warning
        self.assertEqual(memories, fallback_memories)
        self.assertIsNotNone(warning)
        self.assertIn("quota", warning.lower())
    
    @patch('app.core.vector_memory.get_quota_guard')
    async def test_store_memory_with_quota_error(self, mock_get_quota_guard):
        """Test store_memory handles quota errors gracefully."""
        # Mock the quota guard
        mock_quota_guard = MagicMock()
        mock_get_quota_guard.return_value = mock_quota_guard
        
        # Set up the mock to return None for embedding and a warning
        mock_quota_guard.get_embedding_safe.return_value = (None, "OpenAI quota exceeded")
        
        # Mock the insert operation
        mock_execute = MagicMock()
        mock_execute.data = [{"id": "test-id"}]
        self.mock_table.insert.return_value.execute.return_value = mock_execute
        
        # Call store_memory
        memory_id, warning = await self.vector_memory.store_memory("test content")
        
        # Verify that the memory is stored without embedding and a warning is returned
        self.assertEqual(memory_id, "test-id")
        self.assertIsNotNone(warning)
        self.assertIn("without embedding", warning.lower())
        
        # Verify that the insert was called with embedding=None
        self.mock_table.insert.assert_called_once()
        args, kwargs = self.mock_table.insert.call_args
        self.assertIsNone(kwargs.get('embedding'))

if __name__ == '__main__':
    unittest.main()
