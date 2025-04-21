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

class LoopCompleteRequest(BaseModel):
    """
    Model for loop completion request.
    
    Used to signal that a loop execution is complete and ready for reflection.
    """
    loop_id: str
    reflection_status: str = Field(..., description="Must be 'done' to trigger reflection")
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Persona to use for reflection")

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
