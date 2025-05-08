from pydantic import BaseModel

class OrchestratorInput(BaseModel):
    operator_input: str
    operator_persona: str
    project_id: str
