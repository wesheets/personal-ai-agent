"""
Memory Engine Module

This module provides the memory engine initialization and access functions.
It is designed to be initialized only when needed, avoiding top-level runtime logic.
"""
import logging
import datetime
import os
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger("app.api.modules.memory_engine")

# Ensure logs directory exists
os.makedirs("/home/ubuntu/personal-ai-agent/logs", exist_ok=True)

class MemoryEngine:
    """
    Memory Engine class for handling memory operations.
    """
    def __init__(self, mock_mode: bool = False):
        """
        Initialize the memory engine.
        
        Args:
            mock_mode: Whether to use mock mode for local development
        """
        self.mock_mode = mock_mode
        self.initialized = False
        self.initialization_error = None
        
        try:
            # Simulate engine initialization
            self._initialize_engine()
            self.initialized = True
            logger.info("Memory engine initialized successfully")
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"Failed to initialize memory engine: {str(e)}")
            self._log_fallback_activation(f"Initialization error: {str(e)}")
    
    def _initialize_engine(self):
        """
        Initialize the memory engine components.
        This is a placeholder for actual initialization logic.
        """
        # In a real implementation, this would initialize database connections,
        # vector stores, etc. For now, it's just a placeholder.
        if self.mock_mode:
            logger.info("Initializing memory engine in MOCK_MODE")
        else:
            logger.info("Initializing memory engine in PRODUCTION mode")
    
    async def read_memory(self, agent_id: str, memory_type: str = "loop", tag: Optional[str] = None) -> Dict[str, Any]:
        """
        Read memory entries for a specific agent and type.
        
        Args:
            agent_id: The agent identifier
            memory_type: The type of memory to read
            tag: Optional tag to filter memory entries
            
        Returns:
            Dict containing memory entry data
        """
        if not self.initialized and not self.mock_mode:
            logger.warning("Memory engine not initialized, using fallback mode")
            self._log_fallback_activation("Read operation with uninitialized engine")
            return self._fallback_read(agent_id, memory_type, tag)
        
        try:
            logger.info(f"Reading memory for agent: {agent_id}, type: {memory_type}, tag: {tag}")
            
            # In a real implementation, this would read from a database
            # For now, return mock data
            memory_content = f"Example {memory_type} memory content for {tag or 'general'} task"
            
            if tag == "build_task":
                memory_content = "scaffold InsightLoop SaaS frontend with dashboard, user management, and analytics"
            
            return {
                "agent_id": agent_id,
                "type": memory_type,
                "tag": tag,
                "content": memory_content,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error reading memory: {str(e)}")
            self._log_fallback_activation(f"Read error: {str(e)}")
            return self._fallback_read(agent_id, memory_type, tag)
    
    async def write_memory(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a memory entry to the memory system.
        
        Args:
            memory_data: Dictionary containing memory entry data
                - agent_id: The agent identifier
                - type: The memory entry type
                - content: The memory entry content
                - tags: Optional list of tags
                
        Returns:
            Dict containing status and memory entry details
        """
        if not self.initialized and not self.mock_mode:
            logger.warning("Memory engine not initialized, using fallback mode")
            self._log_fallback_activation("Write operation with uninitialized engine")
            return self._fallback_write(memory_data)
        
        try:
            logger.info(f"Writing memory for agent: {memory_data.get('agent_id', 'unknown')}")
            
            # In a real implementation, this would write to a database
            # For now, just return a success response
            return {
                "status": "success",
                "message": "Memory write successful",
                "content": memory_data.get("content", ""),
                "agent_id": memory_data.get("agent_id", "unknown"),
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error writing memory: {str(e)}")
            self._log_fallback_activation(f"Write error: {str(e)}")
            return self._fallback_write(memory_data)
    
    def _fallback_read(self, agent_id: str, memory_type: str, tag: Optional[str]) -> Dict[str, Any]:
        """
        Fallback read operation when the primary read fails.
        
        Args:
            agent_id: The agent identifier
            memory_type: The type of memory to read
            tag: Optional tag to filter memory entries
            
        Returns:
            Dict containing fallback memory entry data
        """
        logger.info(f"Using fallback read for agent: {agent_id}, type: {memory_type}")
        
        return {
            "status": "degraded",
            "message": "Using fallback memory read",
            "agent_id": agent_id,
            "type": memory_type,
            "tag": tag,
            "content": f"Fallback {memory_type} content for {agent_id}",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _fallback_write(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback write operation when the primary write fails.
        
        Args:
            memory_data: Dictionary containing memory entry data
            
        Returns:
            Dict containing fallback status
        """
        logger.info(f"Using fallback write for agent: {memory_data.get('agent_id', 'unknown')}")
        
        return {
            "status": "degraded",
            "message": "Using fallback memory write",
            "content": memory_data.get("content", ""),
            "agent_id": memory_data.get("agent_id", "unknown"),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _log_fallback_activation(self, reason: str):
        """
        Log the activation of the memory fallback mechanism.
        
        Args:
            reason: The reason for fallback activation
        """
        import json
        import os
        
        log_file = "/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"
        
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "event": "fallback_activated",
                "reason": reason,
                "mock_mode": self.mock_mode
            }
            
            # Check if log file exists
            if os.path.exists(log_file):
                # Read existing logs
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    # If file exists but is not valid JSON, start with empty list
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info("Memory fallback activation logged successfully")
        except Exception as e:
            logger.error(f"Error logging memory fallback activation: {str(e)}")


# Function to get memory engine instance
def get_memory_engine() -> MemoryEngine:
    """
    Get a memory engine instance.
    
    Returns:
        MemoryEngine: A memory engine instance
    """
    # Check if MOCK_MODE environment variable is set
    mock_mode = os.environ.get("MOCK_MODE", "false").lower() == "true"
    
    # Create and return a new engine instance
    return MemoryEngine(mock_mode=mock_mode)
