from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class DelegateResponse(BaseModel):
    """
    Response model for the Agent Delegate endpoint.
    Contains the delegation result and associated metadata.
    """
    result: str
    status: str
    task_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
