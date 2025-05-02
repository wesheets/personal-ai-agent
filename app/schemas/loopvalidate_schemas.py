# Minimal stub for loop validation schemas
from pydantic import BaseModel
from typing import Dict, Any, Optional

class LoopValidateRequest(BaseModel):
    loop_id: str
    loop_data: Dict[str, Any]
    mode: Optional[str] = None
    complexity: Optional[float] = None
    sensitivity: Optional[float] = None
    time_constraint: Optional[float] = None
    user_preference: Optional[str] = None

class LoopValidateResponse(BaseModel):
    status: str
    loop_id: str
    mode: str
    validation_result: Dict[str, Any]
    prepared_loop: Dict[str, Any]
    processed_by: str

