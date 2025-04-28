# memory_tag: phase4.0_sprint1_cognitive_reflection_chain_activation
"""
Schemas for Reflection Chain Weaving

Defines the request and response structures for the ReflectionChainWeaver agent/endpoint.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReflectionChainRequest(BaseModel):
    """Request to weave a chain of reflections."""
    reflection_ids: List[str] = Field(..., description="List of reflection IDs to include in the chain")
    goal: Optional[str] = Field(None, description="Optional goal or context for weaving the chain")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional parameters for the weaving process")

class MetaInsight(BaseModel):
    """A higher-level insight derived from multiple reflections."""
    insight_id: str = Field(..., description="Unique ID for the meta-insight")
    description: str = Field(..., description="Description of the meta-insight")
    supporting_reflection_ids: List[str] = Field(..., description="Reflection IDs supporting this meta-insight")
    confidence: float = Field(..., description="Confidence score for the meta-insight")

class TriggeredAction(BaseModel):
    """An action triggered based on the reflection chain analysis."""
    action_id: str = Field(..., description="Unique ID for the triggered action")
    action_type: str = Field(..., description="Type of action (e.g., plan_generation, drift_healing, alert)")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the triggered action")
    reason: str = Field(..., description="Reason why this action was triggered")

class ReflectionChainResponse(BaseModel):
    """Response containing the woven reflection chain and derived insights/actions."""
    chain_id: str = Field(..., description="Unique ID for the generated reflection chain")
    reflection_ids: List[str] = Field(..., description="List of reflection IDs included in the chain")
    status: str = Field(..., description="Status of the chain weaving process (e.g., completed, failed, pending)")
    summary: str = Field(..., description="Summary of the reflection chain")
    meta_insights: List[MetaInsight] = Field(default_factory=list, description="List of meta-insights derived from the chain")
    triggered_actions: List[TriggeredAction] = Field(default_factory=list, description="List of actions triggered by the chain analysis")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the chain was created")

