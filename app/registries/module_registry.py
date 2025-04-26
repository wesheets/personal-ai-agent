"""
Module Registry
This module defines the registry of all modules in the Promethios system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class ModuleEntry(BaseModel):
    """Module entry in the registry."""
    name: str = Field(..., description="Name of the module")
    category: str = Field(..., description="Category of the module")
    status: str = Field(..., description="Status of the module (active, planned, or scaffolded)")

class ModuleRegistry(BaseModel):
    """Module registry containing all modules in the system."""
    modules: List[ModuleEntry] = Field(default_factory=list, description="List of all modules")

# Initialize the module registry
MODULE_REGISTRY = ModuleRegistry(modules=[
])

# For backward compatibility, also provide the modules as a list
MODULE_LIST = MODULE_REGISTRY.modules
