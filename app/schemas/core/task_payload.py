# app/schemas/core/task_payload.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BaseTaskPayload(BaseModel):
    """Base schema for task payloads passed between agents."""
    project_id: Optional[str] = Field(None, description="Unique identifier for the project")
    loop_id: Optional[str] = Field(None, description="Unique identifier for the current loop")
    step_index: Optional[int] = Field(None, description="Current step index within the loop")
    task_type: Optional[str] = Field(None, description="Type of task being performed")
    instructions: Optional[str] = Field(None, description="Specific instructions for the task")
    context_history: Optional[list] = Field(default_factory=list, description="History of context or previous steps")
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Any other relevant data")

    class Config:
        extra = "allow" # Allow extra fields not explicitly defined

