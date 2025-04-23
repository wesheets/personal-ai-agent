from pydantic import BaseModel

class BeliefReinforcementRequest(BaseModel):
    loop_id: str
    field: str
    reinforcement_reason: str
    initiator: str
