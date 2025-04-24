"""
Schema Integrity Utility

This module provides utilities for tracking schema checksums and validating schema integrity,
helping to detect schema drift and ensure consistent schema usage across agents.
"""

import hashlib
import inspect
import logging
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger("schema_integrity")

def get_schema_checksum(schema_class: Any) -> str:
    """
    Generate a checksum for a schema class based on its source code.
    
    Args:
        schema_class: The schema class to generate a checksum for
        
    Returns:
        A hexadecimal string representing the SHA-256 hash of the class source
    """
    try:
        # Get the source code of the class
        source_code = inspect.getsource(schema_class)
        
        # Generate SHA-256 hash of the source code
        checksum = hashlib.sha256(source_code.encode()).hexdigest()
        
        logger.info(f"✅ Generated checksum for {schema_class.__name__}: {checksum[:8]}...")
        return checksum
    except Exception as e:
        logger.error(f"❌ Error generating checksum for {getattr(schema_class, '__name__', 'unknown')}: {str(e)}")
        # Return a fallback checksum that indicates an error
        return f"error-{hashlib.sha256(str(e).encode()).hexdigest()[:16]}"

def log_schema_checksum(memory_writer, project_id: str, schema_class: Any) -> Dict[str, Any]:
    """
    Log a schema checksum to memory for drift detection.
    
    Args:
        memory_writer: Function to write to memory (e.g., memory.write)
        project_id: The project ID to log the checksum for
        schema_class: The schema class to generate and log a checksum for
        
    Returns:
        The result of the memory write operation
    """
    try:
        # Get the schema class name
        schema_name = schema_class.__name__
        
        # Generate the checksum
        checksum = get_schema_checksum(schema_class)
        
        # Log to memory
        result = memory_writer(
            project_id=project_id,
            tag="schema_hashes",
            value={schema_name: checksum}
        )
        
        logger.info(f"✅ Logged schema checksum for {schema_name} to memory")
        return result
    except Exception as e:
        logger.error(f"❌ Error logging schema checksum: {str(e)}")
        return {
            "status": "error",
            "message": f"Error logging schema checksum: {str(e)}",
            "schema": getattr(schema_class, '__name__', 'unknown')
        }

def verify_schema_integrity(memory_reader, project_id: str, schema_class: Any) -> Dict[str, Any]:
    """
    Verify the integrity of a schema class against its previously logged checksum.
    
    Args:
        memory_reader: Function to read from memory (e.g., memory.read)
        project_id: The project ID to check the checksum for
        schema_class: The schema class to verify
        
    Returns:
        Dict containing the verification result
    """
    try:
        # Get the schema class name
        schema_name = schema_class.__name__
        
        # Generate the current checksum
        current_checksum = get_schema_checksum(schema_class)
        
        # Read the previous checksum from memory
        memory_data = memory_reader(project_id=project_id, tag="schema_hashes")
        
        if not memory_data or "value" not in memory_data:
            logger.warning(f"⚠️ No previous checksum found for {schema_name}")
            return {
                "status": "unknown",
                "message": f"No previous checksum found for {schema_name}",
                "schema": schema_name,
                "current_checksum": current_checksum
            }
        
        # Get the previous checksum
        previous_checksums = memory_data.get("value", {})
        previous_checksum = previous_checksums.get(schema_name)
        
        if not previous_checksum:
            logger.warning(f"⚠️ No previous checksum found for {schema_name}")
            return {
                "status": "unknown",
                "message": f"No previous checksum found for {schema_name}",
                "schema": schema_name,
                "current_checksum": current_checksum
            }
        
        # Compare checksums
        if current_checksum == previous_checksum:
            logger.info(f"✅ Schema integrity verified for {schema_name}")
            return {
                "status": "verified",
                "message": f"Schema integrity verified for {schema_name}",
                "schema": schema_name,
                "checksum": current_checksum
            }
        else:
            logger.warning(f"⚠️ Schema drift detected for {schema_name}")
            return {
                "status": "drift_detected",
                "message": f"Schema drift detected for {schema_name}",
                "schema": schema_name,
                "current_checksum": current_checksum,
                "previous_checksum": previous_checksum
            }
    except Exception as e:
        logger.error(f"❌ Error verifying schema integrity: {str(e)}")
        return {
            "status": "error",
            "message": f"Error verifying schema integrity: {str(e)}",
            "schema": getattr(schema_class, '__name__', 'unknown')
        }
