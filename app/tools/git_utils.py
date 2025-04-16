import os
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("git_utils")

def git_commit_push(message: str) -> dict:
    """
    Stage all changes, commit, and push to GitHub.
    
    Args:
        message (str): The commit message
        
    Returns:
        dict: A dictionary containing status, message, and output
    """
    try:
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        logger.info(f"Working in repository: {repo_dir}")
        
        # Stage all changes
        stage_process = subprocess.run(
            ["git", "add", "."],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Successfully staged all changes")
        
        # Commit changes
        commit_process = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        # Check if there were changes to commit
        if commit_process.returncode != 0 and "nothing to commit" in commit_process.stdout + commit_process.stderr:
            logger.info("No changes to commit")
            return {
                "status": "success",
                "message": "No changes to commit",
                "output": commit_process.stdout + commit_process.stderr
            }
        
        # If commit failed for other reasons, raise an exception
        if commit_process.returncode != 0:
            raise Exception(f"Commit failed: {commit_process.stderr}")
        
        logger.info(f"Successfully committed changes with message: {message}")
        
        # Push changes
        push_process = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Successfully pushed changes to GitHub")
        
        return {
            "status": "success",
            "message": "Changes committed and pushed successfully",
            "commit_message": message,
            "output": {
                "stage": stage_process.stdout,
                "commit": commit_process.stdout,
                "push": push_process.stdout
            }
        }
    
    except subprocess.CalledProcessError as e:
        error_message = f"Git operation failed: {e.stderr}"
        logger.error(error_message)
        return {
            "status": "error",
            "message": error_message,
            "error": e.stderr,
            "command": e.cmd,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_message = f"Error in git_commit_push: {str(e)}"
        logger.error(error_message)
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the git_utils tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed git_utils.py tool for Phase 3 Agent Toolkit",
            tags=["tools", "git_utils", "installation"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged git_utils tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
