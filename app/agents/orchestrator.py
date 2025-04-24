"""
ORCHESTRATOR Agent Module

This module provides the consolidated implementation for the ORCHESTRATOR agent,
which coordinates task delegation and agent routing.
"""

import logging
import traceback
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logger = logging.getLogger("agents.orchestrator")

# Global project memory (in a production environment, this would be a database)
PROJECT_MEMORY = {}

class OrchestratorAgent:
    """
    Orchestrator Agent implementation.
    
    This agent coordinates agent activities, manages workflow execution,
    and handles task delegation and agent routing.
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the Orchestrator Agent with required configuration."""
        self.agent_id = "orchestrator"
        self.name = "Orchestrator"
        self.description = "Coordinates task delegation and agent routing"
        self.tools = tools or ["delegate", "plan", "resolve"]
        self.version = "1.0.0"
        self.status = "active"
        
        # Initialize project memory structure
        if not PROJECT_MEMORY:
            logger.info("Initializing global project memory structure")
    
    def execute(self, 
                task: str,
                project_id: str,
                tools: List[str] = None) -> Dict[str, Any]:
        """
        Execute the Orchestrator Agent's main functionality.
        
        Args:
            task (str): The task to execute
            project_id (str): The project identifier
            tools (List[str], optional): List of tools to use
            
        Returns:
            Dict[str, Any]: Result of the orchestration operation
        """
        try:
            logger.info(f"Running Orchestrator agent with task: {task}, project_id: {project_id}")
            print(f"🔄 Orchestrator agent executing task '{task}' on project '{project_id}'")
            
            # Initialize tools if None
            if tools is None:
                tools = self.tools
            
            # Initialize project memory if not exists
            if project_id not in PROJECT_MEMORY:
                PROJECT_MEMORY[project_id] = {
                    "loop_count": 0,
                    "decisions": [],
                    "last_agent": None,
                    "last_orchestrator_trigger": None
                }
            
            # Initialize result structure
            result = {
                "status": "success",
                "task": task,
                "tools": tools,
                "project_id": project_id,
                "intent": "orchestration",
                "action": task,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Process different task types
            if task == "initialize":
                # Initialize project orchestration
                result["action"] = "initialize"
                result["output"] = f"Initialized orchestration for project {project_id}"
                result["loop_id"] = f"{project_id}-loop-{PROJECT_MEMORY[project_id]['loop_count']}"
                
                # Determine and trigger the first agent
                next_agent, reason = self._determine_next_agent(project_id)
                trigger_result = self._trigger_next_agent(project_id)
                
                result["next_agent"] = next_agent
                result["trigger_result"] = trigger_result
                result["reason"] = reason
            
            elif task.startswith("complete:"):
                # Mark an agent as completed and determine next steps
                agent_name = task.replace("complete:", "").strip()
                result["action"] = "complete_agent"
                result["completed_agent"] = agent_name
                
                # Update project memory
                PROJECT_MEMORY[project_id]["last_agent"] = agent_name
                
                # Check if all loops are complete
                if self._check_all_loops_complete(project_id):
                    # Mark project as complete
                    self._mark_loop_complete(project_id)
                    result["output"] = f"Agent {agent_name} marked as completed. All loops complete."
                    result["all_loops_complete"] = True
                else:
                    # Determine and trigger the next agent
                    next_agent, reason = self._determine_next_agent(project_id)
                    trigger_result = self._trigger_next_agent(project_id)
                    
                    result["output"] = f"Agent {agent_name} marked as completed. Next agent triggered: {next_agent}"
                    result["next_agent"] = next_agent
                    result["trigger_result"] = trigger_result
                    result["reason"] = reason
            
            elif task == "get_decisions":
                # Get all decisions
                result["action"] = "get_decisions"
                decisions = self._get_orchestrator_decisions(project_id)
                
                result["output"] = f"Retrieved {len(decisions)} orchestrator decisions."
                result["decisions"] = decisions
            
            elif task == "get_last_decision":
                # Get the last decision
                result["action"] = "get_last_decision"
                decision = self._get_last_orchestrator_decision(project_id)
                
                result["output"] = f"Retrieved last orchestrator decision."
                result["decision"] = decision
            
            elif task == "visualize_decisions":
                # Visualize decision log
                result["action"] = "visualize_decisions"
                decisions = self._get_orchestrator_decisions(project_id)
                
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
                
                result["output"] = visualization
                result["decisions"] = decisions
            
            elif task == "trigger_next_agent":
                # Manually trigger the next agent
                result["action"] = "trigger_next_agent"
                trigger_result = self._trigger_next_agent(project_id)
                PROJECT_MEMORY[project_id]["last_orchestrator_trigger"] = trigger_result
                
                result["output"] = f"Triggered next agent: {trigger_result.get('triggered_agent')}"
                result["trigger_result"] = trigger_result
            
            elif task == "plan":
                # Create a plan for the project
                result["action"] = "plan"
                plan = self._create_plan(project_id)
                
                result["output"] = f"Created plan for project {project_id}"
                result["plan"] = plan
            
            elif task == "delegate":
                # Delegate a task to a specific agent
                if ":" not in task:
                    raise ValueError("Invalid delegate task format. Expected 'delegate:agent_name|task_description'")
                
                parts = task.split(":", 1)[1].strip().split("|")
                if len(parts) < 2:
                    raise ValueError("Invalid delegate task format. Expected 'delegate:agent_name|task_description'")
                
                agent_name = parts[0].strip()
                task_description = parts[1].strip()
                
                result["action"] = "delegate"
                result["delegated_agent"] = agent_name
                result["delegated_task"] = task_description
                
                # Record delegation
                delegation_result = self._delegate_task(project_id, agent_name, task_description)
                result["output"] = f"Delegated task to {agent_name}: {task_description}"
                result["delegation_result"] = delegation_result
            
            elif task == "resolve":
                # Resolve conflicts or issues
                result["action"] = "resolve"
                resolution = self._resolve_conflicts(project_id)
                
                result["output"] = f"Resolved conflicts for project {project_id}"
                result["resolution"] = resolution
            
            else:
                # Default action for unknown tasks
                result["action"] = "unknown"
                result["output"] = f"ORCHESTRATOR agent executed task '{task}'"
            
            # Record decision if applicable
            if "next_agent" in result:
                self._record_decision(
                    project_id=project_id,
                    last_agent=result.get("completed_agent", PROJECT_MEMORY[project_id]["last_agent"]),
                    next_agent=result["next_agent"],
                    reason=result.get("reason", "Unknown reason")
                )
            
            return result
            
        except Exception as e:
            error_msg = f"Error running Orchestrator agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            # Return error response
            return {
                "status": "error",
                "task": task,
                "tools": tools if tools else [],
                "project_id": project_id,
                "intent": "orchestration",
                "action": "error",
                "timestamp": datetime.datetime.now().isoformat(),
                "output": f"Error: {error_msg}",
                "error": error_msg
            }
    
    def _determine_next_agent(self, project_id: str) -> Tuple[str, str]:
        """
        Determine the next agent to run based on project state.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            Tuple[str, str]: Next agent name and reason
        """
        # Get project memory
        project_memory = PROJECT_MEMORY.get(project_id, {})
        
        # Get last agent
        last_agent = project_memory.get("last_agent")
        
        # Simple agent sequence for demonstration
        if last_agent is None:
            # First agent in the sequence
            return "core-forge", "Initial planning agent"
        elif last_agent == "core-forge":
            return "hal", "Implementation after planning"
        elif last_agent == "hal":
            return "nova", "UI design after implementation"
        elif last_agent == "nova":
            return "critic", "Review after UI design"
        elif last_agent == "critic":
            return "sage", "Analysis after review"
        elif last_agent == "sage":
            return "memory", "Documentation after analysis"
        else:
            # Default to core-forge if unknown last agent
            return "core-forge", f"Restarting after unknown agent: {last_agent}"
    
    def _trigger_next_agent(self, project_id: str) -> Dict[str, Any]:
        """
        Trigger the next agent in the sequence.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            Dict[str, Any]: Trigger result
        """
        # Determine next agent
        next_agent, reason = self._determine_next_agent(project_id)
        
        # Increment loop count if we're starting a new loop
        if next_agent == "core-forge" and PROJECT_MEMORY[project_id]["last_agent"] != "memory":
            PROJECT_MEMORY[project_id]["loop_count"] += 1
        
        # Create trigger result
        trigger_result = {
            "triggered_agent": next_agent,
            "timestamp": datetime.datetime.now().isoformat(),
            "loop_count": PROJECT_MEMORY[project_id]["loop_count"],
            "reason": reason,
            "status": "triggered"
        }
        
        # In a real implementation, this would actually trigger the agent
        # For demonstration, we just return the result
        
        return trigger_result
    
    def _check_all_loops_complete(self, project_id: str) -> bool:
        """
        Check if all loops are complete for the project.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            bool: True if all loops are complete, False otherwise
        """
        # Get project memory
        project_memory = PROJECT_MEMORY.get(project_id, {})
        
        # Get last agent
        last_agent = project_memory.get("last_agent")
        
        # Check if last agent is the last in the sequence
        return last_agent == "memory"
    
    def _mark_loop_complete(self, project_id: str) -> None:
        """
        Mark the current loop as complete.
        
        Args:
            project_id (str): The project identifier
        """
        # Update project memory
        PROJECT_MEMORY[project_id]["loop_complete"] = True
    
    def _record_decision(self, project_id: str, last_agent: str, next_agent: str, reason: str) -> None:
        """
        Record an orchestrator decision.
        
        Args:
            project_id (str): The project identifier
            last_agent (str): The last agent that ran
            next_agent (str): The next agent to run
            reason (str): The reason for the decision
        """
        # Create decision record
        decision = {
            "timestamp": datetime.datetime.now().isoformat(),
            "loop_count": PROJECT_MEMORY[project_id]["loop_count"],
            "last_agent": last_agent,
            "next_agent": next_agent,
            "reason": reason
        }
        
        # Add to decisions list
        PROJECT_MEMORY[project_id]["decisions"].append(decision)
    
    def _get_orchestrator_decisions(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all orchestrator decisions for the project.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            List[Dict[str, Any]]: List of decisions
        """
        # Get project memory
        project_memory = PROJECT_MEMORY.get(project_id, {})
        
        # Get decisions
        return project_memory.get("decisions", [])
    
    def _get_last_orchestrator_decision(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the last orchestrator decision for the project.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            Optional[Dict[str, Any]]: Last decision or None if no decisions
        """
        # Get all decisions
        decisions = self._get_orchestrator_decisions(project_id)
        
        # Return last decision if any
        if decisions:
            return decisions[-1]
        
        return None
    
    def _create_plan(self, project_id: str) -> Dict[str, Any]:
        """
        Create a plan for the project.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            Dict[str, Any]: Plan details
        """
        # Create a simple plan
        plan = {
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "steps": [
                {"agent": "core-forge", "purpose": "Initial planning"},
                {"agent": "hal", "purpose": "Implementation"},
                {"agent": "nova", "purpose": "UI design"},
                {"agent": "critic", "purpose": "Review"},
                {"agent": "sage", "purpose": "Analysis"},
                {"agent": "memory", "purpose": "Documentation"}
            ],
            "estimated_loops": 2,
            "current_loop": PROJECT_MEMORY[project_id]["loop_count"]
        }
        
        return plan
    
    def _delegate_task(self, project_id: str, agent_name: str, task_description: str) -> Dict[str, Any]:
        """
        Delegate a task to a specific agent.
        
        Args:
            project_id (str): The project identifier
            agent_name (str): The agent to delegate to
            task_description (str): The task description
            
        Returns:
            Dict[str, Any]: Delegation result
        """
        # Create delegation record
        delegation = {
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "task": task_description,
            "status": "delegated"
        }
        
        # In a real implementation, this would actually trigger the agent
        # For demonstration, we just return the result
        
        return delegation
    
    def _resolve_conflicts(self, project_id: str) -> Dict[str, Any]:
        """
        Resolve conflicts or issues in the project.
        
        Args:
            project_id (str): The project identifier
            
        Returns:
            Dict[str, Any]: Resolution result
        """
        # Create resolution record
        resolution = {
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "conflicts_found": 0,
            "conflicts_resolved": 0,
            "status": "no_conflicts"
        }
        
        return resolution

# Main function to run the orchestrator agent
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
            tools = ["delegate", "plan", "resolve"]
        
        # Create orchestrator agent instance
        orchestrator = OrchestratorAgent(tools)
        
        # Execute the task
        return orchestrator.execute(task, project_id, tools)
        
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

# Test function for isolated testing
def test_orchestrator_agent():
    """
    Test the ORCHESTRATOR agent in isolation.
    
    Returns:
        Dict containing test results
    """
    print("\n=== Testing ORCHESTRATOR Agent in isolation ===\n")
    
    try:
        # Create test data
        project_id = "test-project-123"
        
        # Run the agent with initialize task
        initialize_result = run_orchestrator_agent("initialize", project_id)
        
        # Print the result
        print(f"\nInitialize Result:")
        print(f"Status: {initialize_result.get('status', 'unknown')}")
        print(f"Output: {initialize_result.get('output', 'No output')}")
        print(f"Next Agent: {initialize_result.get('next_agent', 'None')}")
        
        # Run the agent with complete task
        complete_result = run_orchestrator_agent("complete:core-forge", project_id)
        
        print(f"\nComplete Result:")
        print(f"Status: {complete_result.get('status', 'unknown')}")
        print(f"Output: {complete_result.get('output', 'No output')}")
        print(f"Next Agent: {complete_result.get('next_agent', 'None')}")
        
        # Run the agent with get_decisions task
        decisions_result = run_orchestrator_agent("get_decisions", project_id)
        
        print(f"\nDecisions Result:")
        print(f"Status: {decisions_result.get('status', 'unknown')}")
        print(f"Output: {decisions_result.get('output', 'No output')}")
        print(f"Decisions Count: {len(decisions_result.get('decisions', []))}")
        
        return {
            "initialize_result": initialize_result,
            "complete_result": complete_result,
            "decisions_result": decisions_result
        }
        
    except Exception as e:
        error_msg = f"Error testing ORCHESTRATOR agent: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    # Run the isolation test if this module is executed directly
    test_orchestrator_agent()
