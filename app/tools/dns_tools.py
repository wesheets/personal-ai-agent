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
logger = logging.getLogger("dns_tools")

def connect_domain(domain: str) -> dict:
    """
    Connect a custom domain to a Vercel deployment using the Vercel CLI.
    
    Args:
        domain (str): The domain to connect to the deployment
        
    Returns:
        dict: A dictionary containing status, message, and output
    """
    try:
        # Validate domain for basic security
        if not _is_valid_domain(domain):
            error_message = f"Invalid domain name: {domain}"
            logger.error(error_message)
            
            # Log to memory
            _log_to_memory("connect_domain", error_message, "error")
            
            return {
                "status": "error",
                "message": error_message,
                "error": "Domain name contains invalid characters"
            }
        
        # Get the current working directory (repository root)
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        logger.info(f"Connecting domain in repository: {repo_dir}")
        
        # Run vercel domain add command
        domain_process = subprocess.run(
            ["vercel", "domains", "add", domain],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Successfully connected domain: {domain}")
        
        # Log to memory
        _log_to_memory("connect_domain", f"Connected domain: {domain} to Vercel deployment", "success")
        
        return {
            "status": "success",
            "message": f"Successfully connected domain: {domain}",
            "domain": domain,
            "output": domain_process.stdout
        }
    
    except subprocess.CalledProcessError as e:
        error_message = f"Vercel domain connection failed: {e.stderr}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("connect_domain", f"Failed to connect domain {domain}: {e.stderr}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": e.stderr,
            "command": e.cmd,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_message = f"Error in connect_domain: {str(e)}"
        logger.error(error_message)
        
        # Log to memory
        _log_to_memory("connect_domain", f"Error connecting domain: {str(e)}", "error")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def _is_valid_domain(domain: str) -> bool:
    """
    Validate domain name for basic security.
    
    Args:
        domain (str): Domain name to validate
        
    Returns:
        bool: True if the domain name is valid, False otherwise
    """
    # Check for shell injection characters
    invalid_chars = ['&', ';', '|', '>', '<', '`', '$', '(', ')', '{', '}', '[', ']', '\\', '\'', '"', '\n', '\r']
    
    # Basic domain validation
    if not domain or len(domain) > 255:
        return False
    
    # Check for shell injection characters
    if any(char in domain for char in invalid_chars):
        return False
    
    # Check for valid domain format (basic check)
    if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
        return False
    
    return True

def _log_to_memory(operation: str, content: str, status: str):
    """
    Log DNS operations to memory.
    
    Args:
        operation (str): The operation performed
        content (str): Description of the operation
        status (str): Status of the operation (success, error)
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="dns_operation",
            content=content,
            tags=["tools", "dns_tools", operation, status],
            task_type="dns_operation",
            status="completed" if status == "success" else status
        )
        
        logger.info(f"Logged {operation} operation to memory with status {status}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the dns_tools tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed dns_tools.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "dns_tools", "installation", "toolkit_ready"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged dns_tools tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
