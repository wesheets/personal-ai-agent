"""
Memory API Quota Guard

This module provides a fail-safe mechanism for handling OpenAI API quota exhaustion
in the memory embedding system. It wraps the embedding API calls in try/except blocks
to catch rate limit errors and other API failures, providing graceful degradation
instead of crashing the application.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import openai
from openai import OpenAI
from openai import APIError, RateLimitError

# Configure logging
logger = logging.getLogger("memory_failsafe")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Track quota failures to avoid excessive logging
_last_quota_error_time = 0
_quota_error_window = 300  # 5 minutes between repeated error logs

class MemoryQuotaGuard:
    """
    A wrapper for OpenAI embedding operations that provides fail-safe handling
    of quota exhaustion and other API errors.
    """
    
    def __init__(self):
        """Initialize the quota guard with OpenAI client"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-ada-002"
    
    def get_embedding_safe(self, text: str) -> Tuple[Optional[List[float]], Optional[str]]:
        """
        Safely get embedding for text using OpenAI's embedding API with error handling
        
        Args:
            text: The text to get embedding for
            
        Returns:
            Tuple of (embedding vector or None, warning message or None)
        """
        global _last_quota_error_time
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding, None
            
        except RateLimitError as e:
            # Handle quota exhaustion
            current_time = time.time()
            if current_time - _last_quota_error_time > _quota_error_window:
                logger.warning(f"[MEMORY FAILSAFE] OpenAI quota exceeded: {e}")
                _last_quota_error_time = current_time
            
            return None, "OpenAI quota exceeded. Memory results limited."
            
        except APIError as e:
            # Handle other OpenAI API errors
            if e.status_code == 429:  # Another way quota might be reported
                current_time = time.time()
                if current_time - _last_quota_error_time > _quota_error_window:
                    logger.warning(f"[MEMORY FAILSAFE] OpenAI API rate limit (429): {e}")
                    _last_quota_error_time = current_time
                
                return None, "OpenAI quota exceeded. Memory results limited."
            else:
                logger.error(f"[MEMORY FAILSAFE] OpenAI API error: {e}")
                return None, f"OpenAI API error: {e.status_code}"
                
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f"[MEMORY FAILSAFE] Unknown embedding failure: {e}")
            return None, "Memory unavailable due to backend error."

    def get_fallback_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Provide fallback memory results when embedding fails
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of fallback memory items
        """
        # Create a simple fallback response with empty or mock memories
        fallback_memories = []
        
        # Add a system note as the first "memory"
        fallback_memories.append({
            "id": "system-note-1",
            "content": "Memory search is currently limited due to backend constraints.",
            "metadata": {"type": "system_note", "source": "failsafe"},
            "similarity": 1.0,
            "priority": True,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })
        
        # Return the fallback memories, limited to requested size
        return fallback_memories[:limit]

# Create a singleton instance
_quota_guard_instance = None

def get_quota_guard() -> MemoryQuotaGuard:
    """
    Get the singleton instance of MemoryQuotaGuard
    
    Returns:
        The MemoryQuotaGuard instance
    """
    global _quota_guard_instance
    if _quota_guard_instance is None:
        _quota_guard_instance = MemoryQuotaGuard()
    return _quota_guard_instance
