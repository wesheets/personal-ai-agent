"""
System Integration Module for Self-Evolving Cognitive Stability Layer

This module implements the system hooks and integration for the self-evolving
cognitive stability layer, connecting the Rebuilder Agent, Project Manifest System,
and Loop CI Test Runner into a cohesive system.

The integration provides:
1. Hooks into the loop execution system
2. Automatic stability checks after loop completion
3. Scheduled CI test runs
4. Coordination of rebuild operations
5. Event logging and notification
"""

import os
import json
import logging
import datetime
import threading
import time
from typing import Dict, List, Any, Optional, Tuple

# Import components
from app.modules.project_manifest import (
    load_manifest,
    save_manifest,
    get_module,
    update_ci_result,
    mark_for_rebuild,
    get_manifest_summary,
    update_stability_score,
    update_rebuild_check
)

from app.modules.loop_ci_test_runner import (
    run_tests,
    get_latest_result,
    get_result_history
)

# Import for rebuilder agent
from app.plugins.agents.rebuilder.rebuilder import run_agent as run_rebuilder_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
STABILITY_CHECK_INTERVAL = 3600  # 1 hour
CI_TEST_INTERVAL = 86400  # 24 hours
INTEGRATION_CONFIG_PATH = "/home/ubuntu/repo/personal-ai-agent/app/config/stability_integration.json"

class StabilityIntegration:
    """Class to manage integration of stability components."""
    
    def __init__(self, project_id: str):
        """
        Initialize stability integration.
        
        Args:
            project_id: ID of the project
        """
        self.project_id = project_id
        self.config = self._load_config()
        self.stability_check_thread = None
        self.ci_test_thread = None
        self.running = False
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load integration configuration.
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(INTEGRATION_CONFIG_PATH):
            try:
                with open(INTEGRATION_CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded integration configuration from {INTEGRATION_CONFIG_PATH}")
                return config
            except Exception as e:
                logger.error(f"Error loading integration configuration: {e}")
        
        # Default configuration
        config = {
            "stability_check_interval": STABILITY_CHECK_INTERVAL,
            "ci_test_interval": CI_TEST_INTERVAL,
            "orchestrator_mode": "BALANCED",
            "auto_rebuild": True,
            "notification_enabled": True,
            "notification_threshold": 0.7,
            "ci_test_modules": []  # Empty list means all modules
        }
        
        # Save default configuration
        try:
            os.makedirs(os.path.dirname(INTEGRATION_CONFIG_PATH), exist_ok=True)
            with open(INTEGRATION_CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Created default integration configuration at {INTEGRATION_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error creating default integration configuration: {e}")
        
        return config
    
    def _save_config(self) -> bool:
        """
        Save integration configuration.
        
        Returns:
            Boolean indicating success
        """
        try:
            os.makedirs(os.path.dirname(INTEGRATION_CONFIG_PATH), exist_ok=True)
            with open(INTEGRATION_CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved integration configuration to {INTEGRATION_CONFIG_PATH}")
            return True
        except Exception as e:
            logger.error(f"Error saving integration configuration: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update integration configuration.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            Boolean indicating success
        """
        for key, value in updates.items():
            self.config[key] = value
        
        return self._save_config()
    
    def start_background_tasks(self) -> bool:
        """
        Start background tasks for stability checks and CI tests.
        
        Returns:
            Boolean indicating success
        """
        if self.running:
            logger.warning("Background tasks already running")
            return False
        
        self.running = True
        
        # Start stability check thread
        self.stability_check_thread = threading.Thread(
            target=self._stability_check_loop,
            daemon=True
        )
        self.stability_check_thread.start()
        
        # Start CI test thread
        self.ci_test_thread = threading.Thread(
            target=self._ci_test_loop,
            daemon=True
        )
        self.ci_test_thread.start()
        
        logger.info("Started background tasks for stability checks and CI tests")
        return True
    
    def stop_background_tasks(self) -> bool:
        """
        Stop background tasks.
        
        Returns:
            Boolean indicating success
        """
        if not self.running:
            logger.warning("Background tasks not running")
            return False
        
        self.running = False
        
        # Wait for threads to terminate
        if self.stability_check_thread:
            self.stability_check_thread.join(timeout=5)
        
        if self.ci_test_thread:
            self.ci_test_thread.join(timeout=5)
        
        logger.info("Stopped background tasks for stability checks and CI tests")
        return True
    
    def _stability_check_loop(self):
        """Background loop for stability checks."""
        logger.info("Starting stability check loop")
        
        while self.running:
            try:
                # Run stability check
                self.run_stability_check()
                
                # Sleep until next check
                interval = self.config.get("stability_check_interval", STABILITY_CHECK_INTERVAL)
                time.sleep(interval)
            
            except Exception as e:
                logger.error(f"Error in stability check loop: {e}")
                time.sleep(60)  # Sleep for a minute before retrying
    
    def _ci_test_loop(self):
        """Background loop for CI tests."""
        logger.info("Starting CI test loop")
        
        while self.running:
            try:
                # Run CI tests
                self.run_ci_tests()
                
                # Sleep until next test run
                interval = self.config.get("ci_test_interval", CI_TEST_INTERVAL)
                time.sleep(interval)
            
            except Exception as e:
                logger.error(f"Error in CI test loop: {e}")
                time.sleep(60)  # Sleep for a minute before retrying
    
    def run_stability_check(self) -> Dict[str, Any]:
        """
        Run a stability check using the Rebuilder Agent.
        
        Returns:
            Result of the stability check
        """
        logger.info(f"Running stability check for project: {self.project_id}")
        
        try:
            # Create context for Rebuilder Agent
            context = {
                "project_id": self.project_id,
                "orchestrator_mode": self.config.get("orchestrator_mode", "BALANCED"),
                "loop_id": f"stability-check-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            }
            
            # Run Rebuilder Agent
            result = run_rebuilder_agent(context)
            
            # Log result
            if result.get("needs_rebuild", False):
                logger.warning(f"Stability check detected need for rebuild, score: {result.get('stability_score', 0.0)}")
                
                # Trigger rebuild if auto_rebuild is enabled
                if self.config.get("auto_rebuild", True):
                    self.trigger_rebuild(result)
                
                # Send notification if enabled
                if (self.config.get("notification_enabled", True) and 
                    result.get("stability_score", 1.0) < self.config.get("notification_threshold", 0.7)):
                    self.send_notification(result)
            else:
                logger.info(f"Stability check passed, score: {result.get('stability_score', 1.0)}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error running stability check: {e}")
            return {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
    
    def run_ci_tests(self, modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run CI tests for the project.
        
        Args:
            modules: Optional list of module names to test
            
        Returns:
            Result of the CI tests
        """
        logger.info(f"Running CI tests for project: {self.project_id}")
        
        try:
            # Use modules from config if not specified
            if not modules:
                modules = self.config.get("ci_test_modules", [])
            
            # Run CI tests
            result = run_tests(self.project_id, modules)
            
            # Log result
            if result.get("status") == "passed":
                logger.info(f"CI tests passed, score: {result.get('ci_score', 1.0)}")
            else:
                logger.warning(f"CI tests failed, score: {result.get('ci_score', 0.0)}")
                
                # Run stability check after failed CI tests
                self.run_stability_check()
            
            return result
        
        except Exception as e:
            logger.error(f"Error running CI tests: {e}")
            return {
                "project_id": self.project_id,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
    
    def trigger_rebuild(self, stability_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger rebuild based on stability check result.
        
        Args:
            stability_result: Result of stability check
            
        Returns:
            Result of rebuild operation
        """
        logger.info(f"Triggering rebuild for project: {self.project_id}")
        
        try:
            # In a real implementation, this would call the Orchestrator API
            # to trigger a rebuild-mode loop
            
            # For now, we'll just return a mock result
            rebuild_id = f"rebuild-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            result = {
                "rebuild_id": rebuild_id,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "project_id": self.project_id,
                "orchestrator_mode": self.config.get("orchestrator_mode", "BALANCED"),
                "status": "triggered",
                "stability_score": stability_result.get("stability_score", 0.0),
                "rebuild_events": stability_result.get("rebuild_events", [])
            }
            
            logger.info(f"Rebuild triggered with ID: {rebuild_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error triggering rebuild: {e}")
            return {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
    
    def send_notification(self, stability_result: Dict[str, Any]) -> bool:
        """
        Send notification about stability issues.
        
        Args:
            stability_result: Result of stability check
            
        Returns:
            Boolean indicating success
        """
        logger.info(f"Sending notification for project: {self.project_id}")
        
        try:
            # In a real implementation, this would send a notification
            # via email, Slack, or other channels
            
            # For now, we'll just log the notification
            notification = {
                "project_id": self.project_id,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "stability_score": stability_result.get("stability_score", 0.0),
                "needs_rebuild": stability_result.get("needs_rebuild", False),
                "rebuild_events": stability_result.get("rebuild_events", []),
                "recommendations": stability_result.get("recommendations", [])
            }
            
            logger.warning(f"STABILITY NOTIFICATION: {json.dumps(notification, indent=2)}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

# Hook functions for integration with loop system

def post_loop_stability_hook(loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hook to run after loop completion to check stability.
    
    Args:
        loop_data: Data from the completed loop
        
    Returns:
        Result of stability check
    """
    logger.info(f"Post-loop stability hook triggered for loop: {loop_data.get('loop_id')}")
    
    try:
        # Extract project ID from loop data
        project_id = loop_data.get("project_id", "default")
        
        # Create stability integration
        integration = StabilityIntegration(project_id)
        
        # Run stability check
        result = integration.run_stability_check()
        
        # Add to loop data
        loop_data["stability_check_result"] = result
        
        return result
    
    except Exception as e:
        logger.error(f"Error in post-loop stability hook: {e}")
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

def scheduled_ci_hook(project_id: str) -> Dict[str, Any]:
    """
    Hook for scheduled CI tests.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Result of CI tests
    """
    logger.info(f"Scheduled CI hook triggered for project: {project_id}")
    
    try:
        # Create stability integration
        integration = StabilityIntegration(project_id)
        
        # Run CI tests
        result = integration.run_ci_tests()
        
        return result
    
    except Exception as e:
        logger.error(f"Error in scheduled CI hook: {e}")
        return {
            "project_id": project_id,
            "error": str(e),
            "status": "error",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

def rebuild_trigger_hook(project_id: str, stability_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hook to trigger rebuild.
    
    Args:
        project_id: ID of the project
        stability_result: Result of stability check
        
    Returns:
        Result of rebuild operation
    """
    logger.info(f"Rebuild trigger hook triggered for project: {project_id}")
    
    try:
        # Create stability integration
        integration = StabilityIntegration(project_id)
        
        # Trigger rebuild
        result = integration.trigger_rebuild(stability_result)
        
        return result
    
    except Exception as e:
        logger.error(f"Error in rebuild trigger hook: {e}")
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

def start_stability_monitoring(project_id: str) -> bool:
    """
    Start stability monitoring for a project.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Boolean indicating success
    """
    logger.info(f"Starting stability monitoring for project: {project_id}")
    
    try:
        # Create stability integration
        integration = StabilityIntegration(project_id)
        
        # Start background tasks
        success = integration.start_background_tasks()
        
        return success
    
    except Exception as e:
        logger.error(f"Error starting stability monitoring: {e}")
        return False

def stop_stability_monitoring(project_id: str) -> bool:
    """
    Stop stability monitoring for a project.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Boolean indicating success
    """
    logger.info(f"Stopping stability monitoring for project: {project_id}")
    
    try:
        # Create stability integration
        integration = StabilityIntegration(project_id)
        
        # Stop background tasks
        success = integration.stop_background_tasks()
        
        return success
    
    except Exception as e:
        logger.error(f"Error stopping stability monitoring: {e}")
        return False

def update_monitoring_config(project_id: str, config_updates: Dict[str, Any]) -> bool:
    """
    Update monitoring configuration for a project.
    
    Args:
        project_id: ID of the project
        config_updates: Dictionary of configuration updates
        
    Returns:
        Boolean indicating success
    """
    logger.info(f"Updating monitoring configuration for project: {project_id}")
    
    try:
        # Create stability integration
        integration = StabilityIntegration(project_id)
        
        # Update configuration
        success = integration.update_config(config_updates)
        
        return success
    
    except Exception as e:
        logger.error(f"Error updating monitoring configuration: {e}")
        return False
