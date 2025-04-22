"""
Plugin Loader Implementation

This file implements the plugin loader for agent registration.
"""

import json
import logging
import os
import importlib
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("app.plugin_loader")

class PluginLoader:
    """
    Plugin loader for agent registration and management.
    """
    
    def __init__(self, plugin_storage_path: str = "plugin_registration/agent_plugin_storage.json"):
        """
        Initialize the plugin loader.
        
        Args:
            plugin_storage_path: Path to the plugin storage JSON file
        """
        self.plugin_storage_path = plugin_storage_path
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self) -> None:
        """Load all plugins from the plugin storage file."""
        try:
            if os.path.exists(self.plugin_storage_path):
                with open(self.plugin_storage_path, 'r') as f:
                    plugin_data = json.load(f)
                    
                    if 'plugins' in plugin_data:
                        for plugin in plugin_data['plugins']:
                            if plugin.get('enabled', False):
                                self.plugins[plugin['id']] = plugin
                                logger.info(f"Loaded plugin: {plugin['name']} (ID: {plugin['id']})")
                            else:
                                logger.info(f"Skipped disabled plugin: {plugin['name']} (ID: {plugin['id']})")
            else:
                logger.warning(f"Plugin storage file not found: {self.plugin_storage_path}")
        except Exception as e:
            logger.error(f"Error loading plugins: {str(e)}")
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: The plugin ID
            
        Returns:
            The plugin data or None if not found
        """
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """
        Get all loaded plugins.
        
        Returns:
            List of all plugin data
        """
        return list(self.plugins.values())
    
    def instantiate_agent(self, plugin_id: str) -> Any:
        """
        Instantiate an agent from a plugin.
        
        Args:
            plugin_id: The plugin ID
            
        Returns:
            The instantiated agent or None if failed
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_id}")
            return None
        
        try:
            # Parse the entry point
            module_path, class_name = plugin['entry_point'].rsplit('.', 1)
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class
            agent_class = getattr(module, class_name)
            
            # Instantiate the agent
            agent = agent_class()
            
            logger.info(f"Instantiated agent from plugin: {plugin['name']} (ID: {plugin_id})")
            return agent
        except Exception as e:
            logger.error(f"Error instantiating agent from plugin {plugin_id}: {str(e)}")
            return None

# Create a singleton instance
plugin_loader = PluginLoader()

def get_plugin_loader() -> PluginLoader:
    """
    Get the plugin loader instance.
    
    Returns:
        The plugin loader instance
    """
    return plugin_loader
