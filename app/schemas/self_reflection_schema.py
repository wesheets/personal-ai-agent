from pydantic import BaseModel

class SelfInquiryRequest(BaseModel):
    loop_id: str
    project_id: str
    prompt: str
    initiator: str
