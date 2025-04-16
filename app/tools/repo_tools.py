import os
import subprocess
import logging
import requests
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("repo_tools")

def create_repo(repo_name: str) -> dict:
    """
    Create a new GitHub repository using the GitHub API.
    
    Args:
        repo_name (str): Name for the new repository
        
    Returns:
        dict: A dictionary containing status, message, and repository details
    """
    try:
        # Get GitHub token from environment
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            error_message = "GITHUB_TOKEN environment variable not set"
            logger.error(error_message)
            
            # Log to memory
            _log_to_memory("create_repo", error_message, "error")
            
            return {
                "status": "error",
                "message": error_message,
                "error": "Missing authentication token"
            }
        
        # Set up the API request
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "name": repo_name,
            "private": False,
            "auto_init": True,
            "description": f"Repository created by Promethios Agent Toolkit"
        }
        
        # Make the API request to create the repository
        response = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            data=json.dumps(data)
        )
        
        # Check if the request was successful
        if response.status_code == 201:
            repo_data = response.json()
            logger.info(f"Successfully created repository: {repo_name}")
            
            # Log to memory
            _log_to_memory("create_repo", f"Created new GitHub repository: {repo_name}", "success")
            
            return {
                "status": "success",
                "message": f"Repository {repo_name} created successfully",
                "repo_url": repo_data.get("html_url"),
                "clone_url": repo_data.get("clone_url"),
                "repo_data": repo_data
            }
        else:
            error_message = f"Failed to create repository: {response.status_code} - {response.text}"
            logger.error(error_message)
            
            # Log to memory
            _log_to_memory("create_repo", error_message, "error")
            
            return {
                "status": "error",
                "message": error_message,
                "status_code": response.status_code,
                "response": response.text
            }
    
    except Exception as e:
        error_message = f"Error in create_repo: {str(e)}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("create_repo", f"Error creating repository: {str(e)}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def install_dependency(package_name: str) -> dict:
    """
    Install an npm package as a dependency.
    
    Args:
        package_name (str): Name of the npm package to install
        
    Returns:
        dict: A dictionary containing status, message, and output
    """
    try:
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        logger.info(f"Installing dependency in repository: {repo_dir}")
        
        # Validate package name for basic security
        if not _is_valid_package_name(package_name):
            error_message = f"Invalid package name: {package_name}"
            logger.error(error_message)
            
            # Log to memory
            _log_to_memory("install_dependency", error_message, "error")
            
            return {
                "status": "error",
                "message": error_message,
                "error": "Package name contains invalid characters"
            }
        
        # Run npm install command
        install_process = subprocess.run(
            ["npm", "install", package_name, "--save"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Successfully installed dependency: {package_name}")
        
        # Log to memory
        _log_to_memory("install_dependency", f"Installed npm package: {package_name}", "success")
        
        return {
            "status": "success",
            "message": f"Successfully installed {package_name}",
            "package": package_name,
            "output": install_process.stdout
        }
    
    except subprocess.CalledProcessError as e:
        error_message = f"npm install failed: {e.stderr}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("install_dependency", f"Failed to install npm package {package_name}: {e.stderr}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": e.stderr,
            "command": e.cmd,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_message = f"Error in install_dependency: {str(e)}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("install_dependency", f"Error installing dependency: {str(e)}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def _is_valid_package_name(package_name: str) -> bool:
    """
    Validate npm package name for basic security.
    
    Args:
        package_name (str): Name of the npm package to validate
        
    Returns:
        bool: True if the package name is valid, False otherwise
    """
    # Check for shell injection characters
    invalid_chars = ['&', ';', '|', '>', '<', '`', '$', '(', ')', '{', '}', '[', ']', '\\', '\'', '"', '\n', '\r']
    return not any(char in package_name for char in invalid_chars)

def _log_to_memory(operation: str, content: str, status: str):
    """
    Log repository operations to memory.
    
    Args:
        operation (str): The operation performed
        content (str): Description of the operation
        status (str): Status of the operation (success, error)
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="repository_operation",
            content=content,
            tags=["tools", "repo_tools", operation, status],
            task_type="repository_operation",
            status="completed" if status == "success" else status
        )
        
        logger.info(f"Logged {operation} operation to memory with status {status}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the repo_tools tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed repo_tools.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "repo_tools", "installation", "toolkit_ready"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged repo_tools tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
