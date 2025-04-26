"""
Endpoint Registry
This module defines the registry of all endpoints in the Promethios system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class EndpointEntry(BaseModel):
    """Endpoint entry in the registry."""
    path: str = Field(..., description="Path of the endpoint")
    method: str = Field(..., description="HTTP method of the endpoint")
    input_schema: Optional[str] = Field(None, description="Input schema of the endpoint")
    output_schema: Optional[str] = Field(None, description="Output schema of the endpoint")
    module: str = Field(..., description="Module hosting the endpoint")

class EndpointRegistry(BaseModel):
    """Endpoint registry containing all endpoints in the system."""
    endpoints: List[EndpointEntry] = Field(default_factory=list, description="List of all endpoints")

# Initialize the endpoint registry
ENDPOINT_REGISTRY = EndpointRegistry(endpoints=[
])

# For backward compatibility, also provide the endpoints as a list
ENDPOINT_LIST = ENDPOINT_REGISTRY.endpoints
