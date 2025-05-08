from pydantic import BaseModel

class NovaInput(BaseModel):
    task_id: str
    design_type: str
    style_preferences: str
    project_id: str
