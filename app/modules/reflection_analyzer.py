"""
Reflection Analyzer Module

This module provides functionality to analyze individual reflection nodes for drift triggers
and recovery paths. It performs deep analysis on reflection data to identify patterns and insights.

# memory_tag: phase3.0_sprint4_cognitive_reflection_plan_chaining
# memory_tag: phase3.0_sprint4_batch3_stub_creation (Module Schema Wrapped)
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4

# Import schemas
from app.schemas.reflection_schemas import ReflectionAnalysisResult, ReflectionInsight, DriftTrigger, RecoveryPath, ReflectionSummary

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
        self.analysis_timestamp = datetime.datetime.now()
        
    def analyze_reflection(self, reflection_id: str) -> ReflectionAnalysisResult:
        """
        Analyze a specific reflection surface by ID.
        
        Args:
            reflection_id: ID of the reflection to analyze
            
        Returns:
            ReflectionAnalysisResult object containing analysis results
        """
        logger.info(f"Starting reflection analysis for ID: {reflection_id}")
        
        # Load reflection data
        reflection_data = self._load_reflection(reflection_id)
        
        if not reflection_data:
            return ReflectionAnalysisResult(
                analysis_id=self.analysis_id,
                reflection_id=reflection_id,
                timestamp=self.analysis_timestamp,
                status="failed",
                error="Failed to load reflection data",
                insights=[],
                drift_triggers=[],
                recovery_paths=[],
                summary=ReflectionSummary(insight_count=0, drift_trigger_count=0, recovery_path_count=0, reflection_health=0.0)
            )
        
        # Analyze reflection data
        insights_raw = self._analyze_reflection_data(reflection_data)
        insights = [ReflectionInsight(**insight) for insight in insights_raw]
        
        # Generate drift triggers
        drift_triggers_raw = self._identify_drift_triggers(reflection_data)
        drift_triggers = [DriftTrigger(**trigger) for trigger in drift_triggers_raw]
        
        # Generate recovery paths
        recovery_paths_raw = self._generate_recovery_paths(reflection_data, drift_triggers_raw)
        recovery_paths = [RecoveryPath(**path) for path in recovery_paths_raw]
        
        # Calculate summary
        summary = ReflectionSummary(
            insight_count=len(insights),
            drift_trigger_count=len(drift_triggers),
            recovery_path_count=len(recovery_paths),
            reflection_health=self._calculate_reflection_health(insights_raw, drift_triggers_raw, recovery_paths_raw)
        )
        
        # Generate analysis result
        analysis_result = ReflectionAnalysisResult(
            analysis_id=self.analysis_id,
            reflection_id=reflection_id,
            timestamp=self.analysis_timestamp,
            status="completed",
            reflection_data=reflection_data, # Keep raw data for context
            insights=insights,
            drift_triggers=drift_triggers,
            recovery_paths=recovery_paths,
            summary=summary
        )
        
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
        # TODO: Use a more robust way to store/retrieve scan results, maybe a dedicated log dir or DB
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
        Analyze reflection data to generate insights (returns raw dicts for now).
        
        Args:
            reflection_data: Reflection data to analyze
            
        Returns:
            List of insights generated from the reflection data
        """
        insights = []
        source_type = reflection_data.get("source_type", "unknown")
        
        if source_type == "agent": insights.extend(self._analyze_agent_reflection(reflection_data))
        elif source_type == "module": insights.extend(self._analyze_module_reflection(reflection_data))
        elif source_type == "schema": insights.extend(self._analyze_schema_reflection(reflection_data))
        
        insights.append({
            "insight_id": str(uuid4()),
            "type": "general",
            "title": "Reflection Node Identified",
            "description": f"Identified reflection node of type 	'{source_type}	' with name 	'{reflection_data.get('name', 'unknown')}	'",
            "confidence": 1.0
        })
        return insights

    def _analyze_agent_reflection(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        metadata = reflection_data.get("metadata", {})
        role = metadata.get("role", "Unknown")
        capabilities = metadata.get("capabilities", [])
        memory_tag = metadata.get("memory_tag", "")

        if "reflection" in role.lower():
            insights.append({"insight_id": str(uuid4()), "type": "agent_role", "title": "Reflection Role Identified", "description": f"Agent has a reflection-related role: 	'{role}	'", "confidence": 0.9})
        
        reflection_capabilities = [cap for cap in capabilities if "reflection" in cap.lower()]
        if reflection_capabilities:
            insights.append({"insight_id": str(uuid4()), "type": "agent_capabilities", "title": "Reflection Capabilities Identified", "description": f"Agent has {len(reflection_capabilities)} reflection-related capabilities", "confidence": 0.8, "details": {"capabilities": reflection_capabilities}})
        
        if memory_tag and "reflection" in memory_tag.lower():
            insights.append({"insight_id": str(uuid4()), "type": "memory_tag", "title": "Reflection Memory Tag Identified", "description": f"Agent has a reflection-related memory tag: 	'{memory_tag}	'", "confidence": 0.9})
        
        return insights

    def _analyze_module_reflection(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        metadata = reflection_data.get("metadata", {})
        category = metadata.get("category", "Unknown")
        status = metadata.get("status", "unknown")
        api_surface = metadata.get("api_surface", "")

        if category == "Reflection/Memory/Core":
            insights.append({"insight_id": str(uuid4()), "type": "module_category", "title": "Core Reflection Module Identified", "description": "Module is categorized as a core reflection/memory component", "confidence": 0.95})
        
        if status == "active":
            insights.append({"insight_id": str(uuid4()), "type": "module_status", "title": "Active Reflection Module", "description": "Reflection module is currently active in the system", "confidence": 0.9})
        
        if api_surface and "reflection" in api_surface.lower():
            insights.append({"insight_id": str(uuid4()), "type": "api_surface", "title": "Reflection API Surface Identified", "description": f"Module exposes a reflection-related API surface: 	'{api_surface}	'", "confidence": 0.9})
        
        return insights

    def _analyze_schema_reflection(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        metadata = reflection_data.get("metadata", {})
        category = metadata.get("category", "Unknown")
        status = metadata.get("status", "unknown")
        api_surface = metadata.get("api_surface", "")

        if "reflection" in category.lower():
            insights.append({"insight_id": str(uuid4()), "type": "schema_category", "title": "Reflection Schema Category Identified", "description": f"Schema is categorized as 	'{category}	'", "confidence": 0.9})
        
        if status == "active":
            insights.append({"insight_id": str(uuid4()), "type": "schema_status", "title": "Active Reflection Schema", "description": "Reflection schema is currently active in the system", "confidence": 0.9})
        
        if api_surface and "reflection" in api_surface.lower():
            insights.append({"insight_id": str(uuid4()), "type": "api_surface", "title": "Reflection API Surface Identified", "description": f"Schema is associated with a reflection-related API surface: 	'{api_surface}	'", "confidence": 0.9})
        
        return insights

    def _identify_drift_triggers(self, reflection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify potential drift triggers in reflection data (returns raw dicts for now).
        
        Args:
            reflection_data: Reflection data to analyze
            
        Returns:
            List of potential drift triggers
        """
        drift_triggers = []
        source_type = reflection_data.get("source_type", "unknown")
        metadata = reflection_data.get("metadata", {})

        if source_type == "agent":
            if not metadata.get("capabilities"): drift_triggers.append({"trigger_id": str(uuid4()), "type": "missing_capabilities", "description": "Agent lacks defined capabilities", "severity": "medium"})
            if not metadata.get("memory_tag"): drift_triggers.append({"trigger_id": str(uuid4()), "type": "missing_memory_tag", "description": "Agent lacks a memory tag", "severity": "high"})
        elif source_type == "module":
            if metadata.get("status") != "active": drift_triggers.append({"trigger_id": str(uuid4()), "type": "inactive_module", "description": f"Module status is 	'{metadata.get('status')}	'", "severity": "medium"})
            if not metadata.get("api_surface"): drift_triggers.append({"trigger_id": str(uuid4()), "type": "missing_api_surface", "description": "Module lacks a defined API surface", "severity": "low"})
        elif source_type == "schema":
            if metadata.get("status") != "active": drift_triggers.append({"trigger_id": str(uuid4()), "type": "inactive_schema", "description": f"Schema status is 	'{metadata.get('status')}	'", "severity": "medium"})

        return drift_triggers

    def _generate_recovery_paths(self, reflection_data: Dict[str, Any], drift_triggers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate potential recovery paths based on drift triggers (returns raw dicts for now).
        
        Args:
            reflection_data: Reflection data analyzed
            drift_triggers: List of identified drift triggers
            
        Returns:
            List of potential recovery paths
        """
        recovery_paths = []
        source_type = reflection_data.get("source_type", "unknown")
        source_id = reflection_data.get("source_id", "unknown")

        for trigger in drift_triggers:
            path = {"path_id": str(uuid4()), "trigger_id": trigger["trigger_id"], "suggested_action": "No suggestion", "confidence": 0.5}
            if trigger["type"] == "missing_memory_tag":
                path["suggested_action"] = f"Assign appropriate memory tag to {source_type} 	'{source_id}	'"
                path["confidence"] = 0.8
            elif trigger["type"] == "inactive_module" or trigger["type"] == "inactive_schema":
                path["suggested_action"] = f"Review and activate {source_type} 	'{source_id}	' or remove if obsolete"
                path["confidence"] = 0.7
            recovery_paths.append(path)
            
        return recovery_paths

    def _calculate_reflection_health(self, insights: List[Dict[str, Any]], drift_triggers: List[Dict[str, Any]], recovery_paths: List[Dict[str, Any]]) -> float:
        """
        Calculate a simple reflection health score.
        
        Args:
            insights: List of generated insights
            drift_triggers: List of identified drift triggers
            recovery_paths: List of generated recovery paths
            
        Returns:
            A health score between 0.0 and 1.0
        """
        # Simple scoring: more insights = better, more triggers = worse
        base_score = 0.5
        insight_bonus = min(len(insights) * 0.05, 0.3) # Max 0.3 bonus
        trigger_penalty = min(len(drift_triggers) * 0.1, 0.5) # Max 0.5 penalty
        
        health_score = max(0.0, min(1.0, base_score + insight_bonus - trigger_penalty))
        return round(health_score, 2)

# Create singleton instance
analyzer = ReflectionAnalyzer()

def analyze_reflection_node(reflection_id: str) -> ReflectionAnalysisResult:
    """
    Analyze a specific reflection surface by ID.
    
    Args:
        reflection_id: ID of the reflection to analyze
        
    Returns:
        ReflectionAnalysisResult object containing analysis results
    """
    # Re-initialize analyzer for each request to get a new analysis_id and timestamp
    current_analyzer = ReflectionAnalyzer()
    return current_analyzer.analyze_reflection(reflection_id)

