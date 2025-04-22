#!/usr/bin/env python3
"""
System tests for verifying merged changes in Promethios v1.0.2
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class TestMergedChanges(unittest.TestCase):
    """Test suite for verifying merged changes in v1.0.2 release"""
    
    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.system_dir = self.project_root / "system"
        self.schemas_dir = self.project_root / "schemas"
        self.app_dir = self.project_root / "app"
        
    def test_agent_manifest(self):
        """Test that agent_manifest.json has all required fields"""
        manifest_path = self.config_dir / "agent_manifest.json"
        self.assertTrue(manifest_path.exists(), "agent_manifest.json not found")
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Check system version
        self.assertEqual(manifest.get("system_version"), "v1.0.2", 
                         "System version should be v1.0.2")
        
        # Check loop hardening flag
        self.assertTrue(manifest.get("loop_hardening"), 
                        "loop_hardening flag should be true")
        
        # Check agent schema compliance
        compliance = manifest.get("agent_schema_compliance", {})
        self.assertEqual(compliance.get("phase"), "2/2", 
                         "Schema compliance phase should be 2/2")
        self.assertEqual(compliance.get("core_agents"), "100% SDK + schema compliant", 
                         "Core agents should be 100% SDK + schema compliant")
        self.assertEqual(compliance.get("compliance_status"), "FULL", 
                         "Compliance status should be FULL")
        self.assertTrue(compliance.get("schema_registry_enabled"), 
                        "Schema registry should be enabled")
        
        # Check all agents are SDK compliant and schema validated
        for agent in manifest.get("agents", []):
            self.assertTrue(agent.get("sdk_compliant"), 
                           f"Agent {agent.get('name')} should be SDK compliant")
            self.assertTrue(agent.get("schema_validated"), 
                           f"Agent {agent.get('name')} should be schema validated")
        
        # Check schema validation components
        validation = manifest.get("schema_validation", {})
        components = validation.get("components", {})
        required_components = [
            "loop_lineage_export", "loop_map_visualization", "visual_settings",
            "rerun_decision", "md_export_format", "html_export_format",
            "loop_trace", "belief_versioning"
        ]
        for component in required_components:
            self.assertEqual(components.get(component), "validated", 
                            f"Component {component} should be validated")
    
    def test_system_status(self):
        """Test that system/status.json has all required fields"""
        status_path = self.system_dir / "status.json"
        self.assertTrue(status_path.exists(), "status.json not found")
        
        with open(status_path, 'r') as f:
            status = json.load(f)
        
        # Check system version
        system_status = status.get("system_status", {})
        self.assertEqual(system_status.get("version"), "v1.0.2", 
                         "System version should be v1.0.2")
        
        # Check root level fields
        self.assertEqual(status.get("system_version"), "v1.0.2", 
                         "System version should be v1.0.2")
        self.assertEqual(status.get("agent_core"), "100% SDK + schema-compliant", 
                         "Agent core should be 100% SDK + schema-compliant")
        self.assertTrue(status.get("loop_hardening"), 
                        "loop_hardening flag should be true")
        self.assertTrue(status.get("schema_registry_enabled"), 
                        "Schema registry should be enabled")
        self.assertEqual(status.get("compliance_status"), "FULL", 
                         "Compliance status should be FULL")
    
    def test_loop_trace_schema(self):
        """Test that loop_trace.schema.json has all required fields"""
        schema_path = self.app_dir / "loop" / "debug" / "loop_trace.schema.json"
        self.assertTrue(schema_path.exists(), "loop_trace.schema.json not found")
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Check required properties
        properties = schema.get("properties", {})
        required_properties = [
            "belief_versions", "audit_info", "snapshots", "project_locks",
            "depth", "orchestrator_mode", "summary", "metrics"
        ]
        for prop in required_properties:
            self.assertIn(prop, properties, f"Property {prop} should exist in loop_trace.schema.json")
        
        # Check belief_versions structure
        belief_versions = properties.get("belief_versions", {})
        self.assertEqual(belief_versions.get("type"), "array", 
                         "belief_versions should be an array")
        
        # Check audit_info structure
        audit_info = properties.get("audit_info", {})
        audit_properties = audit_info.get("properties", {})
        required_audit_fields = [
            "audit_id", "overall_score", "belief_consistency_score", 
            "memory_integrity_score"
        ]
        for field in required_audit_fields:
            self.assertIn(field, audit_properties, 
                         f"Field {field} should exist in audit_info")
    
    def test_release_manifest(self):
        """Test that release_manifest_v1.0.2.md exists"""
        manifest_path = self.project_root / "release_manifest_v1.0.2.md"
        self.assertTrue(manifest_path.exists(), "release_manifest_v1.0.2.md not found")
        
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Check content includes required sections
        required_sections = [
            "Modules Upgraded", "Schema Diffs", "Performance Notes", 
            "Trust Model Integrity Confirmation"
        ]
        for section in required_sections:
            self.assertIn(section, content, 
                         f"Section {section} should exist in release manifest")
    
    def test_schema_validation_components(self):
        """Test that all schema validation components exist"""
        # Check schema files
        schema_files = [
            "loop_lineage_export.schema.json",
            "loop_map_visualization.schema.json",
            "visual_settings.schema.json",
            "md_export_format.schema.json",
            "html_export_format.schema.json"
        ]
        for file in schema_files:
            path = self.schemas_dir / file
            self.assertTrue(path.exists(), f"Schema file {file} not found")
        
        # Check implementation files
        module_files = [
            "app/modules/schema_compliance/visual_settings_validator.py",
            "app/modules/schema_compliance/md_export_validator.py",
            "app/modules/schema_compliance/html_export_validator.py",
            "app/modules/schema_compliance/schema_validation.py",
            "app/schemas/rerun_decision.py"
        ]
        for file in module_files:
            path = self.project_root / file
            self.assertTrue(path.exists(), f"Module file {file} not found")
    
    def test_loop_hardening_components(self):
        """Test that all loop hardening components exist"""
        component_files = [
            "app/modules/auditor_agent.py",
            "app/modules/belief_versioning.py",
            "app/modules/loop_hardening_integration.py",
            "app/modules/summary_realism_scorer.py",
            "app/loop/debug/schema_compatibility_checker.py"
        ]
        for file in component_files:
            path = self.project_root / file
            self.assertTrue(path.exists(), f"Component file {file} not found")

if __name__ == "__main__":
    unittest.main()
