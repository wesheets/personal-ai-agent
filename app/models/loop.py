"""
Loop Models Module

This module defines the data models for loop-related operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class StartLoopRequest(BaseModel):
    """
    Request model for starting a loop execution.
    """
    project_id: str = Field(..., description="The ID of the project to run the loop for")
    agent_name: Optional[str] = Field(None, description="Optional specific agent to run in the loop")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the loop execution")
