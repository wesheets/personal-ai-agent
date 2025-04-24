"""
SAGE Agent Schema Module

This module defines the schemas for the SAGE agent's review functionality
in cascade mode, allowing it to summarize loop beliefs and log structured belief maps.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import datetime

class BeliefScore(BaseModel):
    """
    Represents a belief with its confidence score and optional emotional weight.
    
    Attributes:
        belief: The belief statement
        confidence: Confidence score (0.0 to 1.0)
        emotional_weight: Optional emotional weight or significance (-1.0 to 1.0)
    """
    belief: str = Field(..., description="The belief statement")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    emotional_weight: Optional[float] = Field(None, ge=-1.0, le=1.0, 
                                             description="Emotional weight or significance (-1.0 to 1.0)")
    
    @validator('belief')
    def belief_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Belief statement cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "belief": "The user needs a more efficient workflow for data processing",
                "confidence": 0.85,
                "emotional_weight": 0.3
            }
        }

class SageReviewRequest(BaseModel):
    """
    Request schema for SAGE agent review in cascade mode.
    
    Attributes:
        loop_id: Unique identifier for the loop
        summary_text: Summary text to analyze for beliefs
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    summary_text: str = Field(..., description="Summary text to analyze for beliefs")
    
    @validator('summary_text')
    def summary_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Summary text cannot be empty')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_12345",
                "summary_text": "The user is trying to optimize their data processing pipeline. They've mentioned issues with the current ETL process being too slow and error-prone. They're looking for automated solutions that can handle large datasets efficiently."
            }
        }

class SageReviewResult(BaseModel):
    """
    Response schema for SAGE agent review in cascade mode.
    
    Attributes:
        belief_scores: List of beliefs with confidence scores
        reflection_text: Optional reflection on the beliefs and their implications
        timestamp: When the review was performed
        loop_id: The loop identifier that was reviewed
    """
    belief_scores: List[BeliefScore] = Field(..., description="List of beliefs with confidence scores")
    reflection_text: Optional[str] = Field(None, description="Reflection on the beliefs and their implications")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat(),
                          description="When the review was performed")
    loop_id: str = Field(..., description="The loop identifier that was reviewed")
    
    @validator('belief_scores')
    def must_have_beliefs(cls, v):
        if not v:
            raise ValueError('Must include at least one belief score')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "belief_scores": [
                    {
                        "belief": "The user needs a more efficient workflow for data processing",
                        "confidence": 0.85,
                        "emotional_weight": 0.3
                    },
                    {
                        "belief": "Current ETL process is causing frustration",
                        "confidence": 0.75,
                        "emotional_weight": -0.6
                    },
                    {
                        "belief": "Automation is a high priority for the user",
                        "confidence": 0.9,
                        "emotional_weight": 0.5
                    }
                ],
                "reflection_text": "The user appears to be experiencing significant frustration with their current data processing workflow. There's a strong desire for automation and efficiency improvements, suggesting that solutions focusing on these aspects would be well-received.",
                "timestamp": "2025-04-24T17:02:30.123456",
                "loop_id": "loop_12345"
            }
        }
