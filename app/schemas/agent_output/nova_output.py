from pydantic import BaseModel
from typing import List

class NovaOutput(BaseModel):
    task_id: str
    frontend_files: List[str]
    layout_summary: str
    design_notes: str
