"""
Toolkit Registry Module

This module provides the registry system for all tools available to agents.
It includes the ToolkitEntry class for registering tools with appropriate metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable


@dataclass
class ToolkitEntry:
    """
    Represents a registered tool in the toolkit system.
    
    Attributes:
        name: The fully qualified name of the tool (e.g., 'logo.generate')
        description: A detailed description of what the tool does
        category: The category this tool belongs to (e.g., 'Design & UI')
        timeout_seconds: Maximum execution time allowed for this tool
        max_retries: Number of retry attempts allowed if the tool fails
        requires_reflection: Whether the tool execution should generate a reflection
    """
    name: str
    description: str
    category: str
    timeout_seconds: int = 30
    max_retries: int = 3
    requires_reflection: bool = False
    handler: Optional[Callable] = None
    
    def __post_init__(self):
        """Validate the tool entry after initialization."""
        if not self.name or not self.description or not self.category:
            raise ValueError("Tool name, description, and category are required")


class ToolkitRegistry:
    """
    Registry for all tools available to agents.
    
    This class manages the registration, lookup, and categorization of all tools.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._tools: Dict[str, ToolkitEntry] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(self, tool: ToolkitEntry) -> None:
        """
        Register a new tool in the registry.
        
        Args:
            tool: The ToolkitEntry to register
            
        Raises:
            ValueError: If a tool with the same name already exists
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        
        self._tools[tool.name] = tool
        
        # Add to category index
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        self._categories[tool.category].append(tool.name)
    
    def get_tool(self, name: str) -> Optional[ToolkitEntry]:
        """
        Get a tool by name.
        
        Args:
            name: The fully qualified name of the tool
            
        Returns:
            The ToolkitEntry if found, None otherwise
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            A list of all registered tool names
        """
        return list(self._tools.keys())
    
    def list_categories(self) -> List[str]:
        """
        List all tool categories.
        
        Returns:
            A list of all tool categories
        """
        return list(self._categories.keys())
    
    def get_tools_by_category(self, category: str) -> List[ToolkitEntry]:
        """
        Get all tools in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            A list of ToolkitEntry objects in the specified category
        """
        if category not in self._categories:
            return []
        
        return [self._tools[name] for name in self._categories[category]]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the registry to a dictionary representation.
        
        Returns:
            A dictionary representation of the registry
        """
        return {
            "tools": {name: {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "timeout_seconds": tool.timeout_seconds,
                "max_retries": tool.max_retries,
                "requires_reflection": tool.requires_reflection
            } for name, tool in self._tools.items()},
            "categories": self._categories
        }


# Create a global registry instance
registry = ToolkitRegistry()


def register_tool(
    name: str,
    description: str,
    category: str,
    timeout_seconds: int = 30,
    max_retries: int = 3,
    requires_reflection: bool = False,
    handler: Optional[Callable] = None
) -> ToolkitEntry:
    """
    Register a new tool in the global registry.
    
    Args:
        name: The fully qualified name of the tool
        description: A detailed description of what the tool does
        category: The category this tool belongs to
        timeout_seconds: Maximum execution time allowed for this tool
        max_retries: Number of retry attempts allowed if the tool fails
        requires_reflection: Whether the tool execution should generate a reflection
        handler: Optional function that implements the tool's functionality
        
    Returns:
        The registered ToolkitEntry
        
    Raises:
        ValueError: If a tool with the same name already exists
    """
    tool = ToolkitEntry(
        name=name,
        description=description,
        category=category,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        requires_reflection=requires_reflection,
        handler=handler
    )
    registry.register(tool)
    return tool
