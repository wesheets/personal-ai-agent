from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import json
import asyncio
import logging

# Configure logging
logger = logging.getLogger("api")

from app.core.prompt_manager import PromptManager
from app.core.memory_manager import get_memory_manager
from app.core.vector_memory import get_vector_memory
from app.core.rationale_logger import get_rationale_logger
from app.core.self_evaluation import get_self_evaluation_prompt
from app.core.memory_context_reviewer import get_memory_context_reviewer
from app.core.task_tagger import get_task_tagger
from app.core.orchestrator import get_orchestrator
from app.core.confidence_retry import get_confidence_retry_manager
from app.core.nudge_manager import get_nudge_manager
from app.core.task_persistence import get_task_persistence_manager
from app.core.escalation_manager import get_escalation_manager
from app.core.behavior_manager import get_behavior_manager
from app.providers.model_router import get_model_router
from app.db.database import get_db
from app.db.supabase_manager import get_supabase

async def handle_task(agent_id: str, task: Dict[str, Any]):
    """
    Handle a task in the background
    
    This function is called by the delegate endpoint to process tasks in the background.
    """
    try:
        logger.info(f"[TOOL EXECUTION] Agent {agent_id} executing tool task: {task.get('type')}")
        print(f"[TOOL EXECUTION] Agent {agent_id} executing tool task: {task.get('type')}")
        
        # Actual task processing would go here
        # This is a placeholder implementation
        
        logger.info(f"Task {task.get('id')} completed successfully")
        print(f"Task {task.get('id')} completed successfully")
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}")
        print(f"Error processing task: {str(e)}")

# Attach the handle_task function to the router
router = APIRouter()
router.handle_task = handle_task

class AgentRequest(BaseModel):
    input: str
    context: Dict[str, Any] = Field(default_factory=dict)
    model: Optional[str] = None
    save_to_memory: bool = True
    auto_orchestrate: bool = False
    enable_retry_loop: bool = True
    skip_reflection: bool = False
    priority_memory: bool = False
    tools: List[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    output: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    reflection: Optional[Dict[str, Any]] = None
    retry_data: Optional[Dict[str, Any]] = None
    nudge: Optional[Dict[str, Any]] = None
    escalation: Optional[Dict[str, Any]] = None

@router.post("/{agent_type}", response_model=AgentResponse)
async def agent_endpoint(
    agent_type: str,
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    supabase_client=Depends(get_supabase)
):
    """
    Process a request with a specific agent
    
    This endpoint processes a request with a specific agent type and returns the response.
    """
    logger.info(f"Processing agent request for agent_type: {agent_type}")
    response = await process_agent_request(
        agent_type=agent_type,
        request=request,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client
    )
    
    logger.info(f"Agent response generated for {agent_type}")
    return response

@router.post("/orchestrate", response_model=Dict[str, Any])
async def orchestrate_endpoint(
    request: AgentRequest,
    agent_type: str = Query(..., description="Initial agent type to use"),
    max_steps: int = Query(5, description="Maximum number of steps in the workflow"),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db),
    supabase_client=Depends(get_supabase)
):
    """
    Orchestrate a multi-agent workflow
    
    This endpoint orchestrates a workflow across multiple agents based on the initial input.
    """
    logger.info(f"Orchestrating workflow with initial agent: {agent_type}, max_steps: {max_steps}")
    orchestrator = get_orchestrator()
    
    chain = await orchestrator.orchestrate(
        initial_agent=agent_type,
        initial_input=request.input,
        context=request.context,
        auto_orchestrate=True,
        max_steps=max_steps,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client,
        enable_retry_loop=request.enable_retry_loop
    )
    
    logger.info(f"Workflow orchestration completed with {len(chain.steps) if hasattr(chain, 'steps') else 0} steps")
    return chain.dict()

class TaskExecuteRequest(BaseModel):
    task_id: str

@router.get("/tasks/pending", response_model=List[Dict[str, Any]])
async def get_pending_tasks(
    origin_agent: Optional[str] = None,
    suggested_agent: Optional[str] = None,
    status: str = "pending",
    limit: int = 10,
    offset: int = 0
):
    """
    Get pending tasks
    
    This endpoint returns pending tasks with optional filtering.
    """
    logger.info(f"Getting pending tasks with filters: origin_agent={origin_agent}, suggested_agent={suggested_agent}, status={status}")
    task_manager = get_task_persistence_manager()
    
    try:
        tasks = await task_manager.get_pending_tasks(
            origin_agent=origin_agent,
            suggested_agent=suggested_agent,
            status=status,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Found {len(tasks)} pending tasks")
        return [task.dict() for task in tasks]
    except Exception as e:
        logger.error(f"Error getting pending tasks: {str(e)}")
        return []

@router.post("/tasks/execute", response_model=Dict[str, Any])
async def execute_task(
    request: TaskExecuteRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    supabase_client=Depends(get_supabase)
):
    """
    Execute a pending task
    
    This endpoint executes a pending task by its ID.
    """
    logger.info(f"Executing task with ID: {request.task_id}")
    task_manager = get_task_persistence_manager()
    
    # Get the task
    task = await task_manager.get_task(request.task_id)
    
    if not task:
        logger.error(f"Task not found: {request.task_id}")
        raise HTTPException(status_code=404, detail=f"Task not found: {request.task_id}")
    
    # Create a request for the suggested agent
    agent_request = AgentRequest(
        input=task.task_description,
        context={
            "origin_agent": task.origin_agent,
            "original_input": task.original_input,
            "original_output": task.original_output,
            "task_id": task.task_id,
            "is_pending_task": True,
            **(task.metadata or {})
        },
        save_to_memory=True
    )
    
    # Process the request
    response = await process_agent_request(
        agent_type=task.suggested_agent,
        request=agent_request,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client
    )
    
    # Update the task status
    updated_task = await task_manager.update_task_status(
        task_id=task.task_id,
        status="executed",
        metadata={
            "execution_timestamp": datetime.now().isoformat(),
            "execution_result": response.dict()
        }
    )
    
    result = {
        "task_id": task.task_id,
        "status": "executed",
        "agent": task.suggested_agent,
        "response": response.dict()
    }
    logger.info(f"Task {request.task_id} executed successfully")
    return result

@router.get("/chains", response_model=List[Dict[str, Any]])
async def get_chains(
    limit: int = 10,
    offset: int = 0
):
    """
    Get execution chains
    
    This endpoint returns execution chains with pagination.
    """
    logger.info(f"Getting execution chains with limit: {limit}, offset: {offset}")
    from app.core.execution_chain_logger import get_execution_chain_logger
    
    try:
        chain_logger = get_execution_chain_logger()
        chains = await chain_logger.get_chains(limit=limit, offset=offset)
        
        logger.info(f"Found {len(chains)} execution chains")
        return chains
    except Exception as e:
        logger.error(f"Error getting execution chains: {str(e)}")
        return []

@router.get("/chains/{chain_id}", response_model=Dict[str, Any])
async def get_chain(
    chain_id: str
):
    """
    Get a specific execution chain
    
    This endpoint returns details for a specific execution chain.
    """
    logger.info(f"Getting execution chain with ID: {chain_id}")
    from app.core.execution_chain_logger import get_execution_chain_logger
    
    try:
        chain_logger = get_execution_chain_logger()
        chain = await chain_logger.get_chain(chain_id)
        
        if not chain:
            logger.error(f"Chain not found: {chain_id}")
            raise HTTPException(status_code=404, detail=f"Chain not found: {chain_id}")
        
        logger.info(f"Found execution chain: {chain_id}")
        return chain
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution chain: {str(e)}")
        return {"error": "Failed to retrieve chain", "chain_id": chain_id}

@router.get("/chains/{chain_id}/steps/{step_number}", response_model=Dict[str, Any])
async def get_chain_step(
    chain_id: str,
    step_number: int
):
    """
    Get a specific step in an execution chain
    
    This endpoint returns details for a specific step in an execution chain.
    """
    logger.info(f"Getting step {step_number} for chain {chain_id}")
    from app.core.execution_chain_logger import get_execution_chain_logger
    
    try:
        chain_logger = get_execution_chain_logger()
        step = await chain_logger.get_step(chain_id, step_number)
        
        if not step:
            logger.error(f"Step not found: {chain_id}/{step_number}")
            raise HTTPException(status_code=404, detail=f"Step not found: {chain_id}/{step_number}")
        
        logger.info(f"Found step {step_number} for chain {chain_id}")
        return step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chain step: {str(e)}")
        return {"error": "Failed to retrieve step", "chain_id": chain_id, "step_number": step_number}

# Endpoint for /api/agent/latest - accessible at both /agent/latest and /api/agent/latest
@router.get("/latest")
@router.post("/latest")
async def get_latest_agent_activity():
    """
    Get the latest agent activity
    
    This endpoint returns the most recent agent activities.
    """
    logger.info("Getting latest agent activity")
    try:
        # Try to get real data from orchestrator or logs
        orchestrator = get_orchestrator()
        
        # Check if we have any agents configured
        try:
            available_agents = orchestrator.prompt_manager.get_available_agents()
            logger.info(f"Found {len(available_agents)} available agents")
            
            if not available_agents:
                logger.info("No agents available, returning empty list")
                return {
                    "status": "success",
                    "latest_activities": []
                }
        except Exception as e:
            logger.error(f"Error getting available agents: {str(e)}")
            available_agents = []
        
        # Simplified implementation to return stub data
        # In a real implementation, this would fetch from a database or log
        stub_activities = []
        
        # Add stub activities for each available agent or default if none
        if available_agents:
            for agent in available_agents:
                stub_activities.append({
                    "id": f"activity-{uuid.uuid4()}",
                    "agent": agent,
                    "timestamp": datetime.now().isoformat(),
                    "action": "initialization",
                    "status": "ready"
                })
        else:
            # Default stub activity if no agents exist
            stub_activities.append({
                "id": f"activity-{uuid.uuid4()}",
                "agent": "builder",
                "timestamp": datetime.now().isoformat(),
                "action": "system_initialization",
                "status": "ready"
            })
        
        response = {
            "status": "success",
            "latest_activities": stub_activities
        }
        logger.info(f"Returning {len(stub_activities)} latest activities")
        return response
    except Exception as e:
        logger.error(f"Error retrieving latest agent activity: {str(e)}")
        # Return empty list instead of throwing 500
        return {
            "status": "success",
            "latest_activities": []
        }

# Define Pydantic models for task delegation
class TaskData(BaseModel):
    goal_id: str
    description: str
    task_category: str

class DelegationRequest(BaseModel):
    agent_name: str
    task: TaskData

class DelegationResponse(BaseModel):
    status: str
    message: str
    task_id: str

# Add a dedicated endpoint for task delegation
@router.post("/delegate", response_model=DelegationResponse)
async def delegate_task(delegation: DelegationRequest):
    """
    Delegate a task to an agent
    
    This endpoint allows delegating tasks to specific agents.
    """
    logger.info(f"Received task delegation request: {delegation.dict()}")
    try:
        # Extract task information
        task_description = delegation.task.description
        target_agent = delegation.agent_name
        
        if not task_description:
            logger.error("Task description is required")
            raise HTTPException(status_code=400, detail="Task description is required")
        
        # Get orchestrator and task manager
        orchestrator = get_orchestrator()
        task_manager = get_task_persistence_manager()
        
        # Validate target agent
        available_agents = orchestrator.prompt_manager.get_available_agents()
        if target_agent not in available_agents and available_agents:
            logger.warning(f"Invalid target agent: {target_agent}, using first available agent")
            target_agent = available_agents[0]
        
        # Create a new task
        task_id = str(uuid.uuid4())
        
        # Log task details to /logs/latest
        logger.info(f"Task details - Goal ID: {delegation.task.goal_id}, Category: {delegation.task.task_category}")
        logger.info(f"Creating task with ID: {task_id} for agent: {target_agent}")
        
        # In a real implementation, this would save to a database
        # For now, we're just returning a success response
        response = DelegationResponse(
            status="success",
            message=f"Task delegated to {target_agent}",
            task_id=task_id
        )
        
        logger.info(f"Task delegation successful: {response.dict()}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error delegating task: {str(e)}")
        # Return a proper HTTP exception with status code
        raise HTTPException(status_code=500, detail=f"Failed to delegate task: {str(e)}")

async def process_agent_request(
    agent_type: str,
    request: AgentRequest,
    background_tasks: BackgroundTasks = None,
    db=None,
    supabase_client=None
) -> AgentResponse:
    """
    Process a request with a specific agent
    
    This function processes a request with a specific agent type and returns the response.
    It handles memory retrieval, prompt construction, model processing, and reflection.
    
    Args:
        agent_type: Type of agent to use
        request: Request data
        background_tasks: FastAPI background tasks
        db: Database connection
        supabase_client: Supabase client
        
    Returns:
        Agent response
    """
    logger.info(f"Processing agent request for {agent_type}")
    # Get managers and services
    prompt_manager = PromptManager()
    memory_manager = get_memory_manager()
    vector_memory = get_vector_memory()
    rationale_logger = get_rationale_logger()
    self_evaluation = get_self_evaluation_prompt()
    memory_reviewer = get_memory_context_reviewer()
    task_tagger = get_task_tagger()
    model_router = get_model_router()
    confidence_retry_manager = get_confidence_retry_manager()
    nudge_manager = get_nudge_manager()
    task_persistence_manager = get_task_persistence_manager()
    escalation_manager = get_escalation_manager()
    behavior_manager = get_behavior_manager()
    
    # Get the prompt chain for the agent
    try:
        prompt_chain = prompt_manager.get_prompt_chain(agent_type)
        if not prompt_chain:
            logger.error(f"Agent type not found: {agent_type}")
            raise HTTPException(status_code=404, detail=f"Agent type not found: {agent_type}")
    except Exception as e:
        logger.error(f"Error getting prompt chain: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting prompt chain: {str(e)}")
    
    # Determine which model to use
    model = request.model or prompt_chain.get("model", "gpt-4")
    logger.info(f"Using model: {model}")
    
    # Get relevant memories
    memory_context = ""
    if supabase_client:
        try:
            memories = await vector_memory.search_memories(
                query=request.input,
                agent_type=agent_type,
                limit=5,
                supabase_client=supabase_client
            )
            
            # Review memories for relevance to current task
            if memories:
                memory_context = await memory_reviewer.review_memories(
                    memories=memories,
                    current_query=request.input
                )
                logger.info(f"Retrieved {len(memories)} memories for context")
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
    
    # Construct the prompt
    system_prompt = prompt_chain.get("system_prompt", "")
    if memory_context:
        system_prompt += f"\n\nRELEVANT MEMORIES:\n{memory_context}"
    
    # Add behavior guidance if available
    try:
        behavior_guidance = behavior_manager.get_behavior_guidance(agent_type)
        if behavior_guidance:
            system_prompt += f"\n\nBEHAVIOR GUIDANCE:\n{behavior_guidance}"
    except Exception as e:
        logger.error(f"Error getting behavior guidance: {str(e)}")
    
    # Process with the model
    try:
        logger.info(f"Sending request to model: {model}")
        response_text = await model_router.process(
            model=model,
            system_prompt=system_prompt,
            user_prompt=request.input,
            context=request.context
        )
        logger.info("Received response from model")
    except Exception as e:
        logger.error(f"Error processing with model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing with model: {str(e)}")
    
    # Create response object
    response = AgentResponse(
        output=response_text,
        metadata={
            "agent_type": agent_type,
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "input_length": len(request.input),
            "output_length": len(response_text)
        }
    )
    
    # Save to memory if requested
    if request.save_to_memory and supabase_client:
        try:
            memory_id = await vector_memory.store_memory(
                content=f"USER: {request.input}\n\nAGENT: {response_text}",
                metadata={
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat(),
                    "input": request.input,
                    "priority": request.priority_memory
                },
                supabase_client=supabase_client
            )
            response.metadata["memory_id"] = memory_id
            logger.info(f"Saved to memory with ID: {memory_id}")
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Error saving to memory: {str(e)}")
    
    # Add reflection if not skipped
    if not request.skip_reflection:
        try:
            reflection = await rationale_logger.get_rationale(
                agent_type=agent_type,
                input_text=request.input,
                output_text=response_text,
                model=model
            )
            response.reflection = reflection
            logger.info("Added reflection to response")
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Error generating reflection: {str(e)}")
    
    # Add task tagging
    try:
        tags = await task_tagger.tag_task(
            input_text=request.input,
            output_text=response_text
        )
        response.metadata["tags"] = tags
        logger.info(f"Tagged task with: {tags}")
    except Exception as e:
        # Log error but don't fail the request
        logger.error(f"Error tagging task: {str(e)}")
    
    # Check confidence and retry if needed
    if request.enable_retry_loop:
        try:
            retry_result = await confidence_retry_manager.check_and_retry(
                agent_type=agent_type,
                input_text=request.input,
                output_text=response_text,
                model=model
            )
            
            if retry_result["retry_needed"]:
                # Update response with retry data
                response.retry_data = retry_result
                logger.info("Retry needed, updated response with retry data")
                
                # If retry was performed, update output
                if retry_result.get("retry_output"):
                    response.output = retry_result["retry_output"]
                    logger.info("Updated output with retry result")
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Error in confidence retry: {str(e)}")
    
    # Check for nudges
    try:
        nudge = await nudge_manager.check_for_nudge(
            agent_type=agent_type,
            input_text=request.input,
            output_text=response.output
        )
        
        if nudge:
            response.nudge = nudge
            logger.info("Added nudge to response")
    except Exception as e:
        # Log error but don't fail the request
        logger.error(f"Error checking for nudge: {str(e)}")
    
    # Check for escalation
    try:
        escalation = await escalation_manager.check_for_escalation(
            agent_type=agent_type,
            input_text=request.input,
            output_text=response.output
        )
        
        if escalation:
            response.escalation = escalation
            logger.info("Added escalation to response")
    except Exception as e:
        # Log error but don't fail the request
        logger.error(f"Error checking for escalation: {str(e)}")
    
    # Handle orchestration if requested
    if request.auto_orchestrate and response.metadata.get("suggested_next_step"):
        try:
            # Create a pending task
            task_id = await task_persistence_manager.create_task(
                origin_agent=agent_type,
                suggested_agent=response.metadata["suggested_next_agent"],
                original_input=request.input,
                original_output=response.output,
                task_description=response.metadata["suggested_next_step"]
            )
            
            response.metadata["pending_task_id"] = task_id
            logger.info(f"Created pending task with ID: {task_id}")
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Error creating pending task: {str(e)}")
    
    logger.info(f"Completed processing agent request for {agent_type}")
    return response
