"""
Memory Schema Module

This module defines the schemas for memory-related operations in the application.
It includes the StepType enum and request/response models for memory operations.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class StepType(str, Enum):
    """Enum for different types of memory steps."""
    task = "task"
    summary = "summary"
    reflection = "reflection"
    ui = "ui"
    plan = "plan"
    docs = "docs"

class MemoryItem(BaseModel):
    """Model for a single memory item."""
    agent: str
    role: str
    content: str
    step_type: StepType

class ThreadRequest(BaseModel):
    """Model for a memory thread request with multiple memory items."""
    project_id: str
    chain_id: str
    agent_id: str
    memories: List[MemoryItem]

class SummarizationRequest(BaseModel):
    """Model for a memory summarization request."""
    project_id: str
    chain_id: str
    agent_id: Optional[str] = "orchestrator"
