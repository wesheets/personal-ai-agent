from pydantic import BaseModel
from typing import Dict, Any

class PatchProjectStateRequest(BaseModel):
    project_id: str
    patch: Dict[str, Any]
