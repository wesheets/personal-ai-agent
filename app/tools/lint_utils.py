import os
import subprocess
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("lint_utils")

def run_linter() -> dict:
    """
    Run ESLint or Prettier on the current project and return warnings, errors, or style issues.
    
    Returns:
        dict: A dictionary containing status, message, and linting results
    """
    try:
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        logger.info(f"Running linter in repository: {repo_dir}")
        
        # Check if ESLint is available
        eslint_available = _is_tool_available("eslint")
        
        # Check if Prettier is available
        prettier_available = _is_tool_available("prettier")
        
        results = {
            "eslint": None,
            "prettier": None
        }
        
        # Run ESLint if available
        if eslint_available:
            try:
                eslint_process = subprocess.run(
                    ["npx", "eslint", ".", "--format", "json"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True
                )
                
                # Parse ESLint output
                if eslint_process.returncode == 0:
                    logger.info("ESLint completed with no issues")
                    results["eslint"] = {
                        "status": "success",
                        "issues": []
                    }
                else:
                    try:
                        eslint_issues = json.loads(eslint_process.stdout)
                        logger.info(f"ESLint completed with issues: {len(eslint_issues)}")
                        results["eslint"] = {
                            "status": "issues",
                            "issues": eslint_issues
                        }
                    except json.JSONDecodeError:
                        logger.warning("Could not parse ESLint output as JSON")
                        results["eslint"] = {
                            "status": "error",
                            "message": "Could not parse ESLint output",
                            "stdout": eslint_process.stdout,
                            "stderr": eslint_process.stderr
                        }
            except Exception as e:
                logger.error(f"Error running ESLint: {str(e)}")
                results["eslint"] = {
                    "status": "error",
                    "message": f"Error running ESLint: {str(e)}"
                }
        else:
            logger.warning("ESLint not available")
            results["eslint"] = {
                "status": "not_available",
                "message": "ESLint is not installed or not in PATH"
            }
        
        # Run Prettier if available
        if prettier_available:
            try:
                prettier_process = subprocess.run(
                    ["npx", "prettier", "--check", ".", "--loglevel", "silent"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True
                )
                
                # Parse Prettier output
                if prettier_process.returncode == 0:
                    logger.info("Prettier completed with no issues")
                    results["prettier"] = {
                        "status": "success",
                        "issues": []
                    }
                else:
                    # Extract file paths from Prettier output
                    file_paths = [
                        line.strip()
                        for line in prettier_process.stdout.splitlines()
                        if line.strip() and "[warn]" not in line and "[error]" not in line
                    ]
                    
                    logger.info(f"Prettier completed with issues: {len(file_paths)}")
                    results["prettier"] = {
                        "status": "issues",
                        "files_with_issues": file_paths
                    }
            except Exception as e:
                logger.error(f"Error running Prettier: {str(e)}")
                results["prettier"] = {
                    "status": "error",
                    "message": f"Error running Prettier: {str(e)}"
                }
        else:
            logger.warning("Prettier not available")
            results["prettier"] = {
                "status": "not_available",
                "message": "Prettier is not installed or not in PATH"
            }
        
        # Determine overall status
        if (results["eslint"] and results["eslint"]["status"] == "error") or \
           (results["prettier"] and results["prettier"]["status"] == "error"):
            overall_status = "error"
        elif (results["eslint"] and results["eslint"]["status"] == "issues") or \
             (results["prettier"] and results["prettier"]["status"] == "issues"):
            overall_status = "issues"
        elif (results["eslint"] and results["eslint"]["status"] == "success") or \
             (results["prettier"] and results["prettier"]["status"] == "success"):
            overall_status = "success"
        else:
            overall_status = "not_available"
        
        # Log to memory
        _log_to_memory("run_linter", f"Ran linters with status: {overall_status}", overall_status)
        
        return {
            "status": overall_status,
            "message": f"Linting completed with status: {overall_status}",
            "results": results
        }
    
    except Exception as e:
        error_message = f"Error in run_linter: {str(e)}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("run_linter", f"Error running linters: {str(e)}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def _is_tool_available(name: str) -> bool:
    """
    Check if a command-line tool is available.
    
    Args:
        name (str): Name of the tool to check
        
    Returns:
        bool: True if the tool is available, False otherwise
    """
    try:
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        
        # Try to run the tool with --version
        process = subprocess.run(
            ["npx", name, "--version"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        return process.returncode == 0
    except Exception:
        return False

def _log_to_memory(operation: str, content: str, status: str):
    """
    Log linting operations to memory.
    
    Args:
        operation (str): The operation performed
        content (str): Description of the operation
        status (str): Status of the operation (success, issues, error, not_available)
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="linting_operation",
            content=content,
            tags=["tools", "lint_utils", operation, status],
            task_type="linting_operation",
            status="completed" if status in ["success", "issues"] else status
        )
        
        logger.info(f"Logged {operation} operation to memory with status {status}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the lint_utils tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed lint_utils.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "lint_utils", "installation", "toolkit_ready"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged lint_utils tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
