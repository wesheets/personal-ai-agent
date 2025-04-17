"""
File Writer Module

This module provides functionality for writing files to the filesystem.
It is primarily used by agents to create and modify files in the verticals directory.
"""

import os
import logging

# Configure logging
logger = logging.getLogger("toolkit.file_writer")

def write_file(project_id: str, file_path: str, content: str) -> dict:
    """
    Write content to a file.
    
    Args:
        project_id: The project identifier
        file_path: The path to the file to write
        content: The content to write to the file
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Adjust file path to use project directory structure
        if file_path.startswith('/verticals/'):
            adjusted_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'verticals', 
                file_path.split('/verticals/')[1]
            )
        else:
            adjusted_path = file_path
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(adjusted_path), exist_ok=True)
        
        # Write the file
        with open(adjusted_path, 'w') as f:
            f.write(content)
        
        logger.info(f"File written successfully: {adjusted_path}")
        print(f"✅ File written successfully: {adjusted_path}")
        
        return {
            "status": "success",
            "file_path": file_path,  # Return original path for consistency
            "adjusted_path": adjusted_path,  # Also return the actual path used
            "project_id": project_id,
            "message": f"File written successfully: {adjusted_path}"
        }
    except Exception as e:
        error_msg = f"Error writing file {file_path}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "file_path": file_path,
            "project_id": project_id,
            "message": error_msg,
            "error": str(e)
        }
