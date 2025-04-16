import os
import logging
import json
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("snapshot")

def write_memory_snapshot(project_id: str) -> dict:
    """
    Save current build status, CRITIC score, tool logs to memory.
    
    Args:
        project_id (str): Identifier for the project
        
    Returns:
        dict: A dictionary containing status, message, and snapshot details
    """
    try:
        # Validate project_id
        if not project_id or not isinstance(project_id, str):
            error_message = f"Invalid project_id: {project_id}"
            logger.error(error_message)
            
            # Log to memory
            _log_to_memory("write_memory_snapshot", error_message, "error")
            
            return {
                "status": "error",
                "message": error_message,
                "error": "Project ID must be a non-empty string"
            }
        
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        
        # Collect build status
        build_status = _get_build_status(repo_dir)
        
        # Collect CRITIC score
        critic_score = _get_critic_score(project_id)
        
        # Collect tool logs
        tool_logs = _get_tool_logs()
        
        # Create snapshot data
        timestamp = datetime.datetime.now().isoformat()
        snapshot_data = {
            "project_id": project_id,
            "timestamp": timestamp,
            "build_status": build_status,
            "critic_score": critic_score,
            "tool_logs": tool_logs
        }
        
        # Save snapshot to memory
        snapshot_id = f"{project_id}_{timestamp.replace(':', '-').replace('.', '-')}"
        _save_snapshot_to_memory(snapshot_id, snapshot_data)
        
        logger.info(f"Successfully created memory snapshot for project: {project_id}")
        
        return {
            "status": "success",
            "message": f"Memory snapshot created successfully for project: {project_id}",
            "project_id": project_id,
            "snapshot_id": snapshot_id,
            "timestamp": timestamp,
            "snapshot_data": snapshot_data
        }
    
    except Exception as e:
        error_message = f"Error in write_memory_snapshot: {str(e)}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("write_memory_snapshot", f"Error creating memory snapshot: {str(e)}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def _get_build_status(repo_dir: str) -> dict:
    """
    Get the current build status of the project.
    
    Args:
        repo_dir (str): Path to the repository root
        
    Returns:
        dict: Build status information
    """
    try:
        # Check if package.json exists
        package_json_path = os.path.join(repo_dir, "package.json")
        has_package_json = os.path.exists(package_json_path)
        
        # Check if node_modules exists
        node_modules_path = os.path.join(repo_dir, "node_modules")
        has_node_modules = os.path.exists(node_modules_path)
        
        # Check if .git exists
        git_path = os.path.join(repo_dir, ".git")
        has_git = os.path.exists(git_path)
        
        # Check if .vercel exists
        vercel_path = os.path.join(repo_dir, ".vercel")
        has_vercel = os.path.exists(vercel_path)
        
        # Read package.json if it exists
        package_info = {}
        if has_package_json:
            try:
                with open(package_json_path, 'r') as f:
                    package_info = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read package.json: {str(e)}")
        
        return {
            "has_package_json": has_package_json,
            "has_node_modules": has_node_modules,
            "has_git": has_git,
            "has_vercel": has_vercel,
            "package_name": package_info.get("name", ""),
            "package_version": package_info.get("version", ""),
            "dependencies": package_info.get("dependencies", {}),
            "dev_dependencies": package_info.get("devDependencies", {})
        }
    except Exception as e:
        logger.error(f"Error getting build status: {str(e)}")
        return {
            "error": f"Error getting build status: {str(e)}"
        }

def _get_critic_score(project_id: str) -> dict:
    """
    Get the CRITIC score for the project.
    
    Args:
        project_id (str): Identifier for the project
        
    Returns:
        dict: CRITIC score information
    """
    try:
        # Try to import CRITIC module
        try:
            from app.modules.critic import get_project_score
            critic_score = get_project_score(project_id)
            return critic_score
        except ImportError:
            logger.warning("CRITIC module not available")
            return {
                "status": "not_available",
                "message": "CRITIC module not available"
            }
    except Exception as e:
        logger.error(f"Error getting CRITIC score: {str(e)}")
        return {
            "status": "error",
            "error": f"Error getting CRITIC score: {str(e)}"
        }

def _get_tool_logs() -> list:
    """
    Get recent tool logs from memory.
    
    Returns:
        list: Recent tool logs
    """
    try:
        # Try to import memory reader
        try:
            from app.modules.memory_reader import read_memory
            
            # Get recent tool logs
            tool_logs = read_memory(
                agent_id="system",
                limit=50,
                tags=["tools"]
            )
            
            return tool_logs
        except ImportError:
            logger.warning("Memory reader module not available")
            return []
    except Exception as e:
        logger.error(f"Error getting tool logs: {str(e)}")
        return []

def _save_snapshot_to_memory(snapshot_id: str, snapshot_data: dict):
    """
    Save snapshot data to memory.
    
    Args:
        snapshot_id (str): Identifier for the snapshot
        snapshot_data (dict): Snapshot data to save
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="project_snapshot",
            content=json.dumps(snapshot_data),
            tags=["tools", "snapshot", "project_snapshot", snapshot_data["project_id"]],
            task_type="snapshot",
            status="completed"
        )
        
        logger.info(f"Saved snapshot to memory: {snapshot_id}")
    except Exception as e:
        logger.error(f"Failed to save snapshot to memory: {str(e)}")

def _log_to_memory(operation: str, content: str, status: str):
    """
    Log snapshot operations to memory.
    
    Args:
        operation (str): The operation performed
        content (str): Description of the operation
        status (str): Status of the operation (success, error)
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="snapshot_operation",
            content=content,
            tags=["tools", "snapshot", operation, status],
            task_type="snapshot_operation",
            status="completed" if status == "success" else status
        )
        
        logger.info(f"Logged {operation} operation to memory with status {status}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the snapshot tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed snapshot.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "snapshot", "installation", "toolkit_ready"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged snapshot tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
