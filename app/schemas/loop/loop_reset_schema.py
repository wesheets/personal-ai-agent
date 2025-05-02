from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: phase3.0_sprint1.1_integration_cleanup
class LoopResetRequest(BaseModel):
    """
    Request model for the Loop Reset endpoint.
    Contains parameters for resetting the agent loop.
    """
    loop_id: Optional[str] = None
    reset_options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class LoopResetResponse(BaseModel):
    """
    Response model for the Loop Reset endpoint.
    Contains the result of resetting the agent loop.
    """
    status: str
    loop_id: Optional[str] = None
    message: Optional[str] = None
    reset_timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
