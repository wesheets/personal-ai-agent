"""
Agent Router Tool for the Planner Agent

This tool routes subtasks to the appropriate agents, waits for responses,
logs results, and returns outcomes to the Planner Agent.
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Tool for routing subtasks to appropriate agents and handling responses.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the agent router.
        
        Args:
            base_url: Base URL for the agent API
        """
        self.base_url = base_url
        self.agent_endpoints = {
            "builder": "/agent/builder",
            "research": "/agent/research",
            "memory": "/agent/memory",
            "ops": "/agent/ops",
            "guardian": "/agent/guardian",
            "planner": "/agent/planner"
        }
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname("/app/logs/agent_router.json"), exist_ok=True)
    
    def route_task(self, 
                  subtask: Dict[str, Any], 
                  agent_name: str, 
                  goal_id: str,
                  wait_for_response: bool = True,
                  timeout_seconds: int = 300,
                  retry_count: int = 2) -> Dict[str, Any]:
        """
        Route a subtask to the specified agent.
        
        Args:
            subtask: Subtask details including description, parameters, etc.
            agent_name: Name of the agent to route the subtask to
            goal_id: ID of the parent goal
            wait_for_response: Whether to wait for a response
            timeout_seconds: Timeout in seconds
            retry_count: Number of retries on failure
            
        Returns:
            Response from the agent or status information
        """
        if agent_name not in self.agent_endpoints:
            error_msg = f"Unknown agent: {agent_name}"
            logger.error(error_msg)
            self._log_routing_event(goal_id, subtask, agent_name, "error", error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Prepare the request payload
        payload = {
            "task": subtask,
            "goal_id": goal_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log the routing attempt
        self._log_routing_event(goal_id, subtask, agent_name, "attempt", "Routing subtask to agent")
        
        # Attempt to route the subtask with retries
        for attempt in range(retry_count + 1):
            try:
                # Make the API request
                endpoint = f"{self.base_url}{self.agent_endpoints[agent_name]}"
                response = requests.post(endpoint, json=payload, timeout=timeout_seconds)
                
                # Check if the request was successful
                if response.status_code == 200:
                    result = response.json()
                    self._log_routing_event(goal_id, subtask, agent_name, "success", "Subtask routed successfully")
                    return {
                        "status": "success",
                        "agent": agent_name,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_msg = f"Request failed with status code {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    
                    if attempt < retry_count:
                        logger.info(f"Retrying... Attempt {attempt + 1} of {retry_count}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        self._log_routing_event(goal_id, subtask, agent_name, "error", error_msg)
                        return {
                            "status": "error",
                            "agent": agent_name,
                            "error": error_msg,
                            "timestamp": datetime.now().isoformat()
                        }
            
            except requests.exceptions.Timeout:
                error_msg = f"Request timed out after {timeout_seconds} seconds"
                logger.error(error_msg)
                
                if attempt < retry_count:
                    logger.info(f"Retrying... Attempt {attempt + 1} of {retry_count}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self._log_routing_event(goal_id, subtask, agent_name, "timeout", error_msg)
                    return {
                        "status": "timeout",
                        "agent": agent_name,
                        "error": error_msg,
                        "timestamp": datetime.now().isoformat()
                    }
            
            except Exception as e:
                error_msg = f"Error routing subtask to {agent_name}: {str(e)}"
                logger.error(error_msg)
                
                if attempt < retry_count:
                    logger.info(f"Retrying... Attempt {attempt + 1} of {retry_count}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self._log_routing_event(goal_id, subtask, agent_name, "error", error_msg)
                    return {
                        "status": "error",
                        "agent": agent_name,
                        "error": error_msg,
                        "timestamp": datetime.now().isoformat()
                    }
    
    def route_multiple_tasks(self, 
                           tasks: List[Dict[str, Any]], 
                           goal_id: str,
                           parallel: bool = False) -> List[Dict[str, Any]]:
        """
        Route multiple subtasks to their respective agents.
        
        Args:
            tasks: List of tasks with agent assignments
            goal_id: ID of the parent goal
            parallel: Whether to execute tasks in parallel
            
        Returns:
            List of responses from the agents
        """
        results = []
        
        if parallel:
            # TODO: Implement parallel execution using threading or asyncio
            # For now, fall back to sequential execution
            logger.warning("Parallel execution not yet implemented, falling back to sequential")
            
        # Execute tasks sequentially
        for task in tasks:
            agent_name = task.get("assigned_agent")
            subtask = task.get("subtask")
            
            if not agent_name or not subtask:
                error_msg = "Missing assigned_agent or subtask in task"
                logger.error(error_msg)
                results.append({
                    "status": "error",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Route the subtask
            result = self.route_task(subtask, agent_name, goal_id)
            results.append(result)
        
        return results
    
    def find_best_agent(self, task_description: str, task_type: Optional[str] = None) -> str:
        """
        Find the best agent for a given task based on its description and type.
        
        Args:
            task_description: Description of the task
            task_type: Type of the task (optional)
            
        Returns:
            Name of the best agent for the task
        """
        # Load the planner agent configuration to get agent mapping
        try:
            with open("/app/prompts/planner.json", "r") as f:
                planner_config = json.load(f)
            
            agent_mapping = planner_config.get("agent_mapping", {})
        except Exception as e:
            logger.error(f"Error loading planner configuration: {str(e)}")
            agent_mapping = {
                "code": "builder",
                "architecture": "builder",
                "research": "research",
                "information": "research",
                "memory": "memory",
                "knowledge": "memory",
                "deployment": "ops",
                "infrastructure": "ops",
                "security": "ops",
                "default": "research"
            }
        
        # If task_type is provided and exists in the mapping, use it
        if task_type and task_type in agent_mapping:
            return agent_mapping[task_type]
        
        # Otherwise, analyze the task description to find the best match
        task_lower = task_description.lower()
        
        # Check for keywords in the task description
        for keyword, agent in agent_mapping.items():
            if keyword != "default" and keyword in task_lower:
                return agent
        
        # Fall back to the default agent
        return agent_mapping.get("default", "research")
    
    def _log_routing_event(self, 
                          goal_id: str, 
                          subtask: Dict[str, Any], 
                          agent_name: str, 
                          status: str, 
                          message: str) -> None:
        """
        Log a routing event to the agent_router.json log file.
        
        Args:
            goal_id: ID of the parent goal
            subtask: Subtask details
            agent_name: Name of the agent
            status: Status of the routing event
            message: Message describing the event
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal_id,
            "subtask_id": subtask.get("id", "unknown"),
            "subtask_description": subtask.get("description", "unknown"),
            "agent_name": agent_name,
            "status": status,
            "message": message
        }
        
        try:
            # Read existing logs
            logs = []
            log_file = "/app/logs/agent_router.json"
            
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write back to file
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error logging routing event: {str(e)}")

# Create a singleton instance
_agent_router = None

def get_agent_router() -> AgentRouter:
    """
    Get the singleton instance of the agent router.
    
    Returns:
        AgentRouter instance
    """
    global _agent_router
    if _agent_router is None:
        _agent_router = AgentRouter()
    return _agent_router

def run(subtask: Dict[str, Any], agent_name: str, goal_id: str, **kwargs) -> Dict[str, Any]:
    """
    Run the agent router tool.
    
    Args:
        subtask: Subtask details
        agent_name: Name of the agent to route to
        goal_id: ID of the parent goal
        **kwargs: Additional arguments
        
    Returns:
        Response from the agent
    """
    router = get_agent_router()
    return router.route_task(subtask, agent_name, goal_id, **kwargs)

def run_multiple(tasks: List[Dict[str, Any]], goal_id: str, parallel: bool = False) -> List[Dict[str, Any]]:
    """
    Run the agent router tool for multiple tasks.
    
    Args:
        tasks: List of tasks with agent assignments
        goal_id: ID of the parent goal
        parallel: Whether to execute tasks in parallel
        
    Returns:
        List of responses from the agents
    """
    router = get_agent_router()
    return router.route_multiple_tasks(tasks, goal_id, parallel)

def find_agent(task_description: str, task_type: Optional[str] = None) -> str:
    """
    Find the best agent for a given task.
    
    Args:
        task_description: Description of the task
        task_type: Type of the task (optional)
        
    Returns:
        Name of the best agent for the task
    """
    router = get_agent_router()
    return router.find_best_agent(task_description, task_type)

# For testing purposes
if __name__ == "__main__":
    # Test the agent router
    router = AgentRouter()
    
    # Test finding the best agent
    test_tasks = [
        "Build a new API endpoint for user authentication",
        "Research the latest trends in AI development",
        "Store the results of the analysis in memory",
        "Deploy the application to the production environment"
    ]
    
    for task in test_tasks:
        agent = router.find_best_agent(task)
        print(f"Task: {task}")
        print(f"Best agent: {agent}")
        print()
