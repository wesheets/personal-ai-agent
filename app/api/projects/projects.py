"""
Projects module implementation for Promethios.

This module provides endpoints for creating and querying project containers
as part of the System Lockdown Phase.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import uuid
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("projects")

# Import memory writer
sys.path.append('/home/ubuntu/personal-ai-agent')
from app.modules.memory_writer import write_memory

# Create router
router = APIRouter()

# In-memory storage for projects (will be replaced with proper storage in production)
projects_store = []

# Input and output schemas
class ProjectInput(BaseModel):
    project_id: str
    goal: str
    user_id: str
    tags: Optional[List[str]] = []
    context: Optional[str] = None

class ProjectOutput(BaseModel):
    status: str = "success"
    project_id: str
    created_at: str
    log_id: str
    stored: bool = True

@router.post("/")
async def create_project(request: Request):
    """
    Create a new project container for orchestrated goals.
    
    This endpoint complies with Promethios_Module_Contract_v1.0.0 by:
    - Validating required input fields (project_id, goal, user_id)
    - Returning a structured response with all required fields
    - Writing memory with memory_type="project_meta" and all trace fields
    - Providing proper logging for failures or validation errors
    
    Request body:
    - project_id: Unique identifier for the project (required)
    - goal: Main objective of the project (required)
    - user_id: Identifier of the user who owns the project (required)
    - tags: List of tags for categorizing the project (optional)
    - context: Summary or notes about the project (optional)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - project_id: Project identifier (echoed from request)
    - created_at: Timestamp of project creation
    - log_id: Unique identifier for the log entry
    - stored: Whether the project was stored successfully
    """
    try:
        # Parse request body
        body = await request.json()
        project_input = ProjectInput(**body)
        
        # Generate log_id
        log_id = str(uuid.uuid4())
        
        # Set timestamp
        created_at = datetime.utcnow().isoformat()
        
        # Create project entry
        project_entry = {
            "project_id": project_input.project_id,
            "goal": project_input.goal,
            "user_id": project_input.user_id,
            "tags": project_input.tags,
            "context": project_input.context,
            "created_at": created_at
        }
        
        # Store project entry in memory
        projects_store.append(project_entry)
        
        # Write to memory with proper metadata
        memory = write_memory(
            agent_id=project_input.user_id,  # Using user_id as agent_id for project metadata
            type="project_meta",
            content=f"Project {project_input.project_id} created with goal: {project_input.goal}" + 
                    (f" Context: {project_input.context}" if project_input.context else ""),
            tags=["project", "meta", "sdk_compliant"] + (project_input.tags if project_input.tags else []),
            project_id=project_input.project_id,
            status="active"
        )
        
        # Log success
        logger.info(f"✅ Project created: {project_input.project_id} for user {project_input.user_id}")
        
        # Return response
        return ProjectOutput(
            status="success",
            project_id=project_input.project_id,
            created_at=created_at,
            log_id=log_id,
            stored=True
        )
    except Exception as e:
        # Log error
        logger.error(f"❌ Error creating project: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "failure",
                "project_id": body.get("project_id", "unknown"),
                "created_at": datetime.utcnow().isoformat(),
                "log_id": str(uuid.uuid4()),
                "stored": False,
                "error": str(e)
            }
        )

@router.get("/")
async def get_projects(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)")
):
    """
    Query projects by various parameters.
    
    This endpoint allows filtering projects by project_id, user_id, or tags.
    
    Query parameters:
    - project_id: Filter by project ID (optional)
    - user_id: Filter by user ID (optional)
    - tags: Filter by tags, comma-separated (optional)
    
    Returns:
    - List of matching project metadata
    """
    try:
        # Filter projects based on query parameters
        filtered_projects = projects_store
        
        if project_id:
            filtered_projects = [proj for proj in filtered_projects if proj["project_id"] == project_id]
        
        if user_id:
            filtered_projects = [proj for proj in filtered_projects if proj["user_id"] == user_id]
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            filtered_projects = [
                proj for proj in filtered_projects 
                if any(tag in proj["tags"] for tag in tag_list)
            ]
        
        # Log query
        logger.info(f"📊 Projects query returned {len(filtered_projects)} results")
        
        # Return response
        return filtered_projects
    except Exception as e:
        # Log error
        logger.error(f"❌ Error querying projects: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "failure",
                "error": str(e)
            }
        )
