"""
Tool System Manager

This module provides functionality to manage and execute tools for agents.
"""

import os
import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable, Set

class ToolManager:
    """
    Manager for agent tools
    """
    
    def __init__(self):
        self.tools = {}
        self.tools_dir = os.path.dirname(__file__)
        self._load_tools()
    
    def _load_tools(self):
        """Load all available tools from the tools directory"""
        # Get all Python files in the tools directory
        tool_files = [f for f in os.listdir(self.tools_dir) if f.endswith('.py') and f != '__init__.py']
        
        # Import each tool module
        for tool_file in tool_files:
            tool_name = os.path.splitext(tool_file)[0]
            try:
                # Import the module
                module = importlib.import_module(f"app.tools.{tool_name}")
                
                # Look for get_*_tool function
                getter_name = f"get_{tool_name}_tool"
                if hasattr(module, getter_name):
                    getter = getattr(module, getter_name)
                    tool = getter()
                    self.tools[tool.name] = tool
                    print(f"Loaded tool: {tool.name}")
            except Exception as e:
                print(f"Error loading tool {tool_name}: {str(e)}")
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Get a list of all available tools
        
        Returns:
            List of tool information dictionaries
        """
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]
    
    def get_tool(self, tool_name: str):
        """
        Get a specific tool by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool is not found
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        return await tool.execute(**kwargs)

# Singleton instance
_tool_manager = None

def get_tool_manager():
    """Get the singleton ToolManager instance"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager
