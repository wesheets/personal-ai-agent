"""
Health Monitor Routes - Hardening Step 9

This module implements the API routes for the System Health Monitor, which provides
comprehensive monitoring of system components, predictive maintenance capabilities,
and self-healing functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, List

from app.schemas.health_monitor_schema import (
    HealthCheckRequest, HealthCheckResponse,
    PredictiveMaintenanceRequest, PredictiveMaintenanceResponse,
    SelfHealingRequest, SelfHealingResponse,
    HealthMonitorConfigRequest, HealthMonitorConfigResponse,
    ComponentType
)

from app.modules.health_monitor import get_health_monitor
from app.utils.manifest_manager import register_route, update_manifest

# Create router
router = APIRouter()

@router.post("/health/check", response_model=HealthCheckResponse)
async def check_health(request: HealthCheckRequest):
    """
    Perform a health check on the specified component or the entire system.
    
    Args:
        request: HealthCheckRequest object containing check parameters
        
    Returns:
        HealthCheckResponse with health check results
    """
    health_monitor = get_health_monitor()
    return await health_monitor.check_health(request)

@router.get("/health/check/{component_id}", response_model=HealthCheckResponse)
async def check_component_health(
    component_id: str,
    component_type: Optional[ComponentType] = None,
    include_metrics: bool = True,
    include_recommendations: bool = True
):
    """
    Perform a health check on a specific component.
    
    Args:
        component_id: ID of the component to check
        component_type: Optional type of the component
        include_metrics: Whether to include detailed metrics
        include_recommendations: Whether to include recommendations
        
    Returns:
        HealthCheckResponse with health check results
    """
    request = HealthCheckRequest(
        component_id=component_id,
        component_type=component_type,
        include_metrics=include_metrics,
        include_recommendations=include_recommendations
    )
    health_monitor = get_health_monitor()
    return await health_monitor.check_health(request)

@router.get("/health/system", response_model=HealthCheckResponse)
async def check_system_health(
    include_metrics: bool = True,
    include_recommendations: bool = True
):
    """
    Perform a health check on the entire system.
    
    Args:
        include_metrics: Whether to include detailed metrics
        include_recommendations: Whether to include recommendations
        
    Returns:
        HealthCheckResponse with health check results
    """
    request = HealthCheckRequest(
        component_id=None,
        component_type=None,
        include_metrics=include_metrics,
        include_recommendations=include_recommendations
    )
    health_monitor = get_health_monitor()
    return await health_monitor.check_health(request)

@router.post("/health/maintenance/predict", response_model=PredictiveMaintenanceResponse)
async def predict_maintenance(request: PredictiveMaintenanceRequest):
    """
    Predict maintenance needs for system components.
    
    Args:
        request: PredictiveMaintenanceRequest object
        
    Returns:
        PredictiveMaintenanceResponse with maintenance predictions
    """
    health_monitor = get_health_monitor()
    return await health_monitor.predict_maintenance(request)

@router.get("/health/maintenance/predict/{component_id}", response_model=PredictiveMaintenanceResponse)
async def predict_component_maintenance(
    component_id: str,
    component_type: Optional[ComponentType] = None,
    time_horizon_hours: int = 24,
    confidence_threshold: float = 0.7
):
    """
    Predict maintenance needs for a specific component.
    
    Args:
        component_id: ID of the component to analyze
        component_type: Optional type of the component
        time_horizon_hours: Time horizon for predictions in hours
        confidence_threshold: Minimum confidence threshold for predictions
        
    Returns:
        PredictiveMaintenanceResponse with maintenance predictions
    """
    request = PredictiveMaintenanceRequest(
        component_id=component_id,
        component_type=component_type,
        time_horizon_hours=time_horizon_hours,
        confidence_threshold=confidence_threshold
    )
    health_monitor = get_health_monitor()
    return await health_monitor.predict_maintenance(request)

@router.post("/health/healing", response_model=SelfHealingResponse)
async def perform_self_healing(request: SelfHealingRequest, background_tasks: BackgroundTasks):
    """
    Perform self-healing actions on a component.
    
    Args:
        request: SelfHealingRequest object
        
    Returns:
        SelfHealingResponse with healing results
    """
    health_monitor = get_health_monitor()
    
    # For potentially long-running healing operations, use background tasks
    if request.auto_approve:
        # Run in background if auto-approved
        healing_task = background_tasks.add_task(
            health_monitor.perform_self_healing,
            request
        )
        return SelfHealingResponse(
            request_id="background-task",
            component_id=request.component_id,
            timestamp=None,
            issue_resolved=None,
            actions_performed=[],
            current_status=None,
            recommendations=["Healing operation started in background"]
        )
    else:
        # Run synchronously if manual approval needed
        return await health_monitor.perform_self_healing(request)

@router.post("/health/config", response_model=HealthMonitorConfigResponse)
async def update_health_monitor_config(request: HealthMonitorConfigRequest):
    """
    Update health monitor configuration.
    
    Args:
        request: HealthMonitorConfigRequest object
        
    Returns:
        HealthMonitorConfigResponse with updated configuration
    """
    health_monitor = get_health_monitor()
    return await health_monitor.update_config(request)

@router.get("/health/config", response_model=HealthMonitorConfigResponse)
async def get_health_monitor_config():
    """
    Get current health monitor configuration.
    
    Returns:
        HealthMonitorConfigResponse with current configuration
    """
    health_monitor = get_health_monitor()
    return HealthMonitorConfigResponse(
        request_id="get-config",
        timestamp=None,
        current_config=health_monitor.config,
        changes_applied={},
        restart_required=False
    )

# Register routes with the system manifest
def register_health_monitor_routes():
    """Register health monitor routes with the system manifest."""
    routes = [
        {
            "path": "/health/check",
            "method": "POST",
            "schema": "HealthCheckRequest",
            "response_schema": "HealthCheckResponse",
            "description": "Perform a health check on the specified component or the entire system"
        },
        {
            "path": "/health/check/{component_id}",
            "method": "GET",
            "schema": "None",
            "response_schema": "HealthCheckResponse",
            "description": "Perform a health check on a specific component"
        },
        {
            "path": "/health/system",
            "method": "GET",
            "schema": "None",
            "response_schema": "HealthCheckResponse",
            "description": "Perform a health check on the entire system"
        },
        {
            "path": "/health/maintenance/predict",
            "method": "POST",
            "schema": "PredictiveMaintenanceRequest",
            "response_schema": "PredictiveMaintenanceResponse",
            "description": "Predict maintenance needs for system components"
        },
        {
            "path": "/health/maintenance/predict/{component_id}",
            "method": "GET",
            "schema": "None",
            "response_schema": "PredictiveMaintenanceResponse",
            "description": "Predict maintenance needs for a specific component"
        },
        {
            "path": "/health/healing",
            "method": "POST",
            "schema": "SelfHealingRequest",
            "response_schema": "SelfHealingResponse",
            "description": "Perform self-healing actions on a component"
        },
        {
            "path": "/health/config",
            "method": "POST",
            "schema": "HealthMonitorConfigRequest",
            "response_schema": "HealthMonitorConfigResponse",
            "description": "Update health monitor configuration"
        },
        {
            "path": "/health/config",
            "method": "GET",
            "schema": "None",
            "response_schema": "HealthMonitorConfigResponse",
            "description": "Get current health monitor configuration"
        }
    ]
    
    # Register each route
    for route in routes:
        register_route(
            route_path=route["path"],
            method=route["method"],
            schema=route["schema"],
            status="registered"
        )
    
    # Update manifest to indicate health monitor routes are registered
    update_manifest(
        section="hardening_layers",
        key="health_monitor_enabled",
        value=True
    )
