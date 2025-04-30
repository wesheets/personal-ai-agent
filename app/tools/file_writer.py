import os
import logging
import shutil

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
        # Check if file already exists
        if os.path.exists(path):
            return {
                "status": "error",
                "message": f"File already exists at {path}. Use update_file() to modify existing files.",
                "path": path
            }
            
        # Ensure the directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        
        # Write the content to the file
        with open(path, 'w') as file:
            file.write(content)
        
        logger.info(f"Successfully created file: {path}")
        
        # Log to memory
        _log_to_memory("create_file", f"Created new file at {path}", path)
        
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

def update_file(path: str, new_content: str) -> dict:
    """
    Replace the content of an existing file.
    
    Args:
        path (str): The full path to the file to be updated
        new_content (str): The new content to write to the file
        
    Returns:
        dict: A dictionary containing status and message
    """
    try:
        # Check if file exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"File does not exist at {path}. Use create_file() to create new files.",
                "path": path
            }
            
        # Create a backup of the file
        backup_path = f"{path}.bak"
        shutil.copy2(path, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        
        # Write the new content to the file
        with open(path, 'w') as file:
            file.write(new_content)
        
        logger.info(f"Successfully updated file: {path}")
        
        # Log to memory
        _log_to_memory("update_file", f"Updated existing file at {path}", path)
        
        return {
            "status": "success",
            "message": f"File updated successfully at {path}",
            "path": path,
            "backup_path": backup_path
        }
    
    except Exception as e:
        error_message = f"Error updating file {path}: {str(e)}"
        logger.error(error_message)
        
        # Try to restore from backup if it exists
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, path)
                logger.info(f"Restored from backup after error")
        except Exception as restore_error:
            logger.error(f"Failed to restore from backup: {str(restore_error)}")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def append_to_file(path: str, snippet: str) -> dict:
    """
    Append content to the end of an existing file.
    
    Args:
        path (str): The full path to the file to append to
        snippet (str): The content to append to the file
        
    Returns:
        dict: A dictionary containing status and message
    """
    try:
        # Check if file exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"File does not exist at {path}. Use create_file() to create new files.",
                "path": path
            }
            
        # Create a backup of the file
        backup_path = f"{path}.bak"
        shutil.copy2(path, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        
        # Append the content to the file
        with open(path, 'a') as file:
            file.write(snippet)
        
        logger.info(f"Successfully appended to file: {path}")
        
        # Log to memory
        _log_to_memory("append_to_file", f"Appended content to file at {path}", path)
        
        return {
            "status": "success",
            "message": f"Content appended successfully to {path}",
            "path": path,
            "backup_path": backup_path
        }
    
    except Exception as e:
        error_message = f"Error appending to file {path}: {str(e)}"
        logger.error(error_message)
        
        # Try to restore from backup if it exists
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, path)
                logger.info(f"Restored from backup after error")
        except Exception as restore_error:
            logger.error(f"Failed to restore from backup: {str(restore_error)}")
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def delete_file(path: str) -> dict:
    """
    Delete an existing file.
    
    Args:
        path (str): The full path to the file to be deleted
        
    Returns:
        dict: A dictionary containing status and message
    """
    try:
        # Check if file exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"File does not exist at {path}.",
                "path": path
            }
            
        # Create a backup of the file
        backup_path = f"{path}.bak"
        shutil.copy2(path, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        
        # Delete the file
        os.remove(path)
        
        logger.info(f"Successfully deleted file: {path}")
        
        # Log to memory
        _log_to_memory("delete_file", f"Deleted file at {path}", path)
        
        return {
            "status": "success",
            "message": f"File deleted successfully at {path}",
            "path": path,
            "backup_path": backup_path
        }
    
    except Exception as e:
        error_message = f"Error deleting file {path}: {str(e)}"
        logger.error(error_message)
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }

def file_exists(path: str) -> dict:
    """
    Check if a file exists at the specified path.
    
    Args:
        path (str): The full path to check
        
    Returns:
        dict: A dictionary containing status, message, and exists flag
    """
    try:
        exists = os.path.exists(path)
        is_file = os.path.isfile(path) if exists else False
        
        logger.info(f"Checked existence of file at {path}: {'exists' if exists and is_file else 'does not exist'}")
        
        # Log to memory
        _log_to_memory("file_exists", f"Checked if file exists at {path}: {exists and is_file}", path)
        
        return {
            "status": "success",
            "message": f"File {'exists' if exists and is_file else 'does not exist'} at {path}",
            "path": path,
            "exists": exists and is_file
        }
    
    except Exception as e:
        error_message = f"Error checking file existence at {path}: {str(e)}"
        logger.error(error_message)
        
        return {
            "status": "error",
            "message": error_message,
            "error": str(e),
            "exists": False
        }

def _log_to_memory(operation: str, content: str, path: str):
    """
    Log file operations to memory.
    
    Args:
        operation (str): The operation performed (create, update, append, delete, check)
        content (str): Description of the operation
        path (str): The file path involved
    """
    try:
        from app.api.modules.memory import write_memory
        
        write_memory(
            agent_id="system",
            type="file_operation",
            content=content,
            tags=["tools", "file_writer", operation, path],
            task_type="file_operation",
            status="completed"
        )
        
        logger.info(f"Logged {operation} operation to memory for {path}")
    except Exception as e:
        logger.error(f"Failed to log operation to memory: {str(e)}")

# Add memory logging function for tool installation
def log_installation():
    """
    Log the installation of the file_writer tool to memory.
    This function should be called when the module is first imported.
    """
    try:
        from app.api.modules.memory import write_memory
        
        write_memory(
            agent_id="system",
            type="tool_installation",
            content="Installed enhanced file_writer.py tool for Phase 3.2 Agent Toolkit",
            tags=["tools", "file_writer", "installation", "toolkit_ready"],
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
