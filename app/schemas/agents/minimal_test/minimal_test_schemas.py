from pydantic import BaseModel

class MinimalTestRequest(BaseModel):
    message: str

class MinimalTestResult(BaseModel):
    response: str

