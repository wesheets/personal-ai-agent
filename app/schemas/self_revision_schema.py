from pydantic import BaseModel

class BeliefRevisionRequest(BaseModel):
    loop_id: str
    reason: str
    field_updated: str
    new_value: str
    initiator: str
