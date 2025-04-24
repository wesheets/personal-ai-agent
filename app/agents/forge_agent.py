"""
FORGE Agent Module

This module implements the FORGE agent, which acts as the deep system builder
in the Promethios architecture. It handles building system components, registering routes,
and managing project state.
"""

import os
import json
import logging
import traceback
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import schemas
from app.schemas.forge_schema import ForgeBuildRequest, ForgeBuildResult, ComponentBuildResult

# Import memory operations
from app.modules.memory_writer import write_memory, read_memory
from app.modules.orchestrator_memory_enhanced import log_loop_event

# Import project state operations
from app.modules.project_state import read_project_state, update_project_state

# Import manifest operations
from app.utils.manifest_manager import update_manifest, register_schema, register_route, register_module

# Import snapshot operations
from app.utils.snapshot_manager import create_recovery_snapshot

# Configure logging
logger = logging.getLogger("app.agents.forge")

class ForgeAgent:
    """
    FORGE Agent implementation.
    
    This agent acts as the deep system builder, creating endpoints, schemas, modules,
    registering routes, and managing project state.
    """
    
    def __init__(self):
        """Initialize the FORGE Agent with required configuration."""
        self.name = "forge-agent"
        self.role = "Deep System Builder"
        self.tools = ["scaffold", "wire", "register", "test", "validate", "patch", "version_track"]
        self.permissions = ["read_memory", "write_memory", "update_manifest", "register_routes"]
        self.description = "Deep system builder agent responsible for creating endpoints, schemas, modules, and registering routes"
        self.version = "1.0.0"
        self.status = "active"
        self.tone_profile = {
            "style": "technical",
            "emotion": "neutral",
            "vibe": "builder",
            "persona": "Efficient system architect with a focus on integration and compliance"
        }
        self.schema_path = "schemas/forge_schema.py"
        self.trust_score = 0.95
        self.contract_version = "1.0.0"
    
    async def execute(self, 
                request: ForgeBuildRequest) -> ForgeBuildResult:
        """
        Execute the FORGE Agent's main functionality.
        
        Args:
            request: The build request containing project_id, loop_id, and components to build
            
        Returns:
            ForgeBuildResult containing the results of the build operation
        """
        try:
            logger.info(f"Running FORGE agent with project_id: {request.project_id}, loop_id: {request.loop_id}")
            print(f"🔨 FORGE agent building components {request.components} for project '{request.project_id}', loop '{request.loop_id}'")
            
            # Create a recovery snapshot before starting
            await create_recovery_snapshot(
                loop_id=request.loop_id,
                notes=f"Before FORGE build v{request.version}"
            )
            
            # Log the start of the build operation
            await log_loop_event(
                loop_id=request.loop_id,
                project_id=request.project_id,
                agent="forge",
                task="build_system_components",
                result_tag=f"forge_build_log_{request.loop_id}_v{request.version}",
                status="in_progress",
                additional_data={"components": request.components, "version": request.version}
            )
            
            # Read project state
            project_state = read_project_state(request.project_id)
            
            # Read HAL's result if available
            hal_result = None
            hal_result_tag = request.hal_result_tag or f"hal_build_task_response_{request.loop_id}"
            try:
                hal_result = await read_memory(
                    project_id=request.project_id,
                    tag=hal_result_tag
                )
                logger.info(f"✅ Read HAL result from {hal_result_tag}")
            except Exception as e:
                logger.warning(f"⚠️ Could not read HAL result: {str(e)}")
            
            # Build each component
            components_built = []
            all_files_created = []
            all_routes_registered = []
            overall_status = "success"
            error_message = None
            
            for component in request.components:
                try:
                    # Build the component
                    component_result = await self._build_component(
                        component=component,
                        project_id=request.project_id,
                        loop_id=request.loop_id,
                        version=request.version,
                        hal_result=hal_result
                    )
                    
                    # Add to results
                    components_built.append(component_result)
                    all_files_created.extend(component_result.files_created)
                    
                    # Check if any routes were registered
                    if hasattr(component_result, "routes_registered"):
                        all_routes_registered.extend(component_result.routes_registered)
                    
                    # Update overall status if component build failed
                    if component_result.status == "failed":
                        overall_status = "partial"
                        if error_message is None:
                            error_message = f"Failed to build component {component}: {component_result.error}"
                    
                    logger.info(f"✅ Built component {component} with status {component_result.status}")
                except Exception as e:
                    # Log component build failure
                    error = f"Error building component {component}: {str(e)}"
                    logger.error(f"❌ {error}")
                    logger.error(traceback.format_exc())
                    
                    # Add failed component to results
                    components_built.append(ComponentBuildResult(
                        component_name=component,
                        files_created=[],
                        status="failed",
                        error=error
                    ))
                    
                    # Update overall status
                    overall_status = "partial"
                    if error_message is None:
                        error_message = error
            
            # Update project state
            try:
                await update_project_state(
                    project_id=request.project_id,
                    patch_dict={
                        "files_created": all_files_created,
                        "latest_agent_action": f"Built system components: {', '.join(request.components)}",
                        "next_recommended_step": "Run tests on new components",
                        "forge_version": request.version,
                        "revision_history": project_state.get("revision_history", []) + [
                            {"version": request.version, "timestamp": datetime.utcnow().isoformat()}
                        ]
                    }
                )
                logger.info(f"✅ Updated project state for {request.project_id}")
            except Exception as e:
                logger.error(f"❌ Error updating project state: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Update overall status
                overall_status = "partial"
                if error_message is None:
                    error_message = f"Error updating project state: {str(e)}"
            
            # Create build result
            build_result = ForgeBuildResult(
                project_id=request.project_id,
                loop_id=request.loop_id,
                components_built=components_built,
                files_created=all_files_created,
                manifest_updated=True,
                routes_registered=all_routes_registered,
                version=request.version,
                status=overall_status,
                timestamp=datetime.utcnow().isoformat(),
                error=error_message,
                next_steps=["Run tests on new components", "Review system integration"]
            )
            
            # Log the build result
            await write_memory(
                project_id=request.project_id,
                tag=f"forge_build_log_{request.loop_id}_v{request.version}",
                value=build_result.dict()
            )
            
            # Log the completion of the build operation
            await log_loop_event(
                loop_id=request.loop_id,
                project_id=request.project_id,
                agent="forge",
                task="build_system_components",
                result_tag=f"forge_build_log_{request.loop_id}_v{request.version}",
                status="completed",
                additional_data={
                    "components": request.components,
                    "version": request.version,
                    "build_status": overall_status,
                    "files_created": all_files_created
                }
            )
            
            logger.info(f"✅ FORGE agent completed build with status {overall_status}")
            return build_result
            
        except Exception as e:
            error_msg = f"Error running FORGE agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            
            # Try to log the error
            try:
                await log_loop_event(
                    loop_id=request.loop_id,
                    project_id=request.project_id,
                    agent="forge",
                    task="build_system_components",
                    result_tag=f"forge_build_log_{request.loop_id}_v{request.version}",
                    status="failed",
                    additional_data={"error": error_msg}
                )
            except Exception as log_error:
                logger.error(f"❌ Error logging failure: {str(log_error)}")
            
            # Return error response that will pass schema validation
            return ForgeBuildResult(
                project_id=request.project_id,
                loop_id=request.loop_id,
                components_built=[],
                files_created=[],
                manifest_updated=False,
                routes_registered=[],
                version=request.version,
                status="failed",
                timestamp=datetime.utcnow().isoformat(),
                error=error_msg,
                next_steps=["Review error logs", "Retry with simplified components"]
            )
    
    async def _build_component(self, 
                        component: str,
                        project_id: str,
                        loop_id: str,
                        version: str,
                        hal_result: Optional[Dict[str, Any]] = None) -> ComponentBuildResult:
        """
        Build a specific component.
        
        Args:
            component: The component to build (e.g., "api", "schema", "test")
            project_id: The project identifier
            loop_id: The loop identifier
            version: The version of the build
            hal_result: Optional HAL result to use as input
            
        Returns:
            ComponentBuildResult containing the result of the component build
        """
        # Initialize result
        files_created = []
        routes_registered = []
        
        # Build different components based on type
        if component == "api":
            # Build API component
            api_module_path = f"/home/ubuntu/personal-ai-agent/app/api/modules/{project_id}_api.py"
            api_routes_path = f"/home/ubuntu/personal-ai-agent/app/api/routes/{project_id}_routes.py"
            
            # Create API module
            with open(api_module_path, "w") as f:
                f.write(f'''"""
API Module for {project_id}

This module provides API functionality for the {project_id} project.
Generated by FORGE v{version} on {datetime.utcnow().isoformat()}
"""

import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("app.api.modules.{project_id}_api")

async def process_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an API request.
    
    Args:
        data: The request data
        
    Returns:
        Dict containing the response data
    """
    try:
        logger.info(f"Processing API request for {project_id}")
        
        # Process the request
        result = {{
            "status": "success",
            "message": f"Request processed successfully for {project_id}",
            "data": data
        }}
        
        return result
    except Exception as e:
        logger.error(f"Error processing API request: {{str(e)}}")
        return {{
            "status": "error",
            "message": f"Error processing request: {{str(e)}}"
        }}
''')
            files_created.append(api_module_path)
            
            # Create API routes
            with open(api_routes_path, "w") as f:
                f.write(f'''"""
API Routes for {project_id}

This module defines the API routes for the {project_id} project.
Generated by FORGE v{version} on {datetime.utcnow().isoformat()}
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

# Import API module
from app.api.modules.{project_id}_api import process_request

# Create router
router = APIRouter(tags=["{project_id}"])

class {project_id.capitalize()}Request(BaseModel):
    """Request model for {project_id} API."""
    data: Dict[str, Any]

class {project_id.capitalize()}Response(BaseModel):
    """Response model for {project_id} API."""
    status: str
    message: str
    data: Dict[str, Any]

@router.post("/{project_id}/process", response_model={project_id.capitalize()}Response)
async def process_{project_id}_request(request: {project_id.capitalize()}Request):
    """
    Process a request for the {project_id} project.
    
    Args:
        request: The request data
        
    Returns:
        Response containing the processed data
    """
    try:
        result = await process_request(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {{str(e)}}")
''')
            files_created.append(api_routes_path)
            
            # Register route
            register_route(
                route_path=f"/{project_id}/process",
                method="POST",
                schema_name=f"{project_id.capitalize()}Request",
                status="registered"
            )
            routes_registered.append(f"/{project_id}/process")
            
            # Register module
            register_module(
                module_name=f"{project_id}_api",
                file_path=f"app/api/modules/{project_id}_api.py",
                wrapped_with_schema=True
            )
            
            return ComponentBuildResult(
                component_name=component,
                files_created=files_created,
                status="success",
                error=None
            )
            
        elif component == "schema":
            # Build schema component
            schema_path = f"/home/ubuntu/personal-ai-agent/app/schemas/{project_id}_schema.py"
            
            # Create schema file
            with open(schema_path, "w") as f:
                f.write(f'''"""
Schema Module for {project_id}

This module defines the schemas for the {project_id} project.
Generated by FORGE v{version} on {datetime.utcnow().isoformat()}
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class {project_id.capitalize()}BaseSchema(BaseModel):
    """Base schema for {project_id} project."""
    project_id: str = Field(..., description="Project identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp")

class {project_id.capitalize()}RequestSchema(BaseModel):
    """Request schema for {project_id} project."""
    data: Dict[str, Any] = Field(..., description="Request data")
    options: Optional[Dict[str, Any]] = Field(None, description="Optional request options")
    
    class Config:
        schema_extra = {{
            "example": {{
                "data": {{"key": "value"}},
                "options": {{"option1": True}}
            }}
        }}

class {project_id.capitalize()}ResponseSchema(BaseModel):
    """Response schema for {project_id} project."""
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Response data")
    
    class Config:
        schema_extra = {{
            "example": {{
                "status": "success",
                "message": "Request processed successfully",
                "data": {{"result": "value"}}
            }}
        }}
''')
            files_created.append(schema_path)
            
            # Register schema
            register_schema(
                schema_name=f"{project_id.capitalize()}RequestSchema",
                file_path=f"app/schemas/{project_id}_schema.py",
                routes=[f"/{project_id}/process"],
                version="v1.0.0"
            )
            
            register_schema(
                schema_name=f"{project_id.capitalize()}ResponseSchema",
                file_path=f"app/schemas/{project_id}_schema.py",
                routes=[f"/{project_id}/process"],
                version="v1.0.0"
            )
            
            return ComponentBuildResult(
                component_name=component,
                files_created=files_created,
                status="success",
                error=None
            )
            
        elif component == "test":
            # Build test component
            test_path = f"/home/ubuntu/personal-ai-agent/app/tests/test_{project_id}_api.py"
            
            # Create test file
            with open(test_path, "w") as f:
                f.write(f'''"""
Test Module for {project_id} API

This module provides tests for the {project_id} API.
Generated by FORGE v{version} on {datetime.utcnow().isoformat()}
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_{project_id}_api_success():
    """Test successful API request."""
    # Prepare test data
    test_data = {{"data": {{"key": "value"}}}}
    
    # Send request
    response = client.post("/{project_id}/process", json=test_data)
    
    # Check response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "data" in response.json()
    assert response.json()["data"]["key"] == "value"

def test_{project_id}_api_validation():
    """Test API request validation."""
    # Prepare invalid test data
    test_data = {{"invalid_field": "value"}}
    
    # Send request
    response = client.post("/{project_id}/process", json=test_data)
    
    # Check response
    assert response.status_code == 422  # Validation error
''')
            files_created.append(test_path)
            
            return ComponentBuildResult(
                component_name=component,
                files_created=files_created,
                status="success",
                error=None
            )
            
        else:
            # Unknown component
            return ComponentBuildResult(
                component_name=component,
                files_created=[],
                status="failed",
                error=f"Unknown component type: {component}"
            )

# Function to run FORGE agent (for backward compatibility)
async def run_forge_agent(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the FORGE Agent with the given request.
    
    Args:
        request: The request data
        
    Returns:
        Dict containing the result of the execution
    """
    # Create FORGE agent instance
    forge_agent = ForgeAgent()
    
    # Convert request to ForgeBuildRequest
    build_request = ForgeBuildRequest(**request)
    
    # Execute the request
    result = await forge_agent.execute(build_request)
    
    # Convert result to dict if it's not already
    if hasattr(result, "dict"):
        return result.dict()
    return result
