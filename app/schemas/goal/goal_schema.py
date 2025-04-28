"""
Goal Schema Module

This module defines the schema for goal listing operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class GoalItem(BaseModel):
    """
    Schema for a single goal item.
    """
    goal_id: str = Field(..., description="Unique identifier for the goal")
    title: str = Field(..., description="Title of the goal")
    description: Optional[str] = Field(None, description="Description of the goal")
    status: str = Field(..., description="Current status of the goal")
    priority: Optional[str] = Field(None, description="Priority level of the goal")
    created_at: str = Field(..., description="Timestamp when the goal was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the goal was last updated")
    assigned_to: Optional[str] = Field(None, description="Agent or user assigned to the goal")
    tags: List[str] = Field(default=[], description="Tags associated with the goal")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class GoalListResponse(BaseModel):
    """
    Schema for goal list response.
    """
    goals: List[GoalItem] = Field(..., description="List of goals")
    total_count: int = Field(..., description="Total number of goals")
    status: str = Field(..., description="Status of the operation")
