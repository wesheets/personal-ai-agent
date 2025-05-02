import subprocess
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vercel_deploy")

def deploy() -> dict:
    """
    Deploy the current project to Vercel using 'vercel --prod' command.
    
    Returns:
        dict: A dictionary containing status, message, and output
    """
    try:
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        logger.info(f"Deploying from repository: {repo_dir}")
        
        # Run vercel --prod command
        deploy_process = subprocess.run(
            ["vercel", "--prod"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Successfully deployed to Vercel")
        
        # Extract deployment URL from output if possible
        output_lines = deploy_process.stdout.splitlines()
        deployment_url = None
        for line in output_lines:
            if "https://" in line and ".vercel.app" in line:
                deployment_url = line.strip()
                break
        
        # Log to memory
        _log_to_memory("deploy", f"Successfully deployed to Vercel: {deployment_url if deployment_url else 'URL not found'}", "success")
        
        return {
            "status": "success",
            "message": "Successfully deployed to Vercel",
            "deployment_url": deployment_url,
            "output": deploy_process.stdout
        }
    
    except subprocess.CalledProcessError as e:
        error_message = f"Vercel deployment failed: {e.stderr}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("deploy", f"Vercel deployment failed: {e.stderr}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": e.stderr,
            "command": e.cmd,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_message = f"Error in deploy: {str(e)}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("deploy", f"Error in deployment: {str(e)}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def _log_to_memory(operation: str, content: str, status: str):
    """
    Log deployment operations to memory.
    
    Args:
        operation (str): The operation performed
        content (str): Description of the operation
        status (str): Status of the operation (success, error)
    """
    try:
        from app.api.modules.memory import write_memory
        
        write_memory(
            agent_id="system",
            type="deployment_operation",
            content=content,
            tags=["tools", "vercel_deploy", operation, status],
            task_type="deployment_operation",
            status="completed" if status == "success" else status
        )
        
        logger.info(f"Logged {operation} operation to memory with status {status}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the vercel_deploy tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.api.modules.memory import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed vercel_deploy.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "vercel_deploy", "installation", "toolkit_ready"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged vercel_deploy tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
