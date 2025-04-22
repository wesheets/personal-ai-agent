"""
Memory Agent SDK Integration

This file implements the Memory Agent using the Agent SDK framework.
It provides schema-validated memory operations with proper SDK integration.
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional, Union

# Import the Agent SDK
from agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.memory_agent")

# Global memory storage (in a production environment, this would be a database)
memory_log = []

class MemoryAgent(Agent):
    """
    Memory Agent implementation using the Agent SDK.
    
    This agent manages system memory and logging with structured data storage.
    """
    
    def __init__(self):
        """Initialize the Memory Agent with required configuration."""
        super().__init__(
            name="memory-agent",
            role="System Memory Manager",
            tools=["store", "retrieve", "organize", "log"],
            permissions=["read_memory", "write_memory", "manage_storage"],
            description="System memory and logging with structured data storage",
            version="1.1.0",
            status="active",
            tone_profile={
                "style": "structured",
                "emotion": "neutral",
                "vibe": "archivist",
                "persona": "Meticulous record-keeper with perfect recall and organized thinking"
            },
            schema_path="schemas/memory_output.schema.json",
            trust_score=0.95,
            contract_version="1.0.0"
        )
    
    def execute(self, 
                task: str,
                project_id: str = None,
                tools: List[str] = None) -> Dict[str, Any]:
        """
        Execute the Memory Agent's main functionality.
        
        Args:
            task (str): The memory operation to perform
            project_id (str, optional): The project identifier
            tools (List[str], optional): List of tools to use
            
        Returns:
            Dict[str, Any]: Result of the memory operation
        """
        try:
            logger.info(f"Running Memory Agent with task: {task}, project_id: {project_id}")
            print(f"🧠 Memory agent executing task '{task}'")
            
            # Initialize tools if None
            if tools is None:
                tools = []
            
            # Initialize result structure
            result = {
                "operation_type": "retrieve",
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success",
                "memory_path": f"/projects/{project_id}" if project_id else "/system",
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
            
            # Process different task types
            if task == "RECENT":
                # Return the 10 most recent logs in a readable format
                result["operation_type"] = "retrieve"
                result["data"] = self._get_recent_logs()
                result["output"] = result["data"]
            
            elif task == "RECENT_STRUCTURED":
                # Return the 10 most recent logs in structured JSON format
                result["operation_type"] = "retrieve"
                result["data"] = self._get_recent_logs_structured()
                result["output"] = result["data"]
            
            elif task == "SHOW_STRUCTURED":
                # Return the 10 most recent logs in structured JSON format
                result["operation_type"] = "retrieve"
                result["data"] = self._get_recent_logs_structured()
                result["output"] = result["data"]
            
            elif task == "FULL":
                # Return all logs in a readable format
                result["operation_type"] = "retrieve"
                result["data"] = self._get_all_logs()
                result["output"] = result["data"]
            
            elif task == "FULL_STRUCTURED":
                # Return all logs in structured JSON format
                result["operation_type"] = "retrieve"
                result["data"] = self._get_all_logs_structured()
                result["output"] = result["data"]
            
            elif task.startswith("QUERY:"):
                # Simple query functionality
                result["operation_type"] = "search"
                query = task.replace("QUERY:", "").strip().lower()
                result["query"] = query
                result["data"] = self._query_logs(query)
                result["output"] = result["data"]
            
            elif task.startswith("SEARCH:"):
                # Search functionality
                result["operation_type"] = "search"
                keyword = task.replace("SEARCH:", "").strip().lower()
                result["query"] = keyword
                result["data"] = self._search_logs(keyword)
                result["output"] = result["data"]
            
            elif task.startswith("STORE:"):
                # Store new memory entry
                result["operation_type"] = "store"
                content = task.replace("STORE:", "").strip()
                result["data_reference"] = self._store_memory(content, project_id)
                result["output"] = f"Memory stored: {content}"
            
            else:
                # Unknown task
                result["status"] = "error"
                result["error"] = f"Unknown task: {task}"
                result["output"] = f"🧠 MemoryAgent did not understand: '{task}'"
            
            # Validate the result against the schema
            if not self.validate_schema(result):
                logger.error(f"Schema validation failed for memory operation result")
                result["status"] = "error"
                result["error"] = "Schema validation failed"
                # Create a minimal valid result that will pass validation
                return {
                    "operation_type": "error",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status": "error",
                    "memory_path": f"/projects/{project_id}" if project_id else "/system",
                    "error": "Schema validation failed for original result",
                    "task": task,
                    "tools": tools,
                    "project_id": project_id,
                    "output": "Error: Memory operation failed schema validation"
                }
            
            return result
            
        except Exception as e:
            error_msg = f"Error running Memory agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            # Return error response that will pass schema validation
            return {
                "operation_type": "error",
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "error",
                "memory_path": f"/projects/{project_id}" if project_id else "/system",
                "error": error_msg,
                "task": task,
                "tools": tools if tools else [],
                "project_id": project_id,
                "output": f"Error: {error_msg}"
            }
    
    def _get_recent_logs(self) -> str:
        """Get the 10 most recent logs in a readable format."""
        if not memory_log:
            return "🧠 No recent memory."
        
        result = []
        for entry in memory_log[-10:]:
            if isinstance(entry, dict):
                # Format structured entry
                if "raw_message" in entry:
                    result.append(entry["raw_message"])
                else:
                    # Format structured entry without raw message
                    formatted = f"[{entry.get('timestamp', 'unknown')}] "
                    formatted += f"{entry.get('source', 'unknown')} "
                    
                    if entry.get('type') == "delegation":
                        formatted += f"delegated {entry.get('input', 'task')} to {entry.get('target', 'unknown')}"
                    else:
                        formatted += f"{entry.get('type', 'log')}: {entry.get('input', '')}"
                    
                    result.append(formatted)
            else:
                # Handle legacy string entries
                result.append(entry)
        
        return "\n".join(result)
    
    def _get_recent_logs_structured(self) -> str:
        """Get the 10 most recent logs in structured JSON format."""
        if not memory_log:
            return "🧠 No recent memory."
        
        return json.dumps(memory_log[-10:], indent=2)
    
    def _get_all_logs(self) -> str:
        """Get all logs in a readable format."""
        if not memory_log:
            return "🧠 Memory is empty."
        
        result = []
        for entry in memory_log:
            if isinstance(entry, dict):
                # Format structured entry
                if "raw_message" in entry:
                    result.append(entry["raw_message"])
                else:
                    # Format structured entry without raw message
                    formatted = f"[{entry.get('timestamp', 'unknown')}] "
                    formatted += f"{entry.get('source', 'unknown')} "
                    
                    if entry.get('type') == "delegation":
                        formatted += f"delegated {entry.get('input', 'task')} to {entry.get('target', 'unknown')}"
                    else:
                        formatted += f"{entry.get('type', 'log')}: {entry.get('input', '')}"
                    
                    result.append(formatted)
            else:
                # Handle legacy string entries
                result.append(entry)
        
        return "\n".join(result)
    
    def _get_all_logs_structured(self) -> str:
        """Get all logs in structured JSON format."""
        if not memory_log:
            return "🧠 Memory is empty."
        
        return json.dumps(memory_log, indent=2)
    
    def _query_logs(self, query: str) -> str:
        """Query logs for a specific term."""
        results = []
        for entry in memory_log:
            if isinstance(entry, dict):
                # Search in structured entry
                entry_str = json.dumps(entry).lower()
                if query in entry_str:
                    if "raw_message" in entry:
                        results.append(entry["raw_message"])
                    else:
                        results.append(json.dumps(entry))
            else:
                # Search in legacy string entry
                if query in entry.lower():
                    results.append(entry)
        
        if not results:
            return f"🧠 No memory entries found matching query: '{query}'"
        
        return "\n".join(results)
    
    def _search_logs(self, keyword: str) -> str:
        """Search logs for a specific keyword with formatted results."""
        results = []
        for entry in memory_log:
            if isinstance(entry, dict):
                # For structured entries, search in all fields
                entry_str = json.dumps(entry).lower()
                if keyword in entry_str:
                    # Format the result with timestamp for better readability
                    timestamp = entry.get('timestamp', 'unknown')
                    if "raw_message" in entry:
                        results.append(f"[{timestamp}] {entry['raw_message']}")
                    else:
                        # Create a readable format for structured entries
                        source = entry.get('source', 'unknown')
                        entry_type = entry.get('type', 'log')
                        content = entry.get('input', '')
                        results.append(f"[{timestamp}] {source} - {entry_type}: {content}")
            else:
                # For legacy string entries
                if keyword in entry.lower():
                    results.append(entry)
        
        # Return formatted results
        if not results:
            return f"🔍 SEARCH: No memory entries found matching '{keyword}'"
        
        return f"🔍 SEARCH RESULTS FOR '{keyword}':\n" + "\n".join(results)
    
    def _store_memory(self, message: str, project_id: str = None, details: str = "", source: str = "system") -> str:
        """
        Store a new memory entry.
        
        Args:
            message: The main message
            project_id: The project identifier
            details: Additional details
            source: The source of the memory entry
            
        Returns:
            Reference to the stored memory
        """
        timestamp = datetime.datetime.now().isoformat()
        
        structured_entry = {
            "source": source,
            "type": "log",
            "input": message,
            "details": details,
            "timestamp": timestamp,
            "raw_message": f"{source}: {message}",
            "project_id": project_id
        }
        
        # Validate the entry before storing
        entry_validation = {
            "operation_type": "store",
            "timestamp": timestamp,
            "status": "success",
            "memory_path": f"/projects/{project_id}/logs" if project_id else "/system/logs",
            "data_reference": f"/memory/{len(memory_log)}"
        }
        
        if not self.validate_schema(entry_validation):
            logger.error(f"Schema validation failed for memory entry")
            raise ValueError("Memory entry failed schema validation")
        
        memory_log.append(structured_entry)
        return f"/memory/{len(memory_log) - 1}"

# Function to add memory entry (for backward compatibility)
def add_memory_entry(message: str, details: str = "", source: str = "system") -> Dict[str, Any]:
    """
    Add a new memory entry programmatically.
    
    Args:
        message: The main message
        details: Additional details
        source: The source of the memory entry
        
    Returns:
        The created memory entry
    """
    # Create memory agent instance
    memory_agent = MemoryAgent()
    
    # Use the store method with schema validation
    try:
        memory_path = memory_agent._store_memory(message, None, details, source)
        
        # Return the last entry for backward compatibility
        return memory_log[-1]
    except ValueError as e:
        logger.error(f"Error adding memory entry: {str(e)}")
        
        # Create a basic entry without validation for backward compatibility
        timestamp = datetime.datetime.now().isoformat()
        
        structured_entry = {
            "source": source,
            "type": "log",
            "input": message,
            "details": details,
            "timestamp": timestamp,
            "raw_message": f"{source}: {message}",
            "validation_error": str(e)
        }
        
        memory_log.append(structured_entry)
        return structured_entry

# Function to run memory agent (for backward compatibility)
def run_memory_agent(task: str, project_id: str = None, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the Memory Agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Create memory agent instance
    memory_agent = MemoryAgent()
    
    # Execute the task
    return memory_agent.execute(task, project_id, tools)
