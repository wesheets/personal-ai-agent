from pydantic import BaseModel
from typing import Dict, Any, Optional

# memory_tag: stubbed_phase2.5
class BuilderResponse(BaseModel):
    """
    Response model for the Builder agent endpoint.
    Contains the generated output and associated metadata.
    """
    output: str
    metadata: Dict[str, Any]
