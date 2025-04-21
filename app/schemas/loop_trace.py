"""
Loop Trace Schema Module

This module defines the schema models for loop trace operations in the application.

Includes:
- LoopTraceItem model for individual loop trace entries
- LoopReflectionResult model for reflection results
- LoopCompleteRequest model for loop completion signals
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LoopStatus(str, Enum):
    """Enum defining the possible statuses of a loop."""
    pending = "pending"
    running = "running"
    completed = "completed"
    finalized = "finalized"
    failed = "failed"

class LoopTraceItem(BaseModel):
    """
    Model for a loop trace item.
    
    Represents a single entry in the loop trace log, containing information
    about the loop execution, status, and any rerun information.
    """
    loop_id: str
    status: LoopStatus
    timestamp: str
    summary: Optional[str] = None
    
    # Fields for recursion tracking
    rerun_of: Optional[str] = None
    rerun_reason: Optional[str] = None
    rerun_depth: Optional[int] = Field(default=0, description="Number of reruns deep, 0 for original runs")
    
    # Fields for rerun limit enforcement
    rerun_count: Optional[int] = Field(default=0, description="Total number of times this loop has been rerun")
    max_reruns: Optional[int] = Field(default=3, description="Maximum number of reruns allowed for this loop")
    force_finalize: Optional[bool] = Field(default=False, description="Whether to force finalization regardless of other factors")
    
    # Fields for bias echo detection
    bias_echo: Optional[bool] = Field(default=False, description="Whether the same bias tags have been flagged repeatedly")
    bias_repetition_count: Optional[Dict[str, int]] = Field(default_factory=dict, description="Count of each bias tag repetition")
    bias_trigger: Optional[str] = Field(default=None, description="Component that triggered the bias echo detection")
    
    # Fields for reflection fatigue scoring
    reflection_fatigue: Optional[float] = Field(default=0.0, description="Fatigue score from 0.0 to 1.0")
    fatigue_override: Optional[bool] = Field(default=False, description="Whether fatigue has been manually overridden")
    
    # Fields for rerun reasoning
    rerun_trigger: Optional[List[str]] = Field(default_factory=list, description="Components that triggered the rerun")
    rerun_reason_detail: Optional[str] = Field(default=None, description="Detailed reason for the rerun")
    overridden_by: Optional[str] = Field(default=None, description="Who overrode the rerun decision, if applicable")
    
    # Fields for reflection results
    alignment_score: Optional[float] = None
    drift_score: Optional[float] = None
    summary_valid: Optional[bool] = None
    belief_conflict_flags: Optional[List[str]] = None
    
    # Fields for persona tracking
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Active persona during loop execution")
    persona_switch_reason: Optional[str] = Field(default="default", description="Reason for persona selection")
    reflection_persona: Optional[str] = None

class LoopReflectionResult(BaseModel):
    """
    Model for loop reflection results.
    
    Contains the aggregated results from all reflection agents,
    including alignment score, drift score, and validity assessment.
    """
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Alignment score between 0 and 1")
    drift_score: float = Field(..., ge=0.0, le=1.0, description="Drift score between 0 and 1")
    summary_valid: bool
    belief_conflict_flags: Optional[List[str]] = None
    agent_results: Optional[Dict[str, Any]] = None
    reflection_persona: Optional[str] = Field(default="SAGE", description="Persona used for reflection")
    
    # Fields for bias echo detection
    bias_tags: Optional[List[str]] = Field(default_factory=list, description="Bias tags identified in this reflection")
    bias_echo: Optional[bool] = Field(default=False, description="Whether bias echo was detected")
    
    # Fields for reflection fatigue
    reflection_fatigue: Optional[float] = Field(default=0.0, description="Current fatigue score")
    fatigue_increased: Optional[bool] = Field(default=False, description="Whether fatigue increased in this reflection")
    
    # Fields for rerun reasoning
    rerun_trigger: Optional[List[str]] = Field(default_factory=list, description="Components that triggered the rerun")
    rerun_reason_detail: Optional[str] = Field(default=None, description="Detailed reason for the rerun")

class LoopCompleteRequest(BaseModel):
    """
    Model for loop completion request.
    
    Used to signal that a loop execution is complete and ready for reflection.
    """
    loop_id: str
    reflection_status: str = Field(..., description="Must be 'done' to trigger reflection")
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Persona to use for reflection")
    
    # Fields for manual override
    override_fatigue: Optional[bool] = Field(default=False, description="Whether to override fatigue-based finalization")
    override_max_reruns: Optional[bool] = Field(default=False, description="Whether to override max reruns limit")
    override_reason: Optional[str] = Field(default=None, description="Reason for the override")
    override_by: Optional[str] = Field(default=None, description="Who performed the override")

class RerunDecision(BaseModel):
    """
    Model for rerun decision result.
    
    Contains the decision on whether to rerun a loop and related information.
    """
    decision: str = Field(..., description="Either 'rerun' or 'finalize'")
    loop_id: Optional[str] = None
    original_loop_id: Optional[str] = None
    new_loop_id: Optional[str] = None
    rerun_reason: Optional[str] = None
    rerun_number: Optional[int] = None
    reason: Optional[str] = None
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Persona to use for rerun")
    
    # Fields for guardrails
    rerun_limit_reached: Optional[bool] = Field(default=False, description="Whether the rerun limit was reached")
    bias_echo_detected: Optional[bool] = Field(default=False, description="Whether bias echo was detected")
    fatigue_threshold_exceeded: Optional[bool] = Field(default=False, description="Whether fatigue threshold was exceeded")
    force_finalized: Optional[bool] = Field(default=False, description="Whether finalization was forced")
    
    # Fields for rerun reasoning
    rerun_trigger: Optional[List[str]] = Field(default_factory=list, description="Components that triggered the rerun")
    rerun_reason_detail: Optional[str] = Field(default=None, description="Detailed reason for the rerun")
    overridden_by: Optional[str] = Field(default=None, description="Who overrode the rerun decision, if applicable")

class BiasTag(BaseModel):
    """
    Model for a bias tag.
    
    Represents a specific type of bias identified by the pessimist agent.
    """
    tag: str = Field(..., description="The bias tag identifier")
    description: str = Field(..., description="Description of the bias")
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity of the bias from 0.0 to 1.0")
    occurrences: int = Field(default=1, description="Number of times this bias has been detected")
    first_detected: Optional[str] = Field(default=None, description="Timestamp when this bias was first detected")
    last_detected: Optional[str] = Field(default=None, description="Timestamp when this bias was last detected")
    loops_affected: Optional[List[str]] = Field(default_factory=list, description="List of loop IDs where this bias was detected")
