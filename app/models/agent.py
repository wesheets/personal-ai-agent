from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TaskModel(BaseModel):
    id: str
    goal_id: Optional[str] = None
    description: str
    category: Optional[str] = None

class DelegateRequestModel(BaseModel):
    target_agent: str
    task: TaskModel
