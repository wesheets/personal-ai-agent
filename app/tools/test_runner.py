"""
Test Runner Tool for Autonomous Coding Agents.

This module provides functionality to run pytest on generated code and return pass/fail results
and tracebacks.
"""

import os
import sys
import subprocess
import tempfile
import logging
from typing import Dict, Any, List, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRunner:
    """
    Tool for running pytest on generated code.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the TestRunner.
        
        Args:
            memory_manager: Optional memory manager for storing test results
        """
        self.memory_manager = memory_manager
    
    async def run(
        self,
        code_path: str,
        test_path: Optional[str] = None,
        pytest_args: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run pytest on generated code and return results.
        
        Args:
            code_path: Path to the code file or directory to test
            test_path: Optional path to test file or directory (if different from code_path)
            pytest_args: Optional list of additional pytest arguments
            working_dir: Optional working directory for test execution
            store_memory: Whether to store test results in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing test results
        """
        try:
            # Validate inputs
            if not os.path.exists(code_path):
                return {
                    "status": "error",
                    "error": f"Code path does not exist: {code_path}"
                }
            
            if test_path and not os.path.exists(test_path):
                return {
                    "status": "error",
                    "error": f"Test path does not exist: {test_path}"
                }
            
            # Set default pytest args if not provided
            if not pytest_args:
                pytest_args = ["-v"]
            
            # Set working directory
            if not working_dir:
                working_dir = os.path.dirname(code_path) if os.path.isfile(code_path) else code_path
            
            # Prepare command
            cmd = [sys.executable, "-m", "pytest"]
            
            # Add test path if provided, otherwise use code path
            if test_path:
                cmd.append(test_path)
            else:
                cmd.append(code_path)
            
            # Add pytest arguments
            cmd.extend(pytest_args)
            
            # Run pytest
            process = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            
            # Parse results
            stdout = process.stdout
            stderr = process.stderr
            return_code = process.returncode
            
            # Determine test status
            if return_code == 0:
                status = "passed"
            elif return_code == 1:
                status = "failed"
            elif return_code == 2:
                status = "error"
            elif return_code == 5:
                status = "no_tests_found"
            else:
                status = f"unknown_error_{return_code}"
            
            # Extract test summary
            summary = self._extract_test_summary(stdout)
            
            # Extract failures and errors
            failures = self._extract_failures(stdout)
            
            # Prepare result
            result = {
                "status": status,
                "return_code": return_code,
                "summary": summary,
                "failures": failures,
                "stdout": stdout,
                "stderr": stderr,
                "command": " ".join(cmd)
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager:
                memory_content = {
                    "type": "test_run",
                    "code_path": code_path,
                    "test_path": test_path,
                    "status": status,
                    "summary": summary,
                    "failures": failures
                }
                
                tags = memory_tags or ["test", "pytest"]
                
                # Add status to tags
                tags.append(f"test_{status}")
                
                await self.memory_manager.store(
                    input_text=f"Run tests for {os.path.basename(code_path)}",
                    output_text=f"Test run completed with status: {status}. {summary}",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _extract_test_summary(self, output: str) -> str:
        """
        Extract test summary from pytest output.
        
        Args:
            output: Pytest output
            
        Returns:
            Test summary
        """
        # Look for the summary line
        lines = output.splitlines()
        for line in reversed(lines):
            if "failed" in line and "passed" in line and "=" in line:
                return line.strip()
            if "no tests ran" in line and "=" in line:
                return line.strip()
        
        return "No test summary found"
    
    def _extract_failures(self, output: str) -> List[Dict[str, Any]]:
        """
        Extract test failures from pytest output.
        
        Args:
            output: Pytest output
            
        Returns:
            List of test failures
        """
        failures = []
        lines = output.splitlines()
        
        # Find failure sections
        in_failure = False
        current_failure = {}
        traceback_lines = []
        
        for line in lines:
            if line.startswith("=") and "FAILURES" in line:
                in_failure = True
                continue
            
            if in_failure:
                if line.startswith("_"):
                    # Start of a new failure
                    if current_failure and traceback_lines:
                        current_failure["traceback"] = "\n".join(traceback_lines)
                        failures.append(current_failure)
                    
                    current_failure = {"test": line.strip()}
                    traceback_lines = []
                elif line.startswith("E "):
                    # Error line
                    traceback_lines.append(line)
                    if "AssertionError" in line:
                        current_failure["error_type"] = "AssertionError"
                    elif ":" in line:
                        error_type = line.split(":", 1)[0].replace("E ", "").strip()
                        if error_type:
                            current_failure["error_type"] = error_type
                elif line.startswith("=") and "=" in line:
                    # End of failures section
                    if current_failure and traceback_lines:
                        current_failure["traceback"] = "\n".join(traceback_lines)
                        failures.append(current_failure)
                    in_failure = False
                else:
                    # Other traceback lines
                    traceback_lines.append(line)
        
        # Add the last failure if there is one
        if in_failure and current_failure and traceback_lines:
            current_failure["traceback"] = "\n".join(traceback_lines)
            failures.append(current_failure)
        
        return failures
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_test_runner(memory_manager=None):
    """
    Get a TestRunner instance.
    
    Args:
        memory_manager: Optional memory manager for storing test results
        
    Returns:
        TestRunner instance
    """
    return TestRunner(memory_manager=memory_manager)
