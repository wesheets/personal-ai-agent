from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uuid
import httpx
import asyncio
from datetime import datetime
from src.utils.debug_logger import log_test_result

router = APIRouter()

class ProjectStartRequest(BaseModel):
    goal: str

@router.post("/start")
async def start_project(request: Request):
    """
    Start a new project with a simple goal.
    
    This endpoint transforms a simple user goal into a multi-agent instruction chain
    involving HAL, ASH, and NOVA. It executes the chain and returns the results.
    
    Args:
        request: The FastAPI request object containing the goal
        
    Returns:
        dict: Project information including project_id, chain_id, and agent results
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Validate request format
        if not isinstance(body, dict) or "goal" not in body:
            raise HTTPException(status_code=400, detail="Request must include a 'goal' field")
        
        goal = body["goal"]
        
        # Generate project_id
        project_id = str(uuid.uuid4())
        
        # Log project start
        log_test_result(
            "Project", 
            "/api/project/start", 
            "INFO", 
            f"Starting new project", 
            f"Project ID: {project_id}, Goal: {goal}"
        )
        
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
            }
        ]
        
        # Log instruction chain generation
        log_test_result(
            "Project", 
            "/api/project/start", 
            "INFO", 
            f"Generated instruction chain", 
            f"Chain length: {len(instruction_chain)}, Agents: hal → ash → nova"
        )
        
        # Execute the chain by calling /api/orchestrator/chain
        try:
            async with httpx.AsyncClient() as client:
                chain_response = await client.post(
                    "http://localhost:3000/api/orchestrator/chain",
                    json=instruction_chain,
                    timeout=300.0  # 5 minute timeout for the entire chain execution
                )
                
                # Check if the request was successful
                if chain_response.status_code != 200:
                    error_detail = chain_response.text
                    log_test_result(
                        "Project", 
                        "/api/project/start", 
                        "ERROR", 
                        f"Chain execution failed with status {chain_response.status_code}", 
                        error_detail
                    )
                    return JSONResponse(
                        status_code=500,
                        content={
                            "status": "error",
                            "message": f"Chain execution failed: {error_detail}"
                        }
                    )
                
                # Parse the chain response
                chain_result = chain_response.json()
                
                # Extract chain_id
                chain_id = chain_result.get("chain_id", "unknown")
                
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
                log_test_result(
                    "Project", 
                    "/api/project/start", 
                    "SUCCESS", 
                    f"Chain execution completed", 
                    f"Project ID: {project_id}, Chain ID: {chain_id}, Agents: {len(response['agents'])}"
                )
                
                return response
                
        except httpx.RequestError as e:
            # Log connection error
            log_test_result(
                "Project", 
                "/api/project/start", 
                "ERROR", 
                f"Connection error during chain execution", 
                f"Error: {str(e)}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Connection error during chain execution: {str(e)}"
                }
            )
            
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log unexpected errors
        log_test_result(
            "Project", 
            "/api/project/start", 
            "ERROR", 
            f"Unexpected error: {str(e)}", 
            "Check server logs for details"
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Project start failed: {str(e)}"
            }
        )
