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

# Import memory operations
from app.modules.memory_writer import write_memory
from app.api.modules.memory import read_memory

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
    logger.info(f"🔍 DEBUG: loop_create endpoint called with plan_id: {request.plan_id}")
    
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
        if os.path.exists(loop_file):
            # Read existing loop entries
            try:
                with open(loop_file, 'r') as f:
                    loop_store = json.load(f)
                    if not isinstance(loop_store, dict):
                        loop_store = {}
            except json.JSONDecodeError:
                loop_store = {}
        else:
            loop_store = {}
        
        # Add new loop entry
        loop_store[loop_id] = loop_entry
        
        # Write updated loop store
        with open(loop_file, 'w') as f:
            json.dump(loop_store, f, indent=2)
        
        logger.info(f"✅ Successfully created loop with ID: {loop_id}")
        return LoopCreateResponse(
            loop_id=loop_id,
            plan_id=request.plan_id,
            loop_type=request.loop_type,
            status="success",
            timestamp=str(datetime.now()),
            metadata=request.metadata
        )
    except Exception as e:
        logger.error(f"❌ Error creating loop with plan_id {request.plan_id}: {str(e)}")
        
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
    logger.info(f"🔍 DEBUG: loop_get endpoint called with loop_id: {loop_id}")
    
    try:
        # In a real implementation, this would retrieve data from a database
        # For this minimal viable handler, we'll retrieve it from the simple JSON file
        
        loop_file = "/home/ubuntu/personal-ai-agent/logs/simple_loop_store.json"
        
        # Check if loop file exists
        if not os.path.exists(loop_file):
            raise HTTPException(status_code=404, detail=f"Loop ID not found: {loop_id}")
        
        # Read loop entries
        try:
            with open(loop_file, 'r') as f:
                loop_store = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to read loop store")
        
        # Check if loop_id exists
        if loop_id not in loop_store:
            raise HTTPException(status_code=404, detail=f"Loop ID not found: {loop_id}")
        
        # Get loop entry
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
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving loop with ID {loop_id}: {str(e)}")
        
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

@router.post("/api/loop/plan", response_model=LoopPlanResponse)
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

@router.post("/api/loop/complete", response_model=LoopCompletionResponse)
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

@router.post("/api/loop/respond", response_model=LoopResponseResult)
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
        
        # Write to memory
        memory_result = write_memory(memory_data)
        
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

@router.post("/api/loop/validate", response_model=LoopValidateResponse)
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

@router.get("/api/loop/trace", response_model=LoopTraceResponse)
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

@router.post("/api/loop/reset", response_model=LoopResetResponse)
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

@router.post("/api/loop/persona-reflect", response_model=PersonaReflectResponse)
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
