from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Any, Literal
import uuid # For generating violation_id
from datetime import datetime # For timestamp

class ViolationDetails(BaseModel):
    checked_value: Any | None = Field(None, description="The actual value that was checked against the invariant.")
    invariant_condition: str | None = Field(None, description="A description of the invariant condition that was violated (e.g., 'trust_score < 0.3').")
    agent_responsible: str | None = Field(None, description="The ID of the agent whose action or output led to the violation, if applicable.")

class InvariantViolationRecord(BaseModel):
    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="A unique identifier for this violation instance.")
    loop_id: str = Field(..., description="The ID of the loop execution during which the violation occurred.")
    invariant_id_violated: str = Field(..., description="The ID of the system invariant that was violated.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The ISO 8601 timestamp of when the violation was detected.")
    details: ViolationDetails = Field(..., description="Specific details about the violation.")
    severity_of_violation: Literal["critical", "warning", "info"] = Field(..., description="The severity of the violated invariant.")
    action_taken: Literal["halt_loop_operator_review", "log_warning", "log_info", "none"] = Field(..., description="The enforcement action taken as a result of the violation.")

class InvariantViolationLog(RootModel[List[InvariantViolationRecord]]):
    """A list of invariant violation records."""
    pass

