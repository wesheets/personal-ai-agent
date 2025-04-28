"""
Reflection Analyzer Module

This module provides functionality to analyze individual reflection nodes for drift triggers
and recovery paths. It performs deep analysis on reflection data to identify patterns and insights.

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

class ReflectionAnalyzer:
    """
    Analyzer for examining reflection nodes and identifying drift triggers and recovery paths.
    
    This class provides methods to analyze individual reflection nodes, identify patterns,
    and generate insights about system reflection capabilities.
    """
    
    def __init__(self, base_path: str = ""):
        """
        Initialize the reflection analyzer.
        
        Args:
            base_path: Base path to prepend to file paths
        """
        self.base_path = base_path
        self.aci_path = os.path.join(base_path, "system", "agent_cognition_index.json")
        self.pice_path = os.path.join(base_path, "system", "system_consciousness_index.json")
        self.analysis_id = str(uuid4())
        self.analysis_timestamp = datetime.datetime.now().isoformat()
        
    def analyze_reflection(self, reflection_id: str) -> Dict[str, Any]:
        """
        Analyze a specific reflection surface by ID.
        
        Args:
            reflection_id: ID of the reflection to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting reflection analysis for ID: {reflection_id}")
        
        # Load reflection data
        reflection_data = self._load_reflection(reflection_id)
        
        if not reflection_data:
            return {
                "analysis_id": self.analysis_id,
                "reflection_id": reflection_id,
                "timestamp": self.analysis_timestamp,
                "status": "failed",
                "error": "Failed to load reflection data",
                "insights": []
            }
        
        # Analyze reflection data
        insights = self._analyze_reflection_data(reflection_data)
        
        # Generate drift triggers
        drift_triggers = self._identify_drift_triggers(reflection_data)
        
        # Generate recovery paths
        recovery_paths = self._generate_recovery_paths(reflection_data, drift_triggers)
        
        # Generate analysis result
        analysis_result = {
            "analysis_id": self.analysis_id,
            "reflection_id": reflection_id,
            "timestamp": self.analysis_timestamp,
            "status": "completed",
            "reflection_data": reflection_data,
            "insights": insights,
            "drift_triggers": drift_triggers,
            "recovery_paths": recovery_paths,
            "summary": {
                "insight_count": len(insights),
                "drift_trigger_count": len(drift_triggers),
                "recovery_path_count": len(recovery_paths),
                "reflection_health": self._calculate_reflection_health(insights, drift_triggers, recovery_paths)
            }
        }
        
        logger.info(f"Reflection analysis completed for ID: {reflection_id}")
        
        return analysis_result
    
    def _load_reflection(self, reflection_id: str) -> Optional[Dict[str, Any]]:
        """
        Load reflection data by ID.
        
        Args:
            reflection_id: ID of the reflection to load
            
        Returns:
            Dictionary containing the reflection data, or None if loading failed
        """
        # First, check if this is a scan result ID
        scan_path = os.path.join(self.base_path, "logs", "reflection_scans", f"{reflection_id}.json")
        if os.path.exists(scan_path):
            try:
                with open(scan_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading scan result {scan_path}: {str(e)}")
        
        # If not a scan result, try to find the reflection node in cognitive surfaces
        try:
            # Load ACI
            aci_data = self._load_json_file(self.aci_path)
            if aci_data and "agents" in aci_data:
                for agent in aci_data["agents"]:
                    if agent.get("id") == reflection_id or agent.get("name") == reflection_id:
                        return {
                            "node_id": reflection_id,
                            "source_type": "agent",
                            "source_id": agent.get("id", agent.get("name", "unknown")),
                            "name": agent.get("name", "Unnamed Agent"),
                            "reflection_type": "agent_reflection",
                            "metadata": {
                                "role": agent.get("role", "Unknown"),
                                "capabilities": agent.get("capabilities", []),
                                "memory_tag": agent.get("memory_tag", "")
                            },
                            "full_data": agent
                        }
            
            # Load PICE
            pice_data = self._load_json_file(self.pice_path)
            if pice_data:
                # Check modules
                if "modules" in pice_data:
                    for module in pice_data["modules"]:
                        if module.get("name") == reflection_id:
                            return {
                                "node_id": reflection_id,
                                "source_type": "module",
                                "source_id": module.get("name", "unknown"),
                                "name": module.get("name", "Unnamed Module"),
                                "reflection_type": "module_reflection",
                                "metadata": {
                                    "category": module.get("category", "Unknown"),
                                    "status": module.get("status", "unknown"),
                                    "api_surface": module.get("api_surface", "")
                                },
                                "full_data": module
                            }
                
                # Check schemas
                if "schemas" in pice_data:
                    for schema in pice_data["schemas"]:
                        if schema.get("name") == reflection_id:
                            return {
                                "node_id": reflection_id,
                                "source_type": "schema",
                                "source_id": schema.get("name", "unknown"),
                                "name": schema.get("name", "Unnamed Schema"),
                                "reflection_type": "schema_reflection",
                                "metadata": {
                                    "category": schema.get("category", "Unknown"),
                                    "status": schema.get("status", "unknown"),
                                    "api_surface": schema.get("api_surface", "")
                                },
                                "full_data": schema
                            }
        except Exception as e:
            logger.error(f"Error searching for reflection node {reflection_id}: {str(e)}")
        
        logger.error(f"Reflection node not found: {reflection_id}")
        return None
    
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
    
    def _analyze_reflection_data(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze reflection data to generate insights.
        
        Args:
            reflection_data: Reflection data to analyze
            
        Returns:
            List of insights generated from the reflection data
        """
        insights = []
        
        # Extract source type
        source_type = reflection_data.get("source_type", "unknown")
        
        # Generate insights based on source type
        if source_type == "agent":
            insights.extend(self._analyze_agent_reflection(reflection_data))
        elif source_type == "module":
            insights.extend(self._analyze_module_reflection(reflection_data))
        elif source_type == "schema":
            insights.extend(self._analyze_schema_reflection(reflection_data))
        
        # Generate general insights
        insights.append({
            "insight_id": str(uuid4()),
            "type": "general",
            "title": "Reflection Node Identified",
            "description": f"Identified reflection node of type '{source_type}' with name '{reflection_data.get('name', 'unknown')}'",
            "confidence": 1.0
        })
        
        return insights
    
    def _analyze_agent_reflection(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze agent reflection data.
        
        Args:
            reflection_data: Agent reflection data to analyze
            
        Returns:
            List of insights generated from the agent reflection data
        """
        insights = []
        
        # Extract agent metadata
        metadata = reflection_data.get("metadata", {})
        role = metadata.get("role", "Unknown")
        capabilities = metadata.get("capabilities", [])
        memory_tag = metadata.get("memory_tag", "")
        
        # Generate insights based on role
        if "reflection" in role.lower():
            insights.append({
                "insight_id": str(uuid4()),
                "type": "agent_role",
                "title": "Reflection Role Identified",
                "description": f"Agent has a reflection-related role: '{role}'",
                "confidence": 0.9
            })
        
        # Generate insights based on capabilities
        reflection_capabilities = [cap for cap in capabilities if "reflection" in cap.lower()]
        if reflection_capabilities:
            insights.append({
                "insight_id": str(uuid4()),
                "type": "agent_capabilities",
                "title": "Reflection Capabilities Identified",
                "description": f"Agent has {len(reflection_capabilities)} reflection-related capabilities",
                "confidence": 0.8,
                "details": {
                    "capabilities": reflection_capabilities
                }
            })
        
        # Generate insights based on memory tag
        if memory_tag and "reflection" in memory_tag.lower():
            insights.append({
                "insight_id": str(uuid4()),
                "type": "memory_tag",
                "title": "Reflection Memory Tag Identified",
                "description": f"Agent has a reflection-related memory tag: '{memory_tag}'",
                "confidence": 0.9
            })
        
        return insights
    
    def _analyze_module_reflection(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze module reflection data.
        
        Args:
            reflection_data: Module reflection data to analyze
            
        Returns:
            List of insights generated from the module reflection data
        """
        insights = []
        
        # Extract module metadata
        metadata = reflection_data.get("metadata", {})
        category = metadata.get("category", "Unknown")
        status = metadata.get("status", "unknown")
        api_surface = metadata.get("api_surface", "")
        
        # Generate insights based on category
        if category == "Reflection/Memory/Core":
            insights.append({
                "insight_id": str(uuid4()),
                "type": "module_category",
                "title": "Core Reflection Module Identified",
                "description": "Module is categorized as a core reflection/memory component",
                "confidence": 0.95
            })
        
        # Generate insights based on status
        if status == "active":
            insights.append({
                "insight_id": str(uuid4()),
                "type": "module_status",
                "title": "Active Reflection Module",
                "description": "Reflection module is currently active in the system",
                "confidence": 0.9
            })
        
        # Generate insights based on API surface
        if api_surface and "reflection" in api_surface.lower():
            insights.append({
                "insight_id": str(uuid4()),
                "type": "api_surface",
                "title": "Reflection API Surface Identified",
                "description": f"Module exposes a reflection-related API surface: '{api_surface}'",
                "confidence": 0.9
            })
        
        return insights
    
    def _analyze_schema_reflection(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze schema reflection data.
        
        Args:
            reflection_data: Schema reflection data to analyze
            
        Returns:
            List of insights generated from the schema reflection data
        """
        insights = []
        
        # Extract schema metadata
        metadata = reflection_data.get("metadata", {})
        category = metadata.get("category", "Unknown")
        status = metadata.get("status", "unknown")
        api_surface = metadata.get("api_surface", "")
        
        # Generate insights based on category
        if "reflection" in category.lower():
            insights.append({
                "insight_id": str(uuid4()),
                "type": "schema_category",
                "title": "Reflection Schema Category Identified",
                "description": f"Schema is categorized as '{category}'",
                "confidence": 0.9
            })
        
        # Generate insights based on status
        if status == "active":
            insights.append({
                "insight_id": str(uuid4()),
                "type": "schema_status",
                "title": "Active Reflection Schema",
                "description": "Reflection schema is currently active in the system",
                "confidence": 0.9
            })
        
        # Generate insights based on API surface
        if api_surface and "reflection" in api_surface.lower():
            insights.append({
                "insight_id": str(uuid4()),
                "type": "api_surface",
                "title": "Reflection API Surface Identified",
                "description": f"Schema is associated with a reflection-related API surface: '{api_surface}'",
                "confidence": 0.9
            })
        
        return insights
    
    def _identify_drift_triggers(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify potential drift triggers in reflection data.
        
        Args:
            reflection_data: Reflection data to analyze
            
        Returns:
            List of potential drift triggers
        """
        drift_triggers = []
        
        # Extract source type
        source_type = reflection_data.get("source_type", "unknown")
        
        # Generate drift triggers based on source type
        if source_type == "agent":
            # Check for missing capabilities
            metadata = reflection_data.get("metadata", {})
            capabilities = metadata.get("capabilities", [])
            if not any("reflection" in cap.lower() for cap in capabilities):
                drift_triggers.append({
                    "trigger_id": str(uuid4()),
                    "type": "missing_capability",
                    "title": "Missing Reflection Capability",
                    "description": "Agent is identified as reflection-related but lacks explicit reflection capabilities",
                    "severity": "medium",
                    "affected_component": reflection_data.get("name", "unknown")
                })
        
        elif source_type == "module":
            # Check for inactive status
            metadata = reflection_data.get("metadata", {})
            status = metadata.get("status", "unknown")
            if status != "active":
                drift_triggers.append({
                    "trigger_id": str(uuid4()),
                    "type": "inactive_module",
                    "title": "Inactive Reflection Module",
                    "description": f"Reflection module has non-active status: '{status}'",
                    "severity": "high",
                    "affected_component": reflection_data.get("name", "unknown")
                })
        
        # Check for missing memory tag
        metadata = reflection_data.get("metadata", {})
        memory_tag = metadata.get("memory_tag", "")
        if not memory_tag:
            drift_triggers.append({
                "trigger_id": str(uuid4()),
                "type": "missing_memory_tag",
                "title": "Missing Memory Tag",
                "description": "Reflection component is missing a memory tag",
                "severity": "medium",
                "affected_component": reflection_data.get("name", "unknown")
            })
        
        return drift_triggers
    
    def _generate_recovery_paths(self, reflection_data: Dict[str, Any], drift_triggers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recovery paths for identified drift triggers.
        
        Args:
            reflection_data: Reflection data being analyzed
            drift_triggers: List of identified drift triggers
            
        Returns:
            List of recovery paths
        """
        recovery_paths = []
        
        for trigger in drift_triggers:
            trigger_type = trigger.get("type", "unknown")
            affected_component = trigger.get("affected_component", "unknown")
            
            if trigger_type == "missing_capability":
                recovery_paths.append({
                    "path_id": str(uuid4()),
                    "trigger_id": trigger.get("trigger_id", ""),
                    "title": "Add Reflection Capability",
                    "description": f"Add explicit reflection capability to agent '{affected_component}'",
                    "steps": [
                        "Locate agent definition in agent_cognition_index.json",
                        "Add 'reflection' to the capabilities array",
                        "Update memory tag to reflect the change"
                    ],
                    "estimated_effort": "low"
                })
            
            elif trigger_type == "inactive_module":
                recovery_paths.append({
                    "path_id": str(uuid4()),
                    "trigger_id": trigger.get("trigger_id", ""),
                    "title": "Activate Reflection Module",
                    "description": f"Set module '{affected_component}' status to 'active'",
                    "steps": [
                        "Locate module definition in system_consciousness_index.json",
                        "Change status field to 'active'",
                        "Verify module functionality after activation"
                    ],
                    "estimated_effort": "medium"
                })
            
            elif trigger_type == "missing_memory_tag":
                recovery_paths.append({
                    "path_id": str(uuid4()),
                    "trigger_id": trigger.get("trigger_id", ""),
                    "title": "Add Memory Tag",
                    "description": f"Add appropriate memory tag to component '{affected_component}'",
                    "steps": [
                        f"Locate component definition in cognitive surface",
                        "Add memory_tag field with appropriate value",
                        "Ensure memory tag follows governance standards"
                    ],
                    "estimated_effort": "low"
                })
        
        return recovery_paths
    
    def _calculate_reflection_health(self, insights: List[Dict[str, Any]], drift_triggers: List[Dict[str, Any]], recovery_paths: List[Dict[str, Any]]) -> float:
        """
        Calculate reflection health score based on insights, drift triggers, and recovery paths.
        
        Args:
            insights: List of insights
            drift_triggers: List of drift triggers
            recovery_paths: List of recovery paths
            
        Returns:
            Reflection health score (0.0 to 1.0)
        """
        # Base health score
        health_score = 0.8
        
        # Adjust based on insights
        insight_score = min(len(insights) * 0.05, 0.2)
        health_score += insight_score
        
        # Adjust based on drift triggers
        trigger_penalty = 0.0
        for trigger in drift_triggers:
            severity = trigger.get("severity", "medium")
            if severity == "high":
                trigger_penalty += 0.1
            elif severity == "medium":
                trigger_penalty += 0.05
            elif severity == "low":
                trigger_penalty += 0.02
        
        health_score -= min(trigger_penalty, 0.5)
        
        # Adjust based on recovery paths
        if drift_triggers and len(recovery_paths) >= len(drift_triggers):
            health_score += 0.1
        
        # Ensure health score is between 0.0 and 1.0
        health_score = max(0.0, min(health_score, 1.0))
        
        return health_score

# Create singleton instance
analyzer = ReflectionAnalyzer()

def analyze_reflection(reflection_id: str) -> Dict[str, Any]:
    """
    Analyze a specific reflection surface by ID.
    
    Args:
        reflection_id: ID of the reflection to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    return analyzer.analyze_reflection(reflection_id)
