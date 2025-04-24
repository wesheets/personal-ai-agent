"""
Health Monitor Module - Hardening Step 9

This module implements the System Health Monitor functionality, which provides
comprehensive monitoring of system components, predictive maintenance capabilities,
and self-healing functionality.

The Health Monitor tracks the health of various system components, detects
potential issues before they cause failures, and can automatically take corrective
actions when problems are detected.
"""

import os
import uuid
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

from fastapi import HTTPException

from app.schemas.health_monitor_schema import (
    HealthStatus, ComponentType, HealthMetric, ComponentHealth,
    SystemHealthSummary, HealthCheckRequest, HealthCheckResponse,
    PredictiveMaintenanceRequest, MaintenancePrediction, PredictiveMaintenanceResponse,
    SelfHealingAction, SelfHealingRequest, HealingActionResult, SelfHealingResponse,
    HealthMonitorConfigRequest, HealthMonitorConfigResponse
)

from app.utils.retry_handler import retry_with_backoff
from app.utils.error_classification import classify_error, log_error_to_memory
from app.utils.manifest_manager import load_manifest, update_manifest

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "check_interval_seconds": 300,  # 5 minutes
    "enable_predictive_maintenance": True,
    "enable_self_healing": False,  # Disabled by default for safety
    "alert_thresholds": {
        "cpu_usage": {
            "warning": 70.0,  # 70% CPU usage
            "critical": 90.0  # 90% CPU usage
        },
        "memory_usage": {
            "warning": 80.0,  # 80% memory usage
            "critical": 95.0  # 95% memory usage
        },
        "response_time": {
            "warning": 1000,  # 1000ms response time
            "critical": 3000  # 3000ms response time
        },
        "error_rate": {
            "warning": 0.05,  # 5% error rate
            "critical": 0.10  # 10% error rate
        },
        "disk_usage": {
            "warning": 85.0,  # 85% disk usage
            "critical": 95.0  # 95% disk usage
        }
    },
    "excluded_components": []
}

# Path to store health monitor data
HEALTH_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "health_monitor")
CONFIG_FILE_PATH = os.path.join(HEALTH_DATA_DIR, "config.json")
HEALTH_HISTORY_PATH = os.path.join(HEALTH_DATA_DIR, "health_history.json")
PREDICTIONS_PATH = os.path.join(HEALTH_DATA_DIR, "predictions.json")
HEALING_ACTIONS_PATH = os.path.join(HEALTH_DATA_DIR, "healing_actions.json")

# Ensure data directory exists
os.makedirs(HEALTH_DATA_DIR, exist_ok=True)


class HealthMonitor:
    """
    Health Monitor class for tracking system component health, predicting issues,
    and performing self-healing actions.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HealthMonitor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.config = self._load_config()
        self.component_cache = {}
        self.last_check_time = {}
        self.prediction_models = {}
        self.healing_strategies = self._initialize_healing_strategies()
        
        # Initialize data files if they don't exist
        if not os.path.exists(HEALTH_HISTORY_PATH):
            with open(HEALTH_HISTORY_PATH, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(PREDICTIONS_PATH):
            with open(PREDICTIONS_PATH, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(HEALING_ACTIONS_PATH):
            with open(HEALING_ACTIONS_PATH, 'w') as f:
                json.dump([], f)
        
        logger.info("Health Monitor initialized")

    def _load_config(self) -> Dict:
        """Load configuration from file or create with defaults if it doesn't exist."""
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = DEFAULT_CONFIG.copy()
                    merged_config.update(config)
                    return merged_config
            except Exception as e:
                logger.error(f"Error loading health monitor config: {str(e)}")
                return DEFAULT_CONFIG
        else:
            # Create default config file
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            return DEFAULT_CONFIG

    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving health monitor config: {str(e)}")

    def _initialize_healing_strategies(self) -> Dict:
        """Initialize self-healing strategies for different component types."""
        return {
            ComponentType.AGENT: {
                SelfHealingAction.RESTART_COMPONENT: self._restart_agent,
                SelfHealingAction.CLEAR_CACHE: self._clear_agent_cache,
            },
            ComponentType.MODULE: {
                SelfHealingAction.RESTART_COMPONENT: self._restart_module,
                SelfHealingAction.ROLLBACK_TO_SNAPSHOT: self._rollback_module,
            },
            ComponentType.ROUTE: {
                SelfHealingAction.RESET_CONNECTION: self._reset_route_connection,
            },
            ComponentType.DATABASE: {
                SelfHealingAction.CLEAR_CACHE: self._clear_db_cache,
                SelfHealingAction.RESET_CONNECTION: self._reset_db_connection,
            },
            ComponentType.MEMORY: {
                SelfHealingAction.CLEAR_CACHE: self._clear_memory_cache,
                SelfHealingAction.ROLLBACK_TO_SNAPSHOT: self._rollback_memory,
            },
            ComponentType.SYSTEM: {
                SelfHealingAction.RESTART_COMPONENT: self._restart_system_component,
                SelfHealingAction.SCALE_RESOURCES: self._scale_system_resources,
            }
        }

    @retry_with_backoff(max_retries=3, base_delay=1, backoff_factor=2)
    async def check_health(self, request: HealthCheckRequest) -> HealthCheckResponse:
        """
        Perform a health check on the specified component or the entire system.
        
        Args:
            request: HealthCheckRequest object containing check parameters
            
        Returns:
            HealthCheckResponse with health check results
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Get components to check
            components_to_check = self._get_components_to_check(
                component_id=request.component_id,
                component_type=request.component_type
            )
            
            # Check health of each component
            component_health_list = []
            for component in components_to_check:
                health = self._check_component_health(
                    component,
                    include_metrics=request.include_metrics,
                    include_recommendations=request.include_recommendations
                )
                component_health_list.append(health)
                
                # Update component cache
                self.component_cache[component["component_id"]] = health
                self.last_check_time[component["component_id"]] = datetime.utcnow()
            
            # Generate system health summary
            summary = self._generate_health_summary(component_health_list)
            
            # Save health check results to history
            self._save_health_check_history(request_id, summary, component_health_list)
            
            return HealthCheckResponse(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                summary=summary,
                components=component_health_list
            )
        
        except Exception as e:
            error_info = classify_error(e)
            log_error_to_memory(
                error=e,
                error_type=error_info.error_type,
                source="health_monitor.check_health",
                details={"request": request.dict() if request else None}
            )
            logger.error(f"Error in health check: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

    def _get_components_to_check(
        self, component_id: Optional[str] = None, component_type: Optional[ComponentType] = None
    ) -> List[Dict]:
        """
        Get the list of components to check based on filters.
        
        Args:
            component_id: Optional specific component ID to check
            component_type: Optional component type to filter by
            
        Returns:
            List of component dictionaries to check
        """
        # Load system manifest to get component information
        manifest = load_manifest()
        
        components = []
        
        # If specific component ID is provided, only check that component
        if component_id:
            # Find the component in the manifest
            if component_id in manifest.get("agents", {}):
                component_data = manifest["agents"][component_id]
                components.append({
                    "component_id": component_id,
                    "component_name": component_id,
                    "component_type": ComponentType.AGENT,
                    "data": component_data
                })
            elif component_id in manifest.get("modules", {}):
                component_data = manifest["modules"][component_id]
                components.append({
                    "component_id": component_id,
                    "component_name": component_id,
                    "component_type": ComponentType.MODULE,
                    "data": component_data
                })
            elif component_id in manifest.get("routes", {}):
                component_data = manifest["routes"][component_id]
                components.append({
                    "component_id": component_id,
                    "component_name": component_id,
                    "component_type": ComponentType.ROUTE,
                    "data": component_data
                })
            elif component_id in manifest.get("schemas", {}):
                component_data = manifest["schemas"][component_id]
                components.append({
                    "component_id": component_id,
                    "component_name": component_id,
                    "component_type": ComponentType.SCHEMA,
                    "data": component_data
                })
            else:
                # Component not found in manifest
                raise ValueError(f"Component with ID {component_id} not found in system manifest")
        else:
            # Add agents
            for agent_id, agent_data in manifest.get("agents", {}).items():
                if agent_id not in self.config["excluded_components"]:
                    components.append({
                        "component_id": agent_id,
                        "component_name": agent_id,
                        "component_type": ComponentType.AGENT,
                        "data": agent_data
                    })
            
            # Add modules
            for module_id, module_data in manifest.get("modules", {}).items():
                if module_id not in self.config["excluded_components"]:
                    components.append({
                        "component_id": module_id,
                        "component_name": module_id,
                        "component_type": ComponentType.MODULE,
                        "data": module_data
                    })
            
            # Add routes
            for route_id, route_data in manifest.get("routes", {}).items():
                if route_id not in self.config["excluded_components"]:
                    components.append({
                        "component_id": route_id,
                        "component_name": route_id,
                        "component_type": ComponentType.ROUTE,
                        "data": route_data
                    })
            
            # Add schemas
            for schema_id, schema_data in manifest.get("schemas", {}).items():
                if schema_id not in self.config["excluded_components"]:
                    components.append({
                        "component_id": schema_id,
                        "component_name": schema_id,
                        "component_type": ComponentType.SCHEMA,
                        "data": schema_data
                    })
            
            # Add system components
            components.append({
                "component_id": "system_memory",
                "component_name": "System Memory",
                "component_type": ComponentType.MEMORY,
                "data": manifest.get("memory", {})
            })
            
            components.append({
                "component_id": "system_core",
                "component_name": "System Core",
                "component_type": ComponentType.SYSTEM,
                "data": manifest.get("manifest_meta", {})
            })
        
        # Filter by component type if specified
        if component_type:
            components = [c for c in components if c["component_type"] == component_type]
        
        return components

    def _check_component_health(
        self, component: Dict, include_metrics: bool = True, include_recommendations: bool = True
    ) -> ComponentHealth:
        """
        Check the health of a specific component.
        
        Args:
            component: Component dictionary with metadata
            include_metrics: Whether to include detailed metrics
            include_recommendations: Whether to include recommendations
            
        Returns:
            ComponentHealth object with health information
        """
        component_id = component["component_id"]
        component_type = component["component_type"]
        
        # Get component-specific metrics
        metrics = []
        if include_metrics:
            metrics = self._get_component_metrics(component)
        
        # Determine overall status based on metrics
        status = self._determine_component_status(metrics)
        
        # Identify issues
        issues = self._identify_component_issues(component, metrics)
        
        # Generate recommendations if needed
        recommendations = []
        if include_recommendations and issues:
            recommendations = self._generate_recommendations(component, issues, metrics)
        
        return ComponentHealth(
            component_id=component_id,
            component_name=component["component_name"],
            component_type=component_type,
            status=status,
            metrics=metrics,
            last_checked=datetime.utcnow(),
            issues=issues,
            recommendations=recommendations
        )

    def _get_component_metrics(self, component: Dict) -> List[HealthMetric]:
        """
        Get health metrics for a specific component.
        
        Args:
            component: Component dictionary with metadata
            
        Returns:
            List of HealthMetric objects
        """
        component_id = component["component_id"]
        component_type = component["component_type"]
        metrics = []
        
        # Common metrics for all components
        metrics.append(self._get_uptime_metric(component))
        metrics.append(self._get_error_rate_metric(component))
        
        # Component-specific metrics
        if component_type == ComponentType.AGENT:
            metrics.extend(self._get_agent_metrics(component))
        elif component_type == ComponentType.MODULE:
            metrics.extend(self._get_module_metrics(component))
        elif component_type == ComponentType.ROUTE:
            metrics.extend(self._get_route_metrics(component))
        elif component_type == ComponentType.SCHEMA:
            metrics.extend(self._get_schema_metrics(component))
        elif component_type == ComponentType.MEMORY:
            metrics.extend(self._get_memory_metrics(component))
        elif component_type == ComponentType.SYSTEM:
            metrics.extend(self._get_system_metrics(component))
        
        return metrics

    def _get_uptime_metric(self, component: Dict) -> HealthMetric:
        """Get uptime metric for a component."""
        # For demonstration, we'll use a random uptime value
        # In a real implementation, this would be retrieved from the system
        uptime_hours = 24 * 7  # 1 week
        
        return HealthMetric(
            name="uptime",
            value=uptime_hours,
            unit="hours",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow()
        )

    def _get_error_rate_metric(self, component: Dict) -> HealthMetric:
        """Get error rate metric for a component."""
        # In a real implementation, this would be calculated from error logs
        error_rate = 0.02  # 2% error rate
        
        # Determine status based on thresholds
        status = HealthStatus.HEALTHY
        if error_rate >= self.config["alert_thresholds"]["error_rate"]["critical"]:
            status = HealthStatus.CRITICAL
        elif error_rate >= self.config["alert_thresholds"]["error_rate"]["warning"]:
            status = HealthStatus.DEGRADED
        
        return HealthMetric(
            name="error_rate",
            value=error_rate,
            unit="percentage",
            threshold_warning=self.config["alert_thresholds"]["error_rate"]["warning"],
            threshold_critical=self.config["alert_thresholds"]["error_rate"]["critical"],
            status=status,
            timestamp=datetime.utcnow()
        )

    def _get_agent_metrics(self, component: Dict) -> List[HealthMetric]:
        """Get metrics specific to agent components."""
        metrics = []
        
        # Response time metric
        response_time = 250  # 250ms
        response_status = HealthStatus.HEALTHY
        if response_time >= self.config["alert_thresholds"]["response_time"]["critical"]:
            response_status = HealthStatus.CRITICAL
        elif response_time >= self.config["alert_thresholds"]["response_time"]["warning"]:
            response_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="response_time",
            value=response_time,
            unit="ms",
            threshold_warning=self.config["alert_thresholds"]["response_time"]["warning"],
            threshold_critical=self.config["alert_thresholds"]["response_time"]["critical"],
            status=response_status,
            timestamp=datetime.utcnow()
        ))
        
        # Success rate metric
        success_rate = 0.98  # 98% success rate
        success_status = HealthStatus.HEALTHY
        if success_rate < 0.9:
            success_status = HealthStatus.CRITICAL
        elif success_rate < 0.95:
            success_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="success_rate",
            value=success_rate,
            unit="percentage",
            threshold_warning=0.95,
            threshold_critical=0.9,
            status=success_status,
            timestamp=datetime.utcnow()
        ))
        
        return metrics

    def _get_module_metrics(self, component: Dict) -> List[HealthMetric]:
        """Get metrics specific to module components."""
        metrics = []
        
        # Execution time metric
        execution_time = 150  # 150ms
        execution_status = HealthStatus.HEALTHY
        if execution_time >= 500:
            execution_status = HealthStatus.CRITICAL
        elif execution_time >= 300:
            execution_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="execution_time",
            value=execution_time,
            unit="ms",
            threshold_warning=300,
            threshold_critical=500,
            status=execution_status,
            timestamp=datetime.utcnow()
        ))
        
        # Function call count metric
        call_count = 1250
        metrics.append(HealthMetric(
            name="call_count",
            value=call_count,
            unit="calls",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow()
        ))
        
        return metrics

    def _get_route_metrics(self, component: Dict) -> List[HealthMetric]:
        """Get metrics specific to route components."""
        metrics = []
        
        # Request count metric
        request_count = 5000
        metrics.append(HealthMetric(
            name="request_count",
            value=request_count,
            unit="requests",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow()
        ))
        
        # Average response time metric
        avg_response_time = 180  # 180ms
        response_status = HealthStatus.HEALTHY
        if avg_response_time >= self.config["alert_thresholds"]["response_time"]["critical"]:
            response_status = HealthStatus.CRITICAL
        elif avg_response_time >= self.config["alert_thresholds"]["response_time"]["warning"]:
            response_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="avg_response_time",
            value=avg_response_time,
            unit="ms",
            threshold_warning=self.config["alert_thresholds"]["response_time"]["warning"],
            threshold_critical=self.config["alert_thresholds"]["response_time"]["critical"],
            status=response_status,
            timestamp=datetime.utcnow()
        ))
        
        return metrics

    def _get_schema_metrics(self, component: Dict) -> List[HealthMetric]:
        """Get metrics specific to schema components."""
        metrics = []
        
        # Validation count metric
        validation_count = 3500
        metrics.append(HealthMetric(
            name="validation_count",
            value=validation_count,
            unit="validations",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow()
        ))
        
        # Validation failure rate metric
        failure_rate = 0.01  # 1% failure rate
        failure_status = HealthStatus.HEALTHY
        if failure_rate >= 0.05:
            failure_status = HealthStatus.CRITICAL
        elif failure_rate >= 0.02:
            failure_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="validation_failure_rate",
            value=failure_rate,
            unit="percentage",
            threshold_warning=0.02,
            threshold_critical=0.05,
            status=failure_status,
            timestamp=datetime.utcnow()
        ))
        
        return metrics

    def _get_memory_metrics(self, component: Dict) -> List[HealthMetric]:
        """Get metrics specific to memory components."""
        metrics = []
        
        # Memory usage metric
        memory_usage = 75.0  # 75% usage
        memory_status = HealthStatus.HEALTHY
        if memory_usage >= self.config["alert_thresholds"]["memory_usage"]["critical"]:
            memory_status = HealthStatus.CRITICAL
        elif memory_usage >= self.config["alert_thresholds"]["memory_usage"]["warning"]:
            memory_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="memory_usage",
            value=memory_usage,
            unit="percentage",
            threshold_warning=self.config["alert_thresholds"]["memory_usage"]["warning"],
            threshold_critical=self.config["alert_thresholds"]["memory_usage"]["critical"],
            status=memory_status,
            timestamp=datetime.utcnow()
        ))
        
        # Read operations metric
        read_ops = 25000
        metrics.append(HealthMetric(
            name="read_operations",
            value=read_ops,
            unit="operations",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow()
        ))
        
        # Write operations metric
        write_ops = 10000
        metrics.append(HealthMetric(
            name="write_operations",
            value=write_ops,
            unit="operations",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow()
        ))
        
        return metrics

    def _get_system_metrics(self, component: Dict) -> List[HealthMetric]:
        """Get metrics specific to system components."""
        metrics = []
        
        # CPU usage metric
        cpu_usage = 65.0  # 65% usage
        cpu_status = HealthStatus.HEALTHY
        if cpu_usage >= self.config["alert_thresholds"]["cpu_usage"]["critical"]:
            cpu_status = HealthStatus.CRITICAL
        elif cpu_usage >= self.config["alert_thresholds"]["cpu_usage"]["warning"]:
            cpu_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="cpu_usage",
            value=cpu_usage,
            unit="percentage",
            threshold_warning=self.config["alert_thresholds"]["cpu_usage"]["warning"],
            threshold_critical=self.config["alert_thresholds"]["cpu_usage"]["critical"],
            status=cpu_status,
            timestamp=datetime.utcnow()
        ))
        
        # Disk usage metric
        disk_usage = 72.0  # 72% usage
        disk_status = HealthStatus.HEALTHY
        if disk_usage >= self.config["alert_thresholds"]["disk_usage"]["critical"]:
            disk_status = HealthStatus.CRITICAL
        elif disk_usage >= self.config["alert_thresholds"]["disk_usage"]["warning"]:
            disk_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="disk_usage",
            value=disk_usage,
            unit="percentage",
            threshold_warning=self.config["alert_thresholds"]["disk_usage"]["warning"],
            threshold_critical=self.config["alert_thresholds"]["disk_usage"]["critical"],
            status=disk_status,
            timestamp=datetime.utcnow()
        ))
        
        # Active connections metric
        active_connections = 120
        conn_status = HealthStatus.HEALTHY
        if active_connections >= 500:
            conn_status = HealthStatus.CRITICAL
        elif active_connections >= 300:
            conn_status = HealthStatus.DEGRADED
        
        metrics.append(HealthMetric(
            name="active_connections",
            value=active_connections,
            unit="connections",
            threshold_warning=300,
            threshold_critical=500,
            status=conn_status,
            timestamp=datetime.utcnow()
        ))
        
        return metrics

    def _determine_component_status(self, metrics: List[HealthMetric]) -> HealthStatus:
        """
        Determine overall component status based on metrics.
        
        Args:
            metrics: List of component metrics
            
        Returns:
            Overall HealthStatus
        """
        if not metrics:
            return HealthStatus.UNKNOWN
        
        # If any metric is critical, the component is critical
        if any(metric.status == HealthStatus.CRITICAL for metric in metrics):
            return HealthStatus.CRITICAL
        
        # If any metric is degraded, the component is degraded
        if any(metric.status == HealthStatus.DEGRADED for metric in metrics):
            return HealthStatus.DEGRADED
        
        # If all metrics are healthy, the component is healthy
        if all(metric.status == HealthStatus.HEALTHY for metric in metrics):
            return HealthStatus.HEALTHY
        
        # Default to unknown if metrics have mixed or unknown statuses
        return HealthStatus.UNKNOWN

    def _identify_component_issues(self, component: Dict, metrics: List[HealthMetric]) -> List[str]:
        """
        Identify issues with a component based on metrics.
        
        Args:
            component: Component dictionary with metadata
            metrics: List of component metrics
            
        Returns:
            List of issue descriptions
        """
        issues = []
        
        # Check for issues based on metric statuses
        for metric in metrics:
            if metric.status == HealthStatus.CRITICAL:
                issues.append(f"Critical: {metric.name} is {metric.value} {metric.unit or ''}, exceeds critical threshold of {metric.threshold_critical}")
            elif metric.status == HealthStatus.DEGRADED:
                issues.append(f"Warning: {metric.name} is {metric.value} {metric.unit or ''}, exceeds warning threshold of {metric.threshold_warning}")
        
        # Check for component-specific issues
        component_type = component["component_type"]
        component_id = component["component_id"]
        
        if component_type == ComponentType.AGENT:
            # Check for agent-specific issues
            if "errors" in component["data"] and component["data"]["errors"]:
                issues.append(f"Agent has reported errors: {len(component['data']['errors'])} errors recorded")
        
        elif component_type == ComponentType.ROUTE:
            # Check for route-specific issues
            if "status" in component["data"] and component["data"]["status"] != "registered":
                issues.append(f"Route status is {component['data']['status']}, expected 'registered'")
            
            if "errors" in component["data"] and component["data"]["errors"]:
                issues.append(f"Route has reported errors: {len(component['data']['errors'])} errors recorded")
        
        elif component_type == ComponentType.SCHEMA:
            # Check for schema-specific issues
            if "checksum" in component["data"] and component["data"]["checksum"] == "initial":
                issues.append("Schema is using initial checksum, may need updating")
        
        return issues

    def _generate_recommendations(
        self, component: Dict, issues: List[str], metrics: List[HealthMetric]
    ) -> List[str]:
        """
        Generate recommendations for resolving component issues.
        
        Args:
            component: Component dictionary with metadata
            issues: List of identified issues
            metrics: List of component metrics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        component_type = component["component_type"]
        
        for issue in issues:
            if "Critical:" in issue:
                # Generate recommendations for critical issues
                if "cpu_usage" in issue:
                    recommendations.append("Reduce system load or scale up CPU resources")
                elif "memory_usage" in issue:
                    recommendations.append("Check for memory leaks or increase memory allocation")
                elif "disk_usage" in issue:
                    recommendations.append("Clean up disk space or expand storage")
                elif "error_rate" in issue:
                    recommendations.append("Investigate error logs and fix recurring issues")
                elif "response_time" in issue or "execution_time" in issue:
                    recommendations.append("Optimize code performance or scale up resources")
                else:
                    # Generic recommendation for other critical issues
                    recommendations.append("Immediate attention required: Consider restarting the component")
            
            elif "Warning:" in issue:
                # Generate recommendations for warning issues
                if "cpu_usage" in issue:
                    recommendations.append("Monitor CPU usage trends and optimize if consistently high")
                elif "memory_usage" in issue:
                    recommendations.append("Review memory usage patterns and optimize memory-intensive operations")
                elif "disk_usage" in issue:
                    recommendations.append("Schedule disk cleanup to prevent critical space issues")
                elif "error_rate" in issue:
                    recommendations.append("Review recent error logs to identify potential issues")
                elif "response_time" in issue or "execution_time" in issue:
                    recommendations.append("Monitor performance trends and optimize if consistently degraded")
                else:
                    # Generic recommendation for other warning issues
                    recommendations.append("Monitor the component and plan for optimization")
        
        # Component-specific recommendations
        if component_type == ComponentType.AGENT:
            if any("error" in issue.lower() for issue in issues):
                recommendations.append("Review agent error logs and fix recurring issues")
            
            if any("response_time" in issue.lower() for issue in issues):
                recommendations.append("Consider optimizing agent prompt or using a faster model")
        
        elif component_type == ComponentType.ROUTE:
            if any("status" in issue.lower() for issue in issues):
                recommendations.append("Check route registration in main.py and ensure proper initialization")
            
            if any("error" in issue.lower() for issue in issues):
                recommendations.append("Review route handler code for exceptions and add proper error handling")
        
        elif component_type == ComponentType.SCHEMA:
            if any("checksum" in issue.lower() for issue in issues):
                recommendations.append("Update schema checksum by running schema validation")
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        return unique_recommendations

    def _generate_health_summary(self, component_health_list: List[ComponentHealth]) -> SystemHealthSummary:
        """
        Generate a summary of overall system health.
        
        Args:
            component_health_list: List of ComponentHealth objects
            
        Returns:
            SystemHealthSummary object
        """
        # Initialize counters
        component_statuses = {
            ComponentType.AGENT: {status: 0 for status in HealthStatus},
            ComponentType.MODULE: {status: 0 for status in HealthStatus},
            ComponentType.ROUTE: {status: 0 for status in HealthStatus},
            ComponentType.SCHEMA: {status: 0 for status in HealthStatus},
            ComponentType.DATABASE: {status: 0 for status in HealthStatus},
            ComponentType.MEMORY: {status: 0 for status in HealthStatus},
            ComponentType.INTEGRATION: {status: 0 for status in HealthStatus},
            ComponentType.SYSTEM: {status: 0 for status in HealthStatus}
        }
        
        critical_issues_count = 0
        warning_issues_count = 0
        healthy_components_count = 0
        total_components_count = len(component_health_list)
        
        # Count components by status and type
        for health in component_health_list:
            component_statuses[health.component_type][health.status] += 1
            
            if health.status == HealthStatus.CRITICAL:
                critical_issues_count += len(health.issues)
            elif health.status == HealthStatus.DEGRADED:
                warning_issues_count += len(health.issues)
            elif health.status == HealthStatus.HEALTHY:
                healthy_components_count += 1
        
        # Determine overall system status
        overall_status = HealthStatus.HEALTHY
        if critical_issues_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_issues_count > 0:
            overall_status = HealthStatus.DEGRADED
        elif healthy_components_count < total_components_count:
            overall_status = HealthStatus.UNKNOWN
        
        return SystemHealthSummary(
            overall_status=overall_status,
            component_statuses=component_statuses,
            critical_issues_count=critical_issues_count,
            warning_issues_count=warning_issues_count,
            healthy_components_count=healthy_components_count,
            total_components_count=total_components_count,
            last_updated=datetime.utcnow()
        )

    def _save_health_check_history(
        self, request_id: str, summary: SystemHealthSummary, components: List[ComponentHealth]
    ) -> None:
        """
        Save health check results to history.
        
        Args:
            request_id: Unique identifier for the health check request
            summary: SystemHealthSummary object
            components: List of ComponentHealth objects
        """
        try:
            # Load existing history
            with open(HEALTH_HISTORY_PATH, 'r') as f:
                history = json.load(f)
            
            # Add new health check result
            history.append({
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": summary.dict(),
                "components": [comp.dict() for comp in components]
            })
            
            # Keep only the last 100 health checks
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            with open(HEALTH_HISTORY_PATH, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Error saving health check history: {str(e)}")

    @retry_with_backoff(max_retries=3, base_delay=1, backoff_factor=2)
    async def predict_maintenance(
        self, request: PredictiveMaintenanceRequest
    ) -> PredictiveMaintenanceResponse:
        """
        Predict maintenance needs for system components.
        
        Args:
            request: PredictiveMaintenanceRequest object
            
        Returns:
            PredictiveMaintenanceResponse with maintenance predictions
        """
        try:
            if not self.config["enable_predictive_maintenance"]:
                raise HTTPException(
                    status_code=400,
                    detail="Predictive maintenance is disabled in the system configuration"
                )
            
            request_id = str(uuid.uuid4())
            
            # Get components to analyze
            components_to_analyze = self._get_components_to_check(
                component_id=request.component_id,
                component_type=request.component_type
            )
            
            # Generate predictions for each component
            predictions = []
            for component in components_to_analyze:
                component_predictions = self._predict_component_maintenance(
                    component,
                    time_horizon_hours=request.time_horizon_hours,
                    confidence_threshold=request.confidence_threshold
                )
                predictions.extend(component_predictions)
            
            # Count predictions by priority
            high_priority_count = sum(1 for p in predictions if p.priority == "high")
            medium_priority_count = sum(1 for p in predictions if p.priority == "medium")
            low_priority_count = sum(1 for p in predictions if p.priority == "low")
            
            # Save predictions
            self._save_predictions(request_id, predictions)
            
            return PredictiveMaintenanceResponse(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                predictions=predictions,
                total_predictions_count=len(predictions),
                high_priority_count=high_priority_count,
                medium_priority_count=medium_priority_count,
                low_priority_count=low_priority_count
            )
        
        except Exception as e:
            error_info = classify_error(e)
            log_error_to_memory(
                error=e,
                error_type=error_info.error_type,
                source="health_monitor.predict_maintenance",
                details={"request": request.dict() if request else None}
            )
            logger.error(f"Error in predictive maintenance: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Predictive maintenance failed: {str(e)}")

    def _predict_component_maintenance(
        self, component: Dict, time_horizon_hours: int, confidence_threshold: float
    ) -> List[MaintenancePrediction]:
        """
        Predict maintenance needs for a specific component.
        
        Args:
            component: Component dictionary with metadata
            time_horizon_hours: Time horizon for predictions in hours
            confidence_threshold: Minimum confidence threshold for predictions
            
        Returns:
            List of MaintenancePrediction objects
        """
        component_id = component["component_id"]
        component_type = component["component_type"]
        predictions = []
        
        # Load health history for trend analysis
        health_history = self._get_component_health_history(component_id)
        
        # Skip prediction if not enough history data
        if len(health_history) < 3:
            return predictions
        
        # Analyze trends for each metric
        metrics_trends = self._analyze_metric_trends(health_history)
        
        # Generate predictions based on trends
        for metric_name, trend_data in metrics_trends.items():
            if trend_data["trend"] == "increasing" and trend_data["is_concerning"]:
                # Calculate confidence based on trend strength and consistency
                confidence = trend_data["trend_strength"] * trend_data["consistency"]
                
                # Skip if confidence is below threshold
                if confidence < confidence_threshold:
                    continue
                
                # Calculate time to failure based on trend rate and thresholds
                time_to_failure = self._calculate_time_to_failure(
                    trend_data["current_value"],
                    trend_data["rate_of_change"],
                    trend_data["critical_threshold"],
                    trend_data["unit"]
                )
                
                # Skip if time to failure is beyond the requested horizon
                if time_to_failure is not None and time_to_failure > time_horizon_hours:
                    continue
                
                # Determine priority based on time to failure
                priority = "low"
                if time_to_failure is not None:
                    if time_to_failure < 24:  # Less than 1 day
                        priority = "high"
                    elif time_to_failure < 72:  # Less than 3 days
                        priority = "medium"
                
                # Generate prediction
                prediction = MaintenancePrediction(
                    component_id=component_id,
                    component_name=component["component_name"],
                    component_type=component_type,
                    predicted_issue=f"{metric_name} is trending toward critical levels",
                    confidence=confidence,
                    time_to_failure=time_to_failure,
                    recommended_action=self._get_recommended_action(component_type, metric_name),
                    priority=priority,
                    prediction_timestamp=datetime.utcnow()
                )
                
                predictions.append(prediction)
        
        return predictions

    def _get_component_health_history(self, component_id: str) -> List[Dict]:
        """
        Get health history for a specific component.
        
        Args:
            component_id: Component ID to get history for
            
        Returns:
            List of historical health records for the component
        """
        try:
            # Load health history
            with open(HEALTH_HISTORY_PATH, 'r') as f:
                history = json.load(f)
            
            # Extract component history
            component_history = []
            for check in history:
                for comp in check.get("components", []):
                    if comp.get("component_id") == component_id:
                        component_history.append(comp)
            
            return component_history
        
        except Exception as e:
            logger.error(f"Error loading component health history: {str(e)}")
            return []

    def _analyze_metric_trends(self, health_history: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze trends for component metrics.
        
        Args:
            health_history: List of historical health records for a component
            
        Returns:
            Dictionary mapping metric names to trend data
        """
        metrics_trends = {}
        
        # Skip if not enough history
        if len(health_history) < 3:
            return metrics_trends
        
        # Get all unique metric names
        metric_names = set()
        for record in health_history:
            for metric in record.get("metrics", []):
                metric_names.add(metric.get("name"))
        
        # Analyze trend for each metric
        for metric_name in metric_names:
            # Extract metric values and timestamps
            values = []
            timestamps = []
            units = []
            thresholds = []
            
            for record in health_history:
                for metric in record.get("metrics", []):
                    if metric.get("name") == metric_name:
                        # Skip non-numeric values
                        if not isinstance(metric.get("value"), (int, float)):
                            continue
                        
                        values.append(metric.get("value"))
                        timestamps.append(datetime.fromisoformat(record.get("last_checked")))
                        units.append(metric.get("unit"))
                        
                        # Get threshold if available
                        threshold = None
                        if metric.get("threshold_critical") is not None:
                            threshold = metric.get("threshold_critical")
                        thresholds.append(threshold)
            
            # Skip if not enough data points
            if len(values) < 3:
                continue
            
            # Calculate trend
            trend_data = self._calculate_trend(metric_name, values, timestamps, units, thresholds)
            if trend_data:
                metrics_trends[metric_name] = trend_data
        
        return metrics_trends

    def _calculate_trend(
        self, metric_name: str, values: List[float], timestamps: List[datetime],
        units: List[str], thresholds: List[float]
    ) -> Optional[Dict]:
        """
        Calculate trend for a specific metric.
        
        Args:
            metric_name: Name of the metric
            values: List of metric values
            timestamps: List of timestamps for the values
            units: List of units for the values
            thresholds: List of critical thresholds for the values
            
        Returns:
            Dictionary with trend data or None if trend cannot be calculated
        """
        # Skip if not enough data points
        if len(values) < 3 or len(timestamps) < 3:
            return None
        
        # Convert timestamps to hours since first timestamp
        first_timestamp = min(timestamps)
        hours_since_first = [(ts - first_timestamp).total_seconds() / 3600 for ts in timestamps]
        
        # Calculate linear regression
        try:
            # Simple linear regression: y = mx + b
            n = len(values)
            sum_x = sum(hours_since_first)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(hours_since_first, values))
            sum_xx = sum(x * x for x in hours_since_first)
            
            # Calculate slope (m) and intercept (b)
            m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            b = (sum_y - m * sum_x) / n
            
            # Calculate R-squared (coefficient of determination)
            y_mean = sum_y / n
            ss_total = sum((y - y_mean) ** 2 for y in values)
            ss_residual = sum((y - (m * x + b)) ** 2 for x, y in zip(hours_since_first, values))
            r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
            
            # Determine trend direction
            trend = "stable"
            if m > 0.001:  # Small positive threshold to account for noise
                trend = "increasing"
            elif m < -0.001:  # Small negative threshold to account for noise
                trend = "decreasing"
            
            # Get the most recent value and unit
            current_value = values[-1]
            unit = units[-1] if units else None
            
            # Get the most recent threshold
            critical_threshold = thresholds[-1] if thresholds and thresholds[-1] is not None else None
            
            # Determine if trend is concerning
            is_concerning = False
            if trend == "increasing" and critical_threshold is not None:
                # Trend is concerning if it's increasing and approaching a critical threshold
                is_concerning = current_value > critical_threshold * 0.7
            elif trend == "decreasing" and metric_name in ["success_rate", "availability"]:
                # For metrics where lower is worse, decreasing trend is concerning
                is_concerning = True
            
            return {
                "trend": trend,
                "rate_of_change": m,  # Change per hour
                "trend_strength": abs(m),
                "consistency": r_squared,
                "current_value": current_value,
                "unit": unit,
                "critical_threshold": critical_threshold,
                "is_concerning": is_concerning
            }
        
        except Exception as e:
            logger.error(f"Error calculating trend for {metric_name}: {str(e)}")
            return None

    def _calculate_time_to_failure(
        self, current_value: float, rate_of_change: float, critical_threshold: Optional[float], unit: Optional[str]
    ) -> Optional[int]:
        """
        Calculate estimated time to failure based on trend.
        
        Args:
            current_value: Current metric value
            rate_of_change: Rate of change per hour
            critical_threshold: Critical threshold value
            unit: Unit of measurement
            
        Returns:
            Estimated time to failure in hours or None if cannot be calculated
        """
        if critical_threshold is None or rate_of_change <= 0:
            return None
        
        # Calculate hours until critical threshold is reached
        hours_to_threshold = (critical_threshold - current_value) / rate_of_change
        
        # Return None if negative (already past threshold) or too far in the future
        if hours_to_threshold <= 0 or hours_to_threshold > 720:  # 30 days
            return None
        
        return int(hours_to_threshold)

    def _get_recommended_action(self, component_type: ComponentType, metric_name: str) -> str:
        """
        Get recommended action for a predicted issue.
        
        Args:
            component_type: Type of the component
            metric_name: Name of the metric with the issue
            
        Returns:
            Recommended action description
        """
        # Component-specific recommendations
        if component_type == ComponentType.AGENT:
            if metric_name == "error_rate":
                return "Review agent error logs and fix recurring issues"
            elif metric_name == "response_time":
                return "Optimize agent prompt or consider using a faster model"
            elif metric_name == "success_rate":
                return "Investigate failed agent operations and implement fixes"
        
        elif component_type == ComponentType.MODULE:
            if metric_name == "error_rate":
                return "Review module error logs and fix recurring issues"
            elif metric_name == "execution_time":
                return "Optimize module code performance"
        
        elif component_type == ComponentType.ROUTE:
            if metric_name == "error_rate":
                return "Add error handling to route handler code"
            elif metric_name == "avg_response_time":
                return "Optimize route handler performance"
        
        elif component_type == ComponentType.MEMORY:
            if metric_name == "memory_usage":
                return "Clean up unused memory entries or increase memory allocation"
        
        elif component_type == ComponentType.SYSTEM:
            if metric_name == "cpu_usage":
                return "Reduce system load or scale up CPU resources"
            elif metric_name == "memory_usage":
                return "Check for memory leaks or increase memory allocation"
            elif metric_name == "disk_usage":
                return "Clean up disk space or expand storage"
            elif metric_name == "active_connections":
                return "Implement connection pooling or increase connection limit"
        
        # Generic recommendations based on metric name
        if "usage" in metric_name:
            return f"Monitor {metric_name} and consider resource expansion"
        elif "time" in metric_name:
            return f"Optimize performance to reduce {metric_name}"
        elif "rate" in metric_name:
            return f"Investigate and address factors affecting {metric_name}"
        
        # Default recommendation
        return "Schedule preventive maintenance based on trend analysis"

    def _save_predictions(self, request_id: str, predictions: List[MaintenancePrediction]) -> None:
        """
        Save maintenance predictions to history.
        
        Args:
            request_id: Unique identifier for the prediction request
            predictions: List of MaintenancePrediction objects
        """
        try:
            # Load existing predictions
            with open(PREDICTIONS_PATH, 'r') as f:
                history = json.load(f)
            
            # Add new predictions
            history.append({
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "predictions": [pred.dict() for pred in predictions]
            })
            
            # Keep only the last 50 prediction sets
            if len(history) > 50:
                history = history[-50:]
            
            # Save updated predictions
            with open(PREDICTIONS_PATH, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")

    @retry_with_backoff(max_retries=3, base_delay=1, backoff_factor=2)
    async def perform_self_healing(self, request: SelfHealingRequest) -> SelfHealingResponse:
        """
        Perform self-healing actions on a component.
        
        Args:
            request: SelfHealingRequest object
            
        Returns:
            SelfHealingResponse with healing results
        """
        try:
            if not self.config["enable_self_healing"]:
                raise HTTPException(
                    status_code=400,
                    detail="Self-healing is disabled in the system configuration"
                )
            
            request_id = str(uuid.uuid4())
            
            # Get component information
            component = None
            components = self._get_components_to_check(component_id=request.component_id)
            if components:
                component = components[0]
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Component with ID {request.component_id} not found"
                )
            
            # Validate suggested actions
            valid_actions = self._validate_healing_actions(
                component["component_type"],
                request.suggested_actions,
                request.max_impact_level
            )
            
            if not valid_actions:
                return SelfHealingResponse(
                    request_id=request_id,
                    component_id=request.component_id,
                    timestamp=datetime.utcnow(),
                    issue_resolved=False,
                    actions_performed=[],
                    current_status=HealthStatus.UNKNOWN,
                    recommendations=["No valid healing actions available for this component and impact level"]
                )
            
            # Perform healing actions
            action_results = []
            for action in valid_actions:
                result = await self._execute_healing_action(
                    component,
                    action,
                    request.issue_description,
                    auto_approve=request.auto_approve
                )
                action_results.append(result)
            
            # Check if issue was resolved
            issue_resolved = any(result.success for result in action_results)
            
            # Get current component status
            current_status = HealthStatus.UNKNOWN
            try:
                health_check = await self.check_health(HealthCheckRequest(
                    component_id=request.component_id,
                    include_metrics=True,
                    include_recommendations=True
                ))
                if health_check.components:
                    current_status = health_check.components[0].status
            except Exception as e:
                logger.error(f"Error checking component status after healing: {str(e)}")
            
            # Generate recommendations if issue not resolved
            recommendations = []
            if not issue_resolved:
                recommendations = [
                    "Consider manual intervention to resolve the issue",
                    "Check system logs for more detailed error information",
                    "Contact system administrator if issue persists"
                ]
            
            # Save healing action results
            self._save_healing_actions(request_id, request.component_id, action_results, issue_resolved)
            
            return SelfHealingResponse(
                request_id=request_id,
                component_id=request.component_id,
                timestamp=datetime.utcnow(),
                issue_resolved=issue_resolved,
                actions_performed=action_results,
                current_status=current_status,
                recommendations=recommendations
            )
        
        except Exception as e:
            error_info = classify_error(e)
            log_error_to_memory(
                error=e,
                error_type=error_info.error_type,
                source="health_monitor.perform_self_healing",
                details={"request": request.dict() if request else None}
            )
            logger.error(f"Error in self-healing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Self-healing failed: {str(e)}")

    def _validate_healing_actions(
        self, component_type: ComponentType, suggested_actions: List[SelfHealingAction], max_impact_level: str
    ) -> List[SelfHealingAction]:
        """
        Validate and filter healing actions based on component type and impact level.
        
        Args:
            component_type: Type of the component
            suggested_actions: List of suggested healing actions
            max_impact_level: Maximum allowed impact level
            
        Returns:
            List of valid healing actions
        """
        valid_actions = []
        
        # Define impact levels for each action
        action_impact_levels = {
            SelfHealingAction.RESTART_COMPONENT: "high",
            SelfHealingAction.CLEAR_CACHE: "low",
            SelfHealingAction.RESET_CONNECTION: "medium",
            SelfHealingAction.ROLLBACK_TO_SNAPSHOT: "high",
            SelfHealingAction.SCALE_RESOURCES: "medium",
            SelfHealingAction.APPLY_PATCH: "high",
            SelfHealingAction.NOTIFY_ADMIN: "low",
            SelfHealingAction.NO_ACTION: "low"
        }
        
        # Define impact level hierarchy
        impact_hierarchy = {
            "low": 1,
            "medium": 2,
            "high": 3
        }
        
        # Get maximum allowed impact level value
        max_impact_value = impact_hierarchy.get(max_impact_level.lower(), 1)
        
        # Get available actions for this component type
        available_actions = self.healing_strategies.get(component_type, {}).keys()
        
        # Filter actions based on availability and impact level
        for action in suggested_actions:
            action_impact = action_impact_levels.get(action, "high")
            action_impact_value = impact_hierarchy.get(action_impact, 3)
            
            if action in available_actions and action_impact_value <= max_impact_value:
                valid_actions.append(action)
        
        return valid_actions

    async def _execute_healing_action(
        self, component: Dict, action: SelfHealingAction, issue_description: str, auto_approve: bool = False
    ) -> HealingActionResult:
        """
        Execute a healing action on a component.
        
        Args:
            component: Component dictionary with metadata
            action: Healing action to perform
            issue_description: Description of the issue to address
            auto_approve: Whether to automatically approve the action
            
        Returns:
            HealingActionResult with action result
        """
        component_id = component["component_id"]
        component_type = component["component_type"]
        
        # Define impact levels for each action
        action_impact_levels = {
            SelfHealingAction.RESTART_COMPONENT: "high",
            SelfHealingAction.CLEAR_CACHE: "low",
            SelfHealingAction.RESET_CONNECTION: "medium",
            SelfHealingAction.ROLLBACK_TO_SNAPSHOT: "high",
            SelfHealingAction.SCALE_RESOURCES: "medium",
            SelfHealingAction.APPLY_PATCH: "high",
            SelfHealingAction.NOTIFY_ADMIN: "low",
            SelfHealingAction.NO_ACTION: "low"
        }
        
        impact_level = action_impact_levels.get(action, "high")
        
        # Log the healing action attempt
        logger.info(f"Attempting healing action {action} on component {component_id} for issue: {issue_description}")
        
        start_time = time.time()
        success = False
        details = ""
        
        try:
            # Get the appropriate healing function
            healing_function = self.healing_strategies.get(component_type, {}).get(action)
            
            if healing_function:
                # Execute the healing function
                success, details = await healing_function(component, issue_description, auto_approve)
            else:
                details = f"No implementation available for action {action} on component type {component_type}"
        
        except Exception as e:
            details = f"Error executing healing action: {str(e)}"
            logger.error(details)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        return HealingActionResult(
            action=action,
            success=success,
            timestamp=datetime.utcnow(),
            details=details,
            impact_level=impact_level,
            duration_ms=duration_ms
        )

    def _save_healing_actions(
        self, request_id: str, component_id: str, action_results: List[HealingActionResult], issue_resolved: bool
    ) -> None:
        """
        Save healing action results to history.
        
        Args:
            request_id: Unique identifier for the healing request
            component_id: ID of the component that was healed
            action_results: List of HealingActionResult objects
            issue_resolved: Whether the issue was resolved
        """
        try:
            # Load existing healing actions
            with open(HEALING_ACTIONS_PATH, 'r') as f:
                history = json.load(f)
            
            # Add new healing actions
            history.append({
                "request_id": request_id,
                "component_id": component_id,
                "timestamp": datetime.utcnow().isoformat(),
                "actions": [result.dict() for result in action_results],
                "issue_resolved": issue_resolved
            })
            
            # Keep only the last 100 healing action sets
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated healing actions
            with open(HEALING_ACTIONS_PATH, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Error saving healing actions: {str(e)}")

    @retry_with_backoff(max_retries=3, base_delay=1, backoff_factor=2)
    async def update_config(self, request: HealthMonitorConfigRequest) -> HealthMonitorConfigResponse:
        """
        Update health monitor configuration.
        
        Args:
            request: HealthMonitorConfigRequest object
            
        Returns:
            HealthMonitorConfigResponse with updated configuration
        """
        try:
            request_id = str(uuid.uuid4())
            changes_applied = {}
            restart_required = False
            
            # Update check interval
            if request.check_interval_seconds is not None:
                if request.check_interval_seconds < 60:
                    raise HTTPException(
                        status_code=400,
                        detail="Check interval must be at least 60 seconds"
                    )
                changes_applied["check_interval_seconds"] = {
                    "old": self.config["check_interval_seconds"],
                    "new": request.check_interval_seconds
                }
                self.config["check_interval_seconds"] = request.check_interval_seconds
            
            # Update predictive maintenance setting
            if request.enable_predictive_maintenance is not None:
                changes_applied["enable_predictive_maintenance"] = {
                    "old": self.config["enable_predictive_maintenance"],
                    "new": request.enable_predictive_maintenance
                }
                self.config["enable_predictive_maintenance"] = request.enable_predictive_maintenance
            
            # Update self-healing setting
            if request.enable_self_healing is not None:
                changes_applied["enable_self_healing"] = {
                    "old": self.config["enable_self_healing"],
                    "new": request.enable_self_healing
                }
                self.config["enable_self_healing"] = request.enable_self_healing
                restart_required = True
            
            # Update alert thresholds
            if request.alert_thresholds is not None:
                changes_applied["alert_thresholds"] = {
                    "old": self.config["alert_thresholds"],
                    "new": request.alert_thresholds
                }
                
                # Merge with existing thresholds
                for metric, thresholds in request.alert_thresholds.items():
                    if metric not in self.config["alert_thresholds"]:
                        self.config["alert_thresholds"][metric] = {}
                    
                    for level, value in thresholds.items():
                        self.config["alert_thresholds"][metric][level] = value
            
            # Update excluded components
            if request.excluded_components is not None:
                changes_applied["excluded_components"] = {
                    "old": self.config["excluded_components"],
                    "new": request.excluded_components
                }
                self.config["excluded_components"] = request.excluded_components
            
            # Save updated configuration
            self._save_config()
            
            return HealthMonitorConfigResponse(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                current_config=self.config,
                changes_applied=changes_applied,
                restart_required=restart_required
            )
        
        except Exception as e:
            error_info = classify_error(e)
            log_error_to_memory(
                error=e,
                error_type=error_info.error_type,
                source="health_monitor.update_config",
                details={"request": request.dict() if request else None}
            )
            logger.error(f"Error updating health monitor config: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Config update failed: {str(e)}")

    # Self-healing action implementations
    
    async def _restart_agent(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Restart an agent component."""
        # This is a placeholder implementation
        # In a real system, this would restart the agent process
        return True, f"Agent {component['component_id']} restarted successfully"

    async def _clear_agent_cache(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Clear agent cache."""
        # This is a placeholder implementation
        # In a real system, this would clear the agent's cache
        return True, f"Cache cleared for agent {component['component_id']}"

    async def _restart_module(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Restart a module component."""
        # This is a placeholder implementation
        # In a real system, this would restart the module
        return True, f"Module {component['component_id']} restarted successfully"

    async def _rollback_module(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Rollback a module to a previous version."""
        # This is a placeholder implementation
        # In a real system, this would rollback the module to a previous version
        return True, f"Module {component['component_id']} rolled back to previous version"

    async def _reset_route_connection(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Reset route connection."""
        # This is a placeholder implementation
        # In a real system, this would reset the route's connection
        return True, f"Connection reset for route {component['component_id']}"

    async def _clear_db_cache(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Clear database cache."""
        # This is a placeholder implementation
        # In a real system, this would clear the database cache
        return True, f"Cache cleared for database {component['component_id']}"

    async def _reset_db_connection(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Reset database connection."""
        # This is a placeholder implementation
        # In a real system, this would reset the database connection
        return True, f"Connection reset for database {component['component_id']}"

    async def _clear_memory_cache(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Clear memory cache."""
        # This is a placeholder implementation
        # In a real system, this would clear the memory cache
        return True, f"Cache cleared for memory {component['component_id']}"

    async def _rollback_memory(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Rollback memory to a previous state."""
        # This is a placeholder implementation
        # In a real system, this would rollback memory to a previous state
        return True, f"Memory {component['component_id']} rolled back to previous state"

    async def _restart_system_component(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Restart a system component."""
        # This is a placeholder implementation
        # In a real system, this would restart the system component
        return True, f"System component {component['component_id']} restarted successfully"

    async def _scale_system_resources(self, component: Dict, issue_description: str, auto_approve: bool) -> Tuple[bool, str]:
        """Scale system resources."""
        # This is a placeholder implementation
        # In a real system, this would scale system resources
        return True, f"Resources scaled for system component {component['component_id']}"


# Singleton instance
_health_monitor_instance = None

def get_health_monitor() -> HealthMonitor:
    """Get the singleton instance of the HealthMonitor."""
    global _health_monitor_instance
    if _health_monitor_instance is None:
        _health_monitor_instance = HealthMonitor()
    return _health_monitor_instance
