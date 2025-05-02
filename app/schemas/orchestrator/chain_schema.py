"""
Chain Schema Module

This module defines the schema for chain operations.
"""
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class ChainInstructionItem(BaseModel):
    """
    Schema for a single instruction in a chain.
    """
    agent: str = Field(..., description="The agent to execute the instruction")
    goal: str = Field(..., description="The goal of the instruction")
    chain_id: Optional[str] = Field(None, description="The chain identifier")
    memory_context: Optional[Dict[str, Any]] = Field(None, description="Memory context for the instruction")

# memory_tag: stubbed_phase2.5
class ChainRequest(RootModel):
    """
    Schema for chain request.
    """
    root: List[Dict[str, Any]] = Field(..., description="List of instruction objects")

# memory_tag: stubbed_phase2.5
class ChainStepResponse(BaseModel):
    """
    Schema for a single step in a chain response.
    """
    agent: str = Field(..., description="The agent that executed the instruction")
    status: str = Field(..., description="Status of the step execution")
    step_number: int = Field(..., description="Step number in the chain")
    reflection: Optional[str] = Field(None, description="Agent reflection on the execution")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Outputs of the step execution")
    retry_attempted: Optional[bool] = Field(None, description="Whether a retry was attempted")
    retry_status: Optional[str] = Field(None, description="Status of the retry")
    redeemed: Optional[bool] = Field(None, description="Whether the step was redeemed after failure")
    redemption_reflection: Optional[str] = Field(None, description="Reflection on the redemption")
    error: Optional[str] = Field(None, description="Error message if the step failed")

# memory_tag: stubbed_phase2.5
class ChainResponse(BaseModel):
    """
    Schema for chain response.
    """
    status: str = Field(..., description="Status of the chain execution")
    chain_id: str = Field(..., description="The chain identifier")
    steps: List[ChainStepResponse] = Field(..., description="List of step responses")
