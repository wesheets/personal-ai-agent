import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("file_reader")

def read_file(path: str) -> dict:
    """
    Read content from a file for HAL, ASH, or CRITIC to analyze.
    
    Args:
        path (str): The full path to the file to be read
        
    Returns:
        dict: A dictionary containing status, message, and content
    """
    try:
        # Check if file exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"File does not exist at {path}.",
                "path": path,
                "content": None
            }
            
        # Check if path is a file
        if not os.path.isfile(path):
            return {
                "status": "error",
                "message": f"Path {path} exists but is not a file.",
                "path": path,
                "content": None
            }
        
        # Read the content from the file
        with open(path, 'r') as file:
            content = file.read()
        
        logger.info(f"Successfully read file: {path}")
        
        # Log to memory
        _log_to_memory("read_file", f"Read file content from {path}", path)
        
        return {
            "status": "success",
            "message": f"File read successfully from {path}",
            "path": path,
            "content": content,
            "size_bytes": os.path.getsize(path)
        }
    
    except UnicodeDecodeError as e:
        error_message = f"Error reading file {path}: File appears to be binary or uses an unsupported encoding."
        logger.error(error_message)
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e),
            "path": path,
            "content": None,
            "is_binary": True
        }
    
    except Exception as e:
        error_message = f"Error reading file {path}: {str(e)}"
        logger.error(error_message)
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e),
            "path": path,
            "content": None
        }

def _log_to_memory(operation: str, content: str, path: str):
    """
    Log file operations to memory.
    
    Args:
        operation (str): The operation performed (read)
        content (str): Description of the operation
        path (str): The file path involved
    """
    try:
        from app.api.modules.memory import write_memory
        
        write_memory(
            agent_id="system",
            type="file_operation",
            content=content,
            tags=["tools", "file_reader", operation, path],
            task_type="file_operation",
            status="completed"
        )
        
        logger.info(f"Logged {operation} operation to memory for {path}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the file_reader tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.api.modules.memory import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed file_reader.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "file_reader", "installation", "toolkit_ready"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged file_reader tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
