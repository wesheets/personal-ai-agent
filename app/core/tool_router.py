"""
Tool Router for the Personal AI Agent System.

This module provides dynamic discovery, routing, fallback mechanisms, and logging
for all tools available to the agent system.
"""

import os
import importlib
import inspect
import logging
from typing import Dict, List, Any, Callable, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app/logs/tool_logs/tool_execution.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("tool_router")

class ToolRouter:
    """
    Dynamic tool router that discovers, loads, and routes tool calls.
    Provides fallback mechanisms and logging for all tool executions.
    """
    
    def __init__(self, tools_dir: str = "app/tools"):
        """
        Initialize the tool router.
        
        Args:
            tools_dir: Directory containing tool modules
        """
        self.tools_dir = tools_dir
        self.tools: Dict[str, Callable] = {}
        self.discover_tools()
        
    def discover_tools(self) -> None:
        """
        Dynamically discover all available tools in the tools directory.
        Tools must have a 'run' function to be considered valid.
        """
        logger.info(f"Discovering tools in directory: {self.tools_dir}")
        
        # Get the absolute path to the tools directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tools_path = os.path.join(base_dir, "tools")
        
        # Get all Python files in the tools directory
        try:
            tool_files = [
                f[:-3] for f in os.listdir(tools_path) 
                if f.endswith('.py') and f != '__init__.py'
            ]
        except Exception as e:
            logger.error(f"Error accessing tools directory: {str(e)}")
            return
        
        for tool_file in tool_files:
            try:
                # Import the module
                module_path = f"app.tools.{tool_file}"
                module = importlib.import_module(module_path)
                
                # Check if the module has a run function
                if hasattr(module, 'run') and callable(module.run):
                    # Register the tool with its name (file name without extension)
                    self.tools[tool_file] = module.run
                    logger.info(f"Successfully loaded tool: {tool_file}")
                else:
                    logger.warning(f"Tool {tool_file} does not have a 'run' function and will be skipped")
            except Exception as e:
                logger.error(f"Error loading tool {tool_file}: {str(e)}")
    
    def list_available_tools(self) -> List[str]:
        """
        Return a list of all available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool information
        """
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool_func = self.tools[tool_name]
        signature = inspect.signature(tool_func)
        
        return {
            "name": tool_name,
            "parameters": str(signature),
            "docstring": inspect.getdoc(tool_func) or "No documentation available"
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with the provided arguments.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not found"
            logger.error(error_msg)
            return self._handle_fallback(tool_name, error_msg, kwargs)
        
        try:
            # Log the tool execution
            self._log_tool_execution(tool_name, kwargs)
            
            logger.info(f"Executing tool: {tool_name} with args: {kwargs}")
            result = self.tools[tool_name](**kwargs)
            logger.info(f"Tool {tool_name} executed successfully")
            
            # Log the tool result
            self._log_tool_result(tool_name, result)
            
            # Check if we should store memory
            if kwargs.get('store_memory', False) and 'memory_manager' in kwargs:
                self._store_tool_memory(tool_name, kwargs, result, kwargs['memory_manager'])
            
            return {"success": True, "result": result}
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return self._handle_fallback(tool_name, error_msg, kwargs)
    
    def _handle_fallback(self, tool_name: str, error_msg: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle fallback when a tool fails to execute.
        
        Args:
            tool_name: Name of the failed tool
            error_msg: Error message
            args: Arguments that were passed to the tool
            
        Returns:
            Fallback result
        """
        logger.info(f"Attempting fallback for failed tool: {tool_name}")
        
        # Basic fallback: return error information
        fallback_result = {
            "success": False,
            "error": error_msg,
            "attempted_tool": tool_name,
            "attempted_args": args
        }
        
        # Suggest alternative tools if possible
        similar_tools = self._find_similar_tools(tool_name)
        if similar_tools:
            fallback_result["suggested_alternatives"] = similar_tools
        
        return fallback_result
    
    def _find_similar_tools(self, tool_name: str) -> List[str]:
        """
        Find tools with similar names to the requested tool.
        
        Args:
            tool_name: Name of the tool to find alternatives for
            
        Returns:
            List of similar tool names
        """
        # Simple string similarity check
        return [
            name for name in self.tools.keys()
            if name.startswith(tool_name[:3]) or tool_name.startswith(name[:3])
        ]
    
    def _log_tool_execution(self, tool_name: str, args: Dict[str, Any]) -> None:
        """
        Log tool execution details.
        
        Args:
            tool_name: Name of the tool
            args: Arguments passed to the tool
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "args": {k: v for k, v in args.items() if k != 'memory_manager'},
                "type": "execution"
            }
            
            log_file = f"app/logs/tool_logs/{tool_name}_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Error logging tool execution: {str(e)}")
    
    def _log_tool_result(self, tool_name: str, result: Any) -> None:
        """
        Log tool execution result.
        
        Args:
            tool_name: Name of the tool
            result: Result of the tool execution
        """
        try:
            # Truncate result if too large
            result_str = str(result)
            if len(result_str) > 1000:
                result_str = result_str[:1000] + "... [truncated]"
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "result_summary": result_str,
                "type": "result"
            }
            
            log_file = f"app/logs/tool_logs/{tool_name}_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Error logging tool result: {str(e)}")
    
    def _store_tool_memory(self, tool_name: str, args: Dict[str, Any], result: Any, memory_manager) -> None:
        """
        Store tool execution in memory.
        
        Args:
            tool_name: Name of the tool
            args: Arguments passed to the tool
            result: Result of the tool execution
            memory_manager: Memory manager instance
        """
        try:
            # Create memory entry
            memory_entry = {
                "tool": tool_name,
                "args_summary": str(args),
                "result_summary": str(result)[:500],  # Truncate for memory storage
                "timestamp": datetime.now().isoformat()
            }
            
            # Add memory tags
            tags = args.get('memory_tags', ['tool_execution'])
            if not isinstance(tags, list):
                tags = ['tool_execution']
            
            # Store in memory
            memory_manager.add_memory(
                content=json.dumps(memory_entry),
                scope=args.get('memory_scope', 'agent'),
                tags=tags
            )
        except Exception as e:
            logger.error(f"Error storing tool memory: {str(e)}")

# Create a singleton instance
tool_router = ToolRouter()

def get_router() -> ToolRouter:
    """
    Get the singleton instance of the tool router.
    
    Returns:
        ToolRouter instance
    """
    return tool_router
