"""
Orchestrator Start Project Module - Multi-Agent Project Initializer

This module provides the /api/orchestrator/start-project endpoint for initializing
a new project with a goal, executing a chain of agents (HAL, ASH, NOVA, CRITIC),
and storing all agent outputs in a single batched memory thread.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import logging
from datetime import datetime

# Import memory-related functions
from app.modules.memory_thread import thread_memory
from app.utils.chain_runner import run_internal_chain

# Configure logging
logger = logging.getLogger("api.modules.orchestrator.start_project")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/orchestrator/start-project -> start_project")

class ProjectStartRequest(BaseModel):
    """Request model for the start-project endpoint"""
    project_id: str
    goal: str

@router.post("/start-project")
async def start_project(request: Request):
    """
    Start a new project with orchestrated memory batching.
    
    This endpoint transforms a user goal into a multi-agent instruction chain
    involving HAL, ASH, NOVA, and CRITIC. It executes the chain and stores
    all agent outputs in a single batched memory thread.
    
    Args:
        request: The FastAPI request object containing the project_id and goal
        
    Returns:
        dict: Project information including project_id, chain_id, and agent results
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Validate request
        if not isinstance(body, dict) or "project_id" not in body or "goal" not in body:
            raise HTTPException(status_code=400, detail="Request must include 'project_id' and 'goal' fields")
        
        project_id = body["project_id"]
        goal = body["goal"]
        
        # Generate chain_id
        chain_id = f"chain-{str(uuid.uuid4())[:8]}"
        
        # Log project start
        logger.info(f"Starting new project: Project ID: {project_id}, Chain ID: {chain_id}, Goal: {goal}")
        
        # Generate instruction chain
        instruction_chain = [
            {
                "agent": "hal",
                "goal": goal,
                "expected_outputs": ["task.output"],
                "checkpoints": ["reflection"],
                "project_id": project_id
            },
            {
                "agent": "ash",
                "goal": "Summarize HAL's output and explain the approach",
                "expected_outputs": ["summary.task.output"],
                "checkpoints": ["reflection"],
                "project_id": project_id
            },
            {
                "agent": "nova",
                "goal": "Design a simple HTML block or text output that reflects HAL's result",
                "expected_outputs": ["ui.preview"],
                "checkpoints": ["reflection"],
                "project_id": project_id
            },
            {
                "agent": "critic",
                "goal": "Provide feedback on the overall solution",
                "expected_outputs": ["feedback.output"],
                "checkpoints": ["reflection"],
                "project_id": project_id
            }
        ]
        
        # Log instruction chain generation
        logger.info(f"Generated instruction chain: Chain length: {len(instruction_chain)}, Agents: hal → ash → nova → critic")
        
        # Execute the chain by calling /api/orchestrator/chain internally
        try:
            # Use the chain runner helper to avoid circular imports
            chain_result = await run_internal_chain(instruction_chain, request.app)
            
            # Check if the request was successful
            if chain_result.get("status") == "error":
                error_detail = chain_result.get("message", "Unknown error")
                logger.error(f"Chain execution failed: {error_detail}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": f"Chain execution failed: {error_detail}"
                    }
                )
            
            # Extract agent outputs
            hal_output = ""
            ash_output = ""
            nova_output = ""
            feedback = ""
            
            for step in chain_result.get("steps", []):
                agent = step.get("agent")
                outputs = step.get("outputs", [])
                
                # Extract content from outputs
                content = ""
                for output in outputs:
                    if isinstance(output, dict) and "content" in output:
                        content = output["content"]
                        break
                
                # Store content based on agent
                if agent == "hal":
                    hal_output = content
                elif agent == "ash":
                    ash_output = content
                elif agent == "nova":
                    nova_output = content
                elif agent == "critic":
                    feedback = content
            
            # Store all agent outputs in a single batched memory thread
            try:
                # Use the new batch-based ThreadRequest
                memory_result = await thread_memory({
                    "project_id": project_id,
                    "chain_id": chain_id,
                    "agent_id": "orchestrator",
                    "memories": [
                        {
                            "agent": "hal",
                            "role": "agent",
                            "content": hal_output,
                            "step_type": "plan"
                        },
                        {
                            "agent": "ash",
                            "role": "agent",
                            "content": ash_output,
                            "step_type": "docs"
                        },
                        {
                            "agent": "nova",
                            "role": "agent",
                            "content": nova_output,
                            "step_type": "ui"
                        },
                        {
                            "agent": "critic",
                            "role": "agent",
                            "content": feedback,
                            "step_type": "reflection"
                        }
                    ]
                })
                
                logger.info(f"📝 Memory Thread: Stored 4 memories under key {project_id}::{chain_id}")
            except Exception as e:
                logger.error(f"Error storing memories: {str(e)}")
            
            # Format the response
            response = {
                "project_id": project_id,
                "chain_id": chain_id,
                "agents": []
            }
            
            # Extract agent results
            for step in chain_result.get("steps", []):
                agent_result = {
                    "agent": step.get("agent"),
                    "status": step.get("status"),
                    "reflection": step.get("reflection"),
                    "outputs": step.get("outputs", [])
                }
                
                # Add retry information if available
                if step.get("retry_attempted"):
                    agent_result["retry_attempted"] = True
                    agent_result["retry_status"] = step.get("retry_status")
                    agent_result["redeemed"] = step.get("redeemed")
                    agent_result["redemption_reflection"] = step.get("redemption_reflection")
                
                response["agents"].append(agent_result)
            
            # Log successful chain execution
            logger.info(f"Chain execution completed: Project ID: {project_id}, Chain ID: {chain_id}, Agents: {len(response['agents'])}")
            
            return response
                
        except Exception as e:
            # Log unexpected errors during chain execution
            logger.error(f"Unexpected error during chain execution: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Unexpected error during chain execution: {str(e)}",
                    "project_id": project_id
                }
            )
            
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Project start failed: {str(e)}"
            }
        )
