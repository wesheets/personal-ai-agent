"""
Updated loop_routes.py to integrate with HAL code generation functionality

# memory_tag: phase3.0_sprint1_core_cognitive_handler_activation
"""
from fastapi import APIRouter, HTTPException, Depends, Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging
import traceback
import uuid
import os
import json

# Import schemas
from app.schemas.loop_schema import (
    LoopResponseRequest,
    LoopResponseResult
)
from app.schemas.loop.loop_reset_schema import LoopResetRequest, LoopResetResponse
from app.schemas.loop.loop_trace_schema import LoopTraceRequest, LoopTraceResponse
from app.schemas.loop.loop_create_schema import LoopCreateRequest, LoopCreateResponse

# from app.modules.memory_writer import write_memory # Removed - Use memory_engine
# from app.api.modules.memory import read_memory # Removed - Use memory_engine

# Import agent modules
from app.agents.hal_agent import HALAgent # Corrected import
from app.agents.ash import run_ash_agent
from app.agents.critic import run_critic_agent

# Import code generation module
from app.modules.code_generation.hal_code_generator import process_build_task
from app.schemas.loopvalidate_schemas import LoopValidateRequest
from app.schemas.loopvalidate_schemas import LoopValidateResponse

# Configure logging
logger = logging.getLogger("app.routes.loop_routes")

# Ensure logs directory exists
os.makedirs("/home/ubuntu/personal-ai-agent/logs", exist_ok=True)

router = APIRouter(tags=["loop"])

class LoopPlanRequest(BaseModel):
    prompt: str
    loop_id: str
    orchestrator_persona: Optional[str] = None

class LoopPlanResponse(BaseModel):
    plan: Dict[str, Any]
    loop_id: str
    orchestrator_persona: str
    status: str

class LoopCompletionRequest(BaseModel):
    loop_id: str
    project_id: str
    executor: str
    notes: str

class LoopCompletionResponse(BaseModel):
    status: str
    loop_id: str
    project_id: str
    executor: str
    message: str
    orchestration_status: Dict[str, Any]

class LoopValidateRequest(BaseModel):
    loop_id: str
    loop_data: Dict[str, Any]
    mode: Optional[str] = None
    complexity: Optional[float] = None
    sensitivity: Optional[float] = None
    time_constraint: Optional[float] = None
    user_preference: Optional[str] = None

class LoopValidateResponse(BaseModel):
    status: str
    loop_id: str
    mode: str
    validation_result: Dict[str, Any]
    prepared_loop: Dict[str, Any]
    processed_by: str

class PersonaReflectRequest(BaseModel):
    persona: str
    reflection: str
    loop_id: str

class PersonaReflectResponse(BaseModel):
    status: str
    persona: str
    loop_id: str
    message: str

@router.post("/create", response_model=LoopCreateResponse)
async def create_loop(request: LoopCreateRequest):
    """
    Create a simple loop record with plan ID and loop type.
    
    Args:
        request: LoopCreateRequest containing plan_id and loop_type
            
    Returns:
        LoopCreateResponse containing status and loop_id
    """
    logger.info(f"➡️ Entering create_loop endpoint for plan_id: {request.plan_id}")
    loop_id = str(uuid.uuid4())
    logger.info(f"Generated loop_id: {loop_id}")
    
    try:
        # In a real implementation, this would store the data in a database
        # For this minimal viable handler, we'll store it in a simple JSON file
        
        loop_file = "/home/ubuntu/personal-ai-agent/logs/simple_loop_store.json"
        
        # Generate a unique loop ID
        loop_id = str(uuid.uuid4())
        
        # Create loop entry
        loop_entry = {
            "loop_id": loop_id,
            "plan_id": request.plan_id,
            "loop_type": request.loop_type,
            "metadata": request.metadata,
            "status": "created",
            "timestamp": str(datetime.now())
        }
        
        # Check if loop file exists
        logger.info(f"Checking for loop store file: {loop_file}")
        if os.path.exists(loop_file):
            # Read existing loop entries
            logger.info(f"Reading existing loop store from {loop_file}")
            try:
                with open(loop_file, 'r') as f:
                    loop_store = json.load(f)
                    if not isinstance(loop_store, dict):
                        logger.warning("Loop store file content is not a dictionary, initializing as empty.")
                        loop_store = {}
                    else:
                        logger.info(f"Successfully loaded {len(loop_store)} existing loop entries.")
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode JSON from {loop_file}, initializing as empty.")
                loop_store = {}
        else:
            logger.info(f"Loop store file {loop_file} not found, initializing as empty.")
            loop_store = {}
        
        # Add new loop entry
        logger.info(f"Adding new loop entry for loop_id: {loop_id}")
        loop_store[loop_id] = loop_entry
        
        # Write updated loop store
        logger.info(f"Writing updated loop store ({len(loop_store)} entries) to {loop_file}")
        try:
            with open(loop_file, 'w') as f:
                json.dump(loop_store, f, indent=2)
            logger.info(f"Successfully wrote updated loop store to {loop_file}")
        except Exception as write_error:
            logger.error(f"❌ Failed to write loop store to {loop_file}: {str(write_error)}")
            # Optionally re-raise or handle this critical error
            raise HTTPException(status_code=500, detail=f"Failed to save loop data: {str(write_error)}")
        
        logger.info(f"✅ Successfully created loop with ID: {loop_id}. Exiting create_loop endpoint.")
        return LoopCreateResponse(
            loop_id=loop_id,
            plan_id=request.plan_id,
            loop_type=request.loop_type,
            status="success",
            timestamp=str(datetime.now()),
            metadata=request.metadata
        )
    except Exception as e:
        logger.error(f"❌ Error in create_loop for plan_id {request.plan_id}: {str(e)}")
        logger.error(traceback.format_exc()) # Log full traceback
        
        # Log the error to loop_fallback.json
        try:
            log_file = "/home/ubuntu/personal-ai-agent/logs/loop_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.now()),
                "event": "route_error",
                "endpoint": "loop_create",
                "error": str(e)
            }
            
            # Check if log file exists
            if os.path.exists(log_file):
                # Read existing logs
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as log_error:
            logger.error(f"Failed to log loop route error: {str(log_error)}")
        
        raise HTTPException(status_code=500, detail=f"Failed to create loop: {str(e)}")

@router.get("/{loop_id}", response_model=LoopCreateResponse)
async def get_loop(loop_id: str = Path(..., description="Loop ID to retrieve")):
    """
    Retrieve existing loop metadata by loop_id.
    
    Args:
        loop_id: The loop ID to retrieve
            
    Returns:
        LoopCreateResponse containing the loop metadata
    """
    logger.info(f"➡️ Entering get_loop endpoint for loop_id: {loop_id}")
    
    try:
        # In a real implementation, this would retrieve data from a database
        # For this minimal viable handler, we'll retrieve it from the simple JSON file
        
        loop_file = "/home/ubuntu/personal-ai-agent/logs/simple_loop_store.json"
        
        # Check if loop file exists
        logger.info(f"Checking for loop store file: {loop_file}")
        if not os.path.exists(loop_file):
            logger.warning(f"Loop store file {loop_file} not found for loop_id: {loop_id}")
            raise HTTPException(status_code=404, detail=f"Loop ID not found: {loop_id}")
        
        # Read loop entries
        logger.info(f"Reading loop store from {loop_file}")
        try:
            with open(loop_file, 'r') as f:
                loop_store = json.load(f)
            logger.info(f"Successfully loaded loop store data.")
        except json.JSONDecodeError as json_err:
            logger.error(f"❌ Failed to decode JSON from {loop_file}: {str(json_err)}")
            raise HTTPException(status_code=500, detail=f"Failed to read loop store: {str(json_err)}")
        except Exception as read_err:
            logger.error(f"❌ Failed to read loop store file {loop_file}: {str(read_err)}")
            raise HTTPException(status_code=500, detail=f"Failed to read loop store: {str(read_err)}")
        
        # Check if loop_id exists
        logger.info(f"Checking if loop_id {loop_id} exists in the store.")
        if loop_id not in loop_store:
            logger.warning(f"Loop ID {loop_id} not found in loop store.")
            raise HTTPException(status_code=404, detail=f"Loop ID not found: {loop_id}")
        
        # Get loop entry
        logger.info(f"Retrieving loop entry for loop_id: {loop_id}")
        loop_entry = loop_store[loop_id]
        
        logger.info(f"✅ Successfully retrieved loop with ID: {loop_id}")
        return LoopCreateResponse(
            loop_id=loop_id,
            plan_id=loop_entry["plan_id"],
            loop_type=loop_entry["loop_type"],
            status="success",
            timestamp=loop_entry["timestamp"],
            metadata=loop_entry.get("metadata")
        )
    except HTTPException:
        # Re-raise HTTP exceptions after logging
        logger.warning(f"HTTPException encountered in get_loop for loop_id {loop_id}: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"❌ Unhandled error in get_loop for loop_id {loop_id}: {str(e)}")
        logger.error(traceback.format_exc()) # Log full traceback
        
        # Log the error to loop_fallback.json
        try:
            log_file = "/home/ubuntu/personal-ai-agent/logs/loop_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.now()),
                "event": "route_error",
                "endpoint": "loop_get",
                "error": str(e)
            }
            
            # Check if log file exists
            if os.path.exists(log_file):
                # Read existing logs
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as log_error:
            logger.error(f"Failed to log loop route error: {str(log_error)}")
        
        raise HTTPException(status_code=500, detail=f"Failed to retrieve loop: {str(e)}")

@router.post("/plan", response_model=LoopPlanResponse)
async def plan_loop(request: LoopPlanRequest):
    """
    Create execution plan for a loop.
    """
    logger.info(f"➡️ Entering plan_loop endpoint for loop_id: {request.loop_id}")
    # This would normally create a plan based on the prompt
    # For now, return a mock response
    logger.info(f"✅ Mock plan generated for loop_id: {request.loop_id}. Exiting plan_loop endpoint.")
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

@router.post("/complete", response_model=LoopCompletionResponse)
async def loop_complete_endpoint(request: LoopCompletionRequest):
    """
    Handle loop completion and initiate loop execution.
    
    This endpoint is called when a loop is ready to be executed and triggers:
    - Loop log writing
    - Memory state activation
    - Orchestration delegation to HAL/NOVA/CRITIC
    """
    logger.info(f"➡️ Entering loop_complete_endpoint for loop_id: {request.loop_id}, project_id: {request.project_id}, executor: {request.executor}")
    
    # Validate required fields
    if not request.loop_id or not request.project_id or not request.executor:
        logger.error(f"❌ Validation failed: loop_id, project_id, and executor are required. loop_id={request.loop_id}, project_id={request.project_id}, executor={request.executor}")
        raise HTTPException(status_code=400, detail="loop_id, project_id, and executor are required")
    logger.info("Request validation successful.")
    
    try:
        # Write to loop log (Mock)
        logger.info(f"Attempting to write loop log entry for loop_id: {request.loop_id}")
        # This would normally write to a persistent storage
        loop_log_entry = {
            "loop_id": request.loop_id,
            "project_id": request.project_id,
            "executor": request.executor,
            "notes": request.notes,
            "status": "activated",
            "timestamp": datetime.now().isoformat()
        }
        logger.info("Mock loop log entry created.")
        
        # Activate memory state (Mock)
        logger.info(f"Attempting to activate memory state for loop_id: {request.loop_id}")
        # This would normally update the memory state in a database
        memory_activation_result = {
            "status": "success",
            "loop_id": request.loop_id,
            "memory_state": "active"
        }
        logger.info("Mock memory state activation completed.")
        
        # Delegate to orchestration systems (Mock)
        logger.info(f"Attempting to delegate orchestration for loop_id: {request.loop_id}")
        # This would normally trigger the orchestration systems
        orchestration_result = {
            "status": "delegated",
            "systems": ["HAL", "NOVA", "CRITIC"],
            "loop_id": request.loop_id
        }
        logger.info("Mock orchestration delegation completed.")
        
        # Return success response
        logger.info(f"✅ Successfully activated loop {request.loop_id}. Exiting loop_complete_endpoint.")
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
        logger.error(f"❌ Error activating loop {request.loop_id}: {str(e)}")
        logger.error(traceback.format_exc()) # Log full traceback
        raise HTTPException(status_code=500, detail=f"Failed to activate loop: {str(e)}")

@router.post("/respond", response_model=LoopResponseResult)
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
        # --- Refactored: Use memory_engine ---
        from app.api.modules.memory_engine import get_memory_engine
        memory_engine = get_memory_engine()
        # --- End Refactor ---

        # Retrieve prior memory using memory.read
        try:
            # Modified to use agent_id instead of project_id and loop_id
            # Using the loop_id as the agent_id for compatibility
            prior_memory_result = await memory_engine.read_memory(
                agent_id=request.loop_id, # Using loop_id as agent_id for this context
                memory_type="loop",
                tag=request.input_key
            )
            
            if not prior_memory_result or prior_memory_result.get("status") != "success" or not prior_memory_result.get("value"):
                raise HTTPException(
                    status_code=404, 
                    detail=f"Memory not found or failed to read for key: {request.input_key} in loop: {request.loop_id}"
                )
            prior_memory = prior_memory_result.get("value") # Extract the actual value
                
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
                    # Instantiate HALAgent and create payload
                    hal_agent_instance = HALAgent()
                    payload = {
                        "project_id": request.project_id,
                        "loop_id": request.loop_id,
                        "task": f"Generate {request.response_type} for {prior_memory.get('content', '')}",
                        "details": {},
                        "source_agent": "loop_respond_endpoint"
                    }
                    # Execute HAL agent
                    agent_result = await hal_agent_instance.execute(payload)
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
        
        # Write to memory using memory_engine
        memory_result = await memory_engine.write_memory(memory_data)
        
        # Return success response
        return {
            "status": "success",
            "agent": request.agent,
            "input_key": request.input_key,
            "output_tag": output_key,
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

@router.post("/validate", response_model=LoopValidateResponse)
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

@router.get("/trace/{loop_id}", response_model=LoopTraceResponse)
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

@router.post("/trace")
async def add_loop_trace(data: LoopTraceRequest):
    """
    Inject synthetic loop trace.
    """
    # This would normally store the loop trace
    # For now, return a success response
    return {
        "status": "success",
        "loop_id": data.loop_id,
        "message": f"Loop trace for {data.loop_id} added successfully"
    }

@router.post("/reset", response_model=LoopResetResponse)
async def reset_loop(request: LoopResetRequest = None):
    """
    Memory reset for clean test runs.
    """
    # This would normally reset loop-related memory
    # For now, return a success response
    return LoopResetResponse(
        status="success",
        message="Loop memory reset successfully",
        timestamp=datetime.now().isoformat()
    )

@router.post("/persona-reflect", response_model=PersonaReflectResponse)
async def persona_reflect(data: PersonaReflectRequest):
    """
    Inject mode-aligned reflection trace.
    """
    # This would normally store the reflection
    # For now, return a success response
    return {
        "status": "success",
        "persona": data.persona,
        "loop_id": data.loop_id,
        "message": f"Reflection for {data.loop_id} with persona {data.persona} added successfully"
    }


# Added placeholder for missing /start route
from app.models.loop import StartLoopRequest # Ensure schema is imported

@router.post("/start", tags=["loop"])
async def start_loop(request: StartLoopRequest):
    """
    Placeholder for starting a loop execution.
    
    Args:
        request: StartLoopRequest containing project_id and optional agent_name/parameters
            
    Returns:
        Simple success message.
    """
    logger.info(f"Received request to start loop for project_id: {request.project_id}")
    logger.info(f"Agent name: {request.agent_name}, Parameters: {request.parameters}")
    
    # In a real implementation, this would trigger the loop controller/orchestrator
    # For now, just return a placeholder success response
    loop_id = str(uuid.uuid4()) # Generate a dummy ID for the response
    return {
        "status": "success", 
        "message": f"Placeholder: Loop start initiated for project {request.project_id}",
        "loop_id": loop_id
    }


