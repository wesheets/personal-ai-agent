from pydantic import BaseModel
from typing import List

class BeliefIntrospectionOutput(BaseModel):
    analysis_summary: str
    insights: List[str]
    conflicts_detected: List[str]
