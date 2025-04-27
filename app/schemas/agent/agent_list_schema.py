from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AgentListResponse(BaseModel):
    """
    Response schema for the agent list endpoint.
    
    This schema defines the standardized format for agent listing responses,
    including status and a list of agent metadata objects.
    
    Attributes:
        status (str): Response status, typically "ok" or "error"
        agents (List[Dict[str, Any]]): List of agent metadata objects
        
    Memory Tag: SCHEMA_STUBBED_AGENT_LIST_RESPONSE
    """
    status: str
    agents: List[Dict[str, Any]]
    message: Optional[str] = None
