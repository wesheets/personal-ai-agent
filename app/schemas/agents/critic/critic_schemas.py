from typing import List, Literal, Optional, Dict

from app.schemas.core.agent_result import AgentResult, ResultStatus
from app.schemas.core.task_payload import BaseTaskPayload


class CriticReviewRequest(BaseTaskPayload):
    """Input schema for the Critic agent."""
    source_agent: Literal["forge", "hal", "nova"]
    loop_id: str
    output_payload: Dict  # Raw result from agent
    task_type: Optional[str] = None  # "build", "ui", "research"
    project_id: Optional[str] = None


class CriticReviewResult(AgentResult):
    """Output schema for the Critic agent."""
    passed: bool
    review_notes: List[str] = []
    issues_detected: Optional[List[str]] = []
    reroute_recommended: Optional[str] = None  # e.g., "forge", "nova"
    reflection_id: Optional[str] = None

