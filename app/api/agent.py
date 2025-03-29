from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Union
import os
import json
import glob
from app.core.prompt_manager import PromptManager
from app.core.memory_manager import MemoryManager
from app.core.vector_memory import VectorMemorySystem
from app.core.shared_memory import get_shared_memory
from app.core.execution_logger import get_execution_logger
from app.core.rationale_logger import get_rationale_logger
from app.core.self_evaluation import SelfEvaluationPrompt
from app.core.memory_context_reviewer import get_memory_context_reviewer
from app.core.task_tagger import get_task_tagger, TaskMetadata
from app.core.orchestrator import get_orchestrator, OrchestratorChain, OrchestratorStep
from app.core.execution_chain_logger import get_execution_chain_logger
from app.core.confidence_retry import get_confidence_retry_manager
from app.core.nudge_manager import get_nudge_manager
from app.core.task_persistence import get_task_persistence_manager, PendingTask
from app.models.workflow import WorkflowResponse, AgentStep
from app.providers import process_with_model
from app.db.database import get_database
from app.db.supabase_manager import get_supabase_client
from app.tools import get_tool_manager

# Create router with dynamic route generation
router = APIRouter()
prompt_manager = PromptManager()
memory_manager = MemoryManager()
vector_memory = VectorMemorySystem()
shared_memory = get_shared_memory()
execution_logger = get_execution_logger()
rationale_logger = get_rationale_logger()
memory_context_reviewer = get_memory_context_reviewer()
task_tagger = get_task_tagger()
tool_manager = get_tool_manager()
orchestrator = get_orchestrator()
execution_chain_logger = get_execution_chain_logger()
confidence_retry_manager = get_confidence_retry_manager()
nudge_manager = get_nudge_manager()
task_persistence_manager = get_task_persistence_manager()

class AgentRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[bool] = True
    model: Optional[str] = None  # Allow model override via API parameter
    tools_to_use: Optional[List[str]] = None  # Allow tool override via API parameter
    skip_reflection: Optional[bool] = False  # Option to skip reflection for faster responses
    auto_orchestrate: Optional[bool] = False  # Option to enable automatic orchestration
    enable_retry_loop: Optional[bool] = True  # Option to enable confidence-based retry loop

class AgentResponse(BaseModel):
    output: str
    metadata: Dict[str, Any]
    reflection: Optional[Dict[str, Any]] = None  # Include reflection data if available
    retry_data: Optional[Dict[str, Any]] = None  # Include retry data if retry was triggered
    nudge: Optional[Dict[str, Any]] = None  # Include nudge data if nudge was triggered

class OrchestrationResponse(BaseModel):
    steps: List[Dict[str, Any]]
    chain_id: str
    status: str
    metadata: Dict[str, Any]

class ExecuteTaskRequest(BaseModel):
    task_id: str

class TaskListResponse(BaseModel):
    tasks: List[Dict[str, Any]]
    total: int
    page: int
    limit: int

async def save_interaction_to_memory(
    agent_type: str, 
    input_text: str, 
    output_text: str, 
    metadata: Dict[str, Any],
    scope: str = "agent"
):
    """Background task to save interaction to memory"""
    # Save to regular memory
    await memory_manager.store(
        input_text=input_text,
        output_text=output_text,
        metadata=metadata
    )
    
    # Save to vector memory
    combined_text = f"User: {input_text}\nAssistant: {output_text}"
    await vector_memory.store_memory(
        content=combined_text,
        metadata=metadata,
        priority=metadata.get("priority", False)
    )
    
    # Save to shared memory
    topics = metadata.get("topics", [])
    if "agent" not in topics:
        topics.append("agent")
    if agent_type not in topics:
        topics.append(agent_type)
    
    # Add task category as a topic if available
    task_category = metadata.get("task_category")
    if task_category and task_category not in topics:
        topics.append(task_category)
    
    await shared_memory.store_memory(
        content=combined_text,
        metadata=metadata,
        priority=metadata.get("priority", False),
        scope=scope,
        topics=topics,
        agent_name=agent_type
    )

async def retrieve_and_analyze_memories(
    input_text: str, 
    agent_type: str,
    model: str,
    context: Optional[Dict[str, Any]] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Retrieve relevant memories and analyze their connection to the current task"""
    return await memory_context_reviewer.retrieve_and_analyze_memories(
        model=model,
        agent_type=agent_type,
        input_text=input_text,
        limit=limit,
        context=context
    )

async def execute_tools(
    tools_to_use: List[str],
    input_text: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute the specified tools
    
    Args:
        tools_to_use: List of tool names to execute
        input_text: User input text
        context: Request context
        
    Returns:
        Dictionary of tool results
    """
    tool_results = {}
    tools_used = []
    
    for tool_name in tools_to_use:
        try:
            # Get the tool
            tool = tool_manager.get_tool(tool_name)
            if not tool:
                print(f"Tool not found: {tool_name}")
                continue
            
            # Execute the tool with appropriate parameters
            # This is a simplified approach - in a real system, you'd need to
            # parse the input to determine the right parameters for each tool
            if tool_name == "search_google":
                result = await tool_manager.execute_tool(
                    tool_name=tool_name,
                    query=input_text
                )
            elif tool_name == "github_commit":
                # For demo purposes, we'll just pass some dummy values
                result = await tool_manager.execute_tool(
                    tool_name=tool_name,
                    repo_path="/path/to/repo",
                    commit_message=f"Commit related to: {input_text[:30]}...",
                    files=None,
                    branch="main"
                )
            else:
                # Generic execution for other tools
                result = await tool_manager.execute_tool(
                    tool_name=tool_name,
                    input=input_text,
                    context=context
                )
            
            # Store the result
            tool_results[tool_name] = result
            tools_used.append(tool_name)
            
        except Exception as e:
            print(f"Error executing tool {tool_name}: {str(e)}")
            tool_results[tool_name] = {"error": str(e)}
    
    return {
        "results": tool_results,
        "tools_used": tools_used
    }

async def process_agent_request(
    agent_type: str,
    request: AgentRequest, 
    background_tasks: BackgroundTasks,
    db=None,
    supabase_client=None
):
    """
    Process a request using the specified agent type
    
    Args:
        agent_type: The type of agent to use
        request: The agent request
        background_tasks: FastAPI background tasks
        db: Database connection
        supabase_client: Supabase client
        
    Returns:
        The processed result
    """
    try:
        # Load the agent prompt chain
        prompt_chain = prompt_manager.get_prompt_chain(agent_type)
        
        # Get tools from prompt chain or request
        tools_to_use = request.tools_to_use
        if tools_to_use is None and "tools" in prompt_chain:
            tools_to_use = prompt_chain.get("tools", [])
        
        # Execute tools if specified
        tool_execution_results = {}
        tools_used = []
        if tools_to_use:
            tool_execution = await execute_tools(
                tools_to_use=tools_to_use,
                input_text=request.input,
                context=request.context or {}
            )
            tool_execution_results = tool_execution.get("results", {})
            tools_used = tool_execution.get("tools_used", [])
        
        # Determine which model to use
        model = request.model if request.model else prompt_chain.get("model", "gpt-4")
        
        # Retrieve and analyze relevant memories
        memory_analysis = await retrieve_and_analyze_memories(
            input_text=request.input,
            agent_type=agent_type,
            model=model,
            context=request.context
        )
        
        memory_context = memory_analysis.get("memory_context", "")
        memory_analysis_text = memory_analysis.get("analysis", "")
        
        # Prepare the system prompt with memory context and analysis
        system_prompt = prompt_chain.get("system", "")
        
        if memory_context:
            system_prompt = f"{memory_context}\n\n{system_prompt}"
        
        if memory_analysis_text:
            system_prompt += f"\n\nMemory Analysis:\n{memory_analysis_text}"
        
        # If we have tool results, add them to the context
        if tool_execution_results:
            tool_context = "## Tool Results\n\n"
            for tool_name, result in tool_execution_results.items():
                tool_context += f"### {tool_name}\n"
                tool_context += f"```json\n{json.dumps(result, indent=2)}\n```\n\n"
            
            # Add tool context to system prompt
            system_prompt += "\n\n" + tool_context
        
        # Update the prompt chain with the enhanced system prompt
        prompt_chain["system"] = system_prompt
        
        # Process the input through the prompt chain
        result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=request.input,
            context=request.context
        )
        
        # Get the output content
        output_text = result.get("content", "")
        
        # Categorize the task
        task_metadata = await task_tagger.categorize_task(
            input_text=request.input,
            output_text=output_text,
            model=model,
            context=request.context
        )
        
        # Prepare metadata
        metadata = {
            "agent": agent_type,
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "timestamp": result.get("timestamp"),
            "model": result.get("model", model),
            "provider": result.get("provider", "unknown"),
            "priority": task_metadata.priority,
            "tools_used": tools_used,
            "task_category": task_metadata.task_category,
            "suggested_next_step": task_metadata.suggested_next_step,
            "tags": task_metadata.tags
        }
        
        # Log the execution
        log_id = await execution_logger.log_execution(
            agent_name=agent_type,
            model=metadata["model"],
            input_text=request.input,
            output_text=output_text,
            metadata=metadata,
            tools_used=tools_used
        )
        metadata["log_id"] = log_id
        
        # Save to memory if requested
        if request.save_to_memory:
            background_tasks.add_task(
                save_interaction_to_memory,
                agent_type,
                request.input,
                output_text,
                metadata,
                "agent"  # Default scope
            )
        
        # Skip reflection if requested
        if request.skip_reflection:
            return AgentResponse(
                output=output_text,
                metadata=metadata
            )
        
        # Generate rationale
        rationale_data = await SelfEvaluationPrompt.generate_rationale(
            model=model,
            agent_type=agent_type,
            input_text=request.input,
            output_text=output_text,
            context=request.context
        )
        
        # Generate self-evaluation
        evaluation_data = await SelfEvaluationPrompt.generate_self_evaluation(
            model=model,
            agent_type=agent_type,
            input_text=request.input,
            output_text=output_text,
            context=request.context
        )
        
        # Log the rationale and self-evaluation
        rationale_log_id = await rationale_logger.log_rationale(
            agent_name=agent_type,
            input_text=request.input,
            output_text=output_text,
            rationale=rationale_data.get("rationale", ""),
            assumptions=rationale_data.get("assumptions", ""),
            improvement_suggestions=rationale_data.get("improvement_suggestions", ""),
            confidence_level=evaluation_data.get("confidence_level", ""),
            failure_points=evaluation_data.get("failure_points", ""),
            task_category=metadata.get("task_category"),
            suggested_next_step=metadata.get("suggested_next_step"),
            metadata=metadata,
            execution_log_id=log_id
        )
        
        # Add reflection data to metadata
        reflection_data = {
            "rationale": rationale_data.get("rationale", ""),
            "assumptions": rationale_data.get("assumptions", ""),
            "improvement_suggestions": rationale_data.get("improvement_suggestions", ""),
            "confidence_level": evaluation_data.get("confidence_level", ""),
            "failure_points": evaluation_data.get("failure_points", ""),
            "memory_analysis": memory_analysis_text,
            "rationale_log_id": rationale_log_id
        }
        
        # Initialize response
        response = AgentResponse(
            output=output_text,
            metadata=metadata,
            reflection=reflection_data
        )
        
        # Check if we should trigger a retry based on confidence
        retry_data = {}
        if request.enable_retry_loop:
            retry_data = await confidence_retry_manager.check_confidence(
                confidence_level=evaluation_data.get("confidence_level", ""),
                agent_type=agent_type,
                model=model,
                input_text=request.input,
                output_text=output_text,
                reflection_data=reflection_data
            )
            
            if retry_data.get("retry_triggered", False):
                response.retry_data = retry_data
                # Update the output with the retry response if confidence improved
                original_confidence = confidence_retry_manager._parse_confidence(evaluation_data.get("confidence_level", ""))
                retry_confidence = confidence_retry_manager._parse_confidence(retry_data.get("retry_confidence", ""))
                
                if retry_confidence > original_confidence:
                    response.output = retry_data.get("retry_response", output_text)
        
        # Check if we should generate a nudge
        nudge_data = await nudge_manager.check_for_nudge(
            agent_name=agent_type,
            input_text=request.input,
            output_text=output_text,
            reflection_data=reflection_data
        )
        
        if nudge_data.get("nudge_needed", False):
            response.nudge = nudge_data
        
        # If auto_orchestrate is false but there's a suggested next step, store it as a pending task
        if not request.auto_orchestrate and metadata.get("suggested_next_step"):
            # Determine the suggested agent based on the task category and suggested next step
            suggested_agent = await orchestrator._determine_next_agent(
                current_agent=agent_type,
                suggested_next_step=metadata.get("suggested_next_step", ""),
                task_category=metadata.get("task_category"),
                tags=metadata.get("tags", [])
            )
            
            if suggested_agent:
                # Store the pending task
                await task_persistence_manager.store_pending_task(
                    task_description=metadata.get("suggested_next_step", ""),
                    origin_agent=agent_type,
                    suggested_agent=suggested_agent,
                    priority=metadata.get("priority", False),
                    metadata={
                        "task_category": metadata.get("task_category"),
                        "tags": metadata.get("tags", []),
                        "log_id": log_id,
                        "rationale_log_id": rationale_log_id
                    },
                    original_input=request.input,
                    original_output=output_text
                )
        
        # Return the processed result
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing {agent_type} request: {str(e)}")

async def orchestrate_workflow(
    agent_type: str,
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    db=None,
    supabase_client=None
):
    """
    Orchestrate a multi-agent workflow
    
    Args:
        agent_type: The type of the initial agent
        request: The agent request
        background_tasks: FastAPI background tasks
        db: Database connection
        supabase_client: Supabase client
        
    Returns:
        The orchestration result
    """
    try:
        # Use the orchestrator to handle the workflow
        chain = await orchestrator.orchestrate(
            initial_agent=agent_type,
            initial_input=request.input,
            context=request.context,
            auto_orchestrate=request.auto_orchestrate,
            max_steps=5,  # Limit to 5 steps to prevent infinite loops
            background_tasks=background_tasks,
            db=db,
            supabase_client=supabase_client
        )
        
        # Convert the chain to a response format
        steps = []
        for step in chain.steps:
            step_dict = {
                "step_number": step.step_number,
                "agent_name": step.agent_name,
                "input": step.input_text,
                "output": step.output_text,
                "metadata": step.metadata,
                "reflection": step.reflection
            }
            steps.append(step_dict)
        
        # Return the orchestration result
        return OrchestrationResponse(
            steps=steps,
            chain_id=chain.chain_id,
            status=chain.status,
            metadata={
                "created_at": chain.created_at,
                "updated_at": chain.updated_at,
                "step_count": len(chain.steps)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error orchestrating workflow: {str(e)}")

async def get_agent_history(agent_type: str, limit: int = 10, db=None):
    """
    Get history of agent interactions
    
    Args:
        agent_type: The type of agent
        limit: Maximum number of results to return
        db: Database connection
        
    Returns:
        List of agent interactions
    """
    try:
        # Query the memory for agent interactions
        results = await memory_manager.query(
            query=f"agent:{agent_type}",
            limit=limit
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving {agent_type} history: {str(e)}")

# Dynamically register routes for all agent types based on prompt files
def register_agent_routes():
    """Register routes for all agent types based on prompt files"""
    # Get the prompts directory
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
    
    # Find all JSON prompt files
    prompt_files = glob.glob(os.path.join(prompts_dir, "*.json"))
    
    # Register a route for each agent type
    for prompt_file in prompt_files:
        agent_type = os.path.splitext(os.path.basename(prompt_file))[0]
        
        # Register the main agent endpoint
        @router.post(f"/{agent_type}", response_model=Union[AgentResponse, OrchestrationResponse])
        async def process_request(
            request: AgentRequest,
            background_tasks: BackgroundTasks,
            db=Depends(get_database),
            supabase_client=Depends(get_supabase_client),
            agent_type=agent_type
        ):
            # If auto_orchestrate is enabled, use the orchestrator
            if request.auto_orchestrate:
                return await orchestrate_workflow(
                    agent_type=agent_type,
                    request=request,
                    background_tasks=background_tasks,
                    db=db,
                    supabase_client=supabase_client
                )
            else:
                # Otherwise, just process the request with a single agent
                return await process_agent_request(
                    agent_type=agent_type,
                    request=request,
                    background_tasks=background_tasks,
                    db=db,
                    supabase_client=supabase_client
                )
        
        # Register the history endpoint
        @router.get(f"/{agent_type}/history", response_model=List[Dict[str, Any]])
        async def get_history(
            limit: int = 10,
            db=Depends(get_database),
            agent_type=agent_type
        ):
            return await get_agent_history(
                agent_type=agent_type,
                limit=limit,
                db=db
            )
        
        # Register the rationale logs endpoint
        @router.get(f"/{agent_type}/rationale", response_model=List[Dict[str, Any]])
        async def get_rationale_logs(
            limit: int = 10,
            offset: int = 0,
            agent_type=agent_type
        ):
            return await rationale_logger.get_rationale_logs(
                agent_name=agent_type,
                limit=limit,
                offset=offset
            )
        
        print(f"Registered agent routes for: {agent_type}")

# Register all agent routes
register_agent_routes()

# Register orchestration routes
@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(
    request: AgentRequest,
    agent_type: str,
    background_tasks: BackgroundTasks,
    db=Depends(get_database),
    supabase_client=Depends(get_supabase_client)
):
    """
    Orchestrate a multi-agent workflow starting with the specified agent
    """
    # Force auto_orchestrate to True for this endpoint
    request.auto_orchestrate = True
    
    return await orchestrate_workflow(
        agent_type=agent_type,
        request=request,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client
    )

@router.get("/chains", response_model=List[Dict[str, Any]])
async def get_chains(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None
):
    """
    Get execution chains with optional filtering
    """
    chains = await execution_chain_logger.get_chains(
        limit=limit,
        offset=offset,
        status=status
    )
    
    return [chain.dict() for chain in chains]

@router.get("/chains/{chain_id}", response_model=Dict[str, Any])
async def get_chain(chain_id: str):
    """
    Get an execution chain by ID
    """
    chain = await execution_chain_logger.get_chain(chain_id)
    
    if not chain:
        raise HTTPException(status_code=404, detail=f"Chain not found: {chain_id}")
    
    return chain.dict()

@router.get("/chains/{chain_id}/steps/{step_number}", response_model=Dict[str, Any])
async def get_chain_step(chain_id: str, step_number: int):
    """
    Get a step in an execution chain
    """
    step = await execution_chain_logger.get_step(chain_id, step_number)
    
    if not step:
        raise HTTPException(status_code=404, detail=f"Step not found: {chain_id}/{step_number}")
    
    return step.dict()

# Register nudge routes
@router.get("/nudges", response_model=List[Dict[str, Any]])
async def get_nudges(
    limit: int = 10,
    offset: int = 0,
    agent_name: Optional[str] = None
):
    """
    Get nudge logs with optional filtering
    """
    nudges = await nudge_manager.get_nudge_logs(
        limit=limit,
        offset=offset,
        agent_name=agent_name
    )
    
    return nudges

# Register pending tasks routes
@router.get("/tasks/pending", response_model=TaskListResponse)
async def get_pending_tasks(
    limit: int = 10,
    offset: int = 0,
    origin_agent: Optional[str] = None,
    suggested_agent: Optional[str] = None,
    status: str = "pending"
):
    """
    Get pending tasks with optional filtering
    """
    tasks = await task_persistence_manager.get_pending_tasks(
        limit=limit,
        offset=offset,
        origin_agent=origin_agent,
        suggested_agent=suggested_agent,
        status=status
    )
    
    return TaskListResponse(
        tasks=[task.dict() for task in tasks],
        total=len(tasks),
        page=offset // limit + 1 if limit > 0 else 1,
        limit=limit
    )

@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(task_id: str):
    """
    Get a specific pending task by ID
    """
    task = await task_persistence_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    return task.dict()

@router.post("/tasks/execute", response_model=Dict[str, Any])
async def execute_task(
    request: ExecuteTaskRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_database),
    supabase_client=Depends(get_supabase_client)
):
    """
    Execute a pending task
    """
    result = await task_persistence_manager.execute_task(
        task_id=request.task_id,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client
    )
    
    return result

@router.patch("/tasks/{task_id}/status", response_model=Dict[str, Any])
async def update_task_status(
    task_id: str,
    status: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Update the status of a pending task
    """
    task = await task_persistence_manager.update_task_status(
        task_id=task_id,
        status=status,
        metadata=metadata
    )
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    return task.dict()
