# /home/ubuntu/personal-ai-agent/app/modules/memory_writer.py

import logging
import datetime
from typing import Dict, Any, Optional, List

# Import the actual memory store configuration
from app.modules.memory_config import MEMORY_STORE
# Alias for lowercase import compatibility
memory_store = MEMORY_STORE

# Import the actual write_memory function from its new location
try:
    from app.api.modules.memory import write_memory as actual_write_memory
    ACTUAL_WRITE_MEMORY_AVAILABLE = True
except ImportError:
    logging.error("❌ Failed to import actual write_memory from app.api.modules.memory")
    ACTUAL_WRITE_MEMORY_AVAILABLE = False
    # Define a mock if the real one isn't available to prevent further import errors downstream
    async def actual_write_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
        logging.warning("⚠️ Using mock actual_write_memory due to import failure.")
        return {"status": "mock_error", "message": "Actual write_memory unavailable"}

logger = logging.getLogger(__name__)

# Compatibility layer for write_memory
async def write_memory(
    agent_id: str,
    memory_type: Optional[str] = None, # 'type' in new signature
    tag: Optional[str] = None, # Part of 'tags' in new signature
    value: Optional[Any] = None, # 'content' in new signature
    content: Optional[Any] = None, # Allow 'content' directly too
    tags: Optional[List[str]] = None, # Allow 'tags' directly
    project_id: Optional[str] = None, # Not directly used in new signature, maybe add to tags?
    status: Optional[str] = None, # Not directly used in new signature, maybe add to tags?
    task_id: Optional[str] = None, # Not directly used in new signature, maybe add to tags?
    task_type: Optional[str] = None, # Not directly used in new signature, maybe add to tags?
    target_agent_id: Optional[str] = None, # Not directly used in new signature, maybe add to tags?
    **kwargs: Any # Catch any other arguments
) -> Dict[str, Any]:
    """
    Compatibility wrapper for write_memory.
    Accepts the old signature with individual arguments and calls the
    new write_memory function (expecting a dictionary) from app.api.modules.memory.
    """
    if not ACTUAL_WRITE_MEMORY_AVAILABLE:
        logger.error("Cannot execute write_memory compatibility wrapper: Actual function unavailable.")
        return {"status": "error", "message": "Actual write_memory function failed to import."}

    logger.warning(f"⚠️ Using compatibility wrapper for write_memory call from agent {agent_id}")

    # Construct the dictionary for the new function signature
    memory_data: Dict[str, Any] = {
        "agent_id": agent_id,
        # Map old 'memory_type' or 'type' kwarg to new 'type'
        "type": memory_type or kwargs.get("type", "unknown"),
        # Map old 'value' or 'content' to new 'content'
        "content": value if value is not None else content,
        # Combine 'tag' and 'tags' into the new 'tags' list
        "tags": tags or [],
    }
    if tag:
        memory_data["tags"].append(tag)
    
    # Add other common optional fields as tags if provided
    if project_id:
        memory_data["tags"].append(f"project:{project_id}")
    if status:
        memory_data["tags"].append(f"status:{status}")
    if task_id:
        memory_data["tags"].append(f"task:{task_id}")
    if task_type:
         memory_data["tags"].append(f"task_type:{task_type}")
    if target_agent_id:
         memory_data["tags"].append(f"target_agent:{target_agent_id}")

    # Log any unexpected kwargs
    if kwargs:
        logger.warning(f"Compatibility write_memory received unexpected arguments: {kwargs}")
        # Add unexpected kwargs as tags too, prefixed
        for k, v in kwargs.items():
            if k not in ["agent_id", "memory_type", "tag", "value", "content", "tags", "project_id", "status", "task_id", "task_type", "target_agent_id"]:
                 memory_data["tags"].append(f"kwarg_{k}:{v}")

    try:
        # Call the actual write_memory function
        result = await actual_write_memory(memory_data=memory_data)
        return result
    except Exception as e:
        logger.error(f"Error calling actual_write_memory via compatibility wrapper: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to execute actual write_memory via wrapper: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

# Ensure MEMORY_STORE is still available for direct import if needed elsewhere
# (Though ideally, direct access should be minimized)
__all__ = ["write_memory", "MEMORY_STORE", "memory_store", "generate_reflection"]


# Import the actual generate_reflection function from its location
try:
    from app.modules.reflect import generate_reflection
    GENERATE_REFLECTION_AVAILABLE = True
except ImportError:
    logging.error("❌ Failed to import generate_reflection from app.modules.reflect")
    GENERATE_REFLECTION_AVAILABLE = False
    # Define a mock if the real one isn't available
    def generate_reflection(*args, **kwargs):
        logging.warning("⚠️ Using mock generate_reflection due to import failure.")
        return "Mock reflection due to import error"

