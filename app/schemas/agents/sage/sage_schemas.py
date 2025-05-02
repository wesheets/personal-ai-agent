from typing import List, Literal, Optional

from app.schemas.core.agent_result import AgentResult, ResultStatus
from app.schemas.core.task_payload import BaseTaskPayload


class SageReflectionRequest(BaseTaskPayload):
    """Input schema for the Sage agent."""
    loop_id: str
    project_id: str
    source_agent: Literal["orchestrator", "forge", "hal", "nova"]
    output_summary: Optional[str] = None
    operator_persona: Optional[Literal["light", "medium", "deep"]] = "medium"


class SageReflectionResult(AgentResult):
    """Output schema for the Sage agent."""
    passed: bool
    tone_summary: Optional[str] = None
    philosophical_notes: Optional[str] = None
    improvement_suggestions: Optional[List[str]] = []
    reflection_id: Optional[str] = None

