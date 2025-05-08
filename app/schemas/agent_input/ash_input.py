from pydantic import BaseModel

class AshInput(BaseModel):
    scenario_id: str
    context: dict
    test_parameters: dict
