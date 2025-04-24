"""
SAGE Agent Schema Definitions

This module defines the schemas for SAGE agent requests and responses.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class BeliefScore(BaseModel):
    """
    Schema for a belief score entry.
    """
    belief: str = Field(..., description="The belief statement")
    confidence: float = Field(
        ..., 
        description="Confidence score for the belief (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    emotional_weight: Optional[float] = Field(
        None, 
        description="Emotional weight of the belief (-1.0 to 1.0)",
        ge=-1.0,
        le=1.0
    )


class SageReviewRequest(BaseModel):
    """
    Schema for SAGE agent review request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    summary_text: str = Field(..., description="Summary text to analyze for beliefs")
    project_id: str = Field(..., description="Project identifier")
    tools: Optional[List[str]] = Field(
        default=["reflect", "summarize", "score_belief"],
        description="List of tools to use for the analysis"
    )


class SageReviewResult(BaseModel):
    """
    Schema for SAGE agent review result.
    """
    status: str = Field(..., description="Status of the review (success or error)")
    loop_id: str = Field(..., description="Unique identifier for the reviewed loop")
    belief_scores: Optional[List[BeliefScore]] = Field(
        None, 
        description="List of extracted beliefs with confidence and emotional weight"
    )
    reflection_text: Optional[str] = Field(
        None, 
        description="Generated reflection based on the beliefs"
    )
    timestamp: Optional[str] = Field(None, description="ISO format timestamp of the review")
    message: Optional[str] = Field(None, description="Error message if status is error")


class SageSummarizeRequest(BaseModel):
    """
    Schema for SAGE agent summarize request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    content: str = Field(..., description="Content to summarize")
    project_id: str = Field(..., description="Project identifier")
    tools: Optional[List[str]] = Field(
        default=["reflect", "summarize", "score_belief"],
        description="List of tools to use for summarization"
    )


class SageSummarizeResult(BaseModel):
    """
    Schema for SAGE agent summarize result.
    """
    status: str = Field(..., description="Status of the summarization (success or error)")
    loop_id: str = Field(..., description="Unique identifier for the loop")
    summary: Optional[str] = Field(None, description="Generated summary")
    original_word_count: Optional[int] = Field(None, description="Word count of original content")
    summary_word_count: Optional[int] = Field(None, description="Word count of summary")
    compression_ratio: Optional[float] = Field(None, description="Ratio of summary to original length")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp of the summarization")
    message: Optional[str] = Field(None, description="Error message if status is error")


class SageScoreBeliefRequest(BaseModel):
    """
    Schema for SAGE agent score belief request.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    belief: str = Field(..., description="Belief statement to score")
    project_id: str = Field(..., description="Project identifier")
    tools: Optional[List[str]] = Field(
        default=["reflect", "summarize", "score_belief"],
        description="List of tools to use for belief scoring"
    )


class SageScoreBeliefResult(BaseModel):
    """
    Schema for SAGE agent score belief result.
    """
    status: str = Field(..., description="Status of the scoring (success or error)")
    loop_id: str = Field(..., description="Unique identifier for the loop")
    belief: Optional[str] = Field(None, description="The belief statement")
    confidence: Optional[float] = Field(
        None, 
        description="Confidence score for the belief (0.0-1.0)"
    )
    emotional_weight: Optional[float] = Field(
        None, 
        description="Emotional weight of the belief (-1.0 to 1.0)"
    )
    timestamp: Optional[str] = Field(None, description="ISO format timestamp of the scoring")
    message: Optional[str] = Field(None, description="Error message if status is error")


# Fallback schema for handling errors
class SageErrorResult(BaseModel):
    """
    Schema for SAGE agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    task: Optional[str] = Field(None, description="Original task")
    tools: Optional[List[str]] = Field(None, description="Tools used")
    project_id: Optional[str] = Field(None, description="Project identifier")
    loop_id: Optional[str] = Field(None, description="Loop identifier if applicable")
