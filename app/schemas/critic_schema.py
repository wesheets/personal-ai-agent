"""
CRITIC Agent Schema Definitions

This module defines the schemas for CRITIC agent requests and responses.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class CriticReviewRequest(BaseModel):
    """
    Schema for CRITIC agent review request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop being reviewed")
    agent_outputs: Dict[str, str] = Field(
        ..., 
        description="Dictionary mapping agent IDs to their outputs"
    )
    project_id: str = Field(..., description="Project identifier")
    tools: Optional[List[str]] = Field(
        default=["review", "reject", "log_reason"],
        description="List of tools to use for the review"
    )


class CriticScores(BaseModel):
    """
    Schema for CRITIC agent evaluation scores.
    """
    technical_accuracy: int = Field(
        ..., 
        description="Score for technical accuracy (0-10)",
        ge=0,
        le=10
    )
    ux_clarity: int = Field(
        ..., 
        description="Score for UX clarity (0-10)",
        ge=0,
        le=10
    )
    visual_design: int = Field(
        ..., 
        description="Score for visual design (0-10)",
        ge=0,
        le=10
    )
    monetization_strategy: int = Field(
        ..., 
        description="Score for monetization strategy (0-10)",
        ge=0,
        le=10
    )


class CriticUsage(BaseModel):
    """
    Schema for API usage metrics.
    """
    prompt_tokens: int = Field(..., description="Number of prompt tokens used")
    completion_tokens: int = Field(..., description="Number of completion tokens used")
    total_tokens: int = Field(..., description="Total number of tokens used")


class CriticReviewResult(BaseModel):
    """
    Schema for CRITIC agent review result.
    """
    status: str = Field(..., description="Status of the review (success or error)")
    loop_id: str = Field(..., description="Unique identifier for the reviewed loop")
    reflection: Optional[str] = Field(None, description="Overall analysis and suggestions for improvement")
    scores: Optional[CriticScores] = Field(None, description="Evaluation scores for different criteria")
    rejection: Optional[bool] = Field(False, description="Whether the output is rejected")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if rejected")
    usage: Optional[CriticUsage] = Field(None, description="API usage metrics")
    timestamp: Optional[float] = Field(None, description="Timestamp of the review")
    message: Optional[str] = Field(None, description="Error message if status is error")
    raw_response: Optional[str] = Field(None, description="Raw response if parsing failed")


class CriticRejectRequest(BaseModel):
    """
    Schema for CRITIC agent rejection request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop being rejected")
    reason: str = Field(..., description="Reason for rejection")
    project_id: str = Field(..., description="Project identifier")
    tools: Optional[List[str]] = Field(
        default=["review", "reject", "log_reason"],
        description="List of tools to use for the rejection"
    )


class CriticRejectResult(BaseModel):
    """
    Schema for CRITIC agent rejection result.
    """
    status: str = Field(..., description="Status of the rejection (success or error)")
    loop_id: str = Field(..., description="Unique identifier for the rejected loop")
    rejection: bool = Field(True, description="Whether the output is rejected")
    rejection_reason: str = Field(..., description="Reason for rejection")
    timestamp: Optional[float] = Field(None, description="Timestamp of the rejection")
    message: Optional[str] = Field(None, description="Error message if status is error")


class CriticLogReasonRequest(BaseModel):
    """
    Schema for CRITIC agent log reason request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    reason_type: str = Field(
        ..., 
        description="Type of reason (e.g., 'improvement', 'concern', 'praise')"
    )
    reason_text: str = Field(..., description="Detailed explanation")
    project_id: str = Field(..., description="Project identifier")
    tools: Optional[List[str]] = Field(
        default=["review", "reject", "log_reason"],
        description="List of tools to use for logging the reason"
    )


class CriticLogReasonResult(BaseModel):
    """
    Schema for CRITIC agent log reason result.
    """
    status: str = Field(..., description="Status of the log operation (success or error)")
    loop_id: str = Field(..., description="Unique identifier for the loop")
    reason_type: str = Field(..., description="Type of reason")
    reason_text: str = Field(..., description="Detailed explanation")
    timestamp: Optional[float] = Field(None, description="Timestamp of the log operation")
    message: Optional[str] = Field(None, description="Error message if status is error")


# Fallback schema for handling errors
class CriticErrorResult(BaseModel):
    """
    Schema for CRITIC agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    task: Optional[str] = Field(None, description="Original task")
    tools: Optional[List[str]] = Field(None, description="Tools used")
    project_id: Optional[str] = Field(None, description="Project identifier")
    loop_id: Optional[str] = Field(None, description="Loop identifier if applicable")


class LoopSummaryReviewRequest(BaseModel):
    """
    Schema for CRITIC loop summary review request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop being reviewed")
    output_tag: str = Field(..., description="Memory tag where the agent output is stored")
    agent: str = Field(..., description="Identifier of the agent whose output is being reviewed")
    schema_hash: Optional[str] = Field(None, description="Optional schema hash for validation")


class LoopReflectionRejection(BaseModel):
    """
    Schema for CRITIC loop reflection rejection.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    status: str = Field("rejected", description="Status of the reflection (rejected)")
    reason: str = Field(..., description="Reason for rejection")
    recommendation: Optional[str] = Field(None, description="Recommended recovery step")
    timestamp: datetime = Field(..., description="Timestamp of the rejection")


class LoopReflectionApproval(BaseModel):
    """
    Schema for CRITIC loop reflection approval.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    status: str = Field("approved", description="Status of the reflection (approved)")
    message: str = Field(..., description="Approval message")
    timestamp: datetime = Field(..., description="Timestamp of the approval")

