from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: phase3.0_sprint1_core_cognitive_handler_activation
class MemoryAddRequest(BaseModel):
    """
    Request model for the Memory Add endpoint.
    Contains the key and value to be stored in memory.
    """
    key: str
    value: Any
    metadata: Optional[Dict[str, Any]] = None

class MemoryAddResponse(BaseModel):
    """
    Response model for the Memory Add endpoint.
    Contains the generated memory_id and status information.
    """
    memory_id: str
    status: str
    key: str
    metadata: Optional[Dict[str, Any]] = None
