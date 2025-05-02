from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
import httpx
from src.utils.debug_logger import log_test_result

# Import modules
from app.api.orchestrator.consult import consult_agent, InstructionSchema
from app.modules.memory_writer import write_memory
from app.modules.agent_reflection import generate_reflection

router = APIRouter()

@router.post("/chain")
async def chain_instructions(request: Request):
    """
    Execute a chain of instructions across multiple agents in sequence.
    
    Each agent in the chain can access the memory and outputs of previous agents.
    Results are returned as an ordered stack of agent responses.
    
    Returns:
        dict: Status and result information for the entire chain
    """
    try:
        # Parse request body - expecting an array of instruction objects
        body = await request.json()
        
        if not isinstance(body, list):
            raise HTTPException(status_code=400, detail="Request body must be an array of instruction objects")
        
        # Generate chain ID
        chain_id = str(uuid.uuid4())
        
        # Log the start of chain execution
        log_test_result(
            "Orchestrator", 
            "/api/orchestrator/chain", 
            "INFO", 
            f"Starting instruction chain execution", 
            f"Chain ID: {chain_id}, Steps: {len(body)}"
        )
        
        # Initialize response steps array
        steps = []
        
        # Process each instruction in sequence
        for index, instruction_data in enumerate(body):
            # Add chain_id to instruction
            instruction_data["chain_id"] = chain_id
            
            # If this is not the first agent in the chain, add memory context
            if index > 0:
                # Get the list of previous agents in the chain
                previous_agents = [step["agent"] for step in body[:index]]
                
                # Add memory context to instruction data
                instruction_data["memory_context"] = {
                    "previous_agents": previous_agents,
                    "chain_id": chain_id
                }
                
                # Log memory linking
                log_test_result(
                    "Chain", 
                    "/api/orchestrator/chain", 
                    "INFO", 
                    f"Memory linking for step {index + 1}", 
                    f"Agent {instruction_data.get('agent')} can access memories from: {', '.join(previous_agents)}"
                )
            
            # Log current step
            log_test_result(
                "Chain", 
                "/api/orchestrator/chain", 
                "INFO", 
                f"Executing step {index + 1}/{len(body)}", 
                f"Agent: {instruction_data.get('agent')}, Goal: {instruction_data.get('goal')}"
            )
            
            try:
                # Create a mock request object with the instruction data
                mock_request = MockRequest(instruction_data)
                
                # Call the consult endpoint directly
                result = await consult_agent(mock_request)
                
                # Extract relevant information for the step response
                step_response = {
                    "agent": instruction_data.get("agent"),
                    "status": result.get("status"),
                    "reflection": result.get("reflection"),
                    "outputs": result.get("validation_details"),
                    "step_number": index + 1
                }
                
                # Add retry information if available
                if result.get("retry_attempted"):
                    step_response["retry_attempted"] = True
                    step_response["retry_status"] = result.get("retry_status")
                    step_response["redeemed"] = result.get("redeemed")
                    step_response["redemption_reflection"] = result.get("redemption_reflection")
                
                # Add step to steps array
                steps.append(step_response)
                
                # Log step completion
                log_test_result(
                    "Chain", 
                    "/api/orchestrator/chain", 
                    result.get("status").upper(), 
                    f"Step {index + 1} {result.get('status')}", 
                    f"Agent: {instruction_data.get('agent')}"
                )
                
                # If step failed and wasn't redeemed, stop chain execution
                if result.get("status") == "failed" and not result.get("redeemed", False):
                    log_test_result(
                        "Chain", 
                        "/api/orchestrator/chain", 
                        "FAIL", 
                        f"Chain execution stopped at step {index + 1}", 
                        f"Agent {instruction_data.get('agent')} failed and was not redeemed"
                    )
                    break
                
            except Exception as e:
                # Log step failure
                log_test_result(
                    "Chain", 
                    "/api/orchestrator/chain", 
                    "FAIL", 
                    f"Step {index + 1} failed", 
                    f"Error: {str(e)}"
                )
                
                # Add failed step to steps array
                steps.append({
                    "agent": instruction_data.get("agent"),
                    "status": "failed",
                    "error": str(e),
                    "step_number": index + 1
                })
                
                # Stop chain execution on failure
                break
        
        # Determine overall chain status
        chain_status = "complete"
        for step in steps:
            if step.get("status") != "complete":
                chain_status = "failed"
                break
        
        # Write a chain completion memory for reference
        try:
            chain_summary = f"Chain execution {chain_status}. {len(steps)}/{len(body)} steps completed."
            chain_memory = write_memory(
                agent_id="orchestrator",
                type="chain_execution",
                content=chain_summary,
                tags=["chain", f"status:{chain_status}", "phase:11.4"],
                goal_id=chain_id  # Use chain_id as goal_id for thread linking
            )
            
            log_test_result(
                "Chain", 
                "/api/orchestrator/chain", 
                "INFO", 
                "Chain memory written", 
                f"Memory ID: {chain_memory['memory_id']}"
            )
        except Exception as e:
            log_test_result(
                "Chain", 
                "/api/orchestrator/chain", 
                "WARN", 
                "Failed to write chain memory", 
                f"Error: {str(e)}"
            )
        
        # Log chain completion
        log_test_result(
            "Orchestrator", 
            "/api/orchestrator/chain", 
            chain_status.upper(), 
            f"Chain execution {chain_status}", 
            f"Chain ID: {chain_id}, Steps completed: {len(steps)}/{len(body)}"
        )
        
        # Return response
        return {
            "status": chain_status,
            "chain_id": chain_id,
            "steps": steps
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log unexpected errors
        log_test_result(
            "Orchestrator", 
            "/api/orchestrator/chain", 
            "FAIL", 
            f"Unexpected error: {str(e)}", 
            "Check server logs for details"
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Chain execution failed: {str(e)}"
            }
        )

class MockRequest:
    """
    Mock request class to simulate FastAPI request object for internal calls.
    """
    def __init__(self, json_data):
        self.json_data = json_data
    
    async def json(self):
        return self.json_data
