from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class AnalyzePromptRequest(BaseModel):
    """
    Request model for the Analyze Prompt endpoint.
    Contains the prompt text to be analyzed.
    """
    prompt: str
    options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AnalyzePromptResponse(BaseModel):
    """
    Response model for the Analyze Prompt endpoint.
    Contains the analysis results of the provided prompt.
    """
    analysis: Dict[str, Any]
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
