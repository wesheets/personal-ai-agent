# Environment Variables Standardization

import os
import logging

logger = logging.getLogger("env")

class EnvManager:
    """
    Centralized environment variable manager to standardize access
    and provide proper error handling for missing variables.
    """
    
    @staticmethod
    def get(key, default=None, required=False):
        """
        Get an environment variable with proper error handling.
        
        Args:
            key (str): The environment variable name
            default: The default value if not found
            required (bool): Whether the variable is required
            
        Returns:
            The environment variable value or default
            
        Raises:
            ValueError: If the variable is required but not found
        """
        value = os.environ.get(key, default)
        
        if required and value is None:
            error_msg = f"Required environment variable {key} is not set"
            logger.error(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)
            
        return value
