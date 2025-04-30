"""
Orchestrator Build Module - Task Plan Executor

This module provides the /api/modules/orchestrator/build endpoint for executing pre-generated task plans
by dynamically assigning each task to an agent based on skill match and availability.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import logging
import asyncio

# Import memory-related functions
from app.api.modules.memory import write_memory

# Import agent verification function
from app.modules.agent_verify import verify_task as verify_agent_for_task

# Import delegation function
from app.modules.agent_fallback import delegate_task_internal

# Configure logging
logger = logging.getLogger("api.modules.orchestrator_build")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/modules/orchestrator/build -> execute_task_plan")

# Define the models
class TaskDefinition(BaseModel):
    """Model for a task in the build request"""
    task_id: str
    description: str
    required_skills: List[str]

class BuildRequest(BaseModel):
    """Request model for the build endpoint"""
    plan_id: str
    tasks: List[TaskDefinition]
    project_id: Optional[str] = None

class DelegatedTask(BaseModel):
    """Model for a delegated task in the build response"""
    task_id: str
    assigned_agent: str
    delegation_task_id: str

class BuildResponse(BaseModel):
    """Response model for the build endpoint"""
    status: str = "executing"
    delegated_tasks: List[DelegatedTask]
    memory_id: str

@router.post("/build", response_model=BuildResponse)
async def execute_task_plan(request: Request):
    """
    Execute a pre-generated task plan by dynamically assigning each task to an agent.
    
    This endpoint takes a plan with multiple tasks and assigns each task to the most
    suitable agent based on skill match and availability.
    
    Request body:
    - plan_id: ID of the plan to execute
    - tasks: List of tasks with task_id, description, and required_skills
    - project_id: (Optional) Project ID for context
    
    Returns:
    - status: "executing" if the plan is being executed
    - delegated_tasks: List of delegated tasks with task_id, assigned_agent, and delegation_task_id
    - memory_id: ID of the memory entry for the build log
    """
    try:
        # Parse request body
        body = await request.json()
        build_request = BuildRequest(**body)
        
        # Initialize response
        delegated_tasks = []
        unassigned_tasks = []
        
        # Process each task in the plan
        for task in build_request.tasks:
            # Find the best agent for the task
            agent_result = await find_best_agent_for_task(task)
            
            if agent_result["qualified"]:
                # Delegate the task to the agent
                delegation_result = await delegate_task_to_agent(
                    from_agent="orchestrator",
                    to_agent=agent_result["agent_id"],
                    task_id=task.task_id,
                    description=task.description,
                    project_id=build_request.project_id
                )
                
                if delegation_result["status"] == "ok":
                    # Add to delegated tasks
                    delegated_tasks.append(DelegatedTask(
                        task_id=task.task_id,
                        assigned_agent=agent_result["agent_id"],
                        delegation_task_id=delegation_result["task_id"]
                    ))
                else:
                    # Add to unassigned tasks
                    unassigned_tasks.append({
                        "task_id": task.task_id,
                        "reason": f"Delegation failed: {delegation_result.get('log', 'Unknown error')}"
                    })
            else:
                # No qualified agent found
                unassigned_tasks.append({
                    "task_id": task.task_id,
                    "reason": f"No qualified agent found: {agent_result.get('justification', 'Unknown reason')}"
                })
        
        # Create build log content
        build_log_content = {
            "plan_id": build_request.plan_id,
            "delegated_tasks": [task.dict() for task in delegated_tasks],
            "unassigned_tasks": unassigned_tasks,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Write build log to memory
        memory = write_memory(
            agent_id="orchestrator",
            type="build_log",
            content=json.dumps(build_log_content),
            tags=["build_log", f"plan:{build_request.plan_id}"],
            project_id=build_request.project_id,
            status="executing",
            task_type="build",
            task_id=build_request.plan_id
        )
        
        # Return the response
        return BuildResponse(
            status="executing" if delegated_tasks else "failed",
            delegated_tasks=delegated_tasks,
            memory_id=memory["memory_id"]
        )
    except Exception as e:
        logger.error(f"Error executing task plan: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error executing task plan: {str(e)}"
            }
        )

async def find_best_agent_for_task(task: TaskDefinition) -> Dict[str, Any]:
    """
    Find the best agent for a task based on skill match.
    
    Args:
        task: Task definition with description and required skills
        
    Returns:
        Dictionary with agent verification result
    """
    try:
        # Create verification request
        verification_request = {
            "agent_id": "hal",  # Start with HAL as default
            "task_description": task.description,
            "required_skills": task.required_skills
        }
        
        # Verify if HAL is qualified
        hal_result = await verify_agent_for_task(verification_request)
        
        # If HAL is qualified with high confidence, use HAL
        if hal_result.qualified and hal_result.confidence_score >= 0.7:
            return hal_result.dict()
        
        # If HAL suggested alternative agents, check them
        if hal_result.suggested_agents:
            for agent_id in hal_result.suggested_agents:
                # Create verification request for alternative agent
                alt_verification_request = {
                    "agent_id": agent_id,
                    "task_description": task.description,
                    "required_skills": task.required_skills
                }
                
                # Verify if alternative agent is qualified
                alt_result = await verify_agent_for_task(alt_verification_request)
                
                # If alternative agent is qualified with higher confidence than HAL, use alternative agent
                if alt_result.qualified and alt_result.confidence_score > hal_result.confidence_score:
                    return alt_result.dict()
        
        # If no better agent found, return HAL's result
        return hal_result.dict()
    except Exception as e:
        logger.error(f"Error finding best agent: {str(e)}")
        return {
            "qualified": False,
            "agent_id": "hal",
            "confidence_score": 0.0,
            "justification": f"Error finding best agent: {str(e)}"
        }

async def delegate_task_to_agent(from_agent: str, to_agent: str, task_id: str, description: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Delegate a task to an agent.
    
    Args:
        from_agent: ID of the agent delegating the task
        to_agent: ID of the agent receiving the task
        task_id: ID of the task
        description: Description of the task
        project_id: (Optional) Project ID for context
        
    Returns:
        Dictionary with delegation result
    """
    try:
        # Delegate the task
        delegation_result = await delegate_task_internal(
            from_agent=from_agent,
            to_agent=to_agent,
            task_id=task_id,
            notes=description,
            project_id=project_id
        )
        
        return delegation_result
    except Exception as e:
        logger.error(f"Error delegating task: {str(e)}")
        return {
            "status": "error",
            "log": f"Error delegating task: {str(e)}"
        }
