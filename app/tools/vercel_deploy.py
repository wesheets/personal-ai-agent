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
        
        return {
            "status": "success",
            "message": "Successfully deployed to Vercel",
            "deployment_url": deployment_url,
            "output": deploy_process.stdout
        }
    
    except subprocess.CalledProcessError as e:
        error_message = f"Vercel deployment failed: {e.stderr}"
        logger.error(error_message)
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
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the vercel_deploy tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed vercel_deploy.py tool for Phase 3 Agent Toolkit",
            tags=["tools", "vercel_deploy", "installation"],
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
