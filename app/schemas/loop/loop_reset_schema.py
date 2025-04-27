from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class LoopResetRequest(BaseModel):
    """
    Request model for the Loop Reset endpoint.
    Contains parameters for resetting the agent loop.
    """
    loop_id: Optional[str] = None
    reset_options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
