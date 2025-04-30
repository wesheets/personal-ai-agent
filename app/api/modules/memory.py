"""
Memory module for reading and writing memory entries
"""
import logging
import datetime
from typing import Dict, Any, List, Optional

import os
import json
import traceback

# Configure logging
logger = logging.getLogger("app.api.modules.memory")
logging.basicConfig(level=logging.INFO) # Basic config, adjust as needed

async def write_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write a memory entry to the memory system by appending to a JSON Lines file.
    
    Args:
        memory_data: Dictionary containing memory entry data
            - agent_id: The agent identifier (used for logging context)
            - type: The memory entry type (determines target file: 'loop_trace' or 'reflection_thread')
            - content: The memory entry content (the actual data to log)
            - tags: Optional list of tags
            
    Returns:
        Dict containing status and memory entry details
    """
    log_dir = "/home/ubuntu/personal-ai-agent/logs"
    memory_type = memory_data.get("type")
    agent_id = memory_data.get("agent_id", "unknown_agent")
    content_to_log = memory_data.get("content", {})
    tags = memory_data.get("tags", [])
    timestamp = datetime.datetime.now().isoformat()

    # Validation as per directive
    if not memory_type or not isinstance(content_to_log, dict):
        logger.error(f"Invalid memory_data for agent {agent_id}: Missing type or content is not a dict.")
        return {
            "status": "error",
            "message": "Invalid memory_data: Missing type or content is not a dict.",
            "timestamp": timestamp
        }

    if memory_type == "loop_trace":
        log_file = os.path.join(log_dir, "loop_trace.json")
        required_keys = ["loop_id", "plan", "agent_output", "tool_used"]
    elif memory_type == "reflection_thread":
        log_file = os.path.join(log_dir, "reflection_thread.json")
        required_keys = ["loop_id", "agent", "text"]
    else:
        logger.error(f"Unknown memory_type '{memory_type}' for agent {agent_id}. Cannot log.")
        return {
            "status": "error",
            "message": f"Unknown memory_type: {memory_type}",
            "timestamp": timestamp
        }

    # Check for required keys in content_to_log
    missing_keys = [key for key in required_keys if key not in content_to_log]
    if missing_keys:
        logger.error(f"Invalid content for memory_type '{memory_type}' for agent {agent_id}: Missing required keys: {missing_keys}")
        return {
            "status": "error",
            "message": f"Invalid content for memory_type '{memory_type}': Missing required keys: {missing_keys}",
            "timestamp": timestamp
        }

    # Construct the final log entry, ensuring timestamp is present
    log_entry = {
        "timestamp": timestamp,
        "agent_id": agent_id, # Log the agent_id passed in memory_data
        "type": memory_type,
        "tags": tags,
        **content_to_log # Spread the actual content dictionary
    }

    try:
        # Ensure log directory exists (already created, but good practice)
        os.makedirs(log_dir, exist_ok=True)

        logger.info(f"Attempting to write memory type '{memory_type}' for agent {agent_id} to {log_file}")
        with open(log_file, "a") as f:
            json.dump(log_entry, f)
            f.write("\n") # Write each entry as a new line (JSON Lines format)
        
        logger.info(f"✅ Successfully wrote memory type '{memory_type}' for agent {agent_id} to {log_file}")
        return {
            "status": "success",
            "message": "Memory write successful to file.",
            "written": True,
            "file": log_file,
            "timestamp": timestamp
        }

    except Exception as e:
        logger.error(f"❌ Error writing memory type '{memory_type}' for agent {agent_id} to {log_file}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Failed to write memory to file: {str(e)}",
            "timestamp": timestamp
        }

# Add a basic read_memory function if needed elsewhere, or keep it minimal
async def read_memory(agent_id: str, memory_type: str = "loop", tag: Optional[str] = None) -> Dict[str, Any]:
    logger.warning(f"read_memory called for {agent_id}, type {memory_type}. Returning mock data.")
    return {
        "agent_id": agent_id,
        "type": memory_type,
        "tag": tag,
        "content": f"Mock read memory content for {agent_id}",
        "timestamp": datetime.datetime.now().isoformat()
    }

