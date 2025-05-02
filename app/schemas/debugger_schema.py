"""
Debugger Schema Module

This module defines the schema models for debugger-related operations in the application.

Includes:
- DebuggerTraceRequest model for failure debugging input
- DebuggerTraceResult model for failure debugging output
- DebuggerReport model for memory reports
- PatchPlan model for recovery plans
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PatchPlan(BaseModel):
    """
    Model for a failure recovery patch plan.
    
    Contains steps to recover from a failure and confidence
    in the proposed solution.
    """
    steps: List[str] = Field(
        default_factory=list,
        description="List of steps to recover from the failure"
    )
    confidence: float = Field(
        ..., 
        description="Confidence in the patch plan from 0.0 to 1.0",
        ge=0.0,
        le=1.0
    )

class DebuggerReport(BaseModel):
    """
    Model for debugger reports injected into memory.
    
    Each report represents a failure diagnosis with associated
    metadata, root cause analysis, and recovery plan.
    """
    loop_id: str = Field(..., description="ID of the loop")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO format timestamp of when the report was generated"
    )
    failure_type: str = Field(..., description="Type of failure detected")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Information about the root cause"
    )
    suggested_fix: str = Field(..., description="Recommendation for fixing the issue")
    patch_plan: PatchPlan = Field(
        ...,
        description="Steps and confidence for recovery"
    )
    next_agent: str = Field(..., description="Agent that should handle the failure next")

class DebuggerTraceRequest(BaseModel):
    """
    Model for a debugger trace request.
    
    Contains all necessary inputs for the debugger agent to diagnose
    failures and propose recovery plans.
    """
    loop_id: str = Field(..., description="String identifier for the loop")
    failure_logs: str = Field(..., description="Traceback string from the failure")
    memory: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current memory state dictionary"
    )
    loop_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional context information about the loop"
    )
    memory_tag: Optional[str] = Field(
        None,
        description="Optional custom memory tag, defaults to debugger_trace_<loop_id>"
    )

class DebuggerTraceResult(BaseModel):
    """
    Model for a debugger trace result.
    
    Contains the updated memory with debugger reports and additional
    metadata about the failure diagnosis.
    """
    updated_memory: Dict[str, Any] = Field(
        ...,
        description="Updated memory dictionary with debugger reports"
    )
    failure_type: str = Field(..., description="Type of failure detected")
    patch_plan: PatchPlan = Field(
        ...,
        description="Steps and confidence for recovery"
    )
    next_agent: str = Field(..., description="Agent that should handle the failure next")
    suggested_fix: str = Field(..., description="Recommendation for fixing the issue")
    report: DebuggerReport = Field(
        ...,
        description="The debugger report that was generated and injected into memory"
    )

# Fallback schema support
def validate_debugger_trace_request(data: Dict[str, Any]) -> DebuggerTraceRequest:
    """
    Validates and converts a dictionary to a DebuggerTraceRequest.
    
    Provides fallback support for schema validation by handling
    missing or invalid fields with appropriate defaults.
    
    Args:
        data: Dictionary containing request data
        
    Returns:
        DebuggerTraceRequest: Validated request object
    """
    try:
        # Try standard validation first
        return DebuggerTraceRequest(**data)
    except Exception as e:
        # Fallback with minimal required fields
        fallback_data = {
            "loop_id": data.get("loop_id", f"fallback_{datetime.utcnow().isoformat()}"),
            "failure_logs": data.get("failure_logs", "Unknown error occurred"),
            "memory": data.get("memory", {}),
            "loop_context": data.get("loop_context", {})
        }
        return DebuggerTraceRequest(**fallback_data)

def validate_debugger_trace_result(data: Dict[str, Any]) -> DebuggerTraceResult:
    """
    Validates and converts a dictionary to a DebuggerTraceResult.
    
    Provides fallback support for schema validation by handling
    missing or invalid fields with appropriate defaults.
    
    Args:
        data: Dictionary containing result data
        
    Returns:
        DebuggerTraceResult: Validated result object
    """
    try:
        # Try standard validation first
        return DebuggerTraceResult(**data)
    except Exception as e:
        # Create a minimal patch plan if missing
        if "patch_plan" not in data:
            data["patch_plan"] = {
                "steps": ["Review logs for more detailed error information"],
                "confidence": 0.5
            }
        
        # Create a minimal report if missing
        if "report" not in data:
            data["report"] = {
                "loop_id": data.get("loop_id", f"fallback_{datetime.utcnow().isoformat()}"),
                "timestamp": datetime.utcnow().isoformat(),
                "failure_type": data.get("failure_type", "unknown"),
                "details": {},
                "suggested_fix": data.get("suggested_fix", "Review logs for more information"),
                "patch_plan": data.get("patch_plan", {"steps": [], "confidence": 0.5}),
                "next_agent": data.get("next_agent", "critic")
            }
        
        # Fallback with minimal required fields
        fallback_data = {
            "updated_memory": data.get("updated_memory", {}),
            "failure_type": data.get("failure_type", "unknown"),
            "patch_plan": data.get("patch_plan", {"steps": [], "confidence": 0.5}),
            "next_agent": data.get("next_agent", "critic"),
            "suggested_fix": data.get("suggested_fix", "Review logs for more information"),
            "report": data.get("report", {})
        }
        return DebuggerTraceResult(**fallback_data)
