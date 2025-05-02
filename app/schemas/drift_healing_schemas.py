# memory_tag: phase4.0_sprint1_cognitive_reflection_chain_activation

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class DriftHealingRequest(BaseModel):
    """
    Schema for requesting automatic healing of detected drift issues.
    
    This schema defines the structure for requests to the drift auto-healing endpoint.
    """
    drift_id: str = Field(..., description="The unique identifier of the drift issue to heal.")
    strategy: str = Field("auto", description="Strategy to use for healing (auto, rollback, patch, realign).")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the chosen strategy.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "drift_id": "drift_47ac10b58cc4",
                "strategy": "patch",
                "parameters": {
                    "max_changes": 5,
                    "validation_level": "strict"
                }
            }
        }

class DriftHealingResult(BaseModel):
    """
    Schema for the response after attempting to heal drift issues.
    
    This schema defines the structure for responses from the drift auto-healing endpoint.
    """
    healing_attempt_id: str = Field(..., description="Unique identifier for this healing attempt.")
    drift_id: str = Field(..., description="The unique identifier of the drift issue that was addressed.")
    status: str = Field(..., description="The status of the healing operation (success, failed, pending_validation).")
    message: str = Field(..., description="Descriptive message about the healing attempt.")
    timestamp: str = Field(..., description="Timestamp when the healing was attempted.")
    changes: Optional[List[Dict[str, Any]]] = Field(None, description="List of changes made during healing, if successful.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "healing_attempt_id": "heal_a1b2c3d4",
                "drift_id": "drift_47ac10b58cc4",
                "status": "success",
                "message": "Successfully applied patch strategy to resolve schema drift",
                "timestamp": "2025-04-28T14:00:00Z",
                "changes": [
                    {"type": "schema_update", "file": "app/schemas/memory_schema.py", "field": "memory_tag"},
                    {"type": "registry_update", "file": "app/registries/agent_registry.py", "agent": "MemoryAgent"}
                ]
            }
        }
