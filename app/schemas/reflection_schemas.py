"""
Reflection Schemas Module

This module defines the schemas for reflection-related endpoints.

# memory_tag: phase3.0_sprint4_cognitive_reflection_plan_chaining
# memory_tag: phase3.0_sprint4_batch3_backward_breadcrumb_audit
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class ReflectionScanRequest(BaseModel):
    """
    Schema for reflection scan requests.
    
    This schema defines the structure of requests to trigger a full system reflection deep scan.
    """
    scan_depth: str = Field(
        default="full",
        description="Depth of the scan: 'quick', 'standard', or 'full'"
    )
    include_agents: bool = Field(
        default=True,
        description="Whether to include agents in the scan"
    )
    include_modules: bool = Field(
        default=True,
        description="Whether to include modules in the scan"
    )
    include_schemas: bool = Field(
        default=True,
        description="Whether to include schemas in the scan"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filters to apply to the scan results"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "scan_depth": "full",
                "include_agents": True,
                "include_modules": True,
                "include_schemas": True,
                "filters": {
                    "source_type": ["agent", "module"],
                    "reflection_type": "agent_reflection",
                    "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
                }
            }
        }

class ReflectionNode(BaseModel):
    """
    Schema for reflection nodes.
    
    This schema defines the structure of reflection nodes found during a scan.
    """
    node_id: str = Field(
        description="Unique identifier for the reflection node"
    )
    source_type: str = Field(
        description="Type of source: 'agent', 'module', or 'schema'"
    )
    source_id: str = Field(
        description="Identifier of the source component"
    )
    name: str = Field(
        description="Name of the reflection node"
    )
    reflection_type: str = Field(
        description="Type of reflection: 'agent_reflection', 'module_reflection', or 'schema_reflection'"
    )
    metadata: Dict[str, Any] = Field(
        description="Additional metadata about the reflection node"
    )

class ReflectionScanSummary(BaseModel):
    """
    Schema for reflection scan summary.
    
    This schema defines the structure of the summary of a reflection scan.
    """
    total_nodes: int = Field(
        description="Total number of reflection nodes found"
    )
    agent_nodes: int = Field(
        description="Number of agent reflection nodes found"
    )
    module_nodes: int = Field(
        description="Number of module reflection nodes found"
    )
    schema_nodes: int = Field(
        description="Number of schema reflection nodes found"
    )

class ReflectionScanResponse(BaseModel):
    """
    Schema for reflection scan responses.
    
    This schema defines the structure of responses from a full system reflection deep scan.
    """
    scan_id: str = Field(
        description="Unique identifier for the scan"
    )
    timestamp: str = Field(
        description="Timestamp of when the scan was performed"
    )
    status: str = Field(
        description="Status of the scan: 'completed', 'failed', or 'in_progress'"
    )
    parameters: ReflectionScanRequest = Field(
        description="Parameters used for the scan"
    )
    reflection_nodes: List[ReflectionNode] = Field(
        description="List of reflection nodes found during the scan"
    )
    summary: ReflectionScanSummary = Field(
        description="Summary of the scan results"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the scan failed"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-04-28T11:42:30.123456",
                "status": "completed",
                "parameters": {
                    "scan_depth": "full",
                    "include_agents": True,
                    "include_modules": True,
                    "include_schemas": True,
                    "filters": {
                        "source_type": ["agent", "module"],
                        "reflection_type": "agent_reflection"
                    }
                },
                "reflection_nodes": [
                    {
                        "node_id": "550e8400-e29b-41d4-a716-446655440001",
                        "source_type": "agent",
                        "source_id": "reflection_trigger",
                        "name": "Reflection Trigger",
                        "reflection_type": "agent_reflection",
                        "metadata": {
                            "role": "Reflection Trigger",
                            "capabilities": ["reflection", "trigger"],
                            "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
                        }
                    }
                ],
                "summary": {
                    "total_nodes": 1,
                    "agent_nodes": 1,
                    "module_nodes": 0,
                    "schema_nodes": 0
                }
            }
        }

class ReflectionSummary(BaseModel):
    """
    Schema for reflection summary.
    
    This schema defines the structure of a reflection summary.
    """
    reflection_id: str = Field(
        description="Reflection ID this summary relates to"
    )
    summary: str = Field(
        description="Summary of the reflection insights"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp of the summary creation"
    )

class InsightType(str, Enum):
    """
    Enumeration of insight types.
    """
    GENERAL = "general"
    AGENT_ROLE = "agent_role"
    AGENT_CAPABILITIES = "agent_capabilities"
    MEMORY_TAG = "memory_tag"
    MODULE_CATEGORY = "module_category"
    MODULE_STATUS = "module_status"
    API_SURFACE = "api_surface"
    SCHEMA_CATEGORY = "schema_category"
    SCHEMA_STATUS = "schema_status"

class Insight(BaseModel):
    """
    Schema for insights.
    
    This schema defines the structure of insights generated during reflection analysis.
    """
    insight_id: str = Field(
        description="Unique identifier for the insight"
    )
    type: str = Field(
        description="Type of insight"
    )
    title: str = Field(
        description="Title of the insight"
    )
    description: str = Field(
        description="Description of the insight"
    )
    confidence: float = Field(
        description="Confidence score for the insight (0.0 to 1.0)"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional details about the insight"
    )

class DriftTrigger(BaseModel):
    """
    Schema for drift triggers.
    
    This schema defines the structure of drift triggers identified during reflection analysis.
    """
    trigger_id: str = Field(
        description="Unique identifier for the drift trigger"
    )
    type: str = Field(
        description="Type of drift trigger"
    )
    title: str = Field(
        description="Title of the drift trigger"
    )
    description: str = Field(
        description="Description of the drift trigger"
    )
    severity: str = Field(
        description="Severity of the drift trigger: 'low', 'medium', or 'high'"
    )
    affected_component: str = Field(
        description="Component affected by the drift trigger"
    )

class RecoveryPath(BaseModel):
    """
    Schema for recovery paths.
    
    This schema defines the structure of recovery paths generated for drift triggers.
    """
    path_id: str = Field(
        description="Unique identifier for the recovery path"
    )
    trigger_id: str = Field(
        description="Identifier of the associated drift trigger"
    )
    title: str = Field(
        description="Title of the recovery path"
    )
    description: str = Field(
        description="Description of the recovery path"
    )
    steps: List[str] = Field(
        description="Steps to follow for recovery"
    )
    estimated_effort: str = Field(
        description="Estimated effort required: 'low', 'medium', or 'high'"
    )

class ReflectionAnalysisSummary(BaseModel):
    """
    Schema for reflection analysis summary.
    
    This schema defines the structure of the summary of a reflection analysis.
    """
    insight_count: int = Field(
        description="Number of insights generated"
    )
    drift_trigger_count: int = Field(
        description="Number of drift triggers identified"
    )
    recovery_path_count: int = Field(
        description="Number of recovery paths generated"
    )
    reflection_health: float = Field(
        description="Overall health score for the reflection (0.0 to 1.0)"
    )

class ReflectionAnalysisResult(BaseModel):
    """
    Schema for reflection analysis results.
    
    This schema defines the structure of results from analyzing a specific reflection surface.
    """
    analysis_id: str = Field(
        description="Unique identifier for the analysis"
    )
    reflection_id: str = Field(
        description="Identifier of the reflection being analyzed"
    )
    timestamp: str = Field(
        description="Timestamp of when the analysis was performed"
    )
    status: str = Field(
        description="Status of the analysis: 'completed', 'failed', or 'in_progress'"
    )
    reflection_data: Optional[Dict[str, Any]] = Field(
        description="Data of the reflection being analyzed"
    )
    insights: List[Insight] = Field(
        description="List of insights generated during the analysis"
    )
    drift_triggers: List[DriftTrigger] = Field(
        description="List of drift triggers identified during the analysis"
    )
    recovery_paths: List[RecoveryPath] = Field(
        description="List of recovery paths generated for the identified drift triggers"
    )
    summary: ReflectionAnalysisSummary = Field(
        description="Summary of the analysis results"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the analysis failed"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "analysis_id": "550e8400-e29b-41d4-a716-446655440002",
                "reflection_id": "550e8400-e29b-41d4-a716-446655440001",
                "timestamp": "2025-04-28T11:45:30.123456",
                "status": "completed",
                "reflection_data": {
                    "node_id": "550e8400-e29b-41d4-a716-446655440001",
                    "source_type": "agent",
                    "source_id": "reflection_trigger",
                    "name": "Reflection Trigger",
                    "reflection_type": "agent_reflection",
                    "metadata": {
                        "role": "Reflection Trigger",
                        "capabilities": ["reflection", "trigger"],
                        "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
                    }
                },
                "insights": [
                    {
                        "insight_id": "550e8400-e29b-41d4-a716-446655440003",
                        "type": "agent_role",
                        "title": "Reflection Role Identified",
                        "description": "Agent has a reflection-related role: 'Reflection Trigger'",
                        "confidence": 0.9
                    }
                ],
                "drift_triggers": [
                    {
                        "trigger_id": "550e8400-e29b-41d4-a716-446655440004",
                        "type": "missing_capability",
                        "title": "Missing Reflection Capability",
                        "description": "Agent is identified as reflection-related but lacks explicit reflection capabilities",
                        "severity": "medium",
                        "affected_component": "Reflection Trigger"
                    }
                ],
                "recovery_paths": [
                    {
                        "path_id": "550e8400-e29b-41d4-a716-446655440005",
                        "trigger_id": "550e8400-e29b-41d4-a716-446655440004",
                        "title": "Add Reflection Capability",
                        "description": "Add explicit reflection capability to agent 'Reflection Trigger'",
                        "steps": [
                            "Locate agent definition in agent_cognition_index.json",
                            "Add 'reflection' to the capabilities array",
                            "Update memory tag to reflect the change"
                        ],
                        "estimated_effort": "low"
                    }
                ],
                "summary": {
                    "insight_count": 1,
                    "drift_trigger_count": 1,
                    "recovery_path_count": 1,
                    "reflection_health": 0.75
                }
            }
        }
