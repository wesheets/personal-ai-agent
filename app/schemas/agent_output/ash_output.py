from pydantic import BaseModel
from typing import List

class AshOutput(BaseModel):
    risk_factors: List[str]
    test_results: List[str]
    recommendations: List[str]
