from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from src.utils.debug_logger import log_test_result

# Import stubs (to be implemented)
# These will be replaced with actual implementations later
from app.modules.agent_tool_runner import run_agent_tool
from app.modules.agent_reflection import generate_agent_reflection
from app.modules.instruction_validator import validate_instruction_outputs

class InstructionSchema(BaseModel):
    agent: str
    goal: str
    expected_outputs: List[str]
    checkpoints: Optional[List[str]] = []
    
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
        
        # Generate reflection
        try:
            reflection = generate_agent_reflection(
                agent_id=instruction.agent,
                goal=instruction.goal,
                tool_result=tool_result
            )
            
            log_test_result(
                "Agent", 
                f"/api/agent/{instruction.agent}/reflect", 
                "PASS", 
                "Agent reflection generated", 
                f"Goal: {instruction.goal}"
            )
        except Exception as e:
            log_test_result(
                "Agent", 
                f"/api/agent/{instruction.agent}/reflect", 
                "FAIL", 
                f"Agent reflection failed: {str(e)}", 
                f"Goal: {instruction.goal}"
            )
            raise HTTPException(status_code=500, detail=f"Agent reflection failed: {str(e)}")
        
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
        
        # Return response
        return {
            "status": status,
            "consultation_id": consultation_id,
            "agent": instruction.agent,
            "goal": instruction.goal,
            "reflection": reflection,
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
