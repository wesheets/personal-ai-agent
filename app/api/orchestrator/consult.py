from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from src.utils.debug_logger import log_test_result

# Import modules
from app.modules.agent_tool_runner import run_agent_tool
from app.modules.agent_reflection import generate_reflection
from app.modules.instruction_validator import validate_instruction_outputs, extract_outputs_from_memory
from app.modules.memory_writer import write_memory

class InstructionSchema(BaseModel):
    agent: str
    goal: str
    expected_outputs: List[str]
    checkpoints: Optional[List[str]] = []
    goal_id: Optional[str] = None
    instruction_id: Optional[str] = None
    
router = APIRouter()

@router.post("/consult")
async def consult_agent(request: Request):
    """
    Consult an agent with a specific goal and expected outputs.
    
    This endpoint triggers agent tool execution, writes outputs to memory,
    generates a reflection, and validates the results against expected outputs.
    
    If the agent fails, it will reflect on the failure, retry the task,
    and log a redemption reflection if the retry succeeds.
    
    Returns:
        dict: Status and result information
    """
    try:
        # Parse request body
        body = await request.json()
        instruction = InstructionSchema(**body)
        
        # Generate consultation ID
        consultation_id = str(uuid.uuid4())
        
        # Log the start of consultation
        log_test_result(
            "Orchestrator", 
            "/api/orchestrator/consult", 
            "INFO", 
            f"Starting consultation with agent {instruction.agent}", 
            f"Goal: {instruction.goal}"
        )
        
        # Run agent tool with the goal
        try:
            tool_result = run_agent_tool(
                agent_id=instruction.agent,
                goal=instruction.goal
            )
            
            log_test_result(
                "Agent", 
                f"/api/agent/{instruction.agent}/tool", 
                "PASS", 
                "Agent tool execution completed", 
                f"Goal: {instruction.goal}"
            )
        except Exception as e:
            log_test_result(
                "Agent", 
                f"/api/agent/{instruction.agent}/tool", 
                "FAIL", 
                f"Agent tool execution failed: {str(e)}", 
                f"Goal: {instruction.goal}"
            )
            raise HTTPException(status_code=500, detail=f"Agent tool execution failed: {str(e)}")
        
        # Validate outputs against expected outputs
        try:
            validation_result = validate_instruction_outputs(
                agent_id=instruction.agent,
                expected_outputs=instruction.expected_outputs,
                checkpoints=instruction.checkpoints
            )
            
            status = validation_result["status"]  # "complete" or "failed"
            details = validation_result["details"]
            
            log_test_result(
                "Validator", 
                "/api/modules/instruction_validator", 
                status.upper(), 
                f"Validation {status}", 
                details
            )
        except Exception as e:
            log_test_result(
                "Validator", 
                "/api/modules/instruction_validator", 
                "FAIL", 
                f"Validation error: {str(e)}", 
                f"Agent: {instruction.agent}, Goal: {instruction.goal}"
            )
            raise HTTPException(status_code=500, detail=f"Instruction validation failed: {str(e)}")
        
        # Generate reflection using the new function
        try:
            # Create a summary of the output
            summary_output = details if isinstance(details, str) else str(details)
            
            # Generate reflection
            reflection_data = generate_reflection(
                goal=instruction.goal,
                success=(status == "complete"),
                output_summary=summary_output
            )
            
            # Add thread_id if goal_id or instruction_id is available
            if instruction.goal_id:
                reflection_data["thread_id"] = instruction.goal_id
            elif instruction.instruction_id:
                reflection_data["thread_id"] = instruction.instruction_id
            
            # Write reflection to memory
            memory_result = write_memory(
                agent_id=instruction.agent,
                type=reflection_data["type"],
                content=reflection_data["content"],
                tags=reflection_data["tags"],
                goal_id=instruction.goal_id if instruction.goal_id else instruction.instruction_id
            )
            
            log_test_result(
                "Reflection", 
                "/consult", 
                status.upper(), 
                "Tagged reflection written", 
                f"Goal: {instruction.goal}"
            )
        except Exception as e:
            log_test_result(
                "Reflection", 
                "/consult", 
                "FAIL", 
                f"Reflection generation failed: {str(e)}", 
                f"Goal: {instruction.goal}"
            )
            raise HTTPException(status_code=500, detail=f"Reflection generation failed: {str(e)}")
        
        # PHASE 11.3: Retry on Failure (Redemption Logic)
        retry_status = None
        retry_details = None
        redemption_reflection = None
        
        if status == "failed":
            log_test_result(
                "Retry", 
                "/consult", 
                "INFO", 
                "Initial attempt failed, triggering retry logic", 
                f"Goal: {instruction.goal}"
            )
            
            # Generate and write failure reflection
            try:
                failure_reflection = {
                    "type": "reflection",
                    "goal": instruction.goal,
                    "status": "failed",
                    "tags": [f"instruction.goal:{instruction.goal}", "phase:11.3", "retry.triggered"],
                    "content": f"I failed to complete the instruction. Here's what I think went wrong: {details}"
                }
                
                # Add thread_id if goal_id or instruction_id is available
                if instruction.goal_id:
                    failure_reflection["thread_id"] = instruction.goal_id
                elif instruction.instruction_id:
                    failure_reflection["thread_id"] = instruction.instruction_id
                
                # Write failure reflection to memory
                write_memory(
                    agent_id=instruction.agent,
                    type=failure_reflection["type"],
                    content=failure_reflection["content"],
                    tags=failure_reflection["tags"],
                    goal_id=instruction.goal_id if instruction.goal_id else instruction.instruction_id
                )
                
                log_test_result(
                    "Retry", 
                    "/consult", 
                    "INFO", 
                    "Failure reflection written", 
                    f"Goal: {instruction.goal}"
                )
            except Exception as e:
                log_test_result(
                    "Retry", 
                    "/consult", 
                    "FAIL", 
                    f"Failed to write failure reflection: {str(e)}", 
                    f"Goal: {instruction.goal}"
                )
            
            # Retry the task
            try:
                # Run agent tool again with the same goal
                retry_tool_result = run_agent_tool(
                    agent_id=instruction.agent,
                    goal=instruction.goal
                )
                
                log_test_result(
                    "Retry", 
                    "/consult", 
                    "PASS", 
                    "Retry tool execution completed", 
                    f"Goal: {instruction.goal}"
                )
                
                # Extract outputs from memory and validate
                retry_outputs = extract_outputs_from_memory(
                    agent_id=instruction.agent
                )
                
                retry_validation_result = validate_instruction_outputs(
                    agent_id=instruction.agent,
                    expected_outputs=instruction.expected_outputs,
                    checkpoints=instruction.checkpoints
                )
                
                retry_status = retry_validation_result["status"]
                retry_details = retry_validation_result["details"]
                
                log_test_result(
                    "Retry", 
                    "/consult", 
                    retry_status.upper(), 
                    f"Retry validation {retry_status}", 
                    retry_details
                )
                
                # If retry succeeds, log redemption
                if retry_status == "complete":
                    redemption_reflection = {
                        "type": "reflection",
                        "goal": instruction.goal,
                        "status": "redeemed",
                        "tags": [f"instruction.goal:{instruction.goal}", "phase:11.3", "retry.success"],
                        "content": "I retried the task and succeeded. Here's how I changed my approach or why I believe it worked this time."
                    }
                    
                    # Add thread_id if goal_id or instruction_id is available
                    if instruction.goal_id:
                        redemption_reflection["thread_id"] = instruction.goal_id
                    elif instruction.instruction_id:
                        redemption_reflection["thread_id"] = instruction.instruction_id
                    
                    # Write redemption reflection to memory
                    redemption_memory = write_memory(
                        agent_id=instruction.agent,
                        type=redemption_reflection["type"],
                        content=redemption_reflection["content"],
                        tags=redemption_reflection["tags"],
                        goal_id=instruction.goal_id if instruction.goal_id else instruction.instruction_id
                    )
                    
                    log_test_result(
                        "Retry", 
                        "/consult", 
                        "PASS", 
                        "Redemption reflection written", 
                        f"Goal: {instruction.goal}"
                    )
            except Exception as e:
                log_test_result(
                    "Retry", 
                    "/consult", 
                    "FAIL", 
                    f"Retry process failed: {str(e)}", 
                    f"Goal: {instruction.goal}"
                )
            
            # Log final retry status
            log_test_result(
                "Retry", 
                "/consult", 
                retry_status.upper() if retry_status else "FAIL", 
                "Retry completed", 
                f"Redemption: {retry_status == 'complete'}"
            )
        
        # Return response with retry information if applicable
        response = {
            "status": status,
            "consultation_id": consultation_id,
            "agent": instruction.agent,
            "goal": instruction.goal,
            "reflection": reflection_data["content"],
            "validation_details": details
        }
        
        # Add retry information if retry was attempted
        if retry_status is not None:
            response.update({
                "retry_attempted": True,
                "retry_status": retry_status,
                "retry_details": retry_details,
                "redeemed": retry_status == "complete",
                "redemption_reflection": redemption_reflection["content"] if redemption_reflection else None
            })
        
        return response
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log unexpected errors
        log_test_result(
            "Orchestrator", 
            "/api/orchestrator/consult", 
            "FAIL", 
            f"Unexpected error: {str(e)}", 
            "Check server logs for details"
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Consultation failed: {str(e)}"
            }
        )
