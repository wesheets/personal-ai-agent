from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: phase3.0_sprint1_core_cognitive_handler_activation
class LoopCreateRequest(BaseModel):
    """
    Request model for the Loop Create endpoint.
    Contains the plan ID and loop type to create a simple loop record.
    """
    plan_id: str
    loop_type: str
    metadata: Optional[Dict[str, Any]] = None

class LoopCreateResponse(BaseModel):
    """
    Response model for the Loop Create endpoint.
    Contains the generated loop_id and status information.
    """
    loop_id: str
    plan_id: str
    loop_type: str
    status: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
