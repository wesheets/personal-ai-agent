"""
Drift Summary Schema Module

This module defines the schema for drift summary operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class DriftSummaryRequest(BaseModel):
    """
    Schema for drift summary request.
    """
    loop_id: str = Field(..., description="The loop identifier")
    orchestrator_persona: Optional[str] = Field(None, description="The orchestrator persona")

# memory_tag: stubbed_phase2.5
class DriftSummaryResponse(BaseModel):
    """
    Schema for drift summary response.
    """
    summary: Dict[str, Any] = Field(..., description="The drift summary details")
    loop_id: str = Field(..., description="The loop identifier")
    reflection_persona: str = Field(..., description="The reflection persona")
    status: str = Field(..., description="Status of the drift summary operation")
