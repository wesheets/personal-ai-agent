"""
Memory Writer Module with Block Information

This module extends the memory_writer functionality to include block information
when agents are blocked due to dependencies or other conditions.
"""
import logging
import json
import os
import time
import uuid
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.modules.memory_block_writer")

# Import memory_writer for logging agent actions
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    print("❌ memory_writer import failed")

def write_block_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write memory with block information.
    
    Args:
        memory_data: Dictionary containing memory data with block information
            Required fields:
            - project_id: The project identifier
            - agent: The agent identifier
            - action: The action performed (usually "blocked")
            - content: The content of the memory
            Optional block-specific fields:
            - blocked_due_to: The dependency that caused the block
            - unblock_condition: The condition that would unblock the agent
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        if not MEMORY_WRITER_AVAILABLE:
            error_msg = "Memory writer not available, cannot write block memory"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error": "Memory writer not available"
            }
        
        # Validate required fields
        required_fields = ["project_id", "agent", "action", "content"]
        for field in required_fields:
            if field not in memory_data:
                error_msg = f"Missing required field: {field}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "error": f"Missing required field: {field}"
                }
        
        # Add block information if available
        block_info = {}
        if "blocked_due_to" in memory_data:
            block_info["blocked_due_to"] = memory_data["blocked_due_to"]
        
        if "unblock_condition" in memory_data:
            block_info["unblock_condition"] = memory_data["unblock_condition"]
        
        # Add timestamp for block
        if block_info:
            block_info["blocked_at"] = time.time()
            
            # Add block information to structured_data
            if "structured_data" not in memory_data:
                memory_data["structured_data"] = {}
            
            memory_data["structured_data"]["block_info"] = block_info
        
        # Write memory
        result = write_memory(memory_data)
        
        if result.get("status") == "success":
            logger.info(f"Block memory written for agent {memory_data['agent']} in project {memory_data['project_id']}")
            print(f"📝 Block memory written for agent {memory_data['agent']} in project {memory_data['project_id']}")
        else:
            logger.error(f"Error writing block memory: {result.get('error', 'unknown error')}")
            print(f"❌ Error writing block memory: {result.get('error', 'unknown error')}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error writing block memory: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "error": str(e)
        }

def write_unblock_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write memory with unblock information.
    
    Args:
        memory_data: Dictionary containing memory data with unblock information
            Required fields:
            - project_id: The project identifier
            - agent: The agent identifier
            - action: The action performed (usually "unblocked")
            - content: The content of the memory
            Optional unblock-specific fields:
            - previously_blocked_due_to: The dependency that caused the previous block
            - unblock_reason: The reason the agent was unblocked
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        if not MEMORY_WRITER_AVAILABLE:
            error_msg = "Memory writer not available, cannot write unblock memory"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error": "Memory writer not available"
            }
        
        # Validate required fields
        required_fields = ["project_id", "agent", "action", "content"]
        for field in required_fields:
            if field not in memory_data:
                error_msg = f"Missing required field: {field}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "error": f"Missing required field: {field}"
                }
        
        # Add unblock information if available
        unblock_info = {}
        if "previously_blocked_due_to" in memory_data:
            unblock_info["previously_blocked_due_to"] = memory_data["previously_blocked_due_to"]
        
        if "unblock_reason" in memory_data:
            unblock_info["unblock_reason"] = memory_data["unblock_reason"]
        
        # Add timestamp for unblock
        if unblock_info:
            unblock_info["unblocked_at"] = time.time()
            
            # Add unblock information to structured_data
            if "structured_data" not in memory_data:
                memory_data["structured_data"] = {}
            
            memory_data["structured_data"]["unblock_info"] = unblock_info
        
        # Write memory
        result = write_memory(memory_data)
        
        if result.get("status") == "success":
            logger.info(f"Unblock memory written for agent {memory_data['agent']} in project {memory_data['project_id']}")
            print(f"📝 Unblock memory written for agent {memory_data['agent']} in project {memory_data['project_id']}")
        else:
            logger.error(f"Error writing unblock memory: {result.get('error', 'unknown error')}")
            print(f"❌ Error writing unblock memory: {result.get('error', 'unknown error')}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error writing unblock memory: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "error": str(e)
        }
