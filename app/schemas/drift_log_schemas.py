# memory_tag: phase3.0_sprint4_batch3_stub_creation

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DriftLogRequest(BaseModel):
    """Schema for requesting drift logs."""
    start_time: Optional[datetime] = Field(None, description="Start time for log retrieval.")
    end_time: Optional[datetime] = Field(None, description="End time for log retrieval.")
    event_type: Optional[str] = Field(None, description="Filter logs by event type (e.g., \"drift_detected\", \"healing_attempt\").")
    max_entries: Optional[int] = Field(100, description="Maximum number of log entries to retrieve.")

    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "2025-04-28T00:00:00Z",
                "end_time": "2025-04-28T12:00:00Z",
                "event_type": "drift_detected",
                "max_entries": 50
            }
        }

class DriftLogEntry(BaseModel):
    """Schema for a single entry in the drift log."""
    timestamp: datetime
    event_type: str
    details: Dict[str, Any]
    drift_id: Optional[str] = None
    healing_id: Optional[str] = None

class DriftLogResponse(BaseModel):
    """Schema for the response containing drift logs."""
    log_entries: List[DriftLogEntry] = Field(..., description="List of retrieved drift log entries.")
    total_retrieved: int = Field(..., description="Total number of log entries retrieved.")
    query_details: DriftLogRequest = Field(..., description="The original query parameters used for retrieval.")

    class Config:
        json_schema_extra = {
            "example": {
                "log_entries": [
                    {
                        "timestamp": "2025-04-28T10:15:30Z",
                        "event_type": "drift_detected",
                        "details": {"surface": "ACI", "discrepancy": "Missing agent schema link"},
                        "drift_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479"
                    },
                    {
                        "timestamp": "2025-04-28T11:05:00Z",
                        "event_type": "healing_attempt",
                        "details": {"strategy": "auto", "result": "partial"},
                        "drift_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479",
                        "healing_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
                    }
                ],
                "total_retrieved": 2,
                "query_details": {
                    "start_time": "2025-04-28T00:00:00Z",
                    "end_time": "2025-04-28T12:00:00Z",
                    "event_type": None,
                    "max_entries": 100
                }
            }
        }
