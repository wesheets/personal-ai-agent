from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class LoopResponseRequest(BaseModel):
    """
    Request schema for HAL agent loop response.
    """
    project_id: str
    loop_id: str
    agent: str = "hal"
    input_key: str
    target_file: str
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    metadata: Optional[Dict[str, Any]] = None

class LoopResponseResult(BaseModel):
    """
    Response schema for HAL agent loop response.
    """
    status: str
    output_tag: str
    timestamp: str
    code: str
    metadata: Optional[Dict[str, Any]] = None
