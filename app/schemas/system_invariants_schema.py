from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Any, Literal

class InvariantParameters(BaseModel):
    threshold_value: float | None = None
    comparison_operator: Literal["<", "<=", ">", ">=", "==", "!="] | None = None
    memory_surface_path: str | None = None
    expected_value: Any | None = None

class SystemInvariant(BaseModel):
    invariant_id: str = Field(..., description="A unique identifier for the invariant.")
    description: str = Field(..., description="A human-readable description of the invariant.")
    condition_type: Literal["trust_score_threshold", "budget_limit", "specific_memory_value"] = Field(..., description="The type of condition this invariant represents.")
    parameters: InvariantParameters = Field(..., description="Parameters specific to the condition_type.")
    severity: Literal["critical", "warning", "info"] = Field(..., description="Severity of violating this invariant.")
    enforcement_action: Literal["halt_loop_operator_review", "log_warning", "log_info"] = Field(..., description="Action to take if the invariant is violated.")

class SystemInvariantsList(RootModel[List[SystemInvariant]]):
    """A list of system invariants."""
    pass

