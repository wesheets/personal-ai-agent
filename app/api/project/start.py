from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uuid
import asyncio
import logging
import traceback
from datetime import datetime
from src.utils.debug_logger import log_test_result
from app.utils.chain_runner import run_internal_chain  # Import the chain runner helper

# Configure logging
logger = logging.getLogger("app.api.project.start")

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
        # 🟢 Chain entry (start of function)
        logger.info("🟢 CHAIN START: Entering start_project function")
        print("🟢 CHAIN START: Entering start_project function")
        
        # Parse request body
        body = await request.json()
        logger.info(f"Request body received: {body}")
        
        # Validate request format
        if not isinstance(body, dict) or "goal" not in body:
            logger.error("Invalid request format: 'goal' field missing")
            raise HTTPException(status_code=400, detail="Request must include a 'goal' field")
        
        goal = body["goal"]
        logger.info(f"Goal extracted from request: '{goal}'")
        
        # Generate project_id
        project_id = str(uuid.uuid4())
        logger.info(f"🆔 Generated project_id: {project_id}")
        print(f"🆔 Generated project_id: {project_id}")
        
        # 🛠️ Project state creation
        logger.info(f"🛠️ PROJECT STATE: Creating project state for {project_id}")
        print(f"🛠️ PROJECT STATE: Creating project state for {project_id}")
        
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
        
        logger.info(f"Instruction chain created: {instruction_chain}")
        
        # Log instruction chain generation
        log_test_result(
            "Project", 
            "/api/project/start", 
            "INFO", 
            f"Generated instruction chain", 
            f"Chain length: {len(instruction_chain)}, Agents: hal → ash → nova"
        )
        
        # 🧠 Orchestrator consult call
        logger.info(f"🧠 ORCHESTRATOR CONSULT: Executing chain via run_internal_chain")
        print(f"🧠 ORCHESTRATOR CONSULT: Executing chain via run_internal_chain")
        
        # Execute the chain by calling /api/orchestrator/chain internally
        try:
            # Use the chain runner helper to avoid circular imports
            # Pass request.app as the app reference instead of importing app directly
            logger.info(f"Calling run_internal_chain with payload: {instruction_chain}")
            chain_result = await run_internal_chain(instruction_chain, request.app)
            logger.info(f"Chain execution result: {chain_result}")
            print(f"Chain execution result status: {chain_result.get('status', 'unknown')}")
            
            # Check if the request was successful
            if chain_result.get("status") == "error":
                error_detail = chain_result.get("message", "Unknown error")
                logger.error(f"❌ Chain execution failed: {error_detail}")
                print(f"❌ Chain execution failed: {error_detail}")
                
                # Log detailed error information
                logger.error(f"Full chain result on error: {chain_result}")
                
                log_test_result(
                    "Project", 
                    "/api/project/start", 
                    "ERROR", 
                    f"Chain execution failed", 
                    error_detail
                )
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": f"Chain execution failed: {error_detail}",
                        "project_id": project_id,
                        "goal": goal,
                        "error_details": str(chain_result)
                    }
                )
            
            # Validate chain result contains expected data
            if not chain_result.get("steps"):
                logger.error(f"❌ Chain execution returned no steps")
                print(f"❌ Chain execution returned no steps")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": "Orchestrator chain returned no agent steps",
                        "project_id": project_id,
                        "goal": goal,
                        "chain_result": chain_result
                    }
                )
                
            # Extract chain_id
            chain_id = chain_result.get("chain_id", "unknown")
            logger.info(f"Chain ID extracted: {chain_id}")
                
            # 🔁 Agent loop trigger
            logger.info(f"🔁 AGENT LOOP: Checking for agent execution in chain result")
            print(f"🔁 AGENT LOOP: Checking for agent execution in chain result")
            
            # Check if HAL was triggered
            hal_triggered = False
            for step in chain_result.get("steps", []):
                if step.get("agent") == "hal" and step.get("status") == "complete":
                    hal_triggered = True
                    logger.info(f"✅ HAL agent was successfully triggered and completed")
                    print(f"✅ HAL agent was successfully triggered and completed")
                    break
            
            if not hal_triggered:
                logger.warning(f"⚠️ HAL agent was not successfully triggered or did not complete")
                print(f"⚠️ HAL agent was not successfully triggered or did not complete")
            
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
                logger.info(f"Added agent result for {step.get('agent')}: {agent_result['status']}")
            
            # 🧱 Final output and return
            logger.info(f"🧱 FINAL OUTPUT: Returning successful response with {len(response['agents'])} agent results")
            print(f"🧱 FINAL OUTPUT: Returning successful response with {len(response['agents'])} agent results")
            
            # Log successful chain execution
            log_test_result(
                "Project", 
                "/api/project/start", 
                "SUCCESS", 
                f"Chain execution completed", 
                f"Project ID: {project_id}, Chain ID: {chain_id}, Agents: {len(response['agents'])}"
            )
            
            return response
                
        except Exception as e:
            # Log unexpected errors during chain execution
            logger.error(f"❌ Unexpected error during chain execution: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"❌ Unexpected error during chain execution: {str(e)}")
            
            log_test_result(
                "Project", 
                "/api/project/start", 
                "ERROR", 
                f"Unexpected error during chain execution", 
                f"Error: {str(e)}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Unexpected error during chain execution: {str(e)}",
                    "project_id": project_id,
                    "goal": goal,
                    "error_details": traceback.format_exc()
                }
            )
            
    except HTTPException as e:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        # Log unexpected errors
        logger.error(f"❌ Unexpected error in start_project: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"❌ Unexpected error in start_project: {str(e)}")
        
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
                "message": f"Project start failed: {str(e)}",
                "error_details": traceback.format_exc()
            }
        )
