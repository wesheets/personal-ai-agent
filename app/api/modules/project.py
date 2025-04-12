"""
Project management module for the Promethios system.

This module provides REST API endpoints for managing projects, including:
- Initiating new projects with goals and agent assignments
- Storing project metadata in memory
- Triggering plan generation for project goals
- Retrieving project history and memory entries
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import uuid
import httpx
import asyncio
import os
from datetime import datetime

# Import project models
from app.api.modules.project_models import ProjectInitiateRequest, ProjectInitiateResponse

# Import memory and plan modules for integration
from app.api.modules.memory import write_memory
from app.db.memory_db import memory_db
from app.api.modules.plan_models import UserGoalPlanRequest

# Configure logging
logger = logging.getLogger("api.modules.project")

# Configure environment-based URL for plan generation
# Default to localhost for local development, but allow override via environment variable
PLAN_GENERATION_URL = os.getenv("PLAN_GENERATION_URL", "http://localhost:8000/api/modules/plan/user-goal")

# Create router
router = APIRouter()

@router.post("/initiate")
async def project_initiate(request: ProjectInitiateRequest):
    """
    Initiate a new project with associated goals, memory scopes, and agent assignments.
    
    This endpoint serves as the official starting point for any SaaS deployment, user journey, 
    or long-term goal. It registers new projects, assigns agents, sets memory scope, and 
    optionally triggers planning sequences.
    
    Parameters:
    - user_id: ID of the user initiating the project
    - project_name: Name of the project
    - goal: Main goal or objective of the project
    - agent_id: ID of the agent assigned to the project
    
    Returns:
    - status: "ok" if successful
    - project_id: Unique identifier for the project
    - goal_id: Unique identifier for the project goal
    - agent_id: ID of the agent assigned to the project
    """
    try:
        logger.info(f"🚀 Initiating new project for user {request.user_id}: {request.project_name}")
        
        # Generate unique IDs
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        
        # Create timestamp
        created_at = datetime.utcnow().isoformat()
        
        # Define memory scope
        memory_scope = f"user:{request.user_id}:project:{project_id}"
        
        # Create project metadata
        project_metadata = {
            "project_id": project_id,
            "project_name": request.project_name,
            "user_id": request.user_id,
            "agent_id": request.agent_id,
            "created_at": created_at,
            "memory_scope": memory_scope,
            "goal_id": goal_id
        }
        
        # Write project registration to memory
        project_memory = write_memory(
            agent_id=request.agent_id,
            type="project_registration",
            content=f"Project '{request.project_name}' initiated by user {request.user_id}",
            tags=["project", "registration", memory_scope],
            project_id=project_id,
            status="active",
            metadata=project_metadata
        )
        
        # Write goal definition to memory
        goal_memory = write_memory(
            agent_id=request.agent_id,
            type="goal_definition",
            content=request.goal,
            tags=["goal", "definition", memory_scope],
            project_id=project_id,
            task_id=goal_id,
            metadata={
                "goal_id": goal_id,
                "project_id": project_id,
                "user_id": request.user_id,
                "agent_id": request.agent_id,
                "created_at": created_at
            }
        )
        
        logger.info(f"✅ Project initiated: {project_id}, Goal: {goal_id}")
        
        # Trigger plan generation asynchronously
        asyncio.create_task(trigger_plan_generation(
            user_id=request.user_id,
            goal=request.goal,
            project_id=project_id,
            goal_id=goal_id
        ))
        
        # Return response
        return ProjectInitiateResponse(
            status="ok",
            project_id=project_id,
            goal_id=goal_id,
            agent_id=request.agent_id
        )
    except Exception as e:
        logger.error(f"❌ Error initiating project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating project: {str(e)}")

@router.get("/history")
async def project_history(
    project_id: str = Query(..., description="ID of the project to retrieve history for"),
    memory_type: Optional[str] = Query(None, description="Filter by memory type (e.g., task_plan, task_result, feedback_summary)"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: Optional[int] = Query(100, description="Maximum number of memories to return"),
    sort: Optional[str] = Query("timestamp", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Retrieve all memory entries linked to a specific project_id.
    
    This endpoint returns a chronological list of memory entries associated with a project,
    with optional filtering by memory type, agent ID, user ID, and other parameters.
    
    Parameters:
    - project_id: (Required) ID of the project to retrieve history for
    - memory_type: (Optional) Filter by memory type (e.g., task_plan, task_result, feedback_summary)
    - agent_id: (Optional) Filter by agent ID
    - user_id: (Optional) Filter by user ID
    - limit: (Optional) Maximum number of memories to return, default is 100
    - sort: (Optional) Field to sort by, default is "timestamp"
    - order: (Optional) Sort order (asc or desc), default is "asc"
    
    Returns:
    - status: "ok" if successful
    - project_id: ID of the project
    - memories: List of memory entries in chronological order
    """
    try:
        logger.info(f"📚 Retrieving history for project {project_id}")
        
        # Validate sort field
        valid_sort_fields = ["timestamp", "type", "memory_id"]
        if sort not in valid_sort_fields:
            sort = "timestamp"  # Default to timestamp if invalid sort field
        
        # Validate order
        valid_orders = ["asc", "desc"]
        if order not in valid_orders:
            order = "asc"  # Default to ascending if invalid order
        
        # Query memories from database
        try:
            # First, ensure we have a fresh connection
            memory_db.close()  # Close any existing connection
            # Get a new connection
            conn = memory_db._get_connection()
            
            # Query memories by project_id
            memories = memory_db.read_memories(
                project_id=project_id,
                memory_type=memory_type,
                agent_id=agent_id,
                limit=limit
            )
            
            # Filter by user_id if provided (since user_id is stored in tags)
            if user_id:
                user_tag = f"user:{user_id}"
                memories = [m for m in memories if any(user_tag in tag for tag in m.get("tags", []))]
            
            # Sort memories
            if sort == "timestamp":
                memories.sort(key=lambda x: x.get("timestamp", ""), reverse=(order == "desc"))
            elif sort == "type":
                memories.sort(key=lambda x: x.get("type", ""), reverse=(order == "desc"))
            elif sort == "memory_id":
                memories.sort(key=lambda x: x.get("memory_id", ""), reverse=(order == "desc"))
            
            # Format memories for response
            formatted_memories = []
            for memory in memories:
                formatted_memory = {
                    "type": memory.get("type"),
                    "timestamp": memory.get("timestamp"),
                    "content": memory.get("content")
                }
                
                # Add task_id if available
                if memory.get("task_id"):
                    formatted_memory["task_id"] = memory.get("task_id")
                
                # Add result if available in metadata
                if memory.get("metadata") and "result" in memory.get("metadata"):
                    formatted_memory["result"] = memory.get("metadata").get("result")
                
                # Add metadata if available
                if memory.get("metadata"):
                    formatted_memory["metadata"] = memory.get("metadata")
                
                formatted_memories.append(formatted_memory)
            
            logger.info(f"✅ Retrieved {len(formatted_memories)} memories for project {project_id}")
            
            # Return response
            return JSONResponse(status_code=200, content={
                "status": "ok",
                "project_id": project_id,
                "memories": formatted_memories
            })
        except Exception as e:
            logger.error(f"❌ Error querying memories: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error querying memories: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error retrieving project history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving project history: {str(e)}")

async def trigger_plan_generation(user_id: str, goal: str, project_id: str, goal_id: str):
    """
    Trigger plan generation for a project goal.
    
    This function makes an asynchronous HTTP request to the plan/user-goal endpoint
    to generate a plan for the specified goal.
    
    Parameters:
    - user_id: ID of the user
    - goal: The goal to plan for
    - project_id: ID of the project
    - goal_id: ID of the goal
    """
    try:
        # Create plan request
        plan_request = UserGoalPlanRequest(
            user_id=user_id,
            goal=goal,
            project_id=project_id,
            goal_id=goal_id
        )
        
        # Log the URL being used for plan generation
        logger.info(f"🔌 Using plan generation URL: {PLAN_GENERATION_URL}")
        
        # Make async request to plan endpoint using environment-based URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    PLAN_GENERATION_URL,
                    json=plan_request.dict()
                )
                
                # Log result
                if response.status_code == 200:
                    logger.info(f"✅ Plan generation triggered successfully for goal {goal_id}")
                    # Log response data for debugging
                    try:
                        response_data = response.json()
                        logger.info(f"📋 Plan generation response: {response_data}")
                    except Exception as json_err:
                        logger.warning(f"⚠️ Could not parse plan response as JSON: {str(json_err)}")
                else:
                    logger.warning(f"⚠️ Plan generation failed for goal {goal_id}: Status {response.status_code}, Response: {response.text}")
            except httpx.RequestError as req_err:
                logger.error(f"❌ HTTP request error during plan generation: {str(req_err)}")
            except httpx.TimeoutException:
                logger.error(f"⏱️ Timeout while waiting for plan generation response")
    except Exception as e:
        logger.error(f"❌ Error triggering plan generation: {str(e)}")
        # Log the full error traceback for better debugging
        import traceback
        logger.error(f"❌ Error details: {traceback.format_exc()}")
