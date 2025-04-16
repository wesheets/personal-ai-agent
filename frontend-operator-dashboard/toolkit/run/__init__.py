"""
Toolkit Run Module

This module provides the execution environment for all tools in the toolkit.
It handles tool execution, logging, error handling, and reflection generation.
"""

import json
import time
import traceback
from typing import Any, Dict, Optional
from pathlib import Path

# Import the registry
from ..registry import registry

# Define the log file path
LOG_FILE = Path(__file__).parent.parent.parent / "toolkit_execution_log.json"


class ToolExecutionResult:
    """
    Represents the result of a tool execution.
    
    Attributes:
        success: Whether the tool execution was successful
        result: The result of the tool execution
        error: Error message if the execution failed
        execution_time: Time taken to execute the tool in seconds
        reflection: Optional reflection on the tool execution
    """
    
    def __init__(
        self,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        execution_time: float = 0.0,
        reflection: Optional[str] = None
    ):
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.reflection = reflection
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary representation."""
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "reflection": self.reflection
        }


def execute_tool(tool_name: str, **kwargs) -> ToolExecutionResult:
    """
    Execute a tool by name with the provided arguments.
    
    Args:
        tool_name: The fully qualified name of the tool to execute
        **kwargs: Arguments to pass to the tool
        
    Returns:
        A ToolExecutionResult object containing the execution result
    """
    # Get the tool from the registry
    tool_entry = registry.get_tool(tool_name)
    if not tool_entry:
        return ToolExecutionResult(
            success=False,
            error=f"Tool '{tool_name}' not found in registry"
        )
    
    # Check if the tool has a handler
    if not tool_entry.handler:
        return ToolExecutionResult(
            success=False,
            error=f"Tool '{tool_name}' has no implementation"
        )
    
    # Execute the tool with timing
    start_time = time.time()
    result = None
    error = None
    success = False
    
    try:
        # Execute the tool with retry logic
        for attempt in range(tool_entry.max_retries):
            try:
                result = tool_entry.handler(**kwargs)
                success = True
                break
            except Exception as e:
                if attempt < tool_entry.max_retries - 1:
                    # Wait before retrying
                    time.sleep(1)
                else:
                    # Last attempt failed
                    error = str(e)
                    traceback.print_exc()
    except Exception as e:
        error = str(e)
        traceback.print_exc()
    
    execution_time = time.time() - start_time
    
    # Generate reflection if required
    reflection = None
    if tool_entry.requires_reflection and success:
        try:
            # In a real implementation, this might call an LLM to generate a reflection
            reflection = f"Executed {tool_name} in {execution_time:.2f} seconds with result: {result}"
        except Exception as e:
            # Reflection generation failure should not affect the main result
            print(f"Failed to generate reflection: {e}")
    
    # Create the result object
    tool_result = ToolExecutionResult(
        success=success,
        result=result,
        error=error,
        execution_time=execution_time,
        reflection=reflection
    )
    
    # Log the execution
    log_tool_execution(tool_name, kwargs, tool_result)
    
    return tool_result


def log_tool_execution(tool_name: str, args: Dict[str, Any], result: ToolExecutionResult) -> None:
    """
    Log a tool execution to the toolkit execution log.
    
    Args:
        tool_name: The name of the tool that was executed
        args: The arguments that were passed to the tool
        result: The result of the tool execution
    """
    log_entry = {
        "timestamp": time.time(),
        "tool": tool_name,
        "args": args,
        "result": result.to_dict()
    }
    
    # Ensure the log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing log if it exists
    existing_log = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, 'r') as f:
                existing_log = json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, start with an empty log
            existing_log = []
    
    # Append the new entry
    existing_log.append(log_entry)
    
    # Write back to the log file
    with open(LOG_FILE, 'w') as f:
        json.dump(existing_log, f, indent=2)
