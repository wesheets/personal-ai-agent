"""
ORCHESTRATOR Agent Schema Definitions

This module defines the schemas for ORCHESTRATOR agent requests and responses.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class OrchestratorPlanRequest(BaseModel):
    """
    Schema for ORCHESTRATOR agent plan request.
    """
    project_id: str = Field(..., description="Project identifier")
    task: str = Field(..., description="Task to execute (e.g., 'initialize', 'plan', 'delegate')")
    tools: Optional[List[str]] = Field(
        default=["delegate", "plan", "resolve"],
        description="List of tools to use for orchestration"
    )


class TriggerResult(BaseModel):
    """
    Schema for agent trigger result.
    """
    triggered_agent: str = Field(..., description="Name of the triggered agent")
    timestamp: str = Field(..., description="ISO format timestamp of the trigger")
    loop_count: int = Field(..., description="Current loop count")
    reason: str = Field(..., description="Reason for triggering this agent")
    status: str = Field(..., description="Status of the trigger operation")


class OrchestratorDecision(BaseModel):
    """
    Schema for orchestrator decision.
    """
    timestamp: str = Field(..., description="ISO format timestamp of the decision")
    loop_count: int = Field(..., description="Loop count when decision was made")
    last_agent: Optional[str] = Field(None, description="Last agent that ran")
    next_agent: str = Field(..., description="Next agent to run")
    reason: str = Field(..., description="Reason for the decision")


class PlanStep(BaseModel):
    """
    Schema for a step in an orchestration plan.
    """
    agent: str = Field(..., description="Agent responsible for this step")
    purpose: str = Field(..., description="Purpose of this step")


class OrchestratorPlan(BaseModel):
    """
    Schema for a project orchestration plan.
    """
    project_id: str = Field(..., description="Project identifier")
    timestamp: str = Field(..., description="ISO format timestamp of plan creation")
    steps: List[PlanStep] = Field(..., description="Ordered steps in the plan")
    estimated_loops: int = Field(..., description="Estimated number of loops required")
    current_loop: int = Field(..., description="Current loop count")


class DelegationResult(BaseModel):
    """
    Schema for task delegation result.
    """
    project_id: str = Field(..., description="Project identifier")
    timestamp: str = Field(..., description="ISO format timestamp of delegation")
    agent: str = Field(..., description="Agent the task was delegated to")
    task: str = Field(..., description="Task description")
    status: str = Field(..., description="Status of the delegation")


class ResolutionResult(BaseModel):
    """
    Schema for conflict resolution result.
    """
    project_id: str = Field(..., description="Project identifier")
    timestamp: str = Field(..., description="ISO format timestamp of resolution")
    conflicts_found: int = Field(..., description="Number of conflicts found")
    conflicts_resolved: int = Field(..., description="Number of conflicts resolved")
    status: str = Field(..., description="Status of the resolution")


class OrchestratorPlanResult(BaseModel):
    """
    Schema for ORCHESTRATOR agent operation result.
    """
    status: str = Field(..., description="Status of the operation (success or error)")
    task: str = Field(..., description="Original task")
    tools: List[str] = Field(..., description="Tools used")
    project_id: str = Field(..., description="Project identifier")
    intent: str = Field(..., description="Intent of the operation")
    action: str = Field(..., description="Action performed")
    timestamp: str = Field(..., description="ISO format timestamp of the operation")
    output: str = Field(..., description="Human-readable output of the operation")
    
    # Optional fields based on action type
    loop_id: Optional[str] = Field(None, description="Loop identifier if applicable")
    next_agent: Optional[str] = Field(None, description="Next agent to run if applicable")
    trigger_result: Optional[TriggerResult] = Field(None, description="Trigger result if applicable")
    reason: Optional[str] = Field(None, description="Reason for decision if applicable")
    completed_agent: Optional[str] = Field(None, description="Completed agent if applicable")
    all_loops_complete: Optional[bool] = Field(None, description="Whether all loops are complete")
    decisions: Optional[List[OrchestratorDecision]] = Field(None, description="List of decisions if applicable")
    decision: Optional[OrchestratorDecision] = Field(None, description="Single decision if applicable")
    plan: Optional[OrchestratorPlan] = Field(None, description="Plan if applicable")
    delegated_agent: Optional[str] = Field(None, description="Delegated agent if applicable")
    delegated_task: Optional[str] = Field(None, description="Delegated task if applicable")
    delegation_result: Optional[DelegationResult] = Field(None, description="Delegation result if applicable")
    resolution: Optional[ResolutionResult] = Field(None, description="Resolution result if applicable")
    error: Optional[str] = Field(None, description="Error message if status is error")


# Fallback schema for handling errors
class OrchestratorErrorResult(BaseModel):
    """
    Schema for ORCHESTRATOR agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    task: Optional[str] = Field(None, description="Original task")
    tools: Optional[List[str]] = Field(None, description="Tools used")
    project_id: Optional[str] = Field(None, description="Project identifier")
    intent: Optional[str] = Field("orchestration", description="Intent of the operation")
    action: Optional[str] = Field("error", description="Action performed")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp of the operation")
    output: Optional[str] = Field(None, description="Human-readable output of the error")
    error: Optional[str] = Field(None, description="Detailed error information")
