"""
Health Monitor Schema - Hardening Step 9

This module defines the schemas for the System Health Monitor, which provides
comprehensive monitoring of system components, predictive maintenance capabilities,
and self-healing functionality.

The System Health Monitor tracks the health of various system components, detects
potential issues before they cause failures, and can automatically take corrective
actions when problems are detected.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class HealthStatus(str, Enum):
    """Enum representing the health status of a system component."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """Enum representing the type of system component."""
    AGENT = "agent"
    MODULE = "module"
    ROUTE = "route"
    SCHEMA = "schema"
    DATABASE = "database"
    MEMORY = "memory"
    INTEGRATION = "integration"
    SYSTEM = "system"


class HealthMetric(BaseModel):
    """Model representing a health metric for a system component."""
    name: str = Field(..., description="Name of the metric")
    value: Union[float, int, str, bool] = Field(..., description="Current value of the metric")
    unit: Optional[str] = Field(None, description="Unit of measurement for the metric")
    threshold_warning: Optional[Union[float, int, str, bool]] = Field(None, description="Warning threshold for the metric")
    threshold_critical: Optional[Union[float, int, str, bool]] = Field(None, description="Critical threshold for the metric")
    status: HealthStatus = Field(HealthStatus.UNKNOWN, description="Current status of the metric")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the metric was recorded")


class ComponentHealth(BaseModel):
    """Model representing the health of a system component."""
    component_id: str = Field(..., description="Unique identifier for the component")
    component_name: str = Field(..., description="Human-readable name of the component")
    component_type: ComponentType = Field(..., description="Type of the component")
    status: HealthStatus = Field(..., description="Overall health status of the component")
    metrics: List[HealthMetric] = Field(default_factory=list, description="List of health metrics for the component")
    last_checked: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the component was last checked")
    issues: List[str] = Field(default_factory=list, description="List of identified issues with the component")
    recommendations: List[str] = Field(default_factory=list, description="List of recommendations to improve component health")


class SystemHealthSummary(BaseModel):
    """Model representing a summary of the overall system health."""
    overall_status: HealthStatus = Field(..., description="Overall health status of the system")
    component_statuses: Dict[ComponentType, Dict[HealthStatus, int]] = Field(
        ..., description="Count of components in each health status, grouped by component type"
    )
    critical_issues_count: int = Field(..., description="Number of critical issues detected")
    warning_issues_count: int = Field(..., description="Number of warning issues detected")
    healthy_components_count: int = Field(..., description="Number of healthy components")
    total_components_count: int = Field(..., description="Total number of components monitored")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the summary was last updated")


class HealthCheckRequest(BaseModel):
    """Request model for performing a health check on a specific component or the entire system."""
    component_id: Optional[str] = Field(None, description="Optional component ID to check. If not provided, checks the entire system")
    component_type: Optional[ComponentType] = Field(None, description="Optional component type to filter by")
    include_metrics: bool = Field(True, description="Whether to include detailed metrics in the response")
    include_recommendations: bool = Field(True, description="Whether to include recommendations in the response")


class HealthCheckResponse(BaseModel):
    """Response model for a health check request."""
    request_id: str = Field(..., description="Unique identifier for the health check request")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the health check was performed")
    summary: SystemHealthSummary = Field(..., description="Summary of the system health")
    components: List[ComponentHealth] = Field(default_factory=list, description="List of component health details")


class PredictiveMaintenanceRequest(BaseModel):
    """Request model for predictive maintenance analysis."""
    component_id: Optional[str] = Field(None, description="Optional component ID to analyze. If not provided, analyzes the entire system")
    component_type: Optional[ComponentType] = Field(None, description="Optional component type to filter by")
    time_horizon_hours: int = Field(24, description="Time horizon for predictions in hours")
    confidence_threshold: float = Field(0.7, description="Minimum confidence threshold for predictions")


class MaintenancePrediction(BaseModel):
    """Model representing a maintenance prediction for a system component."""
    component_id: str = Field(..., description="Component ID the prediction applies to")
    component_name: str = Field(..., description="Human-readable name of the component")
    component_type: ComponentType = Field(..., description="Type of the component")
    predicted_issue: str = Field(..., description="Description of the predicted issue")
    confidence: float = Field(..., description="Confidence level of the prediction (0-1)")
    time_to_failure: Optional[int] = Field(None, description="Estimated time to failure in hours")
    recommended_action: str = Field(..., description="Recommended maintenance action")
    priority: str = Field(..., description="Priority of the recommended action (low, medium, high)")
    prediction_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the prediction was made")


class PredictiveMaintenanceResponse(BaseModel):
    """Response model for a predictive maintenance request."""
    request_id: str = Field(..., description="Unique identifier for the predictive maintenance request")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the analysis was performed")
    predictions: List[MaintenancePrediction] = Field(default_factory=list, description="List of maintenance predictions")
    total_predictions_count: int = Field(0, description="Total number of predictions")
    high_priority_count: int = Field(0, description="Number of high priority predictions")
    medium_priority_count: int = Field(0, description="Number of medium priority predictions")
    low_priority_count: int = Field(0, description="Number of low priority predictions")


class SelfHealingAction(str, Enum):
    """Enum representing the type of self-healing action."""
    RESTART_COMPONENT = "restart_component"
    CLEAR_CACHE = "clear_cache"
    RESET_CONNECTION = "reset_connection"
    ROLLBACK_TO_SNAPSHOT = "rollback_to_snapshot"
    SCALE_RESOURCES = "scale_resources"
    APPLY_PATCH = "apply_patch"
    NOTIFY_ADMIN = "notify_admin"
    NO_ACTION = "no_action"


class SelfHealingRequest(BaseModel):
    """Request model for performing self-healing actions."""
    component_id: str = Field(..., description="Component ID to heal")
    issue_description: str = Field(..., description="Description of the issue to address")
    suggested_actions: List[SelfHealingAction] = Field(default_factory=list, description="List of suggested healing actions")
    auto_approve: bool = Field(False, description="Whether to automatically approve and execute healing actions")
    max_impact_level: str = Field("low", description="Maximum allowed impact level of healing actions (low, medium, high)")


class HealingActionResult(BaseModel):
    """Model representing the result of a healing action."""
    action: SelfHealingAction = Field(..., description="The healing action performed")
    success: bool = Field(..., description="Whether the action was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the action was performed")
    details: str = Field(..., description="Details about the action result")
    impact_level: str = Field(..., description="Actual impact level of the action (low, medium, high)")
    duration_ms: int = Field(..., description="Duration of the action in milliseconds")


class SelfHealingResponse(BaseModel):
    """Response model for a self-healing request."""
    request_id: str = Field(..., description="Unique identifier for the self-healing request")
    component_id: str = Field(..., description="Component ID that was healed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when healing was performed")
    issue_resolved: bool = Field(..., description="Whether the issue was resolved")
    actions_performed: List[HealingActionResult] = Field(default_factory=list, description="List of healing actions performed")
    current_status: HealthStatus = Field(..., description="Current health status after healing")
    recommendations: List[str] = Field(default_factory=list, description="Additional recommendations if issue not fully resolved")


class HealthMonitorConfigRequest(BaseModel):
    """Request model for configuring the health monitor."""
    check_interval_seconds: Optional[int] = Field(None, description="Interval between automatic health checks in seconds")
    enable_predictive_maintenance: Optional[bool] = Field(None, description="Whether to enable predictive maintenance")
    enable_self_healing: Optional[bool] = Field(None, description="Whether to enable automatic self-healing")
    alert_thresholds: Optional[Dict[str, Dict[str, Union[float, int, str, bool]]]] = Field(
        None, description="Custom alert thresholds for specific metrics"
    )
    excluded_components: Optional[List[str]] = Field(None, description="List of component IDs to exclude from monitoring")


class HealthMonitorConfigResponse(BaseModel):
    """Response model for health monitor configuration."""
    request_id: str = Field(..., description="Unique identifier for the configuration request")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when configuration was updated")
    current_config: Dict = Field(..., description="Current configuration after updates")
    changes_applied: Dict = Field(..., description="Changes that were applied")
    restart_required: bool = Field(False, description="Whether a restart is required for changes to take effect")
