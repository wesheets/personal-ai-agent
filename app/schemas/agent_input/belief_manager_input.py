from pydantic import BaseModel

class BeliefManagerInput(BaseModel):
    target_belief_key: str
    proposed_value: str
    justification: str
