"""
Historian Schema Module

This module defines the schema models for historian-related operations in the application.

Includes:
- HistorianDriftRequest model for belief drift detection input
- HistorianDriftResult model for belief drift detection output
- BeliefAlignmentScore model for alignment scoring results
- HistorianAlert model for memory alerts
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BeliefAlignmentScore(BaseModel):
    """
    Model for belief alignment scoring results.
    
    Contains the alignment score and any missing beliefs detected
    during the analysis of loop summaries.
    """
    alignment_score: float = Field(
        ..., 
        description="Alignment score between 0.0 (no alignment) and 1.0 (perfect alignment)",
        ge=0.0,
        le=1.0
    )
    missing_beliefs: List[str] = Field(
        default_factory=list,
        description="List of beliefs not referenced in recent loops"
    )

class HistorianAlert(BaseModel):
    """
    Model for historian alerts injected into memory.
    
    Each alert represents a belief drift detection or alignment check
    with associated metadata and suggestions.
    """
    loop_id: str = Field(..., description="ID of the current loop")
    alert_type: str = Field(
        ..., 
        description="Type of alert (belief_drift_detected or belief_alignment_check)"
    )
    missing_beliefs: List[str] = Field(
        default_factory=list,
        description="List of beliefs not referenced in recent loops"
    )
    loop_belief_alignment_score: float = Field(
        ..., 
        description="Overall belief alignment score",
        ge=0.0,
        le=1.0
    )
    suggestion: str = Field(..., description="Recommendation based on alignment score")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO format timestamp of when the alert was generated"
    )

class HistorianDriftRequest(BaseModel):
    """
    Model for a historian belief drift detection request.
    
    Contains all necessary inputs for the historian agent to analyze
    loop summaries and detect belief drift.
    """
    loop_id: str = Field(..., description="String identifier for the current loop")
    loop_summary: str = Field(..., description="Text content of the loop summary")
    recent_loops: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of recent loop summaries"
    )
    beliefs: List[str] = Field(
        default_factory=list,
        description="List of system beliefs to check against"
    )
    memory: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current memory state dictionary"
    )
    memory_tag: Optional[str] = Field(
        None,
        description="Optional custom memory tag, defaults to historian_belief_log_<loop_id>"
    )

class HistorianDriftResult(BaseModel):
    """
    Model for a historian belief drift detection result.
    
    Contains the updated memory with historian alerts and additional
    metadata about the belief drift analysis.
    """
    updated_memory: Dict[str, Any] = Field(
        ...,
        description="Updated memory dictionary with historian alerts"
    )
    alignment_score: float = Field(
        ..., 
        description="Overall belief alignment score",
        ge=0.0,
        le=1.0
    )
    missing_beliefs: List[str] = Field(
        default_factory=list,
        description="List of beliefs not referenced in recent loops"
    )
    suggestion: str = Field(..., description="Recommendation based on alignment score")
    alert: HistorianAlert = Field(
        ...,
        description="The historian alert that was generated and injected into memory"
    )

# Fallback schema support
def validate_historian_drift_request(data: Dict[str, Any]) -> HistorianDriftRequest:
    """
    Validates and converts a dictionary to a HistorianDriftRequest.
    
    Provides fallback support for schema validation by handling
    missing or invalid fields with appropriate defaults.
    
    Args:
        data: Dictionary containing request data
        
    Returns:
        HistorianDriftRequest: Validated request object
    """
    try:
        # Try standard validation first
        return HistorianDriftRequest(**data)
    except Exception as e:
        # Fallback with minimal required fields
        fallback_data = {
            "loop_id": data.get("loop_id", f"fallback_{datetime.utcnow().isoformat()}"),
            "loop_summary": data.get("loop_summary", ""),
            "recent_loops": data.get("recent_loops", []),
            "beliefs": data.get("beliefs", []),
            "memory": data.get("memory", {})
        }
        return HistorianDriftRequest(**fallback_data)

def validate_historian_drift_result(data: Dict[str, Any]) -> HistorianDriftResult:
    """
    Validates and converts a dictionary to a HistorianDriftResult.
    
    Provides fallback support for schema validation by handling
    missing or invalid fields with appropriate defaults.
    
    Args:
        data: Dictionary containing result data
        
    Returns:
        HistorianDriftResult: Validated result object
    """
    try:
        # Try standard validation first
        return HistorianDriftResult(**data)
    except Exception as e:
        # Create a minimal alert if missing
        if "alert" not in data:
            data["alert"] = {
                "loop_id": data.get("loop_id", f"fallback_{datetime.utcnow().isoformat()}"),
                "alert_type": "belief_alignment_check",
                "missing_beliefs": data.get("missing_beliefs", []),
                "loop_belief_alignment_score": data.get("alignment_score", 0.5),
                "suggestion": data.get("suggestion", "Review system beliefs"),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Fallback with minimal required fields
        fallback_data = {
            "updated_memory": data.get("updated_memory", {}),
            "alignment_score": data.get("alignment_score", 0.5),
            "missing_beliefs": data.get("missing_beliefs", []),
            "suggestion": data.get("suggestion", "Review system beliefs"),
            "alert": data.get("alert", {})
        }
        return HistorianDriftResult(**fallback_data)
