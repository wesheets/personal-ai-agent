"""
OBSERVER Agent Schema Definitions

This module defines the schemas for OBSERVER agent requests and responses.
The OBSERVER agent is responsible for journaling system behavior, tracking anomalies,
and documenting agent reflections.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ObserverTaskRequest(BaseModel):
    """
    Schema for OBSERVER agent task request.
    """
    task: str = Field(..., description="Task to perform (e.g., 'journal', 'observe')")
    date: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Date for the observation (defaults to today)"
    )
    tools: Optional[List[str]] = Field(
        default=["journal", "observe", "reflect"],
        description="List of tools to use for the observation"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task": "journal",
                "date": "2025-04-24",
                "tools": ["journal", "observe", "reflect"]
            }
        }

class ObservationEntry(BaseModel):
    """
    Schema for an observation entry.
    """
    date: str = Field(..., description="Date of the observation")
    memory_summary: str = Field(..., description="Summary of agent memory")
    behavior_observed: Optional[str] = Field(None, description="Observed system behavior")
    anomalies: Optional[str] = Field(None, description="Anomalies and failures observed")
    vertical_progress: Optional[str] = Field(None, description="Progress made in vertical capabilities")
    loops_observed: Optional[str] = Field(None, description="Loops observed in system behavior")
    personality_notes: Optional[str] = Field(None, description="Notes on system personality")
    philosophical_questions: Optional[str] = Field(None, description="Philosophical questions raised")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2025-04-24",
                "memory_summary": "System processed 5 tasks with 3 agents involved.",
                "behavior_observed": "Agents collaborated effectively on complex tasks.",
                "anomalies": "No significant anomalies detected.",
                "vertical_progress": "Improved memory retrieval capabilities.",
                "loops_observed": "One recursive loop detected in task delegation.",
                "personality_notes": "System exhibited more confident responses.",
                "philosophical_questions": "How should the system balance efficiency vs. explainability?"
            }
        }

class ObserverTaskResult(BaseModel):
    """
    Schema for OBSERVER agent task result.
    """
    status: str = Field(..., description="Status of the task (success, error)")
    message: str = Field(..., description="Message describing the result")
    task: str = Field(..., description="Task that was performed")
    date: str = Field(..., description="Date of the observation")
    entry: Optional[ObservationEntry] = Field(None, description="Observation entry if task was successful")
    log_path: Optional[str] = Field(None, description="Path to the log file if task was successful")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the task"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Daily journal appended to promethios_observations.md",
                "task": "journal",
                "date": "2025-04-24",
                "entry": {
                    "date": "2025-04-24",
                    "memory_summary": "System processed 5 tasks with 3 agents involved.",
                    "behavior_observed": "Agents collaborated effectively on complex tasks.",
                    "anomalies": "No significant anomalies detected.",
                    "vertical_progress": "Improved memory retrieval capabilities.",
                    "loops_observed": "One recursive loop detected in task delegation.",
                    "personality_notes": "System exhibited more confident responses.",
                    "philosophical_questions": "How should the system balance efficiency vs. explainability?"
                },
                "log_path": "logs/observation/promethios_observations.md",
                "timestamp": "2025-04-24T18:45:22.123456"
            }
        }

class ObserverErrorResult(BaseModel):
    """
    Schema for OBSERVER agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    task: Optional[str] = Field(None, description="Task that was attempted")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
