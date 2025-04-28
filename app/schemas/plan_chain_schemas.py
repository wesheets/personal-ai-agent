"""
Plan Chain Schemas Module

This module defines the schemas for plan chaining operations.

# memory_tag: phase3.0_sprint4_cognitive_reflection_plan_chaining
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class PlanStep(BaseModel):
    """Schema for a single step in a plan chain."""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int = Field(...)
    description: str = Field(...)
    expected_outcome: str = Field(...)
    dependencies: List[str] = Field(default_factory=list)
    estimated_duration: Optional[str] = Field(None)
    resources_required: Optional[List[str]] = Field(None)


class PlanChainRequest(BaseModel):
    """Schema for plan chain generation requests."""
    reflection_id: str = Field(...)
    goal_summary: Optional[str] = Field(None)
    max_steps: Optional[int] = Field(10)
    include_dependencies: Optional[bool] = Field(True)


class PlanChainResponse(BaseModel):
    """Schema for plan chain generation responses."""
    chain_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reflection_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    goal_summary: Optional[str] = Field(None)
    steps: List[PlanStep] = Field(...)
    total_steps: int = Field(...)
    estimated_total_duration: Optional[str] = Field(None)
