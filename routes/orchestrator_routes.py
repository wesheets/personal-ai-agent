"""
Orchestrator Routes Module

This module defines the FastAPI routes for the Orchestrator component,
including the /api/orchestrator/consult endpoint that allows the Orchestrator
to reflect, route tasks, and respond to operator input.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Import orchestrator modules with fallback discovery
try:
    from app.core.orchestrator import get_orchestrator
    print("✅ Successfully imported orchestrator core")
except ImportError as e:
    print(f"⚠️ Failed to import orchestrator core: {e}. Initiating fallback discovery.")
    try:
        # Import schema discovery utility
        from app.utils.schema_discovery import discover_and_import_schema, get_structured_error, log_schema_error_to_memory
        
        # Try to discover and import get_orchestrator
        get_orchestrator, import_statement = discover_and_import_schema("get_orchestrator")
        if get_orchestrator:
            print(f"✅ Successfully discovered and imported get_orchestrator: {import_statement}")
        else:
            print(f"❌ Failed to discover get_orchestrator")
            raise ImportError(f"Could not locate get_orchestrator in any known paths")
    except ImportError as e:
        print(f"❌ Schema discovery failed for orchestrator core: {e}")
        raise HTTPException(
            status_code=422,
            detail=get_structured_error("get_orchestrator", str(e))
        )

try:
    from app.modules.project_state import write_project_state, get_project_state
    print("✅ Successfully imported project_state module")
except ImportError as e:
    print(f"⚠️ Failed to import project_state module: {e}. Initiating fallback discovery.")
    try:
        # Import schema discovery utility
        from app.utils.schema_discovery import discover_and_import_schema, get_structured_error, log_schema_error_to_memory
        
        # Try to discover and import write_project_state
        write_project_state, import_statement1 = discover_and_import_schema("write_project_state")
        if write_project_state:
            print(f"✅ Successfully discovered and imported write_project_state: {import_statement1}")
        else:
            print(f"❌ Failed to discover write_project_state")
            raise ImportError(f"Could not locate write_project_state in any known paths")
            
        # Try to discover and import get_project_state
        get_project_state, import_statement2 = discover_and_import_schema("get_project_state")
        if get_project_state:
            print(f"✅ Successfully discovered and imported get_project_state: {import_statement2}")
        else:
            print(f"❌ Failed to discover get_project_state")
            raise ImportError(f"Could not locate get_project_state in any known paths")
    except ImportError as e:
        print(f"❌ Schema discovery failed for project_state module: {e}")
        raise HTTPException(
            status_code=422,
            detail=get_structured_error("project_state functions", str(e))
        )

try:
    from app.modules.loop import run_agent_from_loop  # ✅ Loop trigger import
    print("✅ Successfully imported loop module")
except ImportError as e:
    print(f"⚠️ Failed to import loop module: {e}. Initiating fallback discovery.")
    try:
        # Import schema discovery utility
        from app.utils.schema_discovery import discover_and_import_schema, get_structured_error, log_schema_error_to_memory
        
        # Try to discover and import run_agent_from_loop
        run_agent_from_loop, import_statement = discover_and_import_schema("run_agent_from_loop")
        if run_agent_from_loop:
            print(f"✅ Successfully discovered and imported run_agent_from_loop: {import_statement}")
        else:
            print(f"❌ Failed to discover run_agent_from_loop")
            raise ImportError(f"Could not locate run_agent_from_loop in any known paths")
    except ImportError as e:
        print(f"❌ Schema discovery failed for loop module: {e}")
        raise HTTPException(
            status_code=422,
            detail=get_structured_error("run_agent_from_loop", str(e))
        )

try:
    from app.modules.orchestrator_memory import (
        log_loop_event, 
        get_loop_log, 
        store_belief, 
        get_beliefs,
        get_latest_loop_events,
        get_agent_activity_summary
    )
    print("✅ Successfully imported orchestrator_memory module")
except ImportError as e:
    print(f"⚠️ Failed to import orchestrator_memory module: {e}. Initiating fallback discovery.")
    try:
        # Import schema discovery utility
        from app.utils.schema_discovery import discover_and_import_schema, get_structured_error, log_schema_error_to_memory
        
        # Try to discover and import each function
        memory_functions = ["log_loop_event", "get_loop_log", "store_belief", "get_beliefs", 
                           "get_latest_loop_events", "get_agent_activity_summary"]
        
        for func_name in memory_functions:
            func, import_statement = discover_and_import_schema(func_name)
            if func:
                print(f"✅ Successfully discovered and imported {func_name}: {import_statement}")
                # Assign the function to the current module's namespace
                locals()[func_name] = func
            else:
                print(f"❌ Failed to discover {func_name}")
                raise ImportError(f"Could not locate {func_name} in any known paths")
    except ImportError as e:
        print(f"❌ Schema discovery failed for orchestrator_memory module: {e}")
        raise HTTPException(
            status_code=422,
            detail=get_structured_error("orchestrator_memory functions", str(e))
        )
import uuid
import datetime
import json
import logging

# Configure logging
logger = logging.getLogger("api")

# Create router
router = APIRouter()

# Define request and response models with fallback discovery
try:
    # Try to import from app.schemas
    from app.schemas.orchestrator_schema import (
        OrchestratorConsultRequest,
        OrchestratorInterpretRequest,
        OrchestratorPlanRequest
    )
    print("✅ Successfully imported orchestrator schema classes")
except ImportError as e:
    print(f"⚠️ Failed to import orchestrator schema classes: {e}. Using local definitions.")
    try:
        # Import schema discovery utility
        from app.utils.schema_discovery import discover_and_import_schema, get_structured_error, log_schema_error_to_memory
        
        # Try to discover each schema class
        schema_classes = ["OrchestratorConsultRequest", "OrchestratorInterpretRequest", "OrchestratorPlanRequest"]
        schema_found = False
        
        for class_name in schema_classes:
            schema_class, import_statement = discover_and_import_schema(class_name)
            if schema_class:
                print(f"✅ Successfully discovered and imported {class_name}: {import_statement}")
                # Assign the class to the current module's namespace
                locals()[class_name] = schema_class
                schema_found = True
        
        # If no schemas were found, define them locally
        if not schema_found:
            print("⚠️ No schema classes found. Using local definitions.")
            
            class OrchestratorConsultRequest(BaseModel):
                """Request model for the orchestrator/consult endpoint"""
                agent_id: str = Field(..., description="Agent identifier")
                project_id: str = Field(..., description="Project context")
                task: str = Field(..., description="Primary task to evaluate")
                objective: Optional[str] = Field(None, description="Optional objective")
                context: Optional[str] = Field(None, description="Optional context")
            
            class OrchestratorInterpretRequest(BaseModel):
                """Request model for the orchestrator/interpret endpoint"""
                input: str = Field(..., description="User input to interpret")
            
            class OrchestratorPlanRequest(BaseModel):
                """Request model for the orchestrator/plan endpoint"""
                project_id: str = Field(..., description="Project identifier")
                current_agent: Optional[str] = Field(None, description="Current agent in the loop")
                task_status: Optional[str] = Field("completed", description="Status of the current task")
                task_result: Optional[str] = Field(None, description="Result of the current task")
                context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
            
            print("✅ Created local schema definitions as fallback")
    except Exception as e:
        print(f"❌ Schema discovery failed: {e}")
        
        # Define locally as last resort
        class OrchestratorConsultRequest(BaseModel):
            """Request model for the orchestrator/consult endpoint"""
            agent_id: str = Field(..., description="Agent identifier")
            project_id: str = Field(..., description="Project context")
            task: str = Field(..., description="Primary task to evaluate")
            objective: Optional[str] = Field(None, description="Optional objective")
            context: Optional[str] = Field(None, description="Optional context")
        
        class OrchestratorInterpretRequest(BaseModel):
            """Request model for the orchestrator/interpret endpoint"""
            input: str = Field(..., description="User input to interpret")
        
        class OrchestratorPlanRequest(BaseModel):
            """Request model for the orchestrator/plan endpoint"""
            project_id: str = Field(..., description="Project identifier")
            current_agent: Optional[str] = Field(None, description="Current agent in the loop")
            task_status: Optional[str] = Field("completed", description="Status of the current task")
            task_result: Optional[str] = Field(None, description="Result of the current task")
            context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
        
        print("⚠️ Using emergency local schema definitions due to discovery failure")

@router.post("/orchestrator/consult")
async def orchestrator_consult(request: OrchestratorConsultRequest, background_tasks: BackgroundTasks = None):
    """
    Consult the Orchestrator for task routing and decision making.
    
    This endpoint allows the Orchestrator to reflect on a task,
    determine which agents should handle it, and provide a decision
    with reasoning.
    
    Args:
        request: The consultation request containing project_id, task, agent_id, and optional objective and context
        background_tasks: Optional background tasks for async operations
        
    Returns:
        JSON response with agent recommendation and reasoning
    """
    try:
        # Get the orchestrator instance
        orchestrator = get_orchestrator()
        
        # Log the consultation request to memory
        await log_loop_event(
            loop_id=request.project_id,
            project_id=request.project_id,
            agent="orchestrator",
            task=f"Consultation for task: {request.task}",
            status="in_progress",
            additional_data={
                "objective": request.objective,
                "context": request.context
            }
        )
        
        # Process the request
        # In a full implementation, this would use more sophisticated logic
        # based on the orchestrator's capabilities
        
        # Use the specified agent_id or determine which agents to delegate to
        delegated_agents = [request.agent_id] if request.agent_id else ["hal", "nova"]
        
        # Generate a decision based on the task and context
        objective_text = request.objective if request.objective else request.task
        context_text = request.context if request.context else "No additional context provided"
        
        decision = f"Initiate project {request.project_id} with {' and '.join(delegated_agents).upper()}"
        
        # Generate a reflection on the decision
        reflection = (
            f"Analyzed task: '{request.task}' with objective: '{objective_text}' in context: '{context_text}'. "
            f"Based on task requirements and agent capabilities, determined that "
            f"{' and '.join(delegated_agents).upper()} are best suited for this task. "
            f"Initiating collaborative workflow with these agents as primary handlers for project {request.project_id}."
        )
        
        # Store belief about agent suitability
        await store_belief(
            project_id=request.project_id,
            belief=f"{' and '.join(delegated_agents).upper()} are well-suited for tasks like '{request.task}'",
            confidence=0.85,
            evidence=[request.task, objective_text, context_text],
            category="agent_selection"
        )
        
        # Log the completed consultation
        await log_loop_event(
            loop_id=request.project_id,
            project_id=request.project_id,
            agent="orchestrator",
            task=f"Consultation for task: {request.task}",
            status="completed",
            additional_data={
                "decision": decision,
                "reflection": reflection,
                "delegated_agents": delegated_agents
            }
        )
        
        # Create and return the response
        return {
            "status": "success",
            "message": "Consultation complete",
            "agent_id": request.agent_id,
            "reasoning": reflection,
            "delegated_agents": delegated_agents,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Log the error
        logger.error(f"Error in orchestrator_consult: {str(e)}")
        
        # Log the failed consultation
        await log_loop_event(
            loop_id=request.project_id,
            project_id=request.project_id,
            agent="orchestrator",
            task=f"Consultation for task: {request.task}",
            status="failed",
            additional_data={
                "error": str(e)
            }
        )
        
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Consultation failed: {str(e)}")

@router.post("/orchestrator/plan")
async def orchestrator_plan(request: OrchestratorPlanRequest):
    """
    Generate a plan for the next steps in a project.
    
    This endpoint analyzes the current state of a project and suggests
    the next agent to run, along with reasoning for the decision.
    
    Args:
        request: The planning request containing project_id and context
        
    Returns:
        JSON response with next agent recommendation and reasoning
    """
    try:
        # Get project state
        project_state = await get_project_state(request.project_id)
        
        if not project_state:
            # Create initial project state if it doesn't exist
            project_state = {
                "project_id": request.project_id,
                "status": "initialized",
                "agents_involved": ["orchestrator"],
                "latest_agent_action": "Project initialized by orchestrator",
                "next_recommended_step": None,
                "loop_count": 0,
                "max_loops": 5,
                "last_completed_agent": None,
                "completed_steps": []
            }
        
        # Get loop history
        loop_history = await get_latest_loop_events(request.project_id, limit=10)
        
        # Get agent activity summary
        agent_activity = await get_agent_activity_summary(request.project_id)
        
        # Get orchestrator beliefs
        beliefs = await get_beliefs(request.project_id)
        
        # Determine next agent based on current state and history
        next_agent = None
        reasoning = ""
        
        # Update project state with current agent completion
        if request.current_agent and request.task_status == "completed":
            if "completed_steps" not in project_state:
                project_state["completed_steps"] = []
                
            project_state["completed_steps"].append(request.current_agent)
            project_state["last_completed_agent"] = request.current_agent
            
            if "loop_count" not in project_state:
                project_state["loop_count"] = 0
                
            project_state["loop_count"] += 1
        
        # Simple agent rotation logic - can be enhanced with more sophisticated decision-making
        if request.current_agent == "hal":
            next_agent = "nova"
            reasoning = "HAL has completed its code generation task. NOVA should now review and enhance the implementation."
        elif request.current_agent == "nova":
            next_agent = "sage"
            reasoning = "NOVA has completed its review. SAGE should now provide high-level guidance and reflection."
        elif request.current_agent == "sage":
            next_agent = "hal"
            reasoning = "SAGE has provided guidance. HAL should now implement the suggested improvements."
        else:
            # Default to starting with HAL
            next_agent = "hal"
            reasoning = "Starting the loop with HAL for initial code generation."
        
        # Check for loop limit
        if project_state.get("loop_count", 0) >= project_state.get("max_loops", 5):
            next_agent = "orchestrator"
            reasoning = "Maximum loop count reached. Orchestrator should finalize the project."
        
        # Update project state with next recommendation
        project_state["next_recommended_step"] = next_agent
        project_state["latest_agent_action"] = f"Orchestrator recommended {next_agent} as next step"
        
        # Add current agent to involved agents if not already present
        if request.current_agent and "agents_involved" in project_state:
            if request.current_agent not in project_state["agents_involved"]:
                project_state["agents_involved"].append(request.current_agent)
        
        # Add next agent to involved agents if not already present
        if next_agent and "agents_involved" in project_state:
            if next_agent not in project_state["agents_involved"]:
                project_state["agents_involved"].append(next_agent)
        
        # Write updated project state
        await write_project_state(request.project_id, project_state)
        
        # Log the planning event
        await log_loop_event(
            loop_id=request.project_id,
            project_id=request.project_id,
            agent="orchestrator",
            task="Planning next steps",
            status="completed",
            additional_data={
                "current_agent": request.current_agent,
                "next_agent": next_agent,
                "reasoning": reasoning
            }
        )
        
        # Store belief about agent sequence
        if request.current_agent and next_agent:
            await store_belief(
                project_id=request.project_id,
                belief=f"{request.current_agent.upper()} should be followed by {next_agent.upper()} in the workflow",
                confidence=0.8,
                evidence=[f"{request.current_agent} completed task with status: {request.task_status}"],
                category="workflow_sequence"
            )
        
        # Return the planning response
        return {
            "status": "success",
            "project_id": request.project_id,
            "current_agent": request.current_agent,
            "next_agent": next_agent,
            "reasoning": reasoning,
            "project_state": project_state,
            "loop_count": project_state.get("loop_count", 0),
            "max_loops": project_state.get("max_loops", 5),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Log the error
        logger.error(f"Error in orchestrator_plan: {str(e)}")
        
        # Log the failed planning
        await log_loop_event(
            loop_id=request.project_id,
            project_id=request.project_id,
            agent="orchestrator",
            task="Planning next steps",
            status="failed",
            additional_data={
                "error": str(e),
                "current_agent": request.current_agent
            }
        )
        
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")

# Add an additional route at /plan that redirects to /orchestrator/plan
@router.post("/plan")
async def plan_redirect(request: OrchestratorPlanRequest):
    """
    Redirect endpoint for /plan to /orchestrator/plan.
    
    This endpoint provides compatibility for clients expecting the plan endpoint
    at /api/plan instead of /api/orchestrator/plan.
    
    Args:
        request: The planning request containing project_id and context
        
    Returns:
        JSON response with next agent recommendation and reasoning
    """
    # Simply call the orchestrator_plan function with the same request
    return await orchestrator_plan(request)

@router.get("/orchestrator/status")
async def orchestrator_status(project_id: str):
    """
    Get the current status of the orchestrator for a specific project.
    
    This endpoint provides comprehensive information about the current state
    of the project, including loop history, agent activity, and orchestrator beliefs.
    
    Args:
        project_id: Project identifier
        
    Returns:
        JSON response with orchestrator status information
    """
    try:
        # Get project state
        project_state = await get_project_state(project_id)
        
        if not project_state:
            return {
                "status": "not_found",
                "message": f"No project state found for project {project_id}",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        
        # Get loop history
        loop_history = await get_latest_loop_events(project_id, limit=5)
        
        # Get agent activity summary
        agent_activity = await get_agent_activity_summary(project_id)
        
        # Get orchestrator beliefs
        beliefs = await get_beliefs(project_id)
        
        # Calculate emotional state based on project progress
        loop_count = project_state.get("loop_count", 0)
        max_loops = project_state.get("max_loops", 5)
        progress_ratio = loop_count / max_loops if max_loops > 0 else 0
        
        emotional_state = "neutral"
        if progress_ratio < 0.2:
            emotional_state = "curious"
        elif progress_ratio < 0.5:
            emotional_state = "engaged"
        elif progress_ratio < 0.8:
            emotional_state = "focused"
        elif progress_ratio < 1.0:
            emotional_state = "determined"
        else:
            emotional_state = "satisfied"
        
        # Check if project memory exists
        memory_status = True
        try:
            memory_result = await read_memory(
                agent_id="orchestrator",
                memory_type="state",
                tag="project_state",
                project_id=project_id
            )
            memory_status = memory_result is not None
        except Exception:
            memory_status = False
            
        # Get simplified loop log for agent completions
        loop_log = []
        if loop_history:
            for entry in loop_history:
                if entry.get("status") == "completed":
                    loop_log.append({
                        "agent": entry.get("agent"),
                        "task": entry.get("task"),
                        "timestamp": entry.get("timestamp")
                    })
        
        # Map emotional state to required format
        emotion = "stable"
        if emotional_state in ["curious", "engaged"]:
            emotion = "reflective"
        elif emotional_state in ["focused", "determined"]:
            emotion = "intense"
            
        # Determine if there's an active loop
        active_loop = project_state.get("status") != "complete" and loop_count < max_loops
        
        # Return enhanced comprehensive status
        return {
            "status": "success",
            "project_id": project_id,
            "project_state": project_state,
            "loop_history": loop_history,
            "agent_activity": agent_activity,
            "beliefs": beliefs,
            "emotional_state": emotional_state,
            "next_agent": project_state.get("next_recommended_step"),
            "last_agent": project_state.get("last_completed_agent"),
            "loop_count": loop_count,
            "max_loops": max_loops,
            "progress_percentage": round(progress_ratio * 100, 1),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            
            # Enhanced fields as required
            "loop_log": loop_log,
            "active_loop": active_loop,
            "emotion": emotion,
            "progress_pct": round(progress_ratio * 100, 1),
            "memory_status": memory_status
        }
        
    except Exception as e:
        # Log the error
        logger.error(f"Error in orchestrator_status: {str(e)}")
        
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.post("/interpret")
async def interpret_user_prompt(request: Request):
    """
    Interpret user prompt and generate a project proposal.
    
    This endpoint takes a user's input text and generates a proposed goal,
    challenge insights, and task list for a new project.
    
    Args:
        request: The request containing the user input
        
    Returns:
        JSON response with project_id, proposed_goal, challenge_insights, and task_list
    """
    try:
        # Parse the request body
        body = await request.json()
        input_text = body.get("input", "")
        logic_modules = body.get("logic_modules", {})
        
        if not input_text:
            raise HTTPException(status_code=400, detail="Input text is required")
        
        # Generate a unique project ID
        project_id = f"loop_autospawned_{str(uuid.uuid4())[:8]}"
        
        # MOCK LOGIC: Replace this with real orchestrator logic when ready
        # In a real implementation, this would use NLP or LLM to analyze the input
        # and generate appropriate responses
        
        # For now, we'll return a mock response based on the input
        proposed_goal = f"Build a solution based on: {input_text}"
        
        # Generate some mock challenge insights
        challenge_insights = [
            "This may require integration with external APIs.",
            "Consider user authentication and data privacy.",
            "Mobile responsiveness will be important for this project."
        ]
        
        # Generate a mock task list
        task_list = [
            "Design user interface mockups",
            "Implement core functionality",
            "Create database schema",
            "Set up authentication system",
            "Develop API endpoints"
        ]
        
        # Log the interpretation event
        await log_loop_event(
            loop_id=project_id,
            project_id=project_id,
            agent="orchestrator",
            task=f"Interpret user prompt: {input_text[:50]}...",
            status="completed",
            additional_data={
                "proposed_goal": proposed_goal,
                "challenge_insights": challenge_insights,
                "task_list": task_list
            }
        )
        
        # Initialize the project in memory
        # This ensures the project exists and can be accessed by /system/status and /project/state
        print(f"🧠 Creating project memory for {project_id} with goal: {proposed_goal}")
        
        # Create initial project state
        initial_state = {
            "project_id": project_id,
            "status": "initialized",
            "goal": proposed_goal,
            "files_created": [],
            "agents_involved": ["orchestrator"],
            "latest_agent_action": "Project initialized by orchestrator",
            "next_recommended_step": "hal",  # Start with HAL agent
            "tool_usage": {},
            "loop_count": 0,
            "max_loops": 5,
            "last_completed_agent": None,
            "completed_steps": [],
            "challenge_insights": challenge_insights,
            "task_list": task_list
        }
        
        # Add logic modules if provided
        if logic_modules:
            initial_state["logic_modules"] = logic_modules
            print(f"🧩 Adding logic modules to project: {logic_modules}")
        
        # Write the project state to memory
        write_result = await write_project_state(project_id, initial_state)
        
        if write_result["status"] != "success":
            print(f"⚠️ Warning: Failed to initialize project memory: {write_result}")
            # Continue anyway, as we want to return the project_id even if memory initialization fails
        
        # Create and return the response
        return {
            "project_id": project_id,
            "proposed_goal": proposed_goal,
            "challenge_insights": challenge_insights,
            "task_list": task_list
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        # Log the error
        logger.error(f"Error in interpret_user_prompt: {str(e)}")
        
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Interpretation failed: {str(e)}")
