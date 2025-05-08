from pydantic import BaseModel
from typing import List

class OrchestratorOutput(BaseModel):
    architecture: List[str]
    next_step: str
    clarifying_questions: List[str]
