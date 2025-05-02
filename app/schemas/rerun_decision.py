"""
RerunDecision Schema Module

This module provides an updated implementation of the RerunDecision model
with schema validation support for Phase 2 of the Schema Compliance initiative.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rerun_decision')

class RerunDecision(BaseModel):
    """
    Model for rerun decision result.
    
    Contains the decision on whether to rerun a loop and related information.
    """
    decision: str = Field(..., description="Either 'rerun' or 'finalize'")
    loop_id: str = Field(..., description="ID of the loop being evaluated")
    original_loop_id: Optional[str] = Field(default=None, description="ID of the original loop if this is a rerun")
    new_loop_id: Optional[str] = Field(default=None, description="ID of the new loop if decision is 'rerun'")
    rerun_reason: Optional[str] = Field(default=None, description="Primary reason for rerun")
    rerun_number: Optional[int] = Field(default=0, description="Number of times the loop has been rerun")
    reason: Optional[str] = Field(default=None, description="Detailed explanation for the decision")
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Persona to use for rerun")
    
    # Fields for guardrails
    rerun_limit_reached: Optional[bool] = Field(default=False, description="Whether the rerun limit was reached")
    bias_echo_detected: Optional[bool] = Field(default=False, description="Whether bias echo was detected")
    fatigue_threshold_exceeded: Optional[bool] = Field(default=False, description="Whether fatigue threshold was exceeded")
    force_finalized: Optional[bool] = Field(default=False, description="Whether finalization was forced")
    
    # Fields for rerun reasoning
    rerun_trigger: Optional[List[str]] = Field(default_factory=list, description="Components that triggered the rerun")
    rerun_reason_detail: Optional[str] = Field(default=None, description="Detailed reason for the rerun")
    overridden_by: Optional[str] = Field(default=None, description="Who overrode the rerun decision, if applicable")
    
    # Fields for reflection results that led to rerun
    alignment_score: Optional[float] = Field(default=None, description="Alignment score that triggered rerun")
    drift_score: Optional[float] = Field(default=None, description="Drift score that triggered rerun")
    belief_conflict_flags: Optional[List[str]] = Field(default_factory=list, description="Belief conflicts that triggered rerun")
    
    # Fields for safety-related reruns
    safety_triggered: Optional[bool] = Field(default=False, description="Whether rerun was triggered by safety concerns")
    safety_trigger_type: Optional[str] = Field(default=None, description="Type of safety concern that triggered rerun")
    safety_severity: Optional[float] = Field(default=None, description="Severity of safety concern (0.0 to 1.0)")
    
    # Fields for operator-triggered reruns
    operator_triggered: Optional[bool] = Field(default=False, description="Whether rerun was triggered by operator")
    operator_id: Optional[str] = Field(default=None, description="ID of operator who triggered rerun")
    operator_reason: Optional[str] = Field(default=None, description="Reason provided by operator")
    
    # Fields for depth control in rerun
    depth: Optional[str] = Field(default="standard", description="Reflection depth for rerun (shallow/standard/deep)")
    depth_escalation: Optional[bool] = Field(default=False, description="Whether depth should be escalated in rerun")
    depth_escalation_reason: Optional[str] = Field(default=None, description="Reason for depth escalation")
    
    # Fields for rerun execution tracking
    timestamp: Optional[str] = Field(default=None, description="When the rerun decision was made")
    execution_priority: Optional[str] = Field(default="normal", description="Priority for rerun execution (low/normal/high)")
    
    # Fields for schema validation
    schema_validated: bool = Field(default=False, description="Whether this decision has been schema-validated")
    validation_timestamp: Optional[str] = Field(default=None, description="When schema validation was performed")
    validation_errors: Optional[List[str]] = Field(default_factory=list, description="Schema validation errors, if any")
    
    @validator('decision')
    def validate_decision(cls, v):
        """Validate that decision is either 'rerun' or 'finalize'"""
        if v not in ['rerun', 'finalize']:
            raise ValueError(f"Decision must be either 'rerun' or 'finalize', got '{v}'")
        return v
    
    @validator('alignment_score', 'drift_score', 'safety_severity')
    def validate_score_range(cls, v):
        """Validate that scores are between 0.0 and 1.0"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got {v}")
        return v
    
    @validator('depth')
    def validate_depth(cls, v):
        """Validate that depth is one of the allowed values"""
        if v not in ['shallow', 'standard', 'deep']:
            raise ValueError(f"Depth must be one of 'shallow', 'standard', 'deep', got '{v}'")
        return v
    
    @validator('execution_priority')
    def validate_priority(cls, v):
        """Validate that execution priority is one of the allowed values"""
        if v not in ['low', 'normal', 'high']:
            raise ValueError(f"Execution priority must be one of 'low', 'normal', 'high', got '{v}'")
        return v
    
    @validator('new_loop_id')
    def validate_new_loop_id(cls, v, values):
        """Validate that new_loop_id is provided if decision is 'rerun'"""
        if values.get('decision') == 'rerun' and not v:
            raise ValueError("New loop ID must be provided when decision is 'rerun'")
        return v
    
    def dict(self, *args, **kwargs):
        """Override dict method to add schema validation metadata"""
        result = super().dict(*args, **kwargs)
        
        # Set schema validation fields
        result['schema_validated'] = True
        result['validation_timestamp'] = datetime.utcnow().isoformat()
        result['validation_errors'] = []
        
        return result
    
    def json(self, *args, **kwargs):
        """Override json method to add schema validation metadata"""
        # Get the dict with validation metadata
        data = self.dict()
        
        # Convert to JSON
        return json.dumps(data, *args, **kwargs)
    
    @classmethod
    def validate_decision_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate rerun decision data against the schema.
        
        Args:
            data: Dictionary containing rerun decision data
            
        Returns:
            Validated data with schema validation metadata
        """
        try:
            # Create instance to validate
            instance = cls(**data)
            
            # Convert to dict with validation metadata
            validated_data = instance.dict()
            
            # Log successful validation
            logger.info(f"RerunDecision validation successful for loop {data.get('loop_id')}")
            
            return validated_data
        
        except Exception as e:
            # Log validation error
            logger.error(f"RerunDecision validation failed: {str(e)}")
            
            # Add validation error metadata
            data['schema_validated'] = False
            data['validation_timestamp'] = datetime.utcnow().isoformat()
            data['validation_errors'] = [str(e)]
            
            return data
