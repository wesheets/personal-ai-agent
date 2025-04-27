from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class MemoryAddResponse(BaseModel):
    """
    Response model for the Memory Add endpoint.
    Contains the generated memory_id and status information.
    """
    memory_id: str
    status: str
    metadata: Optional[Dict[str, Any]] = None
