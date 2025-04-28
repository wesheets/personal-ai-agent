# memory_tag: phase3.0_sprint4_batch3_stub_creation

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class DriftHealingRequest(BaseModel):
    """Schema for requesting automatic healing of detected drift issues."""
    drift_id: str = Field(..., description="The unique identifier of the drift issue to heal.")
    healing_strategy: Optional[str] = Field("auto", description="Strategy to use for healing (auto, conservative, aggressive).")
    max_changes: Optional[int] = Field(10, description="Maximum number of changes to make during healing.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "drift_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479",
                "healing_strategy": "conservative",
                "max_changes": 5
            }
        }

class DriftHealingResult(BaseModel):
    """Schema for the response after attempting to heal drift issues."""
    healing_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this healing operation.")
    drift_id: str = Field(..., description="The unique identifier of the drift issue that was healed.")
    status: str = Field(..., description="The status of the healing operation (success, partial, failed).")
    changes_made: List[Dict[str, Any]] = Field(..., description="List of changes made during healing.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the healing was completed.")
    remaining_issues: Optional[List[Dict[str, Any]]] = Field(None, description="Any remaining issues that couldn't be healed.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "healing_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "drift_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "success",
                "changes_made": [
                    {"type": "schema_update", "file": "app/schemas/memory_schema.py", "field": "memory_tag"},
                    {"type": "registry_update", "file": "app/registries/agent_registry.py", "agent": "MemoryAgent"}
                ],
                "timestamp": "2025-04-28T12:32:00Z",
                "remaining_issues": []
            }
        }
