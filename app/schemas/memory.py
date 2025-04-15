"""
Memory Schema Module

This module defines the schema models for memory-related operations in the application.

Includes:
- StepType enum for categorizing memory entries
- MemoryItem model for individual memory entries
- ThreadRequest model for batch memory operations
- SummarizationRequest model for summarization input
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class StepType(str, Enum):
    """
    Enum defining the types of steps in a memory thread.

    Expanded to include all agent chain step types to prevent 400 errors
    when agents submit memory logs from their specific roles.
    """
    task = "task"
    summary = "summary"
    reflection = "reflection"
    ui = "ui"
    plan = "plan"
    docs = "docs"

class MemoryItem(BaseModel):
    """
    Model for an individual memory item in a thread.

    Each memory item represents a single entry in a memory thread,
    containing the agent, role, content, and step type.
    """
    agent: str
    role: str
    content: str
    step_type: StepType

class ThreadRequest(BaseModel):
    """
    Model for a batch memory thread request.

    Allows submitting multiple memory items in a single request
    to improve efficiency and reduce API calls.
    """
    project_id: str
    chain_id: str
    agent_id: str
    memories: List[MemoryItem]

class SummarizationRequest(BaseModel):
    """
    Model for a memory thread summarization request.

    Includes optional agent_id with default value to prevent validation errors
    when the field is not provided.
    """
    project_id: str
    chain_id: str
    agent_id: Optional[str] = "orchestrator"
