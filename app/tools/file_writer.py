import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("file_writer")

def create_file(path: str, content: str) -> dict:
    """
    Write content to a file, creating directories if they don't exist.
    
    Args:
        path (str): The full path to the file to be created
        content (str): The content to write to the file
        
    Returns:
        dict: A dictionary containing status and message
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        
        # Write the content to the file
        with open(path, 'w') as file:
            file.write(content)
        
        logger.info(f"Successfully created file: {path}")
        
        return {
            "status": "success",
            "message": f"File created successfully at {path}",
            "path": path
        }
    
    except Exception as e:
        error_message = f"Error creating file {path}: {str(e)}"
        logger.error(error_message)
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the file_writer tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed file_writer.py tool for Phase 3 Agent Toolkit",
            tags=["tools", "file_writer", "installation"],
            task_type="installation",
            status="completed"
        )
        
        logger.info("Logged file_writer tool installation to memory")
    except Exception as e:
        logger.error(f"Failed to log tool installation to memory: {str(e)}")

# Log installation when module is imported
if __name__ != "__main__":
    try:
        log_installation()
    except Exception as e:
        logger.error(f"Error during installation logging: {str(e)}")
