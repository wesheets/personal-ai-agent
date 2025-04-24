"""
Health Monitor Test Script

This script tests the Health Monitor implementation by:
1. Running the manifest update script to register the health monitor components
2. Creating a test client to make requests to the health monitor endpoints
3. Verifying the responses from the health monitor endpoints
"""

import os
import sys
import json
import unittest
from datetime import datetime
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the manifest update script
from health_monitor_manifest_update import update_health_monitor_manifest

# Import the main FastAPI app
from app.main import app

# Import health monitor schemas
from app.schemas.health_monitor_schema import (
    HealthStatus, ComponentType, HealthCheckRequest, PredictiveMaintenanceRequest,
    SelfHealingRequest, SelfHealingAction, HealthMonitorConfigRequest
)

class TestHealthMonitor(unittest.TestCase):
    """Test case for the Health Monitor implementation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Update the manifest with health monitor information
        update_result = update_health_monitor_manifest()
        assert update_result, "Failed to update system manifest"
        
        # Create a test client
        cls.client = TestClient(app)
        
        print("✅ Test environment set up successfully")
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        print("\n🔍 Testing health check endpoint...")
        
        # Create a health check request
        request_data = {
            "component_id": None,
            "component_type": None,
            "include_metrics": True,
            "include_recommendations": True
        }
        
        # Make a request to the health check endpoint
        response = self.client.post("/health/check", json=request_data)
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        response_data = response.json()
        
        # Check the response structure
        self.assertIn("request_id", response_data, "Response missing request_id")
        self.assertIn("timestamp", response_data, "Response missing timestamp")
        self.assertIn("summary", response_data, "Response missing summary")
        self.assertIn("components", response_data, "Response missing components")
        
        # Check the summary structure
        summary = response_data["summary"]
        self.assertIn("overall_status", summary, "Summary missing overall_status")
        self.assertIn("component_statuses", summary, "Summary missing component_statuses")
        self.assertIn("critical_issues_count", summary, "Summary missing critical_issues_count")
        self.assertIn("warning_issues_count", summary, "Summary missing warning_issues_count")
        self.assertIn("healthy_components_count", summary, "Summary missing healthy_components_count")
        self.assertIn("total_components_count", summary, "Summary missing total_components_count")
        
        print("✅ Health check endpoint test passed")
    
    def test_component_health_check_endpoint(self):
        """Test the component health check endpoint."""
        print("\n🔍 Testing component health check endpoint...")
        
        # Make a request to the component health check endpoint
        response = self.client.get("/health/check/system_core")
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        response_data = response.json()
        
        # Check the response structure
        self.assertIn("request_id", response_data, "Response missing request_id")
        self.assertIn("timestamp", response_data, "Response missing timestamp")
        self.assertIn("summary", response_data, "Response missing summary")
        self.assertIn("components", response_data, "Response missing components")
        
        # Check that the component is in the response
        components = response_data["components"]
        self.assertTrue(len(components) > 0, "No components in response")
        
        # Check the first component
        component = components[0]
        self.assertEqual(component["component_id"], "system_core", "Wrong component ID")
        
        print("✅ Component health check endpoint test passed")
    
    def test_system_health_endpoint(self):
        """Test the system health endpoint."""
        print("\n🔍 Testing system health endpoint...")
        
        # Make a request to the system health endpoint
        response = self.client.get("/health/system")
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        response_data = response.json()
        
        # Check the response structure
        self.assertIn("request_id", response_data, "Response missing request_id")
        self.assertIn("timestamp", response_data, "Response missing timestamp")
        self.assertIn("summary", response_data, "Response missing summary")
        self.assertIn("components", response_data, "Response missing components")
        
        # Check that there are multiple components in the response
        components = response_data["components"]
        self.assertTrue(len(components) > 1, "Not enough components in response")
        
        print("✅ System health endpoint test passed")
    
    def test_predictive_maintenance_endpoint(self):
        """Test the predictive maintenance endpoint."""
        print("\n🔍 Testing predictive maintenance endpoint...")
        
        # Create a predictive maintenance request
        request_data = {
            "component_id": None,
            "component_type": None,
            "time_horizon_hours": 24,
            "confidence_threshold": 0.7
        }
        
        # Make a request to the predictive maintenance endpoint
        response = self.client.post("/health/maintenance/predict", json=request_data)
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        response_data = response.json()
        
        # Check the response structure
        self.assertIn("request_id", response_data, "Response missing request_id")
        self.assertIn("timestamp", response_data, "Response missing timestamp")
        self.assertIn("predictions", response_data, "Response missing predictions")
        self.assertIn("total_predictions_count", response_data, "Response missing total_predictions_count")
        
        print("✅ Predictive maintenance endpoint test passed")
    
    def test_component_maintenance_endpoint(self):
        """Test the component maintenance endpoint."""
        print("\n🔍 Testing component maintenance endpoint...")
        
        # Make a request to the component maintenance endpoint
        response = self.client.get("/health/maintenance/predict/system_core")
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        response_data = response.json()
        
        # Check the response structure
        self.assertIn("request_id", response_data, "Response missing request_id")
        self.assertIn("timestamp", response_data, "Response missing timestamp")
        self.assertIn("predictions", response_data, "Response missing predictions")
        self.assertIn("total_predictions_count", response_data, "Response missing total_predictions_count")
        
        print("✅ Component maintenance endpoint test passed")
    
    def test_self_healing_endpoint(self):
        """Test the self-healing endpoint."""
        print("\n🔍 Testing self-healing endpoint...")
        
        # Create a self-healing request
        request_data = {
            "component_id": "system_core",
            "issue_description": "Test issue for self-healing",
            "suggested_actions": ["clear_cache", "notify_admin"],
            "auto_approve": False,
            "max_impact_level": "low"
        }
        
        # Make a request to the self-healing endpoint
        response = self.client.post("/health/healing", json=request_data)
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        response_data = response.json()
        
        # Check the response structure
        self.assertIn("request_id", response_data, "Response missing request_id")
        self.assertIn("component_id", response_data, "Response missing component_id")
        self.assertIn("actions_performed", response_data, "Response missing actions_performed")
        
        print("✅ Self-healing endpoint test passed")
    
    def test_config_endpoints(self):
        """Test the configuration endpoints."""
        print("\n🔍 Testing configuration endpoints...")
        
        # Test GET config endpoint
        get_response = self.client.get("/health/config")
        
        # Check the response
        self.assertEqual(get_response.status_code, 200, f"Expected status code 200, got {get_response.status_code}")
        
        # Parse the response
        get_response_data = get_response.json()
        
        # Check the response structure
        self.assertIn("current_config", get_response_data, "Response missing current_config")
        
        # Create a config update request
        request_data = {
            "check_interval_seconds": 600,
            "enable_predictive_maintenance": True,
            "enable_self_healing": False
        }
        
        # Make a request to the config update endpoint
        post_response = self.client.post("/health/config", json=request_data)
        
        # Check the response
        self.assertEqual(post_response.status_code, 200, f"Expected status code 200, got {post_response.status_code}")
        
        # Parse the response
        post_response_data = post_response.json()
        
        # Check the response structure
        self.assertIn("request_id", post_response_data, "Response missing request_id")
        self.assertIn("current_config", post_response_data, "Response missing current_config")
        self.assertIn("changes_applied", post_response_data, "Response missing changes_applied")
        
        # Check that the changes were applied
        self.assertEqual(
            post_response_data["current_config"]["check_interval_seconds"],
            request_data["check_interval_seconds"],
            "Config change not applied"
        )
        
        print("✅ Configuration endpoints test passed")
    
    def test_main_app_integration(self):
        """Test that the health monitor routes are properly integrated with the main app."""
        print("\n🔍 Testing main app integration...")
        
        # Get the OpenAPI schema
        response = self.client.get("/openapi.json")
        
        # Check the response
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse the response
        schema = response.json()
        
        # Check that the health monitor paths are in the schema
        paths = schema.get("paths", {})
        self.assertIn("/health/check", paths, "Health check path not in OpenAPI schema")
        self.assertIn("/health/system", paths, "System health path not in OpenAPI schema")
        self.assertIn("/health/maintenance/predict", paths, "Predictive maintenance path not in OpenAPI schema")
        self.assertIn("/health/healing", paths, "Self-healing path not in OpenAPI schema")
        self.assertIn("/health/config", paths, "Config path not in OpenAPI schema")
        
        print("✅ Main app integration test passed")

if __name__ == "__main__":
    unittest.main()
