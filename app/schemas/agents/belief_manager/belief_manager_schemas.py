# Placeholder for Belief Manager Agent Schemas
from pydantic import BaseModel, Field
from typing import Any, Literal
import uuid
from datetime import datetime

class BeliefManagerInput(BaseModel):
    target_belief_key: str = Field(..., description="The key of the belief to propose changing.")
    proposed_change_type: Literal["added", "modified", "removed"] = Field(..., description="Type of change proposed.")
    proposed_value: Any | None = Field(None, description="The proposed new value (for added/modified).")
    justification: str = Field(..., description="Reason for the proposed change.")

class BeliefChangeProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this proposal.")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO 8601 timestamp when the proposal was created.")
    loop_id: str | None = Field(None, description="The loop ID during which the proposal was generated.") # Will be set by controller
    proposing_agent_id: str | None = Field(None, description="The agent ID that generated this proposal.") # Will be set by controller
    target_belief_key: str = Field(..., description="The key of the belief targeted for change in belief_surface.json.")
    proposed_change_type: Literal["added", "modified", "removed"] = Field(..., description="The type of change proposed.")
    current_value: Any | None = Field(None, description="The current value of the belief (if it exists) at the time of proposal.") # Needs to be fetched
    proposed_value: Any | None = Field(None, description="The proposed new value for the belief (required for 'added' and 'modified').")
    justification: str = Field(..., description="Textual justification explaining the reason for the proposed change.")
    status: Literal["pending_review", "approved", "rejected"] = Field(default="pending_review", description="The current status of the proposal.")
    operator_review_ref: str | None = Field(None, description="Reference to the operator review log or identifier, if applicable.")
    rejection_reason: str | None = Field(None, description="Reason provided if the proposal was rejected.")

class BeliefManagerOutput(BaseModel):
    proposal: BeliefChangeProposal = Field(..., description="The generated belief change proposal.")

