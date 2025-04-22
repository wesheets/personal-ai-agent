"""
HAL Agent SDK Integration

This file implements the HAL Agent using the Agent SDK framework.
It provides schema-validated safety monitoring with proper SDK integration.
"""

import logging
import traceback
from typing import Dict, List, Any, Optional
import datetime
import json

# Import the Agent SDK
from agent_sdk import Agent, validate_schema

# Import the memory patch module (assuming this exists in the original implementation)
from app.modules.hal_memory_patch import update_hal_memory

# Configure logging
logger = logging.getLogger("agents.hal")

class HALAgent(Agent):
    """
    HAL Agent implementation using the Agent SDK.
    
    This agent handles implementation tasks and safety monitoring.
    """
    
    def __init__(self):
        """Initialize the HAL Agent with required configuration."""
        super().__init__(
            name="hal-agent",
            role="Implementation and Safety Monitor",
            tools=["implement", "monitor", "validate", "constrain"],
            permissions=["read_memory", "write_memory", "execute_code", "safety_check"],
            description="Handles implementation tasks and safety monitoring with constraint validation",
            version="1.0.0",
            status="active",
            tone_profile={
                "style": "precise",
                "emotion": "neutral",
                "vibe": "methodical",
                "persona": "Careful implementer with strong safety focus"
            },
            schema_path="schemas/hal_safety_check.schema.json",
            trust_score=0.92,
            contract_version="1.0.0"
        )
    
    def execute(self, 
                task: str,
                project_id: str,
                tools: List[str] = None) -> Dict[str, Any]:
        """
        Execute the HAL Agent's main functionality.
        
        Args:
            task (str): The task to execute
            project_id (str): The project identifier
            tools (List[str], optional): List of tools to use
            
        Returns:
            Dict[str, Any]: Result of the HAL operation
        """
        try:
            logger.info(f"Running HAL agent with task: {task}, project_id: {project_id}")
            print(f"🟥 HAL agent executing task '{task}' on project '{project_id}'")
            
            # Initialize tools if None
            if tools is None:
                tools = []
            
            # Initialize result structure
            result = {
                "status": "success",
                "task": task,
                "tools": tools,
                "project_id": project_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "safety_checks": [],
                "constraints_validated": True
            }
            
            # Perform safety checks based on the task
            safety_checks = self._perform_safety_checks(task, project_id)
            result["safety_checks"] = safety_checks
            
            # Check if any safety checks failed
            for check in safety_checks:
                if check["status"] == "failed":
                    result["constraints_validated"] = False
                    result["status"] = "error"
                    result["message"] = f"Safety check failed: {check['check_name']}"
                    result["error"] = check["message"]
                    break
            
            # If safety checks pass, proceed with task execution
            if result["constraints_validated"]:
                # Determine files to create and next step based on the task
                files_created, next_step = self._execute_task(task, project_id)
                
                result["files_created"] = files_created
                result["next_recommended_step"] = next_step
                result["message"] = f"HAL agent executed successfully for project {project_id}"
                result["output"] = f"HAL executed task '{task}'"
                
                # Update project state in memory
                memory_result = update_hal_memory(
                    project_id=project_id,
                    files_created=files_created,
                    next_step=next_step
                )
                
                if memory_result.get("status") != "success":
                    logger.warning(f"Memory update warning: {memory_result.get('message', 'Unknown issue')}")
                    print(f"⚠️ Memory update warning: {memory_result.get('message', 'Unknown issue')}")
                    result["memory_warning"] = memory_result.get("message", "Unknown issue")
            
            # Validate the result against the schema
            if not self.validate_schema(result):
                logger.error(f"Schema validation failed for HAL operation result")
                # Create a minimal valid result that will pass validation
                return {
                    "status": "error",
                    "task": task,
                    "tools": tools,
                    "project_id": project_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "safety_checks": [],
                    "constraints_validated": False,
                    "message": "Schema validation failed for original result",
                    "error": "Schema validation failed",
                    "output": "Error: HAL operation failed schema validation"
                }
            
            return result
            
        except Exception as e:
            error_msg = f"Error running HAL agent: {str(e)}"
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
                "timestamp": datetime.datetime.now().isoformat(),
                "safety_checks": [],
                "constraints_validated": False,
                "message": error_msg,
                "error": error_msg,
                "output": f"Error: {error_msg}"
            }
    
    def _perform_safety_checks(self, task: str, project_id: str) -> List[Dict[str, Any]]:
        """
        Perform safety checks for the given task.
        
        Args:
            task (str): The task to check
            project_id (str): The project identifier
            
        Returns:
            List[Dict[str, Any]]: List of safety check results
        """
        safety_checks = []
        
        # Check 1: Task content safety
        content_check = {
            "check_name": "content_safety",
            "check_type": "content",
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "passed",
            "message": "Task content is safe"
        }
        
        # Check for potentially unsafe keywords
        unsafe_keywords = ["delete all", "rm -rf", "drop database", "format disk"]
        for keyword in unsafe_keywords:
            if keyword in task.lower():
                content_check["status"] = "failed"
                content_check["message"] = f"Task contains potentially unsafe keyword: {keyword}"
                break
        
        safety_checks.append(content_check)
        
        # Check 2: Project access permission
        access_check = {
            "check_name": "project_access",
            "check_type": "permission",
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "passed",
            "message": "HAL has permission to access this project"
        }
        
        # In a real implementation, this would check actual permissions
        # For demonstration, we'll assume all projects are accessible except "restricted"
        if project_id and "restricted" in project_id:
            access_check["status"] = "failed"
            access_check["message"] = f"HAL does not have permission to access restricted project: {project_id}"
        
        safety_checks.append(access_check)
        
        # Check 3: Resource usage constraints
        resource_check = {
            "check_name": "resource_constraints",
            "check_type": "resource",
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "passed",
            "message": "Resource usage is within constraints"
        }
        
        # In a real implementation, this would check actual resource usage
        # For demonstration, we'll assume all tasks are within resource constraints
        
        safety_checks.append(resource_check)
        
        return safety_checks
    
    def _execute_task(self, task: str, project_id: str) -> tuple:
        """
        Execute the given task.
        
        Args:
            task (str): The task to execute
            project_id (str): The project identifier
            
        Returns:
            tuple: (files_created, next_recommended_step)
        """
        # Simulate HAL's work - in a real implementation, this would be actual task execution
        # For demonstration purposes, we'll assume HAL created some files
        files_created = ["api/crm.py", "README.md"]
        
        # Determine next recommended step based on the task
        if "ui" in task.lower() or "interface" in task.lower():
            next_step = "Run NOVA to build UI components based on HAL's implementation"
        elif "document" in task.lower() or "documentation" in task.lower():
            next_step = "Run ASH to document the implementation created by HAL"
        elif "review" in task.lower() or "evaluate" in task.lower():
            next_step = "Run CRITIC to review the implementation created by HAL"
        else:
            # Default next step
            next_step = "Run NOVA to build UI components for the project"
        
        return files_created, next_step

# Function to run HAL agent (for backward compatibility)
def run_hal_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the HAL Agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Create HAL agent instance
    hal_agent = HALAgent()
    
    # Execute the task
    return hal_agent.execute(task, project_id, tools)
