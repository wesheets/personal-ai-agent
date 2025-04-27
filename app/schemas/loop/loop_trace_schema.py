from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class LoopTraceQuery(BaseModel):
    """
    Request model for the Loop Trace endpoint.
    Contains query parameters for retrieving loop trace information.
    """
    loop_id: Optional[str] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    include_metadata: Optional[bool] = False
