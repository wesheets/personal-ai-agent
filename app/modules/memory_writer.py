"""
Memory Writer Module

This module provides functionality for writing memory entries.
It is primarily used by agents to log their actions and thoughts.
"""

import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.modules.memory_writer")

def write_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write a memory entry.
    
    Args:
        memory_data: Dictionary containing memory data with keys:
            - agent: The agent identifier (e.g., "hal")
            - project_id: The project identifier
            - action: Description of the action performed
            - tool_used: The tool used for the action
            - additional keys as needed
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Generate a unique memory ID
        memory_id = str(uuid.uuid4())
        
        # Add timestamp and memory_id to the data
        memory_entry = {
            "memory_id": memory_id,
            "timestamp": datetime.utcnow().isoformat(),
            **memory_data
        }
        
        # Log the memory entry
        logger.info(f"Memory entry created: {memory_id}")
        print(f"✅ Memory entry created: {memory_id}")
        
        # In a real implementation, this would store to a database
        # For now, we'll write to a JSON file for demonstration
        memory_file = os.path.join(os.path.dirname(__file__), "memory_store.json")
        
        # Read existing memories
        memories = []
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    memories = json.load(f)
            except json.JSONDecodeError:
                memories = []
        
        # Add new memory
        memories.append(memory_entry)
        
        # Write updated memories
        with open(memory_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        return {
            "status": "success",
            "memory_id": memory_id,
            "message": f"Memory entry created: {memory_id}"
        }
    except Exception as e:
        error_msg = f"Error creating memory entry: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "error": str(e)
        }
