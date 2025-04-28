"""
Reflection Scanner Module

This module provides functionality to scan memory surfaces recursively for reflection nodes.
It identifies potential reflection points across the system's cognitive surfaces.

# memory_tag: phase3.0_sprint4_cognitive_reflection_plan_chaining
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4

# Configure logging
logger = logging.getLogger(__name__)

class ReflectionScanner:
    """
    Scanner for identifying reflection nodes across memory surfaces.
    
    This class provides methods to recursively scan memory surfaces for reflection nodes,
    identify potential drift triggers, and map recovery paths.
    """
    
    def __init__(self, base_path: str = ""):
        """
        Initialize the reflection scanner.
        
        Args:
            base_path: Base path to prepend to file paths
        """
        self.base_path = base_path
        self.aci_path = os.path.join(base_path, "system", "agent_cognition_index.json")
        self.pice_path = os.path.join(base_path, "system", "system_consciousness_index.json")
        self.scan_id = str(uuid4())
        self.scan_timestamp = datetime.datetime.now().isoformat()
        
    def trigger_deep_scan(self, scan_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger a full system reflection deep scan.
        
        Args:
            scan_params: Parameters for the scan
            
        Returns:
            Dictionary containing scan results
        """
        logger.info(f"Starting deep reflection scan with ID: {self.scan_id}")
        
        # Load cognitive surfaces
        aci_data = self._load_json_file(self.aci_path)
        pice_data = self._load_json_file(self.pice_path)
        
        if not aci_data or not pice_data:
            return {
                "scan_id": self.scan_id,
                "timestamp": self.scan_timestamp,
                "status": "failed",
                "error": "Failed to load cognitive surfaces",
                "reflection_nodes": []
            }
        
        # Scan for reflection nodes
        reflection_nodes = []
        
        # Scan ACI for reflection nodes
        if aci_data and "agents" in aci_data:
            agent_nodes = self._scan_agents_for_reflection(aci_data["agents"])
            reflection_nodes.extend(agent_nodes)
        
        # Scan PICE for reflection nodes
        if pice_data:
            # Scan modules
            if "modules" in pice_data:
                module_nodes = self._scan_modules_for_reflection(pice_data["modules"])
                reflection_nodes.extend(module_nodes)
            
            # Scan schemas
            if "schemas" in pice_data:
                schema_nodes = self._scan_schemas_for_reflection(pice_data["schemas"])
                reflection_nodes.extend(schema_nodes)
        
        # Apply filters from scan parameters
        if "filters" in scan_params:
            reflection_nodes = self._apply_filters(reflection_nodes, scan_params["filters"])
        
        # Generate scan result
        scan_result = {
            "scan_id": self.scan_id,
            "timestamp": self.scan_timestamp,
            "status": "completed",
            "parameters": scan_params,
            "reflection_nodes": reflection_nodes,
            "summary": {
                "total_nodes": len(reflection_nodes),
                "agent_nodes": sum(1 for node in reflection_nodes if node["source_type"] == "agent"),
                "module_nodes": sum(1 for node in reflection_nodes if node["source_type"] == "module"),
                "schema_nodes": sum(1 for node in reflection_nodes if node["source_type"] == "schema")
            }
        }
        
        logger.info(f"Deep reflection scan completed. Found {len(reflection_nodes)} reflection nodes.")
        
        return scan_result
    
    def _load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing the JSON data, or None if loading failed
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return None
    
    def _scan_agents_for_reflection(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan agents for reflection nodes.
        
        Args:
            agents: List of agent definitions
            
        Returns:
            List of reflection nodes found in agents
        """
        reflection_nodes = []
        
        for agent in agents:
            # Check if agent is reflection-related
            is_reflection_agent = False
            
            if "name" in agent and "reflection" in agent["name"].lower():
                is_reflection_agent = True
            
            if "role" in agent and "reflection" in agent["role"].lower():
                is_reflection_agent = True
            
            if "capabilities" in agent:
                for capability in agent["capabilities"]:
                    if "reflection" in capability.lower():
                        is_reflection_agent = True
                        break
            
            if is_reflection_agent:
                reflection_nodes.append({
                    "node_id": str(uuid4()),
                    "source_type": "agent",
                    "source_id": agent.get("id", agent.get("name", "unknown")),
                    "name": agent.get("name", "Unnamed Agent"),
                    "reflection_type": "agent_reflection",
                    "metadata": {
                        "role": agent.get("role", "Unknown"),
                        "capabilities": agent.get("capabilities", []),
                        "memory_tag": agent.get("memory_tag", "")
                    }
                })
        
        return reflection_nodes
    
    def _scan_modules_for_reflection(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan modules for reflection nodes.
        
        Args:
            modules: List of module definitions
            
        Returns:
            List of reflection nodes found in modules
        """
        reflection_nodes = []
        
        for module in modules:
            # Check if module is reflection-related
            is_reflection_module = False
            
            if "name" in module and "reflection" in module["name"].lower():
                is_reflection_module = True
            
            if "category" in module and "reflection" in module["category"].lower():
                is_reflection_module = True
            
            if is_reflection_module:
                reflection_nodes.append({
                    "node_id": str(uuid4()),
                    "source_type": "module",
                    "source_id": module.get("name", "unknown"),
                    "name": module.get("name", "Unnamed Module"),
                    "reflection_type": "module_reflection",
                    "metadata": {
                        "category": module.get("category", "Unknown"),
                        "status": module.get("status", "unknown"),
                        "api_surface": module.get("api_surface", "")
                    }
                })
        
        return reflection_nodes
    
    def _scan_schemas_for_reflection(self, schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan schemas for reflection nodes.
        
        Args:
            schemas: List of schema definitions
            
        Returns:
            List of reflection nodes found in schemas
        """
        reflection_nodes = []
        
        for schema in schemas:
            # Check if schema is reflection-related
            is_reflection_schema = False
            
            if "name" in schema and "reflection" in schema["name"].lower():
                is_reflection_schema = True
            
            if "category" in schema and "reflection" in schema["category"].lower():
                is_reflection_schema = True
            
            if is_reflection_schema:
                reflection_nodes.append({
                    "node_id": str(uuid4()),
                    "source_type": "schema",
                    "source_id": schema.get("name", "unknown"),
                    "name": schema.get("name", "Unnamed Schema"),
                    "reflection_type": "schema_reflection",
                    "metadata": {
                        "category": schema.get("category", "Unknown"),
                        "status": schema.get("status", "unknown"),
                        "api_surface": schema.get("api_surface", "")
                    }
                })
        
        return reflection_nodes
    
    def _apply_filters(self, nodes: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filters to reflection nodes.
        
        Args:
            nodes: List of reflection nodes
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered list of reflection nodes
        """
        filtered_nodes = nodes
        
        # Filter by source type
        if "source_type" in filters:
            source_types = filters["source_type"]
            if isinstance(source_types, str):
                source_types = [source_types]
            filtered_nodes = [node for node in filtered_nodes if node["source_type"] in source_types]
        
        # Filter by reflection type
        if "reflection_type" in filters:
            reflection_types = filters["reflection_type"]
            if isinstance(reflection_types, str):
                reflection_types = [reflection_types]
            filtered_nodes = [node for node in filtered_nodes if node["reflection_type"] in reflection_types]
        
        # Filter by memory tag
        if "memory_tag" in filters:
            memory_tags = filters["memory_tag"]
            if isinstance(memory_tags, str):
                memory_tags = [memory_tags]
            filtered_nodes = [
                node for node in filtered_nodes 
                if "metadata" in node and "memory_tag" in node["metadata"] and node["metadata"]["memory_tag"] in memory_tags
            ]
        
        return filtered_nodes

# Create singleton instance
scanner = ReflectionScanner()

def trigger_scan_deep(scan_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger a full system reflection deep scan.
    
    Args:
        scan_params: Parameters for the scan
        
    Returns:
        Dictionary containing scan results
    """
    return scanner.trigger_deep_scan(scan_params)
