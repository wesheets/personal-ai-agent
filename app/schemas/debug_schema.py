"""
Debug Schema Module

This module defines the schemas for the Debug Analyzer agent, which acts as a diagnostic tool
for analyzing failed or incomplete loop executions within the Promethios architecture.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class LoopDebugRequest(BaseModel):
    """
    Schema for Loop Debug Analyzer requests.
    
    This schema defines the structure of requests to the Debug Analyzer agent for diagnosing
    failed or incomplete loop executions.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop to analyze")
    project_id: str = Field(..., description="Unique identifier for the project")
    agent_filter: Optional[List[str]] = Field(None, description="Optional list of agents to focus analysis on")
    raw_log_text: Optional[str] = Field(None, description="Optional raw log text to analyze")
    version: Optional[str] = Field("1", description="Version of the diagnosis")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_17",
                "project_id": "demo_writer_001",
                "agent_filter": ["hal", "critic"],
                "raw_log_text": None,
                "version": "1"
            }
        }

class LoopIssue(BaseModel):
    """
    Schema for individual loop issues.
    
    This schema defines the structure of identified issues in a loop execution.
    """
    issue_type: str = Field(..., description="Type of issue (e.g., 'memory_missing', 'agent_failure', 'timeout')")
    description: str = Field(..., description="Detailed description of the issue")
    severity: str = Field(..., description="Severity of the issue (critical, high, medium, low)")
    affected_agent: Optional[str] = Field(None, description="Agent affected by or responsible for the issue")
    affected_memory_tags: Optional[List[str]] = Field(None, description="Memory tags affected by the issue")
    timestamp: Optional[str] = Field(None, description="Timestamp when the issue occurred, if known")
    
    class Config:
        schema_extra = {
            "example": {
                "issue_type": "agent_failure",
                "description": "CRITIC agent failed to complete review due to missing HAL output",
                "severity": "high",
                "affected_agent": "critic",
                "affected_memory_tags": ["hal_build_task_response_loop_17"],
                "timestamp": "2025-04-24T18:30:00.000000"
            }
        }

class RepairSuggestion(BaseModel):
    """
    Schema for repair suggestions.
    
    This schema defines the structure of suggestions for repairing failed loop executions.
    """
    suggestion_type: str = Field(..., description="Type of suggestion (e.g., 'retry', 'skip_agent', 'modify_memory')")
    description: str = Field(..., description="Detailed description of the suggestion")
    priority: int = Field(..., description="Priority of the suggestion (1-5, with 1 being highest)")
    target_agent: Optional[str] = Field(None, description="Agent that should be targeted for the repair")
    required_changes: Optional[List[str]] = Field(None, description="List of changes required for the repair")
    expected_outcome: str = Field(..., description="Expected outcome if the suggestion is implemented")
    
    class Config:
        schema_extra = {
            "example": {
                "suggestion_type": "retry",
                "description": "Retry CRITIC agent with modified input parameters",
                "priority": 1,
                "target_agent": "critic",
                "required_changes": ["Set timeout to 120s", "Provide fallback HAL output"],
                "expected_outcome": "CRITIC should complete review with fallback data"
            }
        }

class LoopDebugResult(BaseModel):
    """
    Schema for Loop Debug Analyzer results.
    
    This schema defines the structure of responses from the Debug Analyzer agent after
    analyzing a failed or incomplete loop execution.
    """
    loop_id: str = Field(..., description="Unique identifier for the analyzed loop")
    project_id: str = Field(..., description="Unique identifier for the project")
    issues: List[LoopIssue] = Field(..., description="List of identified issues")
    agents: List[str] = Field(..., description="List of agents involved in the loop execution")
    failed_agents: List[str] = Field(..., description="List of agents that failed during execution")
    memory_tags_checked: List[str] = Field(..., description="List of memory tags checked during analysis")
    recommendations: List[RepairSuggestion] = Field(..., description="List of repair suggestions")
    confidence_score: float = Field(..., description="Confidence score of the diagnosis (0.0-1.0)")
    analysis_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp of the analysis")
    version: str = Field(..., description="Version of the diagnosis")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_17",
                "project_id": "demo_writer_001",
                "issues": [
                    {
                        "issue_type": "agent_failure",
                        "description": "CRITIC agent failed to complete review due to missing HAL output",
                        "severity": "high",
                        "affected_agent": "critic",
                        "affected_memory_tags": ["hal_build_task_response_loop_17"],
                        "timestamp": "2025-04-24T18:30:00.000000"
                    }
                ],
                "agents": ["hal", "critic", "orchestrator"],
                "failed_agents": ["critic"],
                "memory_tags_checked": [
                    "forge_build_log_loop_17",
                    "critic_review_loop_17",
                    "hal_build_task_response_loop_17",
                    "loop_snapshot_loop_17"
                ],
                "recommendations": [
                    {
                        "suggestion_type": "retry",
                        "description": "Retry CRITIC agent with modified input parameters",
                        "priority": 1,
                        "target_agent": "critic",
                        "required_changes": ["Set timeout to 120s", "Provide fallback HAL output"],
                        "expected_outcome": "CRITIC should complete review with fallback data"
                    }
                ],
                "confidence_score": 0.85,
                "analysis_timestamp": "2025-04-24T19:00:00.000000",
                "version": "1"
            }
        }
