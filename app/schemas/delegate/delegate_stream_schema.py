from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class DelegateStreamResponse(BaseModel):
    """
    Response model for the Delegate Stream endpoint.
    Contains the streaming delegation result and associated metadata.
    """
    stream_id: str
    status: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
