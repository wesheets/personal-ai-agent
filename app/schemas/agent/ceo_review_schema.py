"""
CEO Review Schema Module

This module defines the schema for CEO review operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class CEOReviewRequest(BaseModel):
    """
    Schema for CEO review request.
    """
    summary: str = Field(..., description="The summary to review")
    loop_id: str = Field(..., description="The loop identifier")
    orchestrator_persona: Optional[str] = Field(None, description="The orchestrator persona")

# memory_tag: stubbed_phase2.5
class CEOReviewResponse(BaseModel):
    """
    Schema for CEO review response.
    """
    review: Dict[str, Any] = Field(..., description="The review details")
    loop_id: str = Field(..., description="The loop identifier")
    reflection_persona: str = Field(..., description="The reflection persona")
    status: str = Field(..., description="Status of the review operation")
