from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class PessimistRiskAssessmentInput(BaseModel):
    loop_id: str = Field(..., description="The ID of the current loop.")
    # Batch 20.2: Make plan_file_path optional and add field for mutation details
    plan_file_path: Optional[str] = Field(default=None, description="Absolute path to the proposed plan JSON file (if applicable).")
    mutation_request_details: Optional[Dict[str, Any]] = Field(default=None, description="Details of the mutation request (if applicable).")
    
    # Optional context fields, similar to Critic, if needed for more advanced risk assessment
    # intent_data: Optional[Dict[str, Any]] = Field(default=None, description="The full intent data for the current loop.")
    # belief_surface_path: Optional[str] = Field(default="/home/ubuntu/personal-ai-agent/app/memory/belief_surface.json", description="Path to the belief surface file.")
    # promethios_creed_path: Optional[str] = Field(default="/home/ubuntu/personal-ai-agent/app/memory/promethios_creed.json", description="Path to the Promethios creed file.")

    # Add validation to ensure at least one of plan_file_path or mutation_request_details is provided?
    # For now, assume the calling code (mutation_guard or controller) provides the correct one.

