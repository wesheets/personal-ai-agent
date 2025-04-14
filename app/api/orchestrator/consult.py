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
from app.modules.instruction_validator import validate_instruction_outputs
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
        
        # Return response
        return {
            "status": status,
            "consultation_id": consultation_id,
            "agent": instruction.agent,
            "goal": instruction.goal,
            "reflection": reflection_data["content"],
            "validation_details": details
        }
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
