"""
FORGE Schema Module

This module defines the schemas for the FORGE agent, which acts as the deep system builder
in the Promethios architecture. It handles building system components, registering routes,
and managing project state.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ForgeBuildRequest(BaseModel):
    """
    Schema for FORGE build requests.
    
    This schema defines the structure of requests to the FORGE agent for building
    system components and integrating them into the Promethios architecture.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    loop_id: str = Field(..., description="Unique identifier for the current loop")
    components: List[str] = Field(..., description="List of components to build")
    version: Optional[str] = Field("1.0", description="Version of the build")
    hal_result_tag: Optional[str] = Field(None, description="Memory tag for HAL's result")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "demo_writer_001",
                "loop_id": "loop_17",
                "components": ["api", "schema", "test"],
                "version": "1.0",
                "hal_result_tag": "hal_build_task_response_loop_17"
            }
        }

class ComponentBuildResult(BaseModel):
    """
    Schema for individual component build results.
    
    This schema defines the structure of build results for individual components.
    """
    component_name: str = Field(..., description="Name of the component")
    files_created: List[str] = Field(..., description="List of files created for this component")
    status: str = Field(..., description="Status of the build (success, partial, failed)")
    error: Optional[str] = Field(None, description="Error message if build failed")
    
    class Config:
        schema_extra = {
            "example": {
                "component_name": "api",
                "files_created": ["api_module.py", "api_routes.py"],
                "status": "success",
                "error": None
            }
        }

class ForgeBuildResult(BaseModel):
    """
    Schema for FORGE build results.
    
    This schema defines the structure of responses from the FORGE agent after
    building system components.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    loop_id: str = Field(..., description="Unique identifier for the current loop")
    components_built: List[ComponentBuildResult] = Field(..., description="List of component build results")
    files_created: List[str] = Field(..., description="List of all files created")
    manifest_updated: bool = Field(..., description="Whether the system manifest was updated")
    routes_registered: List[str] = Field(..., description="List of routes registered")
    version: str = Field(..., description="Version of the build")
    status: str = Field(..., description="Overall status of the build (success, partial, failed)")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp of the build")
    error: Optional[str] = Field(None, description="Error message if build failed")
    next_steps: Optional[List[str]] = Field(None, description="Recommended next steps")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "demo_writer_001",
                "loop_id": "loop_17",
                "components_built": [
                    {
                        "component_name": "api",
                        "files_created": ["api_module.py", "api_routes.py"],
                        "status": "success",
                        "error": None
                    },
                    {
                        "component_name": "schema",
                        "files_created": ["api_schema.py"],
                        "status": "success",
                        "error": None
                    },
                    {
                        "component_name": "test",
                        "files_created": ["test_api.py"],
                        "status": "success",
                        "error": None
                    }
                ],
                "files_created": ["api_module.py", "api_routes.py", "api_schema.py", "test_api.py"],
                "manifest_updated": True,
                "routes_registered": ["/api/new_endpoint"],
                "version": "1.0",
                "status": "success",
                "timestamp": "2025-04-24T18:55:00.000000",
                "error": None,
                "next_steps": ["Run tests", "Deploy to staging"]
            }
        }

class ForgeRevisionRequest(BaseModel):
    """
    Schema for FORGE revision requests.
    
    This schema defines the structure of requests to the FORGE agent for revising
    previously built components.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    loop_id: str = Field(..., description="Unique identifier for the current loop")
    components: List[str] = Field(..., description="List of components to revise")
    previous_version: str = Field(..., description="Previous version of the build")
    new_version: str = Field(..., description="New version for the revised build")
    revision_reason: str = Field(..., description="Reason for the revision")
    critic_feedback_tag: Optional[str] = Field(None, description="Memory tag for CRITIC's feedback")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "demo_writer_001",
                "loop_id": "loop_17",
                "components": ["api", "schema"],
                "previous_version": "1.0",
                "new_version": "1.1",
                "revision_reason": "Performance optimization",
                "critic_feedback_tag": "critic_feedback_loop_17"
            }
        }

class ForgeRevisionResult(BaseModel):
    """
    Schema for FORGE revision results.
    
    This schema defines the structure of responses from the FORGE agent after
    revising system components.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    loop_id: str = Field(..., description="Unique identifier for the current loop")
    components_revised: List[ComponentBuildResult] = Field(..., description="List of component revision results")
    files_modified: List[str] = Field(..., description="List of files modified")
    files_created: List[str] = Field(..., description="List of new files created")
    manifest_updated: bool = Field(..., description="Whether the system manifest was updated")
    previous_version: str = Field(..., description="Previous version of the build")
    new_version: str = Field(..., description="New version of the build")
    status: str = Field(..., description="Overall status of the revision (success, partial, failed)")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp of the revision")
    error: Optional[str] = Field(None, description="Error message if revision failed")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "demo_writer_001",
                "loop_id": "loop_17",
                "components_revised": [
                    {
                        "component_name": "api",
                        "files_created": ["api_module.v1.1.py"],
                        "status": "success",
                        "error": None
                    },
                    {
                        "component_name": "schema",
                        "files_created": ["api_schema.v1.1.py"],
                        "status": "success",
                        "error": None
                    }
                ],
                "files_modified": ["api_module.py", "api_schema.py"],
                "files_created": ["api_module.v1.1.py", "api_schema.v1.1.py"],
                "manifest_updated": True,
                "previous_version": "1.0",
                "new_version": "1.1",
                "status": "success",
                "timestamp": "2025-04-24T19:30:00.000000",
                "error": None
            }
        }
