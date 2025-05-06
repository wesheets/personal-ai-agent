from typing import List, Literal, Optional, Dict
from pydantic import BaseModel

from app.schemas.core.agent_result import ResultStatus # Keep ResultStatus if needed
from app.schemas.core.task_payload import BaseTaskPayload


class CriticReviewRequest(BaseTaskPayload):
    """Input schema for the Critic agent."""
    source_agent: Literal["forge", "hal", "nova", "architect"] # Added architect
    loop_id: str
    output_payload: Dict  # Raw result from agent
    task_type: Optional[str] = None  # "build", "ui", "research"
    project_id: Optional[str] = None


# Restore original name, inherit from BaseModel for now
class CriticReviewResult(BaseModel): 
    """Output schema for the Critic agent (fully restored)."""
    task_id: str 
    status: ResultStatus # Add status back
    passed: bool # Add passed back
    review_notes: List[str] = [] # Add review_notes back
    issues_detected: Optional[List[str]] = [] # Add issues_detected back
    reroute_recommended: Optional[str] = None # Add reroute_recommended back
    reflection_id: Optional[str] = None # Add reflection_id back


