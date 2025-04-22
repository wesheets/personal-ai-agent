import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the project_manifest module
from app.modules.project_manifest import (
    ensure_manifest_dir,
    get_manifest_path,
    load_manifest,
    save_manifest,
    create_manifest,
    get_module,
    add_module,
    update_module,
    delete_module,
    update_ci_result,
    update_belief_version,
    mark_for_rebuild,
    update_audit_info,
    get_modules_needing_rebuild,
    get_modules_by_belief_version,
    get_modules_by_ci_status,
    get_manifest_summary,
    list_projects,
    update_stability_score,
    update_rebuild_check
)

class TestProjectManifestSystem(unittest.TestCase):
    """Test cases for the Project Manifest System."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test manifests
        self.test_dir = tempfile.mkdtemp()
        self.original_manifest_dir = os.environ.get('PROJECT_MANIFEST_DIR')
        os.environ['PROJECT_MANIFEST_DIR'] = self.test_dir
        
        # Create a sample project manifest
        self.project_id = "test-project"
        self.manifest_path = os.path.join(self.test_dir, f"{self.project_id}.json")
        self.sample_manifest = {
            "project_id": self.project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "modules": {
                "module1": {
                    "module_name": "module1",
                    "module_type": "standard",
                    "loop_id_created": "loop-123",
                    "agent_created_by": "agent-456",
                    "belief_version": "1.0.0",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "last_audited_loop_id": "loop-789",
                    "last_ci_result": {
                        "status": "passed",
                        "ci_score": 0.95,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "needs_rebuild": False
                },
                "module2": {
                    "module_name": "module2",
                    "module_type": "plugin",
                    "loop_id_created": "loop-234",
                    "agent_created_by": "agent-567",
                    "belief_version": "1.0.0",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "last_audited_loop_id": "loop-890",
                    "last_ci_result": {
                        "status": "passed",
                        "ci_score": 0.85,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "needs_rebuild": False
                }
            },
            "last_stability_score": 0.9,
            "last_rebuild_check": {
                "timestamp": datetime.utcnow().isoformat(),
                "needs_rebuild": False,
                "rebuild_events": [],
                "recommendations": []
            }
        }
        
        with open(self.manifest_path, 'w') as f:
            json.dump(self.sample_manifest, f, indent=2)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
        # Restore original environment variable
        if self.original_manifest_dir:
            os.environ['PROJECT_MANIFEST_DIR'] = self.original_manifest_dir
        else:
            del os.environ['PROJECT_MANIFEST_DIR']

    def test_ensure_manifest_dir(self):
        """Test ensuring manifest directory exists."""
        # Remove the directory to test creation
        shutil.rmtree(self.test_dir)
        
        # Call function
        ensure_manifest_dir()
        
        # Check if directory was created
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.isdir(self.test_dir))

    def test_get_manifest_path(self):
        """Test getting manifest path."""
        path = get_manifest_path(self.project_id)
        
        self.assertEqual(path, self.manifest_path)

    def test_load_manifest_existing(self):
        """Test loading an existing manifest."""
        manifest_data = load_manifest(self.project_id)
        
        self.assertEqual(manifest_data["project_id"], self.project_id)
        self.assertEqual(len(manifest_data["modules"]), 2)

    def test_load_manifest_nonexistent(self):
        """Test loading a nonexistent manifest."""
        nonexistent_project_id = "nonexistent-project"
        
        manifest_data = load_manifest(nonexistent_project_id)
        
        self.assertEqual(manifest_data["project_id"], nonexistent_project_id)
        self.assertEqual(len(manifest_data["modules"]), 0)

    def test_save_manifest(self):
        """Test saving a manifest."""
        # Modify manifest
        manifest_data = self.sample_manifest.copy()
        manifest_data["version"] = "1.1.0"
        
        # Save manifest
        success = save_manifest(self.project_id, manifest_data)
        
        self.assertTrue(success)
        
        # Load manifest and check if changes were saved
        loaded_manifest = load_manifest(self.project_id)
        self.assertEqual(loaded_manifest["version"], "1.1.0")

    def test_create_manifest(self):
        """Test creating a new manifest."""
        new_project_id = "new-project"
        
        manifest_data = create_manifest(new_project_id)
        
        self.assertEqual(manifest_data["project_id"], new_project_id)
        self.assertEqual(len(manifest_data["modules"]), 0)
        
        # Check if file was created
        manifest_path = os.path.join(self.test_dir, f"{new_project_id}.json")
        self.assertTrue(os.path.exists(manifest_path))

    def test_get_module_existing(self):
        """Test getting an existing module."""
        module_data = get_module(self.project_id, "module1")
        
        self.assertIsNotNone(module_data)
        self.assertEqual(module_data["module_name"], "module1")

    def test_get_module_nonexistent(self):
        """Test getting a nonexistent module."""
        module_data = get_module(self.project_id, "nonexistent-module")
        
        self.assertIsNone(module_data)

    def test_add_module(self):
        """Test adding a new module."""
        new_module_name = "new-module"
        
        success = add_module(
            self.project_id,
            new_module_name,
            "loop-456",
            "agent-789",
            "1.0.0",
            "core",
            {"description": "Test module"}
        )
        
        self.assertTrue(success)
        
        # Check if module was added
        module_data = get_module(self.project_id, new_module_name)
        self.assertIsNotNone(module_data)
        self.assertEqual(module_data["module_name"], new_module_name)
        self.assertEqual(module_data["module_type"], "core")
        self.assertEqual(module_data["belief_version"], "1.0.0")
        self.assertEqual(module_data["metadata"]["description"], "Test module")

    def test_add_module_existing(self):
        """Test adding an existing module."""
        success = add_module(
            self.project_id,
            "module1",
            "loop-456",
            "agent-789",
            "1.0.0"
        )
        
        self.assertFalse(success)

    def test_update_module(self):
        """Test updating a module."""
        updates = {
            "belief_version": "2.0.0",
            "metadata": {"updated": True}
        }
        
        success = update_module(self.project_id, "module1", updates)
        
        self.assertTrue(success)
        
        # Check if module was updated
        module_data = get_module(self.project_id, "module1")
        self.assertEqual(module_data["belief_version"], "2.0.0")
        self.assertEqual(module_data["metadata"]["updated"], True)

    def test_update_module_nonexistent(self):
        """Test updating a nonexistent module."""
        updates = {
            "belief_version": "2.0.0"
        }
        
        success = update_module(self.project_id, "nonexistent-module", updates)
        
        self.assertFalse(success)

    def test_delete_module(self):
        """Test deleting a module."""
        success = delete_module(self.project_id, "module1")
        
        self.assertTrue(success)
        
        # Check if module was deleted
        module_data = get_module(self.project_id, "module1")
        self.assertIsNone(module_data)

    def test_delete_module_nonexistent(self):
        """Test deleting a nonexistent module."""
        success = delete_module(self.project_id, "nonexistent-module")
        
        self.assertFalse(success)

    def test_update_ci_result(self):
        """Test updating CI result."""
        ci_result = {
            "status": "failed",
            "ci_score": 0.3,
            "timestamp": datetime.utcnow().isoformat(),
            "failure_reason": "Test failures"
        }
        
        success = update_ci_result(self.project_id, "module1", ci_result)
        
        self.assertTrue(success)
        
        # Check if CI result was updated
        module_data = get_module(self.project_id, "module1")
        self.assertEqual(module_data["last_ci_result"]["status"], "failed")
        self.assertEqual(module_data["last_ci_result"]["ci_score"], 0.3)
        self.assertEqual(module_data["last_ci_result"]["failure_reason"], "Test failures")
        
        # Check if needs_rebuild flag was set
        self.assertTrue(module_data["needs_rebuild"])

    def test_update_belief_version(self):
        """Test updating belief version."""
        success = update_belief_version(self.project_id, "module1", "2.0.0")
        
        self.assertTrue(success)
        
        # Check if belief version was updated
        module_data = get_module(self.project_id, "module1")
        self.assertEqual(module_data["belief_version"], "2.0.0")

    def test_mark_for_rebuild(self):
        """Test marking a module for rebuild."""
        success = mark_for_rebuild(self.project_id, "module1", True, "Test reason")
        
        self.assertTrue(success)
        
        # Check if module was marked for rebuild
        module_data = get_module(self.project_id, "module1")
        self.assertTrue(module_data["needs_rebuild"])
        self.assertEqual(module_data["rebuild_reason"], "Test reason")
        
        # Test clearing rebuild flag
        success = mark_for_rebuild(self.project_id, "module1", False)
        
        self.assertTrue(success)
        
        # Check if rebuild flag was cleared
        module_data = get_module(self.project_id, "module1")
        self.assertFalse(module_data["needs_rebuild"])

    def test_update_audit_info(self):
        """Test updating audit information."""
        audit_info = {
            "audit_id": "audit-123",
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": 0.8,
            "issues": []
        }
        
        success = update_audit_info(self.project_id, "module1", "loop-999", audit_info)
        
        self.assertTrue(success)
        
        # Check if audit information was updated
        module_data = get_module(self.project_id, "module1")
        self.assertEqual(module_data["last_audited_loop_id"], "loop-999")
        self.assertEqual(module_data["last_audit_info"]["audit_id"], "audit-123")
        self.assertEqual(module_data["last_audit_info"]["overall_score"], 0.8)

    def test_get_modules_needing_rebuild(self):
        """Test getting modules needing rebuild."""
        # Mark a module for rebuild
        mark_for_rebuild(self.project_id, "module1", True)
        
        modules = get_modules_needing_rebuild(self.project_id)
        
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0], "module1")

    def test_get_modules_by_belief_version(self):
        """Test getting modules by belief version."""
        # Update belief version for one module
        update_belief_version(self.project_id, "module1", "2.0.0")
        
        modules_v1 = get_modules_by_belief_version(self.project_id, "1.0.0")
        modules_v2 = get_modules_by_belief_version(self.project_id, "2.0.0")
        
        self.assertEqual(len(modules_v1), 1)
        self.assertEqual(modules_v1[0], "module2")
        
        self.assertEqual(len(modules_v2), 1)
        self.assertEqual(modules_v2[0], "module1")

    def test_get_modules_by_ci_status(self):
        """Test getting modules by CI status."""
        # Update CI result for one module
        ci_result = {
            "status": "failed",
            "ci_score": 0.3,
            "timestamp": datetime.utcnow().isoformat(),
            "failure_reason": "Test failures"
        }
        update_ci_result(self.project_id, "module1", ci_result)
        
        modules_passed = get_modules_by_ci_status(self.project_id, "passed")
        modules_failed = get_modules_by_ci_status(self.project_id, "failed")
        
        self.assertEqual(len(modules_passed), 1)
        self.assertEqual(modules_passed[0], "module2")
        
        self.assertEqual(len(modules_failed), 1)
        self.assertEqual(modules_failed[0], "module1")

    def test_get_manifest_summary(self):
        """Test getting manifest summary."""
        # Mark a module for rebuild
        mark_for_rebuild(self.project_id, "module1", True)
        
        # Update CI result for one module
        ci_result = {
            "status": "failed",
            "ci_score": 0.3,
            "timestamp": datetime.utcnow().isoformat(),
            "failure_reason": "Test failures"
        }
        update_ci_result(self.project_id, "module2", ci_result)
        
        summary = get_manifest_summary(self.project_id)
        
        self.assertEqual(summary["project_id"], self.project_id)
        self.assertEqual(summary["total_modules"], 2)
        self.assertEqual(len(summary["modules_needing_rebuild"]), 2)  # Both modules should need rebuild now
        self.assertEqual(len(summary["modules_with_failed_ci"]), 1)
        self.assertEqual(summary["last_stability_score"], 0.9)

    def test_list_projects(self):
        """Test listing projects."""
        # Create another project
        create_manifest("another-project")
        
        projects = list_projects()
        
        self.assertGreaterEqual(len(projects), 2)
        self.assertIn(self.project_id, projects)
        self.assertIn("another-project", projects)

    def test_update_stability_score(self):
        """Test updating stability score."""
        success = update_stability_score(self.project_id, 0.7)
        
        self.assertTrue(success)
        
        # Check if stability score was updated
        manifest_data = load_manifest(self.project_id)
        self.assertEqual(manifest_data["last_stability_score"], 0.7)

    def test_update_rebuild_check(self):
        """Test updating rebuild check information."""
        rebuild_events = [
            {
                "type": "low_stability",
                "timestamp": datetime.utcnow().isoformat(),
                "stability_score": 0.3,
                "threshold": 0.6,
                "message": "System stability score (0.30) is below threshold (0.60)"
            }
        ]
        
        recommendations = [
            {
                "type": "critical_stability",
                "priority": "high",
                "message": "Critical stability issues detected (score: 0.30). Immediate rebuild recommended.",
                "action": "rebuild_system"
            }
        ]
        
        success = update_rebuild_check(self.project_id, True, rebuild_events, recommendations)
        
        self.assertTrue(success)
        
        # Check if rebuild check information was updated
        manifest_data = load_manifest(self.project_id)
        self.assertTrue(manifest_data["last_rebuild_check"]["needs_rebuild"])
        self.assertEqual(len(manifest_data["last_rebuild_check"]["rebuild_events"]), 1)
        self.assertEqual(len(manifest_data["last_rebuild_check"]["recommendations"]), 1)

if __name__ == '__main__':
    unittest.main()
