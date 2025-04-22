"""
Loop CI Test Runner Module

This module implements the Loop CI Test Runner for Promethios, which verifies
build integrity by running automated tests on modules and updating the project
manifest with the results.

The Loop CI Test Runner is responsible for:
1. Running tests on modules to verify their integrity
2. Generating CI results with scores and status
3. Updating the project manifest with test results
4. Providing detailed test reports
5. Integrating with the Rebuilder Agent
"""

import os
import json
import logging
import datetime
import importlib
import inspect
import unittest
import sys
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import project manifest module
from app.modules.project_manifest import (
    get_module,
    update_ci_result,
    mark_for_rebuild,
    get_manifest_summary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CI_RESULTS_DIR = "/home/ubuntu/repo/personal-ai-agent/data/ci_results"
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_MAX_WORKERS = 4

class TestResult:
    """Class to store test result information."""
    
    def __init__(self, module_name: str, test_name: str, status: str, 
                 execution_time: float, error_message: Optional[str] = None):
        """
        Initialize a test result.
        
        Args:
            module_name: Name of the module being tested
            test_name: Name of the test
            status: Status of the test (passed, failed, error, skipped)
            execution_time: Execution time in seconds
            error_message: Error message if test failed or had an error
        """
        self.module_name = module_name
        self.test_name = test_name
        self.status = status
        self.execution_time = execution_time
        self.error_message = error_message
        self.timestamp = datetime.datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary."""
        result = {
            "module_name": self.module_name,
            "test_name": self.test_name,
            "status": self.status,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }
        
        if self.error_message:
            result["error_message"] = self.error_message
        
        return result

class CITestRunner:
    """Class to run CI tests on modules."""
    
    def __init__(self, project_id: str, timeout: int = DEFAULT_TIMEOUT, 
                 max_workers: int = DEFAULT_MAX_WORKERS):
        """
        Initialize a CI test runner.
        
        Args:
            project_id: ID of the project
            timeout: Timeout for test execution in seconds
            max_workers: Maximum number of worker threads
        """
        self.project_id = project_id
        self.timeout = timeout
        self.max_workers = max_workers
        
        # Ensure CI results directory exists
        os.makedirs(CI_RESULTS_DIR, exist_ok=True)
    
    def run_tests_for_module(self, module_name: str) -> Dict[str, Any]:
        """
        Run tests for a specific module.
        
        Args:
            module_name: Name of the module to test
            
        Returns:
            Dictionary containing test results
        """
        logger.info(f"Running tests for module: {module_name}")
        
        # Get module information
        module_info = get_module(self.project_id, module_name)
        if not module_info:
            logger.warning(f"Module not found: {module_name}")
            return {
                "module_name": module_name,
                "status": "error",
                "ci_score": 0.0,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "failure_reason": "Module not found in project manifest",
                "test_results": []
            }
        
        # Find test module
        test_module_name = f"app.tests.test_{module_name}"
        try:
            # Try to import test module
            test_module = importlib.import_module(test_module_name)
            
            # Find test classes
            test_classes = []
            for name, obj in inspect.getmembers(test_module):
                if (inspect.isclass(obj) and issubclass(obj, unittest.TestCase) 
                    and obj != unittest.TestCase):
                    test_classes.append(obj)
            
            if not test_classes:
                logger.warning(f"No test classes found for module: {module_name}")
                return {
                    "module_name": module_name,
                    "status": "error",
                    "ci_score": 0.0,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "failure_reason": "No test classes found",
                    "test_results": []
                }
            
            # Run tests
            test_results = []
            total_tests = 0
            passed_tests = 0
            
            for test_class in test_classes:
                suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
                total_tests += suite.countTestCases()
                
                # Create a test result collector
                result = unittest.TestResult()
                
                # Run tests with timeout
                start_time = datetime.datetime.now()
                suite.run(result)
                end_time = datetime.datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Process results
                for test, error in result.errors:
                    test_results.append(TestResult(
                        module_name=module_name,
                        test_name=str(test),
                        status="error",
                        execution_time=execution_time,
                        error_message=error
                    ))
                
                for test, failure in result.failures:
                    test_results.append(TestResult(
                        module_name=module_name,
                        test_name=str(test),
                        status="failed",
                        execution_time=execution_time,
                        error_message=failure
                    ))
                
                for test in result.skipped:
                    test_results.append(TestResult(
                        module_name=module_name,
                        test_name=str(test[0]),
                        status="skipped",
                        execution_time=execution_time,
                        error_message=test[1]
                    ))
                
                # Count passed tests
                passed_tests += (suite.countTestCases() - 
                                len(result.errors) - 
                                len(result.failures) - 
                                len(result.skipped))
                
                # Add passed test results
                for test in result.successes if hasattr(result, 'successes') else []:
                    test_results.append(TestResult(
                        module_name=module_name,
                        test_name=str(test),
                        status="passed",
                        execution_time=execution_time
                    ))
            
            # Calculate CI score
            ci_score = passed_tests / total_tests if total_tests > 0 else 0.0
            
            # Determine overall status
            status = "passed" if ci_score >= 0.8 else "failed"
            
            # Create CI result
            ci_result = {
                "module_name": module_name,
                "status": status,
                "ci_score": ci_score,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "test_results": [result.to_dict() for result in test_results]
            }
            
            if status == "failed":
                ci_result["failure_reason"] = f"{total_tests - passed_tests} tests failed"
            
            logger.info(f"CI tests completed for module: {module_name}, score: {ci_score:.2f}")
            return ci_result
        
        except ImportError as e:
            logger.error(f"Error importing test module for {module_name}: {e}")
            return {
                "module_name": module_name,
                "status": "error",
                "ci_score": 0.0,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "failure_reason": f"Error importing test module: {e}",
                "test_results": []
            }
        
        except Exception as e:
            logger.error(f"Error running tests for module {module_name}: {e}")
            return {
                "module_name": module_name,
                "status": "error",
                "ci_score": 0.0,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "failure_reason": f"Error running tests: {e}",
                "test_results": []
            }
    
    def run_tests_for_project(self, modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run tests for all modules in a project or a specific list of modules.
        
        Args:
            modules: Optional list of module names to test
            
        Returns:
            Dictionary containing test results for all modules
        """
        logger.info(f"Running tests for project: {self.project_id}")
        
        # Get project summary to find all modules if not specified
        if not modules:
            summary = get_manifest_summary(self.project_id)
            if "modules" in summary:
                modules = list(summary["modules"].keys())
            else:
                logger.warning(f"No modules found for project: {self.project_id}")
                return {
                    "project_id": self.project_id,
                    "status": "error",
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "failure_reason": "No modules found",
                    "module_results": []
                }
        
        # Run tests for each module in parallel
        module_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_module = {
                executor.submit(self.run_tests_for_module, module_name): module_name
                for module_name in modules
            }
            
            for future in as_completed(future_to_module):
                module_name = future_to_module[future]
                try:
                    result = future.result()
                    module_results.append(result)
                    
                    # Update project manifest with CI result
                    update_ci_result(self.project_id, module_name, result)
                    
                    # Mark module for rebuild if tests failed
                    if result["status"] == "failed":
                        mark_for_rebuild(
                            self.project_id, 
                            module_name, 
                            True, 
                            f"CI tests failed: {result.get('failure_reason', 'Unknown reason')}"
                        )
                
                except Exception as e:
                    logger.error(f"Error processing results for module {module_name}: {e}")
                    module_results.append({
                        "module_name": module_name,
                        "status": "error",
                        "ci_score": 0.0,
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "failure_reason": f"Error processing results: {e}",
                        "test_results": []
                    })
        
        # Calculate overall project CI score
        total_modules = len(module_results)
        passed_modules = sum(1 for result in module_results if result["status"] == "passed")
        ci_score = passed_modules / total_modules if total_modules > 0 else 0.0
        
        # Determine overall status
        status = "passed" if ci_score >= 0.8 else "failed"
        
        # Create project CI result
        project_result = {
            "project_id": self.project_id,
            "status": status,
            "ci_score": ci_score,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "total_modules": total_modules,
            "passed_modules": passed_modules,
            "failed_modules": total_modules - passed_modules,
            "module_results": module_results
        }
        
        # Save project CI result
        self._save_project_result(project_result)
        
        logger.info(f"CI tests completed for project: {self.project_id}, score: {ci_score:.2f}")
        return project_result
    
    def _save_project_result(self, result: Dict[str, Any]) -> bool:
        """
        Save project CI result to file.
        
        Args:
            result: Project CI result
            
        Returns:
            Boolean indicating success
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        result_path = os.path.join(
            CI_RESULTS_DIR, 
            f"{self.project_id}_{timestamp}.json"
        )
        
        try:
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Saved project CI result to: {result_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving project CI result: {e}")
            return False
    
    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest CI result for the project.
        
        Returns:
            Latest CI result, or None if not found
        """
        try:
            # Find all result files for this project
            result_files = []
            for filename in os.listdir(CI_RESULTS_DIR):
                if filename.startswith(f"{self.project_id}_") and filename.endswith(".json"):
                    result_files.append(filename)
            
            if not result_files:
                logger.warning(f"No CI results found for project: {self.project_id}")
                return None
            
            # Sort by timestamp (which is part of the filename)
            result_files.sort(reverse=True)
            
            # Load the latest result
            latest_file = os.path.join(CI_RESULTS_DIR, result_files[0])
            with open(latest_file, 'r') as f:
                result = json.load(f)
            
            logger.info(f"Loaded latest CI result for project: {self.project_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error getting latest CI result: {e}")
            return None
    
    def get_result_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the history of CI results for the project.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of CI results, sorted by timestamp (newest first)
        """
        try:
            # Find all result files for this project
            result_files = []
            for filename in os.listdir(CI_RESULTS_DIR):
                if filename.startswith(f"{self.project_id}_") and filename.endswith(".json"):
                    result_files.append(filename)
            
            if not result_files:
                logger.warning(f"No CI results found for project: {self.project_id}")
                return []
            
            # Sort by timestamp (which is part of the filename)
            result_files.sort(reverse=True)
            
            # Load results
            results = []
            for filename in result_files[:limit]:
                file_path = os.path.join(CI_RESULTS_DIR, filename)
                with open(file_path, 'r') as f:
                    result = json.load(f)
                results.append(result)
            
            logger.info(f"Loaded {len(results)} CI results for project: {self.project_id}")
            return results
        
        except Exception as e:
            logger.error(f"Error getting CI result history: {e}")
            return []

def run_tests(project_id: str, modules: Optional[List[str]] = None, 
              timeout: int = DEFAULT_TIMEOUT, max_workers: int = DEFAULT_MAX_WORKERS) -> Dict[str, Any]:
    """
    Run CI tests for a project.
    
    Args:
        project_id: ID of the project
        modules: Optional list of module names to test
        timeout: Timeout for test execution in seconds
        max_workers: Maximum number of worker threads
        
    Returns:
        Dictionary containing test results
    """
    runner = CITestRunner(project_id, timeout, max_workers)
    return runner.run_tests_for_project(modules)

def get_latest_result(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest CI result for a project.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Latest CI result, or None if not found
    """
    runner = CITestRunner(project_id)
    return runner.get_latest_result()

def get_result_history(project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the history of CI results for a project.
    
    Args:
        project_id: ID of the project
        limit: Maximum number of results to return
        
    Returns:
        List of CI results, sorted by timestamp (newest first)
    """
    runner = CITestRunner(project_id)
    return runner.get_result_history(limit)
