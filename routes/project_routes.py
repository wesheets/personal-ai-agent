from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List
from app.modules.project_state import read_project_state
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("api")

router = APIRouter()


@router.get("/state")
async def get_project_state(
    project_id: str = Query(..., description="The project identifier")
):
    """
    Get the current state of a project.

    Args:
        project_id: The project identifier (e.g., "demo_writer_001")

    Returns:
        Dict containing the current project state
    """
    # Read the project state
    state = read_project_state(project_id)

    # Return the state
    return state


@router.get("/output")
async def get_project_output(
    project_id: str = Query(..., description="The project identifier")
):
    """
    Get the output of a project, including files created, last agent, task, and summary.

    Args:
        project_id: The project identifier (e.g., "demo_001")

    Returns:
        Dict containing the project output information
    """
    try:
        logger.info(f"Getting project output for project: {project_id}")
        
        # Read the project state to get files_created
        try:
            state = read_project_state(project_id)
            logger.info(f"Successfully read project state for {project_id}")
        except Exception as e:
            logger.error(f"Error reading project state: {str(e)}")
            state = {
                "status": "unknown",
                "error": f"Failed to read project state: {str(e)}"
            }
        
        # Get files created from project state
        files_created = state.get("files_created", [])
        
        # Try to get the last agent task from memory
        try:
            from memory.memory_reader import get_memory_for_project
            memory_entries = get_memory_for_project(project_id)
            
            # Find the last agent task entry
            last_agent = None
            task = None
            
            if memory_entries:
                # Sort entries by timestamp in descending order
                sorted_entries = sorted(
                    memory_entries, 
                    key=lambda x: x.get("timestamp", ""), 
                    reverse=True
                )
                
                # Find the first entry with an agent and action
                for entry in sorted_entries:
                    if entry.get("agent") and entry.get("action"):
                        last_agent = entry.get("agent")
                        task = entry.get("action")
                        break
        except Exception as e:
            logger.error(f"Error retrieving memory entries: {str(e)}")
            last_agent = None
            task = None
        
        # Try to get summary from system summary endpoint
        try:
            from agents.sage_agent import run_sage_agent
            summary_result = run_sage_agent(project_id, tools=["memory_reader"])
            summary = summary_result.get("summary", "No summary available")
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}")
            summary = "No summary available"
        
        # Determine status based on project state
        status = state.get("status", "unknown")
        
        # Construct response
        response = {
            "project_id": project_id,
            "files_created": files_created,
            "last_agent": last_agent or "None",
            "task": task or "No task information",
            "status": status,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Unexpected error in get_project_output: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "project_id": project_id,
            "files_created": [],
            "last_agent": "None",
            "task": "Error retrieving task information",
            "summary": f"Error: {str(e)}"
        }


@router.post("/start")
async def project_start(request: Dict[str, Any]):
    """
    Start a new project or resume an existing project.
    
    Args:
        request: Dictionary containing project parameters
            - project_id: The project identifier
            - goal: The project goal
            - agent: The agent to use (e.g., "orchestrator")
            
    Returns:
        Dict containing the project start status and details
    """
    # Extract required parameters
    project_id = request.get("project_id")
    goal = request.get("goal")
    agent = request.get("agent")
    
    # Add debug logging for project start
    print(f"🧪 Project start triggered: {project_id} {goal} {agent}")
    
    try:
        # Validate required parameters
        if not project_id:
            return {
                "status": "error",
                "message": "project_id is required",
                "agent": agent or "unknown",
                "goal": goal or "unknown",
                "project_id": "missing"
            }
        if not goal:
            return {
                "status": "error",
                "message": "goal is required",
                "agent": agent or "unknown",
                "goal": "missing",
                "project_id": project_id
            }
        if not agent:
            return {
                "status": "error",
                "message": "agent is required",
                "agent": "missing",
                "goal": goal,
                "project_id": project_id
            }
        
        # Try to import agent runner
        try:
            from app.api.agent.run import run_agent
            from app.modules.agent_runner import AGENT_RUNNERS
            
            # Validate agent exists in AGENT_RUNNERS
            if agent not in AGENT_RUNNERS:
                return {
                    "status": "error",
                    "message": f"Unknown agent: {agent}",
                    "agent": agent,
                    "goal": goal,
                    "project_id": project_id
                }
            
            # Log orchestrator function call
            print(f"⚙️ Calling orchestrator agent...")
            
            try:
                # Run the specified agent
                result = run_agent(
                    agent_id=agent,
                    project_id=project_id,
                    goal=goal,
                    additional_context=request.get("additional_context", {})
                )
                
                # Log orchestrator result
                print(f"✅ Orchestrator result: {result}")
                
                return {
                    "status": "success",
                    "message": f"Project {project_id} started with {agent} agent",
                    "project_id": project_id,
                    "agent": agent,
                    "goal": goal,
                    "result": result
                }
            except Exception as e:
                print(f"❌ Agent execution failed: {e}")
                return {
                    "status": "error",
                    "message": "Agent execution failed",
                    "error_details": str(e),
                    "project_id": project_id,
                    "agent": agent,
                    "goal": goal
                }
        except ImportError as e:
            print(f"❌ Import error: {e}")
            # Fallback if agent runner is not available
            return {
                "status": "error",
                "message": f"Failed to import agent runner: {str(e)}",
                "error_details": str(e),
                "project_id": project_id,
                "agent": agent,
                "goal": goal
            }
    except Exception as e:
        print(f"❌ Unexpected error in project_start: {e}")
        return {
            "status": "error",
            "message": f"Failed to start project",
            "error_details": str(e),
            "project_id": project_id or "unknown",
            "agent": agent or "unknown",
            "goal": goal or "unknown"
        }
