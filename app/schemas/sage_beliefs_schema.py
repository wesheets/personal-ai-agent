from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class BeliefInsight(BaseModel):
    """
    Schema for belief insight.
    """
    theme: str
    insight: str
    application: str
    relevance: float

class SageBeliefRequest(BaseModel):
    """
    Schema for sage belief request.
    """
    topic: str = Field(..., description="Topic to provide beliefs on")
    context: Optional[str] = Field(None, description="Additional context for the beliefs")
    perspective: str = Field(default="balanced", description="Perspective to take (balanced, optimistic, critical, historical, futuristic)")
    depth: str = Field(default="standard", description="Depth of insights (brief, standard, profound)")

class SageBeliefResponse(BaseModel):
    """
    Schema for sage belief response.
    """
    status: str
    message: str
    belief_id: str
    summary: str
    core_beliefs: List[Dict[str, str]]
    insights: List[BeliefInsight]
    perspectives: List[Dict[str, str]]
    wisdom_score: float
    timestamp: str
