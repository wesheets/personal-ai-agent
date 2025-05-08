from pydantic import BaseModel

class ReflectorOutput(BaseModel):
    reflection_log: dict
    status: str
