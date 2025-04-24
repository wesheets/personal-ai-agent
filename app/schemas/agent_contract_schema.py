"""
Agent Contract Schema Module

This module defines the data models for agent contracts,
ensuring agents operate within well-defined, verifiable bounds.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class AgentContract(BaseModel):
    """
    Schema for agent contracts.
    
    This schema defines the structure of contracts that specify
    the required input schema, expected output schema, allowed tools,
    and fallback behaviors for each agent.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    accepted_input_schema: str = Field(..., description="Schema that the agent accepts as input")
    expected_output_schema: str = Field(..., description="Schema that the agent is expected to produce")
    allowed_tools: List[str] = Field(..., description="List of tools that the agent is allowed to use")
    fallback_behaviors: List[str] = Field(..., description="List of fallback behaviors when the agent encounters errors")
    output_must_be_wrapped: bool = Field(..., description="Whether the agent's output must be schema-wrapped")
    can_initiate_recovery: bool = Field(..., description="Whether the agent can initiate recovery procedures")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the contract was created")
    updated_at: Optional[datetime] = Field(None, description="When the contract was last updated")
    version: str = Field("1.0.0", description="Version of the contract")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "accepted_input_schema": "LoopResponseRequest",
                "expected_output_schema": "LoopResponseResult",
                "allowed_tools": ["openai_generate_code", "memory_read", "memory_write"],
                "fallback_behaviors": ["generate_fallback_jsx", "log_error"],
                "output_must_be_wrapped": True,
                "can_initiate_recovery": False,
                "created_at": "2025-04-24T16:26:00.000Z",
                "updated_at": None,
                "version": "1.0.0"
            }
        }

class ContractViolation(BaseModel):
    """
    Schema for contract violations.
    
    This schema defines the structure of contract violation records,
    including the type of violation and relevant details.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    violation_type: str = Field(..., description="Type of contract violation")
    details: str = Field(..., description="Details about the violation")
    input_schema: Optional[str] = Field(None, description="Input schema involved in the violation")
    output_schema: Optional[str] = Field(None, description="Output schema involved in the violation")
    tool_used: Optional[str] = Field(None, description="Tool involved in the violation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the violation occurred")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "violation_type": "output_schema_mismatch",
                "details": "Agent output does not match expected schema LoopResponseResult",
                "input_schema": "LoopResponseRequest",
                "output_schema": "UnknownSchema",
                "tool_used": None,
                "timestamp": "2025-04-24T16:26:00.000Z"
            }
        }

class ContractValidationRequest(BaseModel):
    """
    Schema for contract validation requests.
    
    This schema defines the structure of requests to validate
    agent operations against their contracts.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    input_schema: Optional[str] = Field(None, description="Input schema to validate")
    output_schema: Optional[str] = Field(None, description="Output schema to validate")
    tool_used: Optional[str] = Field(None, description="Tool to validate")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "input_schema": "LoopResponseRequest",
                "output_schema": "LoopResponseResult",
                "tool_used": "openai_generate_code"
            }
        }

class ContractValidationResponse(BaseModel):
    """
    Schema for contract validation responses.
    
    This schema defines the structure of responses from contract validation,
    including whether the validation passed and any violations found.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    valid: bool = Field(..., description="Whether the validation passed")
    violations: List[ContractViolation] = Field(default_factory=list, description="List of contract violations found")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "valid": False,
                "violations": [
                    {
                        "agent_id": "hal",
                        "violation_type": "output_schema_mismatch",
                        "details": "Agent output does not match expected schema LoopResponseResult",
                        "input_schema": "LoopResponseRequest",
                        "output_schema": "UnknownSchema",
                        "tool_used": None,
                        "timestamp": "2025-04-24T16:26:00.000Z"
                    }
                ]
            }
        }
