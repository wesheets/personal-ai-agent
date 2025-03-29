"""
Code Executor Tool for the Personal AI Agent System.

This module provides functionality to execute code in various programming languages
and return the results.
"""

import os
import json
import subprocess
import tempfile
import time
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("code_executor")

def run(
    code: str,
    language: str = "python",
    timeout: int = 30,
    input_data: Optional[str] = None,
    args: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    working_dir: Optional[str] = None,
    save_output: bool = False,
    output_file: Optional[str] = None,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["code_execution", "development"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Execute code in the specified programming language and return the results.
    
    Args:
        code: The code to execute
        language: Programming language (python, javascript, bash, etc.)
        timeout: Maximum execution time in seconds
        input_data: Optional input data to provide to the program
        args: Optional command-line arguments
        env_vars: Optional environment variables
        working_dir: Optional working directory for execution
        save_output: Whether to save the output to a file
        output_file: Path to save the output (if save_output is True)
        store_memory: Whether to store the execution results in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing execution results and metadata
    """
    logger.info(f"Executing {language} code")
    
    try:
        # Validate language
        if language.lower() not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}")
            
        # In a real implementation, this would execute actual code
        # For now, we'll simulate the code execution
        
        # Simulate code execution
        start_time = time.time()
        stdout, stderr, exit_code = _simulate_code_execution(code, language, input_data, args)
        execution_time = time.time() - start_time
        
        result = {
            "success": exit_code == 0,
            "language": language,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "execution_time": execution_time
        }
        
        # Save output to file if requested
        if save_output and output_file:
            try:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
                result["output_saved_to"] = output_file
            except Exception as e:
                logger.error(f"Failed to save output to file: {str(e)}")
                result["output_save_error"] = str(e)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the execution for memory storage
                stdout_summary = stdout[:300] + "..." if len(stdout) > 300 else stdout
                stderr_summary = stderr[:300] + "..." if len(stderr) > 300 else stderr
                
                memory_entry = {
                    "type": "code_execution",
                    "language": language,
                    "code_snippet": code[:100] + "..." if len(code) > 100 else code,
                    "success": exit_code == 0,
                    "stdout_summary": stdout_summary,
                    "stderr_summary": stderr_summary,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored code execution results in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store code execution in memory: {str(e)}")
        
        return result
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "language": language
        }

def _simulate_code_execution(
    code: str,
    language: str,
    input_data: Optional[str],
    args: Optional[List[str]]
) -> tuple:
    """
    Simulate code execution for development purposes.
    
    Args:
        code: The code to execute
        language: Programming language
        input_data: Input data to provide to the program
        args: Command-line arguments
        
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    language = language.lower()
    
    # Check for potentially harmful code patterns
    if _contains_harmful_patterns(code, language):
        return (
            "",
            "Execution blocked: Code contains potentially harmful patterns",
            1
        )
    
    # Simulate execution based on language
    if language == "python":
        return _simulate_python_execution(code, input_data)
    elif language == "javascript" or language == "node":
        return _simulate_javascript_execution(code, input_data)
    elif language == "bash" or language == "shell":
        return _simulate_bash_execution(code, input_data)
    elif language == "sql":
        return _simulate_sql_execution(code)
    elif language == "r":
        return _simulate_r_execution(code)
    else:
        # Generic simulation for other languages
        return (
            f"Simulated {language} execution output\nCode length: {len(code)} characters",
            "",
            0
        )

def _contains_harmful_patterns(code: str, language: str) -> bool:
    """
    Check if code contains potentially harmful patterns.
    
    Args:
        code: The code to check
        language: Programming language
        
    Returns:
        Boolean indicating if harmful patterns were detected
    """
    # This is a simplified check for demonstration purposes
    # In a real implementation, this would be more sophisticated
    
    harmful_patterns = {
        "python": [
            "os.system(", "subprocess.call(", "subprocess.Popen(", 
            "eval(", "exec(", "__import__('os')", "shutil.rmtree("
        ],
        "javascript": [
            "process.exit", "require('child_process')", "exec(", "eval("
        ],
        "bash": [
            "rm -rf", ":(){ :|:& };:", "> /dev/sda", "dd if=/dev/zero of="
        ],
        "sql": [
            "DROP DATABASE", "DROP TABLE", "DELETE FROM", "TRUNCATE TABLE"
        ]
    }
    
    # Get patterns for the specified language, or use a default set
    patterns = harmful_patterns.get(language, [])
    
    # Check for harmful patterns
    for pattern in patterns:
        if pattern in code:
            logger.warning(f"Harmful pattern detected in {language} code: {pattern}")
            return True
    
    return False

def _simulate_python_execution(code: str, input_data: Optional[str]) -> tuple:
    """
    Simulate Python code execution.
    
    Args:
        code: Python code to execute
        input_data: Input data to provide to the program
        
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    # Check for imports and determine output based on them
    if "import pandas" in code or "from pandas" in code:
        if "read_csv" in code or "DataFrame" in code:
            return (
                "   Column1  Column2  Column3\n0        1        2        3\n1        4        5        6\n2        7        8        9",
                "",
                0
            )
    
    if "import matplotlib" in code or "from matplotlib" in code:
        if "pyplot" in code or "plt" in code:
            return (
                "Figure created and displayed",
                "",
                0
            )
    
    if "import numpy" in code or "from numpy" in code:
        if "array" in code or "np.array" in code:
            return (
                "array([1, 2, 3, 4, 5])",
                "",
                0
            )
    
    if "print" in code:
        # Extract what's being printed (simplified)
        try:
            print_content = code.split("print(")[1].split(")")[0]
            if print_content.startswith('"') or print_content.startswith("'"):
                # String literal
                print_content = print_content.strip("'\"")
            else:
                # Assume it's a variable or expression
                print_content = f"Result of expression: {print_content}"
            
            return (print_content, "", 0)
        except:
            pass
    
    # Default output
    return (
        "Python code executed successfully",
        "",
        0
    )

def _simulate_javascript_execution(code: str, input_data: Optional[str]) -> tuple:
    """
    Simulate JavaScript code execution.
    
    Args:
        code: JavaScript code to execute
        input_data: Input data to provide to the program
        
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    if "console.log" in code:
        try:
            log_content = code.split("console.log(")[1].split(")")[0]
            if log_content.startswith('"') or log_content.startswith("'"):
                # String literal
                log_content = log_content.strip("'\"")
            else:
                # Assume it's a variable or expression
                log_content = f"Result of expression: {log_content}"
            
            return (log_content, "", 0)
        except:
            pass
    
    # Check for common libraries
    if "require('express')" in code:
        return (
            "Express server started on port 3000",
            "",
            0
        )
    
    if "fetch(" in code or "axios" in code:
        return (
            '{"data": {"id": 1, "name": "Test Data", "value": 42}}',
            "",
            0
        )
    
    # Default output
    return (
        "JavaScript code executed successfully",
        "",
        0
    )

def _simulate_bash_execution(code: str, input_data: Optional[str]) -> tuple:
    """
    Simulate Bash code execution.
    
    Args:
        code: Bash code to execute
        input_data: Input data to provide to the program
        
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    if "ls" in code:
        return (
            "file1.txt\nfile2.txt\ndirectory1/\ndirectory2/",
            "",
            0
        )
    
    if "echo" in code:
        try:
            echo_content = code.split("echo ")[1].split("\n")[0]
            return (echo_content, "", 0)
        except:
            pass
    
    if "grep" in code:
        return (
            "Line 42: matching content found",
            "",
            0
        )
    
    # Default output
    return (
        "Bash command executed successfully",
        "",
        0
    )

def _simulate_sql_execution(code: str) -> tuple:
    """
    Simulate SQL code execution.
    
    Args:
        code: SQL code to execute
        
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    if "SELECT" in code.upper() or "select" in code:
        return (
            "id | name | value\n------------------\n1 | Item 1 | 100\n2 | Item 2 | 200\n3 | Item 3 | 300\n(3 rows affected)",
            "",
            0
        )
    
    if "INSERT" in code.upper() or "insert" in code:
        return (
            "(1 row affected)",
            "",
            0
        )
    
    if "UPDATE" in code.upper() or "update" in code:
        return (
            "(2 rows affected)",
            "",
            0
        )
    
    # Default output
    return (
        "SQL query executed successfully",
        "",
        0
    )

def _simulate_r_execution(code: str) -> tuple:
    """
    Simulate R code execution.
    
    Args:
        code: R code to execute
        
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    if "ggplot" in code:
        return (
            "Plot created and displayed",
            "",
            0
        )
    
    if "read.csv" in code or "data.frame" in code:
        return (
            "  Column1 Column2 Column3\n1       1       2       3\n2       4       5       6\n3       7       8       9",
            "",
            0
        )
    
    if "print" in code:
        try:
            print_content = code.split("print(")[1].split(")")[0]
            return (f"[1] {print_content}", "", 0)
        except:
            pass
    
    # Default output
    return (
        "R code executed successfully",
        "",
        0
    )

# Define supported languages
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "node",
    "bash",
    "shell",
    "sql",
    "r",
    "java",
    "c",
    "cpp",
    "csharp",
    "go",
    "ruby",
    "php",
    "rust",
    "swift"
]
