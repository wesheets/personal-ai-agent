""" 
ORCHESTRATOR Agent Module 

This module provides implementation for the ORCHESTRATOR agent,
including the Next Agent Planner functionality.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger("agents.orchestrator")

# Import orchestrator logic functions
from app.modules.orchestrator_logic import (
    initialize_orchestrator_memory,
    log_orchestrator_decision,
    get_orchestrator_decisions,
    get_last_orchestrator_decision,
    mark_agent_completed,
    check_loop_completion,
    start_new_loop,
    mark_loop_complete,
    get_last_completed_agent,
    determine_next_agent,
    validate_next_agent_selection
)

# Import schema registry and project memory
from app.schema_registry import SCHEMA_REGISTRY
from app.memory.project_memory import PROJECT_MEMORY


def run_orchestrator_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the ORCHESTRATOR agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Running ORCHESTRATOR agent with task: {task}, project_id: {project_id}")
        print(f"🟪 ORCHESTRATOR agent running task '{task}' on project '{project_id}'")
        
        # Initialize tools if None
        if tools is None:
            tools = []
        
        # Ensure memory structures are initialized
        initialize_orchestrator_memory(project_id)
        
        # If task is to determine next agent
        if task == "determine_next_agent":
            # Determine which agent should run next
            next_agent, reason = determine_next_agent(project_id)
            
            # Validate the selection
            is_valid, error_msg = validate_next_agent_selection(project_id, next_agent)
            
            if not is_valid:
                logger.error(f"Invalid next agent selection: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Invalid next agent selection: {error_msg}",
                    "task": task,
                    "tools": tools,
                    "project_id": project_id
                }
            
            # Return the result
            return {
                "status": "success",
                "output": f"Next agent determined: {next_agent}",
                "next_agent": next_agent,
                "reason": reason,
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
        
        # If task is to mark agent as completed
        elif task.startswith("mark_completed:"):
            # Extract agent name from task
            agent_name = task.split(":", 1)[1].strip()
            
            # Mark agent as completed
            mark_agent_completed(project_id, agent_name)
            
            # Check if loop is complete
            loop_complete = check_loop_completion(project_id)
            
            # If loop is complete, determine if we should start a new loop
            if loop_complete:
                memory = PROJECT_MEMORY[project_id]
                loop_count = memory.get("loop_count", 1)
                max_loops = SCHEMA_REGISTRY.get("loop", {}).get("max_loops", 5)
                
                if loop_count < max_loops:
                    # Start a new loop
                    new_loop_count = start_new_loop(project_id)
                    return {
                        "status": "success",
                        "output": f"Agent {agent_name} marked as completed. Loop {loop_count} complete. Starting new loop {new_loop_count}.",
                        "loop_transition": True,
                        "new_loop_count": new_loop_count,
                        "task": task,
                        "tools": tools,
                        "project_id": project_id
                    }
                else:
                    # Mark loop as complete (all loops finished)
                    mark_loop_complete(project_id)
                    return {
                        "status": "success",
                        "output": f"Agent {agent_name} marked as completed. All loops complete.",
                        "all_loops_complete": True,
                        "task": task,
                        "tools": tools,
                        "project_id": project_id
                    }
            
            # Return success response
            return {
                "status": "success",
                "output": f"Agent {agent_name} marked as completed.",
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
        
        # If task is to get orchestrator decisions
        elif task == "get_decisions":
            # Get all decisions
            decisions = get_orchestrator_decisions(project_id)
            
            # Return the result
            return {
                "status": "success",
                "output": f"Retrieved {len(decisions)} orchestrator decisions.",
                "decisions": decisions,
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
        
        # If task is to get the last decision
        elif task == "get_last_decision":
            # Get the last decision
            decision = get_last_orchestrator_decision(project_id)
            
            # Return the result
            return {
                "status": "success",
                "output": f"Retrieved last orchestrator decision.",
                "decision": decision,
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
        
        # If task is to visualize decision log (debug route)
        elif task == "visualize_decisions":
            # Get all decisions
            decisions = get_orchestrator_decisions(project_id)
            
            # Format decisions for visualization
            visualization = "🧠 ORCHESTRATOR DECISION LOG 🧠\n\n"
            
            if not decisions:
                visualization += "No decisions recorded yet.\n"
            else:
                for i, decision in enumerate(decisions):
                    visualization += f"Decision #{i+1} (Loop {decision['loop_count']}):\n"
                    visualization += f"  Timestamp: {decision['timestamp']}\n"
                    visualization += f"  Last Agent: {decision['last_agent'] or 'None'}\n"
                    visualization += f"  Next Agent: {decision['next_agent'] or 'None'}\n"
                    visualization += f"  Reason: {decision['reason']}\n\n"
            
            # Return the visualization
            return {
                "status": "success",
                "output": visualization,
                "decisions": decisions,
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
        
        # Return default success response for unknown tasks
        return {
            "status": "success",
            "output": f"ORCHESTRATOR agent executed task '{task}'",
            "task": task,
            "tools": tools,
            "project_id": project_id
        }
        
    except Exception as e:
        error_msg = f"Error running ORCHESTRATOR agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "task": task,
            "tools": tools if tools else [],
            "project_id": project_id
        }
