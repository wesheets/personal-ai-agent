"""
Execute Schema Module

This module defines the schema for execute operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class ExecuteRequest(BaseModel):
    """
    Schema for execute request.
    """
    goal: str = Field(..., description="The goal of the execution")
    domain: str = Field(default="saas", description="The domain of the execution")
    details: Optional[str] = Field(None, description="Additional details for the execution")
    theme: Optional[str] = Field(None, description="Theme for the UI design")

# memory_tag: stubbed_phase2.5
class ExecuteResponse(BaseModel):
    """
    Schema for execute response.
    """
    project_id: str = Field(..., description="The project identifier")
    chain_id: str = Field(..., description="The chain identifier")
    hal_plan: Dict[str, Any] = Field(..., description="The HAL plan")
    ash_docs: Dict[str, Any] = Field(..., description="The ASH documentation")
    nova_ui: Dict[str, Any] = Field(..., description="The NOVA UI design")
    critic_review: Dict[str, Any] = Field(..., description="The CRITIC review")
    status: str = Field(..., description="Status of the execution operation")
