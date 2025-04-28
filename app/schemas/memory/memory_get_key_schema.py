from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# memory_tag: phase3.0_sprint1.1_integration_cleanup
class MemoryGetKeyResponse(BaseModel):
    """
    Response model for the Memory Get endpoint.
    Contains the retrieved value for the specified key.
    """
    key: str
    value: Any
    memory_id: str
    status: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
