"""
Analyze Prompt Schema Module

This module defines the schema for prompt analysis operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class AnalyzePromptRequest(BaseModel):
    """
    Schema for analyze prompt request.
    """
    prompt: str = Field(..., description="The prompt text to analyze")
    context: Optional[str] = Field(None, description="Additional context for the analysis")
    analysis_type: Optional[str] = Field("standard", description="Type of analysis to perform")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class AnalyzePromptResponse(BaseModel):
    """
    Schema for analyze prompt response.
    """
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    prompt: str = Field(..., description="The analyzed prompt text")
    structure: Dict[str, Any] = Field(..., description="Structure analysis of the prompt")
    suggestions: List[str] = Field(default=[], description="Suggestions for prompt improvement")
    sentiment: Optional[Dict[str, float]] = Field(None, description="Sentiment analysis results")
    complexity: Optional[Dict[str, Any]] = Field(None, description="Complexity analysis results")
    status: str = Field(..., description="Status of the operation")
