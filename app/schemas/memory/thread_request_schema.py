from pydantic import BaseModel
from typing import Optional, List
from .step_type_enum import StepType

class ThreadRequest(BaseModel):
    thread_id: str
    step_type: StepType
    input_data: Optional[dict] = None
    agent_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = []
