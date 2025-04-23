"""
Updated loop_routes.py to integrate with HAL code generation functionality
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging
import traceback

# Import schemas
from app.schemas.loop_schema import LoopResponseRequest

# Import memory operations
from app.modules.memory_writer import write_memory
from app.api.modules.memory import read_memory

# Import agent modules
from app.agents.hal import run_hal_agent
from app.agents.hal_agent import run_hal_agent as run_hal_agent_v2
from app.agents.ash import run_ash_agent
from app.agents.critic import run_critic_agent

# Import code generation module
from app.modules.code_generation.hal_code_generator import process_build_task

# Configure logging
logger = logging.getLogger("app.routes.loop_routes")

router = APIRouter(tags=["loop"])

class LoopPlanRequest(BaseModel):
    prompt: str
    loop_id: str
    orchestrator_persona: Optional[str] = None

class LoopCompletionRequest(BaseModel):
    loop_id: str
    project_id: str
    executor: str
    notes: str

class LoopValidateRequest(BaseModel):
    loop_id: str
    loop_data: Dict[str, Any]
    mode: Optional[str] = None
    complexity: Optional[float] = None
    sensitivity: Optional[float] = None
    time_constraint: Optional[float] = None
    user_preference: Optional[str] = None

@router.post("/loop/plan")
async def plan_loop(request: LoopPlanRequest):
    """
    Create execution plan for a loop.
    """
    # This would normally create a plan based on the prompt
    # For now, return a mock response
    return {
        "plan": {
            "steps": [
                {"step_id": 1, "description": "Research the topic", "status": "pending"},
                {"step_id": 2, "description": "Analyze findings", "status": "pending"},
                {"step_id": 3, "description": "Generate response", "status": "pending"}
            ]
        },
        "loop_id": request.loop_id,
        "orchestrator_persona": request.orchestrator_persona or "SAGE",
        "status": "success"
    }

@router.post("/loop/complete")
async def loop_complete_endpoint(request: LoopCompletionRequest):
    """
    Handle loop completion and initiate loop execution.
    
    This endpoint is called when a loop is ready to be executed and triggers:
    - Loop log writing
    - Memory state activation
    - Orchestration delegation to HAL/NOVA/CRITIC
    """
    # Validate required fields
    if not request.loop_id or not request.project_id or not request.executor:
        raise HTTPException(status_code=400, detail="loop_id, project_id, and executor are required")
    
    try:
        # Write to loop log
        # This would normally write to a persistent storage
        loop_log_entry = {
            "loop_id": request.loop_id,
            "project_id": request.project_id,
            "executor": request.executor,
            "notes": request.notes,
            "status": "activated",
            "timestamp": datetime.now().isoformat()
        }
        
        # Activate memory state
        # This would normally update the memory state in a database
        memory_activation_result = {
            "status": "success",
            "loop_id": request.loop_id,
            "memory_state": "active"
        }
        
        # Delegate to orchestration systems
        # This would normally trigger the orchestration systems
        orchestration_result = {
            "status": "delegated",
            "systems": ["HAL", "NOVA", "CRITIC"],
            "loop_id": request.loop_id
        }
        
        # Return success response
        return {
            "status": "activated",
            "loop_id": request.loop_id,
            "project_id": request.project_id,
            "executor": request.executor,
            "message": f"Loop {request.loop_id} has been activated successfully",
            "orchestration_status": orchestration_result
        }
    except Exception as e:
        # Log the error and return an error response
        raise HTTPException(status_code=500, detail=f"Failed to activate loop: {str(e)}")

@router.post("/loop/respond")
async def loop_respond_endpoint(request: LoopResponseRequest):
    """
    Handle agent responses to memory within a loop.
    
    This endpoint allows agents (like HAL, ASH, CRITIC) to respond to a memory key
    within a loop and write their structured output to memory, completing the
    loop planning-to-response lifecycle.
    """
    # Validate required fields
    if not request.loop_id or not request.project_id or not request.agent or not request.input_key:
        raise HTTPException(status_code=400, detail="loop_id, project_id, agent, and input_key are required")
    
    # Validate target_file is provided if response_type is code
    if request.response_type == "code" and not request.target_file:
        raise HTTPException(status_code=400, detail="target_file is required when response_type is 'code'")
    
    try:
        # Retrieve prior memory using memory.read
        try:
            # Modified to use agent_id instead of project_id and loop_id
            # Using the loop_id as the agent_id for compatibility
            prior_memory = await read_memory(
                agent_id=request.loop_id,
                memory_type="loop",
                tag=request.input_key
            )
            
            if not prior_memory:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Memory not found for key: {request.input_key} in loop: {request.loop_id}"
                )
                
        except Exception as e:
            logger.error(f"Error reading memory: {str(e)}")
            raise HTTPException(
                status_code=404,
                detail=f"Failed to retrieve memory for key: {request.input_key} - {str(e)}"
            )
        
        # Call corresponding agent module based on agent and response_type
        agent_response = None
        if request.agent.lower() == "hal":
            if request.response_type == "code":
                # Call HAL for code generation
                try:
                    # Process the build task and generate code
                    code_result = await process_build_task(
                        loop_id=request.loop_id,
                        input_key=request.input_key,
                        target_file=request.target_file
                    )
                    
                    if code_result.get("status") != "success":
                        raise Exception(f"Failed to process build task: {code_result.get('message', 'Unknown error')}")
                    
                    # Set agent_response based on the code generation result
                    agent_response = {
                        "code": code_result.get("code", ""),
                        "target_file": request.target_file,
                        "timestamp": code_result.get("timestamp", datetime.now().isoformat()),
                        "description": f"Code generated for {request.target_file}"
                    }
                except Exception as code_error:
                    logger.error(f"Error in code generation: {str(code_error)}")
                    logger.error(traceback.format_exc())
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate code: {str(code_error)}"
                    )
            else:
                # Call HAL for other response types
                try:
                    agent_result = run_hal_agent_v2(
                        task=f"Generate {request.response_type} for {prior_memory.get('content', '')}",
                        project_id=request.project_id
                    )
                    agent_response = {
                        "content": agent_result.get("result", ""),
                        "type": request.response_type
                    }
                except Exception as e:
                    # Try the alternative HAL agent implementation
                    agent_result = run_hal_agent(
                        task=f"Generate {request.response_type} for {prior_memory.get('content', '')}",
                        project_id=request.project_id
                    )
                    agent_response = {
                        "content": agent_result.get("result", ""),
                        "type": request.response_type
                    }
        elif request.agent.lower() == "ash":
            # Call ASH agent
            agent_result = run_ash_agent(
                task=f"Generate {request.response_type} for {prior_memory.get('content', '')}",
                project_id=request.project_id
            )
            agent_response = {
                "content": agent_result.get("result", ""),
                "type": request.response_type
            }
        elif request.agent.lower() == "critic":
            # Call CRITIC agent
            agent_result = run_critic_agent(
                task=f"Generate {request.response_type} for {prior_memory.get('content', '')}",
                project_id=request.project_id
            )
            agent_response = {
                "content": agent_result.get("result", ""),
                "type": request.response_type,
                "judgment": agent_result.get("judgment", "neutral")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported agent: {request.agent}")
        
        # Generate output key in the format: {agent}_{input_key}_response
        output_key = f"{request.agent.lower()}_{request.input_key}_response"
        
        # Write agent response to memory
        timestamp = datetime.now().isoformat()
        memory_data = {
            "agent": request.agent.lower(),
            "project_id": request.project_id,
            "loop_id": request.loop_id,
            "action": f"Generated {request.response_type} response",
            "tool_used": f"{request.agent.lower()}_response_generator",
            "input_key": request.input_key,
            "output_key": output_key,
            "response_type": request.response_type,
            "content": agent_response,
            "timestamp": timestamp
        }
        
        # Write to memory
        memory_result = write_memory(memory_data)
        
        # Return success response
        return {
            "status": "success",
            "agent": request.agent,
            "input_key": request.input_key,
            "output_key": output_key,
            "response_type": request.response_type,
            "timestamp": timestamp,
            "message": f"Response generated successfully by {request.agent}"
        }
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        # Log the error and return an error response
        logger.error(f"Error in loop_respond_endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@router.post("/loop/validate")
async def validate_loop(request: LoopValidateRequest):
    """
    Validate a loop against core requirements and enrich with cognitive controls.
    """
    # This would normally validate the loop data
    # For now, return a mock response
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "mode": request.mode or "balanced",
        "validation_result": {
            "valid": True,
            "warnings": [],
            "enriched": True
        },
        "prepared_loop": request.loop_data,
        "processed_by": "cognitive_control_layer"
    }

@router.get("/loop/trace")
async def get_loop_trace(project_id: Optional[str] = None):
    """
    Get loop memory trace log.
    """
    # This would normally retrieve loop traces from storage
    # For now, return a mock response
    return {
        "traces": [
            {
                "loop_id": "loop_001",
                "status": "completed",
                "timestamp": "2025-04-21T12:00:00Z",
                "summary": "Analyzed quantum computing concepts"
            },
            {
                "loop_id": "loop_002",
                "status": "completed",
                "timestamp": "2025-04-21T12:10:00Z",
                "summary": "Researched machine learning algorithms"
            }
        ]
    }

@router.post("/loop/trace")
async def add_loop_trace(data: Dict[str, Any]):
    """
    Inject synthetic loop trace.
    """
    loop_id = data.get("loop_id")
    status = data.get("status")
    timestamp = data.get("timestamp")
    
    if not loop_id or not status:
        raise HTTPException(status_code=400, detail="loop_id and status are required")
    
    # This would normally store the loop trace
    # For now, return a success response
    return {
        "status": "success",
        "loop_id": loop_id,
        "message": f"Loop trace for {loop_id} added successfully"
    }

@router.post("/loop/reset")
async def reset_loop():
    """
    Memory reset for clean test runs.
    """
    # This would normally reset loop-related memory
    # For now, return a success response
    return {
        "status": "success",
        "message": "Loop memory reset successfully",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/loop/persona-reflect")
async def persona_reflect(data: Dict[str, Any]):
    """
    Inject mode-aligned reflection trace.
    """
    persona = data.get("persona")
    reflection = data.get("reflection")
    loop_id = data.get("loop_id")
    
    if not persona or not reflection or not loop_id:
        raise HTTPException(status_code=400, detail="persona, reflection, and loop_id are required")
    
    # This would normally store the reflection
    # For now, return a success response
    return {
        "status": "success",
        "persona": persona,
        "loop_id": loop_id,
        "message": f"Reflection for {loop_id} with persona {persona} added successfully"
    }
