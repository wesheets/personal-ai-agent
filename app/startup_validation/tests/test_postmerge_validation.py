#!/usr/bin/env python3
"""
Test script for the Post-Merge Surface Validation system.

This script tests the functionality of the post-merge validation system
by creating a test environment and running the validation.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import logging
from unittest.mock import patch

# Add parent directory to path to import validation modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.startup_validation.postmerge_validator import validate_cognitive_surfaces, create_postmerge_memory_tag
from app.startup_validation.utils.health_scorer import calculate_overall_health_score

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_postmerge_validation')

class TestPostMergeValidation(unittest.TestCase):
    """Test cases for the Post-Merge Surface Validation system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        logger.info(f"Created test directory: {self.test_dir}")
        
        # Create necessary directories
        os.makedirs(os.path.join(self.test_dir, 'system'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'app', 'agents'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'app', 'modules'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'app', 'schemas'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'frontend', 'components'), exist_ok=True)
        
        # Create test ACI file
        self.aci_data = {
            "agents": [
                {
                    "id": "test-agent",
                    "name": "TestAgent",
                    "file": "test_agent.py",
                    "description": "Test agent for validation",
                    "status": "active"
                },
                {
                    "id": "missing-agent",
                    "name": "MissingAgent",
                    "file": "missing_agent.py",
                    "description": "Missing agent for validation testing",
                    "status": "active"
                }
            ]
        }
        
        with open(os.path.join(self.test_dir, 'system', 'agent_cognition_index.json'), 'w') as f:
            json.dump(self.aci_data, f, indent=2)
        
        # Create test PICE file
        self.pice_data = {
            "modules": [
                {
                    "id": "test.module",
                    "file": "test_module.py",
                    "description": "Test module for validation",
                    "status": "active"
                },
                {
                    "id": "missing.module",
                    "file": "missing_module.py",
                    "description": "Missing module for validation testing",
                    "status": "active"
                }
            ],
            "schemas": [
                {
                    "id": "TestSchema",
                    "file": "test_schema.json",
                    "description": "Test schema for validation",
                    "status": "active"
                },
                {
                    "id": "MissingSchema",
                    "file": "missing_schema.json",
                    "description": "Missing schema for validation testing",
                    "status": "active"
                }
            ],
            "endpoints": [
                {
                    "path": "/api/test",
                    "method": "GET",
                    "description": "Test endpoint for validation",
                    "status": "active"
                }
            ],
            "components": [
                {
                    "id": "TestComponent",
                    "path": "TestComponent.jsx",
                    "description": "Test component for validation",
                    "status": "active"
                },
                {
                    "id": "MissingComponent",
                    "path": "MissingComponent.jsx",
                    "description": "Missing component for validation testing",
                    "status": "active"
                }
            ]
        }
        
        with open(os.path.join(self.test_dir, 'system', 'system_consciousness_index.json'), 'w') as f:
            json.dump(self.pice_data, f, indent=2)
        
        # Create test agent file
        with open(os.path.join(self.test_dir, 'app', 'agents', 'test_agent.py'), 'w') as f:
            f.write('"""Test agent for validation."""\n\nclass TestAgent:\n    pass\n')
        
        # Create test module file
        os.makedirs(os.path.join(self.test_dir, 'app', 'modules', 'test'), exist_ok=True)
        with open(os.path.join(self.test_dir, 'app', 'modules', 'test', 'module.py'), 'w') as f:
            f.write('"""Test module for validation."""\n\ndef test_function():\n    pass\n')
        
        # Create test schema file
        with open(os.path.join(self.test_dir, 'app', 'schemas', 'test_schema.json'), 'w') as f:
            f.write('{"type": "object", "properties": {"test": {"type": "string"}}}')
        
        # Create test component file
        with open(os.path.join(self.test_dir, 'frontend', 'components', 'TestComponent.jsx'), 'w') as f:
            f.write('import React from "react";\n\nexport default function TestComponent() {\n  return <div>Test</div>;\n}\n')
        
        # Create test system status file
        self.system_status = {
            "system_health": {
                "status": "critical",
                "last_checked": "2025-04-27T14:22:49.386341",
                "memory_surface": {
                    "total_agents": 19,
                    "total_modules": 155,
                    "total_schemas": 233,
                    "total_endpoints": 0,
                    "total_components": 15,
                    "health_score": 10.1
                },
                "memory_tags": {
                    "agent_code": "agent_code_surface_aligned_20250426",
                    "agent_registry": "agent_registry_surface_finalized_20250426",
                    "aci": "aci_snapshot_verified_20250426",
                    "pice": "pice_snapshot_verified_20250426",
                    "system": "system_surface_memory_stabilized_20250426",
                    "startup_validation": "startup_surface_drift_detected_20250427"
                }
            },
            "last_startup_validation_installed": True,
            "last_startup_validation_timestamp": "2025-04-27 14:31:47",
            "current_surface_health_score": 10.1,
            "current_surface_drift_detected": True,
            "baseline_surface_drift_version": "v1.0"
        }
        
        with open(os.path.join(self.test_dir, 'system', 'status.json'), 'w') as f:
            json.dump(self.system_status, f, indent=2)
        
        # Create test system manifest file
        self.system_manifest = {
            "system_manifest": {
                "name": "Promethios Personal AI Agent",
                "version": "0.1.0",
                "deployment_phases": {
                    "phase_1": {
                        "name": "Initial System Deployment",
                        "status": "completed",
                        "completed_date": "2025-04-26",
                        "components": [
                            "Core System",
                            "Base Modules",
                            "Initial Agents"
                        ]
                    },
                    "phase_2": {
                        "name": "Cognitive Surface Stabilization",
                        "subphases": {
                            "phase_2.0": {
                                "name": "Memory Surface Creation",
                                "status": "completed",
                                "completed_date": "2025-04-26",
                                "components": [
                                    "Agent Cognition Index (ACI)",
                                    "System Consciousness Index (PICE)"
                                ]
                            },
                            "phase_2.1": {
                                "name": "Startup Surface Validation",
                                "status": "completed",
                                "completed_date": "2025-04-27",
                                "components": [
                                    "Validation System",
                                    "Drift Detection",
                                    "Health Scoring",
                                    "Memory Tagging"
                                ],
                                "notes": "Completed with Baseline Drift Acceptance (v1.0). Current health score: 10.1%. 421 drift issues detected and documented for future healing phases."
                            }
                        },
                        "status": "in_progress"
                    }
                },
                "last_updated": "2025-04-27T14:32:46",
                "last_updated_by": "Startup Validation Installation"
            }
        }
        
        with open(os.path.join(self.test_dir, 'system', 'system_manifest.json'), 'w') as f:
            json.dump(self.system_manifest, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        logger.info(f"Cleaned up test directory: {self.test_dir}")
    
    @patch('app.startup_validation.utils.memory_tagger.update_system_status')
    @patch('app.startup_validation.utils.memory_tagger.save_memory_tag_file')
    @patch('app.startup_validation.utils.drift_reporter.save_drift_report')
    def test_validation(self, mock_save_report, mock_save_tag, mock_update_status):
        """Test the post-merge validation process."""
        # Mock the save functions to avoid writing to disk
        mock_save_report.return_value = os.path.join(self.test_dir, 'logs', 'postmerge_drift_report_20250427.json')
        mock_save_tag.return_value = os.path.join(self.test_dir, 'logs', 'postmerge_surface_drift_detected_20250427.txt')
        
        # Set environment variable for base path
        os.environ["PROMETHIOS_BASE_PATH"] = self.test_dir
        
        # Run validation
        report, drift_detected = validate_cognitive_surfaces(self.test_dir)
        
        # Verify results
        self.assertTrue(drift_detected, "Drift should be detected")
        self.assertIn('surface_health_score', report, "Report should include health score")
        self.assertIn('surface_drift', report, "Report should include drift issues")
        
        # Verify health score calculation
        self.assertEqual(report['agents_health'], 50.0, "Agents health should be 50%")
        self.assertEqual(report['modules_health'], 50.0, "Modules health should be 50%")
        self.assertEqual(report['schemas_health'], 50.0, "Schemas health should be 50%")
        self.assertEqual(report['endpoints_health'], 0.0, "Endpoints health should be 0%")
        self.assertEqual(report['components_health'], 50.0, "Components health should be 50%")
        
        # Calculate expected overall health score
        expected_health_score = calculate_overall_health_score(
            50.0,  # agents
            50.0,  # modules
            50.0,  # schemas
            0.0,   # endpoints
            50.0   # components
        )
        self.assertEqual(report['surface_health_score'], expected_health_score, 
                         f"Overall health score should be {expected_health_score}%")
        
        # Verify drift issues
        self.assertEqual(len(report['surface_drift']), 5, "Should have 5 drift issues")
        
        # Verify memory tag
        memory_tag = create_postmerge_memory_tag(drift_detected)
        self.assertTrue(memory_tag.startswith('postmerge_surface_drift_detected_'), 
                        "Memory tag should indicate drift detected")
        
        # Verify mock calls
        mock_save_report.assert_called_once()
        mock_save_tag.assert_called_once()
        mock_update_status.assert_called_once()
        
        logger.info("Validation test completed successfully")
        logger.info(f"Health score: {report['surface_health_score']}%")
        logger.info(f"Drift detected: {drift_detected}")
        logger.info(f"Found {len(report['surface_drift'])} drift issues")
        
        return report, drift_detected

if __name__ == '__main__':
    unittest.main()
