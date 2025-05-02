"""
PESSIMIST Agent Schema Definitions

This module defines the schemas for PESSIMIST agent requests and responses.
The PESSIMIST agent is responsible for detecting bias, tracking bias tags over time,
and identifying bias echo patterns in loop summaries.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BiasTagDetail(BaseModel):
    """
    Schema for detailed information about a bias tag.
    """
    tag: str = Field(..., description="Bias tag identifier")
    description: str = Field(..., description="Description of the bias")
    severity: float = Field(
        ..., 
        description="Severity score of the bias (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    occurrences: int = Field(
        ..., 
        description="Number of times this bias has been detected",
        ge=1
    )
    first_detected: str = Field(..., description="ISO timestamp of first detection")
    last_detected: str = Field(..., description="ISO timestamp of last detection")


class PessimistCheckRequest(BaseModel):
    """
    Schema for PESSIMIST agent check request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop being analyzed")
    summary: str = Field(..., description="Loop summary text to analyze for bias")
    tools: Optional[List[str]] = Field(
        default=["analyze_bias", "detect_echo", "track_bias"],
        description="List of tools to use for the pessimist check"
    )


class PessimistAssessment(BaseModel):
    """
    Schema for PESSIMIST agent assessment results.
    """
    realism_score: float = Field(
        ..., 
        description="Overall realism score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    tone_balance: str = Field(
        ..., 
        description="Assessment of tone balance (balanced, slightly_biased, biased, heavily_biased)"
    )
    blind_spots: List[str] = Field(
        default=[],
        description="List of potential blind spots in the analysis"
    )
    warnings: List[str] = Field(
        default=[],
        description="List of warnings about bias issues"
    )


class BiasAnalysis(BaseModel):
    """
    Schema for detailed bias analysis results.
    """
    loop_id: str = Field(..., description="Unique identifier for the analyzed loop")
    realism_score: float = Field(
        ..., 
        description="Overall realism score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    tone_balance: str = Field(
        ..., 
        description="Assessment of tone balance"
    )
    bias_tags: List[str] = Field(
        default=[],
        description="List of bias tags detected"
    )
    bias_tags_detail: List[BiasTagDetail] = Field(
        default=[],
        description="Detailed information about detected bias tags"
    )
    bias_echo: bool = Field(
        ..., 
        description="Whether bias echo was detected"
    )
    echo_tags: List[str] = Field(
        default=[],
        description="List of bias tags that show echo patterns"
    )
    repetition_counts: Dict[str, int] = Field(
        default={},
        description="Count of repetitions for each bias tag"
    )
    action: Optional[str] = Field(
        None,
        description="Recommended action based on bias analysis"
    )
    warnings: List[str] = Field(
        default=[],
        description="List of warnings about bias issues"
    )


class PessimistCheckResult(BaseModel):
    """
    Schema for PESSIMIST agent check result.
    """
    assessment: PessimistAssessment = Field(
        ..., 
        description="Overall assessment of the loop summary"
    )
    bias_analysis: BiasAnalysis = Field(
        ..., 
        description="Detailed bias analysis results"
    )
    loop_id: str = Field(
        ..., 
        description="Unique identifier for the analyzed loop"
    )
    status: str = Field(
        ..., 
        description="Status of the check (success or error)"
    )
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the check"
    )
    message: Optional[str] = Field(
        None, 
        description="Error message if status is error"
    )


class PessimistErrorResult(BaseModel):
    """
    Schema for PESSIMIST agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    loop_id: Optional[str] = Field(None, description="Loop identifier if applicable")
    tools: Optional[List[str]] = Field(None, description="Tools used")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
