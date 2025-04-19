"""
Orchestrator Routes Module

This module defines the FastAPI routes for the Orchestrator component,
including the /api/orchestrator/consult endpoint that allows the Orchestrator
to reflect, route tasks, and respond to operator input.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.core.orchestrator import get_orchestrator
from app.modules.project_state import write_project_state
from app.modules.loop import run_agent_from_loop  # ✅ Loop trigger import
import uuid

# Create router
router = APIRouter()

# Define request and response models
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
        # This would typically use a memory manager, but we'll keep it simple for now
        print(f"Orchestrator consultation request: {request.task} for project {request.project_id}")
        
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
        
        # Create and return the response
        return {
            "status": "success",
            "message": "Consultation complete",
            "agent_id": request.agent_id,
            "reasoning": reflection
        }
        
    except Exception as e:
        # Log the error
        print(f"Error in orchestrator_consult: {str(e)}")
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Consultation failed: {str(e)}")

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
        
        # Write the project state to memory
        write_result = write_project_state(project_id, initial_state)
        
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
        print(f"Error in interpret_user_prompt: {str(e)}")
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Interpretation failed: {str(e)}")
