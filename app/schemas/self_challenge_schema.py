from pydantic import BaseModel

class BeliefChallengeRequest(BaseModel):
    loop_id: str
    field: str
    challenger: str
    challenge_reason: str
    initiator: str
