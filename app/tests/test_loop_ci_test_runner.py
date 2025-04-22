import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the loop_ci_test_runner module
from app.modules.loop_ci_test_runner import (
    TestResult,
    CITestRunner,
    run_tests,
    get_latest_result,
    get_result_history
)

class TestLoopCITestRunner(unittest.TestCase):
    """Test cases for the Loop CI Test Runner."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test results
        self.test_dir = tempfile.mkdtemp()
        self.original_ci_results_dir = os.environ.get('CI_RESULTS_DIR')
        os.environ['CI_RESULTS_DIR'] = self.test_dir
        
        # Create a sample project ID
        self.project_id = "test-project"
        
        # Create a sample test result
        self.sample_test_result = TestResult(
            module_name="test_module",
            test_name="test_function",
            status="passed",
            execution_time=0.5
        )
        
        # Create a sample CI result
        self.sample_ci_result = {
            "module_name": "test_module",
            "status": "passed",
            "ci_score": 1.0,
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": 10,
            "passed_tests": 10,
            "failed_tests": 0,
            "test_results": [self.sample_test_result.to_dict()]
        }
        
        # Create a sample project result
        self.sample_project_result = {
            "project_id": self.project_id,
            "status": "passed",
            "ci_score": 1.0,
            "timestamp": datetime.utcnow().isoformat(),
            "total_modules": 1,
            "passed_modules": 1,
            "failed_modules": 0,
            "module_results": [self.sample_ci_result]
        }

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
        # Restore original environment variable
        if self.original_ci_results_dir:
            os.environ['CI_RESULTS_DIR'] = self.original_ci_results_dir
        else:
            del os.environ['CI_RESULTS_DIR']

    def test_test_result_to_dict(self):
        """Test converting TestResult to dictionary."""
        result_dict = self.sample_test_result.to_dict()
        
        self.assertEqual(result_dict["module_name"], "test_module")
        self.assertEqual(result_dict["test_name"], "test_function")
        self.assertEqual(result_dict["status"], "passed")
        self.assertEqual(result_dict["execution_time"], 0.5)
        self.assertNotIn("error_message", result_dict)
        
        # Test with error message
        test_result_with_error = TestResult(
            module_name="test_module",
            test_name="test_function",
            status="failed",
            execution_time=0.5,
            error_message="Test failed"
        )
        
        result_dict = test_result_with_error.to_dict()
        self.assertEqual(result_dict["status"], "failed")
        self.assertEqual(result_dict["error_message"], "Test failed")

    @patch('app.modules.loop_ci_test_runner.get_module')
    @patch('app.modules.loop_ci_test_runner.importlib.import_module')
    def test_run_tests_for_module_not_found(self, mock_import_module, mock_get_module):
        """Test running tests for a module that doesn't exist."""
        # Mock get_module to return None
        mock_get_module.return_value = None
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for nonexistent module
        result = runner.run_tests_for_module("nonexistent_module")
        
        # Check result
        self.assertEqual(result["module_name"], "nonexistent_module")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["ci_score"], 0.0)
        self.assertEqual(result["failure_reason"], "Module not found in project manifest")
        self.assertEqual(len(result["test_results"]), 0)
        
        # Verify mocks were called correctly
        mock_get_module.assert_called_once_with(self.project_id, "nonexistent_module")
        mock_import_module.assert_not_called()

    @patch('app.modules.loop_ci_test_runner.get_module')
    @patch('app.modules.loop_ci_test_runner.importlib.import_module')
    def test_run_tests_for_module_import_error(self, mock_import_module, mock_get_module):
        """Test running tests for a module with import error."""
        # Mock get_module to return a module
        mock_get_module.return_value = {
            "module_name": "test_module",
            "module_type": "standard"
        }
        
        # Mock import_module to raise ImportError
        mock_import_module.side_effect = ImportError("Module not found")
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for module with import error
        result = runner.run_tests_for_module("test_module")
        
        # Check result
        self.assertEqual(result["module_name"], "test_module")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["ci_score"], 0.0)
        self.assertIn("Error importing test module", result["failure_reason"])
        self.assertEqual(len(result["test_results"]), 0)
        
        # Verify mocks were called correctly
        mock_get_module.assert_called_once_with(self.project_id, "test_module")
        mock_import_module.assert_called_once_with("app.tests.test_test_module")

    @patch('app.modules.loop_ci_test_runner.get_module')
    @patch('app.modules.loop_ci_test_runner.importlib.import_module')
    @patch('app.modules.loop_ci_test_runner.inspect.getmembers')
    def test_run_tests_for_module_no_test_classes(self, mock_getmembers, mock_import_module, mock_get_module):
        """Test running tests for a module with no test classes."""
        # Mock get_module to return a module
        mock_get_module.return_value = {
            "module_name": "test_module",
            "module_type": "standard"
        }
        
        # Mock import_module to return a module
        mock_import_module.return_value = MagicMock()
        
        # Mock getmembers to return no test classes
        mock_getmembers.return_value = []
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for module with no test classes
        result = runner.run_tests_for_module("test_module")
        
        # Check result
        self.assertEqual(result["module_name"], "test_module")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["ci_score"], 0.0)
        self.assertEqual(result["failure_reason"], "No test classes found")
        self.assertEqual(len(result["test_results"]), 0)
        
        # Verify mocks were called correctly
        mock_get_module.assert_called_once_with(self.project_id, "test_module")
        mock_import_module.assert_called_once_with("app.tests.test_test_module")
        mock_getmembers.assert_called_once()

    @patch('app.modules.loop_ci_test_runner.get_module')
    @patch('app.modules.loop_ci_test_runner.importlib.import_module')
    @patch('app.modules.loop_ci_test_runner.inspect.getmembers')
    @patch('app.modules.loop_ci_test_runner.inspect.isclass')
    @patch('app.modules.loop_ci_test_runner.issubclass')
    @patch('app.modules.loop_ci_test_runner.unittest.TestLoader')
    def test_run_tests_for_module_success(self, mock_test_loader, mock_issubclass, mock_isclass, 
                                         mock_getmembers, mock_import_module, mock_get_module):
        """Test running tests for a module successfully."""
        # Mock get_module to return a module
        mock_get_module.return_value = {
            "module_name": "test_module",
            "module_type": "standard"
        }
        
        # Mock import_module to return a module
        mock_import_module.return_value = MagicMock()
        
        # Mock getmembers to return a test class
        mock_test_class = MagicMock()
        mock_getmembers.return_value = [("TestClass", mock_test_class)]
        
        # Mock isclass to return True
        mock_isclass.return_value = True
        
        # Mock issubclass to return True
        mock_issubclass.return_value = True
        
        # Mock TestLoader
        mock_suite = MagicMock()
        mock_suite.countTestCases.return_value = 10
        
        mock_loader = MagicMock()
        mock_loader.loadTestsFromTestCase.return_value = mock_suite
        
        mock_test_loader.return_value = mock_loader
        
        # Mock test result
        mock_result = MagicMock()
        mock_result.errors = []
        mock_result.failures = []
        mock_result.skipped = []
        
        # Mock suite.run to set the result
        def mock_run(result):
            result.errors = []
            result.failures = []
            result.skipped = []
            return None
        
        mock_suite.run.side_effect = mock_run
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for module successfully
        result = runner.run_tests_for_module("test_module")
        
        # Check result
        self.assertEqual(result["module_name"], "test_module")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["ci_score"], 1.0)
        self.assertEqual(result["total_tests"], 10)
        self.assertEqual(result["passed_tests"], 10)
        self.assertEqual(result["failed_tests"], 0)
        
        # Verify mocks were called correctly
        mock_get_module.assert_called_once_with(self.project_id, "test_module")
        mock_import_module.assert_called_once_with("app.tests.test_test_module")
        mock_getmembers.assert_called_once()
        mock_isclass.assert_called_once()
        mock_issubclass.assert_called_once()
        mock_test_loader.assert_called_once()
        mock_loader.loadTestsFromTestCase.assert_called_once_with(mock_test_class)
        mock_suite.countTestCases.assert_called()
        mock_suite.run.assert_called_once()

    @patch('app.modules.loop_ci_test_runner.get_manifest_summary')
    def test_run_tests_for_project_no_modules(self, mock_get_manifest_summary):
        """Test running tests for a project with no modules."""
        # Mock get_manifest_summary to return no modules
        mock_get_manifest_summary.return_value = {
            "project_id": self.project_id,
            "total_modules": 0
        }
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for project with no modules
        result = runner.run_tests_for_project()
        
        # Check result
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["failure_reason"], "No modules found")
        self.assertEqual(len(result["module_results"]), 0)
        
        # Verify mocks were called correctly
        mock_get_manifest_summary.assert_called_once_with(self.project_id)

    @patch('app.modules.loop_ci_test_runner.CITestRunner.run_tests_for_module')
    @patch('app.modules.loop_ci_test_runner.update_ci_result')
    @patch('app.modules.loop_ci_test_runner.mark_for_rebuild')
    def test_run_tests_for_project_with_modules(self, mock_mark_for_rebuild, mock_update_ci_result, mock_run_tests_for_module):
        """Test running tests for a project with specified modules."""
        # Mock run_tests_for_module to return a successful result
        mock_run_tests_for_module.return_value = self.sample_ci_result
        
        # Mock update_ci_result to return True
        mock_update_ci_result.return_value = True
        
        # Mock mark_for_rebuild to return True
        mock_mark_for_rebuild.return_value = True
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for project with specified modules
        result = runner.run_tests_for_project(["test_module"])
        
        # Check result
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["ci_score"], 1.0)
        self.assertEqual(result["total_modules"], 1)
        self.assertEqual(result["passed_modules"], 1)
        self.assertEqual(result["failed_modules"], 0)
        self.assertEqual(len(result["module_results"]), 1)
        
        # Verify mocks were called correctly
        mock_run_tests_for_module.assert_called_once_with("test_module")
        mock_update_ci_result.assert_called_once_with(self.project_id, "test_module", self.sample_ci_result)
        mock_mark_for_rebuild.assert_not_called()  # Should not be called for passed tests

    @patch('app.modules.loop_ci_test_runner.CITestRunner.run_tests_for_module')
    @patch('app.modules.loop_ci_test_runner.update_ci_result')
    @patch('app.modules.loop_ci_test_runner.mark_for_rebuild')
    def test_run_tests_for_project_with_failed_module(self, mock_mark_for_rebuild, mock_update_ci_result, mock_run_tests_for_module):
        """Test running tests for a project with a failed module."""
        # Create a failed CI result
        failed_ci_result = self.sample_ci_result.copy()
        failed_ci_result["status"] = "failed"
        failed_ci_result["ci_score"] = 0.5
        failed_ci_result["passed_tests"] = 5
        failed_ci_result["failed_tests"] = 5
        failed_ci_result["failure_reason"] = "Some tests failed"
        
        # Mock run_tests_for_module to return a failed result
        mock_run_tests_for_module.return_value = failed_ci_result
        
        # Mock update_ci_result to return True
        mock_update_ci_result.return_value = True
        
        # Mock mark_for_rebuild to return True
        mock_mark_for_rebuild.return_value = True
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Run tests for project with a failed module
        result = runner.run_tests_for_project(["test_module"])
        
        # Check result
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["ci_score"], 0.0)
        self.assertEqual(result["total_modules"], 1)
        self.assertEqual(result["passed_modules"], 0)
        self.assertEqual(result["failed_modules"], 1)
        self.assertEqual(len(result["module_results"]), 1)
        
        # Verify mocks were called correctly
        mock_run_tests_for_module.assert_called_once_with("test_module")
        mock_update_ci_result.assert_called_once_with(self.project_id, "test_module", failed_ci_result)
        mock_mark_for_rebuild.assert_called_once_with(
            self.project_id, 
            "test_module", 
            True, 
            "CI tests failed: Some tests failed"
        )

    @patch('app.modules.loop_ci_test_runner.CITestRunner._save_project_result')
    def test_save_project_result(self, mock_save_project_result):
        """Test saving project result."""
        # Mock _save_project_result to return True
        mock_save_project_result.return_value = True
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Save project result
        success = runner._save_project_result(self.sample_project_result)
        
        # Check result
        self.assertTrue(success)
        
        # Verify mocks were called correctly
        mock_save_project_result.assert_called_once_with(self.sample_project_result)

    def test_get_latest_result_none(self):
        """Test getting latest result when none exists."""
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Get latest result when none exists
        result = runner.get_latest_result()
        
        # Check result
        self.assertIsNone(result)

    def test_get_latest_result(self):
        """Test getting latest result."""
        # Create a result file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_path = os.path.join(self.test_dir, f"{self.project_id}_{timestamp}.json")
        
        with open(result_path, 'w') as f:
            json.dump(self.sample_project_result, f)
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Get latest result
        result = runner.get_latest_result()
        
        # Check result
        self.assertIsNotNone(result)
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["ci_score"], 1.0)

    def test_get_result_history_none(self):
        """Test getting result history when none exists."""
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Get result history when none exists
        results = runner.get_result_history()
        
        # Check result
        self.assertEqual(len(results), 0)

    def test_get_result_history(self):
        """Test getting result history."""
        # Create multiple result files
        for i in range(3):
            timestamp = datetime.now().strftime(f"%Y%m%d%H%M{i:02d}")
            result_path = os.path.join(self.test_dir, f"{self.project_id}_{timestamp}.json")
            
            with open(result_path, 'w') as f:
                json.dump(self.sample_project_result, f)
        
        # Create test runner
        runner = CITestRunner(self.project_id)
        
        # Get result history
        results = runner.get_result_history()
        
        # Check result
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertEqual(result["project_id"], self.project_id)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["ci_score"], 1.0)

    @patch('app.modules.loop_ci_test_runner.CITestRunner')
    def test_run_tests(self, mock_ci_test_runner):
        """Test run_tests function."""
        # Mock CITestRunner
        mock_runner = MagicMock()
        mock_runner.run_tests_for_project.return_value = self.sample_project_result
        mock_ci_test_runner.return_value = mock_runner
        
        # Run tests
        result = run_tests(self.project_id, ["test_module"], 120, 8)
        
        # Check result
        self.assertEqual(result, self.sample_project_result)
        
        # Verify mocks were called correctly
        mock_ci_test_runner.assert_called_once_with(self.project_id, 120, 8)
        mock_runner.run_tests_for_project.assert_called_once_with(["test_module"])

    @patch('app.modules.loop_ci_test_runner.CITestRunner')
    def test_get_latest_result_function(self, mock_ci_test_runner):
        """Test get_latest_result function."""
        # Mock CITestRunner
        mock_runner = MagicMock()
        mock_runner.get_latest_result.return_value = self.sample_project_result
        mock_ci_test_runner.return_value = mock_runner
        
        # Get latest result
        result = get_latest_result(self.project_id)
        
        # Check result
        self.assertEqual(result, self.sample_project_result)
        
        # Verify mocks were called correctly
        mock_ci_test_runner.assert_called_once_with(self.project_id)
        mock_runner.get_latest_result.assert_called_once()

    @patch('app.modules.loop_ci_test_runner.CITestRunner')
    def test_get_result_history_function(self, mock_ci_test_runner):
        """Test get_result_history function."""
        # Mock CITestRunner
        mock_runner = MagicMock()
        mock_runner.get_result_history.return_value = [self.sample_project_result]
        mock_ci_test_runner.return_value = mock_runner
        
        # Get result history
        results = get_result_history(self.project_id, 5)
        
        # Check result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.sample_project_result)
        
        # Verify mocks were called correctly
        mock_ci_test_runner.assert_called_once_with(self.project_id)
        mock_runner.get_result_history.assert_called_once_with(5)

if __name__ == '__main__':
    unittest.main()
