from pydantic import BaseModel
from typing import List, Dict, Any
from app.utils.status import ResultStatus # Assuming status is in utils

class ArchitectPlanResult(BaseModel):
    suggested_components: List[str]
    tool_scaffold_plan: List[Dict[str, Any]]
    memory_update: Dict[str, Any]
    status: ResultStatus
    error_message: str | None = None

