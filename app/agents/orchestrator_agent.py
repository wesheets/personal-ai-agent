"""
Orchestrator Agent SDK Integration

This file implements the Orchestrator Agent using the Agent SDK framework.
It provides schema-validated orchestration with proper SDK integration.
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple

# Import the Agent SDK
from agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.orchestrator")

# Global project memory (in a production environment, this would be a database)
PROJECT_MEMORY = {}

class OrchestratorAgent(Agent):
    """
    Orchestrator Agent implementation using the Agent SDK.
    
    This agent coordinates agent activities and manages workflow execution.
    """
    
    def __init__(self):
        """Initialize the Orchestrator Agent with required configuration."""
        super().__init__(
            name="orchestrator-agent",
            role="Workflow Coordinator",
            tools=["coordinate", "manage", "delegate", "monitor"],
            permissions=["read_memory", "write_memory", "invoke_agents", "read_logs"],
            description="Coordinates agent activities and manages workflow execution",
            version="1.0.0",
            status="active",
            tone_profile={
                "style": "directive",
                "emotion": "neutral",
                "vibe": "coordinator",
                "persona": "Efficient orchestrator with a focus on process flow"
            },
            schema_path="schemas/orchestrator_output.schema.json",
            trust_score=0.98,
            contract_version="1.0.0"
        )
    
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
                tools = []
            
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
            
            else:
                # Default action for unknown tasks
                result["action"] = "unknown"
                result["output"] = f"ORCHESTRATOR agent executed task '{task}'"
            
            # Validate the result against the schema
            if not self.validate_schema(result):
                logger.error(f"Schema validation failed for orchestrator operation result")
                # Create a minimal valid result that will pass validation
                return {
                    "status": "error",
                    "task": task,
                    "tools": tools,
                    "project_id": project_id,
                    "intent": "orchestration",
                    "action": "error",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "output": "Error: Orchestrator operation failed schema validation",
                    "error": "Schema validation failed for original result"
                }
            
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
            
            # Return error response that will pass schema validation
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
            return "hal-agent", "Implementation after planning"
        elif last_agent == "hal-agent":
            return "nova-agent", "UI design after implementation"
        elif last_agent == "nova-agent":
            return "critic-agent", "Review after UI design"
        elif last_agent == "critic-agent":
            return "memory-agent", "Documentation after review"
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
        if next_agent == "core-forge" and PROJECT_MEMORY[project_id]["last_agent"] != "critic-agent":
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
        return last_agent == "memory-agent"
    
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

# Function to run orchestrator agent (for backward compatibility)
def run_orchestrator_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the Orchestrator Agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Create orchestrator agent instance
    orchestrator_agent = OrchestratorAgent()
    
    # Execute the task
    return orchestrator_agent.execute(task, project_id, tools)
