"""
Error Classification Module

This module provides utilities for classifying errors into standardized categories,
enabling consistent error handling, logging, and recovery strategies across the system.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Type, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define error categories
ERROR_CATEGORIES = {
    "QuotaError": ["quota", "insufficient", "exceeded your current quota", "billing", "payment required"],
    "RateLimitError": ["rate limit", "too many requests", "429", "throttled"],
    "ModelNotFoundError": ["model not found", "404", "not available", "does not exist"],
    "AuthenticationError": ["authentication", "unauthorized", "invalid api key", "401"],
    "SchemaDriftError": ["schema", "validation error", "422", "invalid format"],
    "NetworkError": ["network", "connection", "timeout", "socket", "unreachable"],
    "MemoryError": ["memory", "storage", "database", "read/write"],
    "ServiceUnavailableError": ["service unavailable", "server error", "503", "502", "500"],
    "InputError": ["input", "invalid parameter", "bad request", "400"],
    "UnknownError": []  # Fallback category
}

def classify_error(e: Exception) -> str:
    """
    Classify an exception into a standardized error category.
    
    Args:
        e: The exception to classify
        
    Returns:
        String representing the error category
    """
    # Convert exception message to lowercase for case-insensitive matching
    error_msg = str(e).lower()
    error_type = type(e).__name__
    
    # Check each category for matching keywords
    for category, keywords in ERROR_CATEGORIES.items():
        # Skip the UnknownError category as it's the fallback
        if category == "UnknownError":
            continue
            
        # Check if any keyword is in the error message or error type
        if any(keyword in error_msg for keyword in keywords) or category.lower() in error_type.lower():
            logger.info(f"✅ Classified error as {category}: {error_msg}")
            return category
    
    # If no category matched, return UnknownError
    logger.warning(f"⚠️ Could not classify error, defaulting to UnknownError: {error_msg}")
    return "UnknownError"

def get_error_details(e: Exception) -> Dict[str, Any]:
    """
    Get detailed information about an exception.
    
    Args:
        e: The exception to analyze
        
    Returns:
        Dict containing error details
    """
    # Get the error category
    category = classify_error(e)
    
    # Get the stack trace
    stack_trace = traceback.format_exc()
    
    # Return structured error details
    return {
        "category": category,
        "type": type(e).__name__,
        "message": str(e),
        "stack_trace": stack_trace
    }

def log_error_to_memory(
    memory_writer: callable,
    project_id: str,
    agent_id: str,
    e: Exception,
    operation: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log an error to memory with classification.
    
    Args:
        memory_writer: Function to write to memory
        project_id: Project identifier
        agent_id: Agent identifier
        e: The exception to log
        operation: Optional description of the operation that failed
        
    Returns:
        Dict containing the result of the memory write operation
    """
    try:
        # Get error details
        error_details = get_error_details(e)
        
        # Add metadata
        error_details.update({
            "timestamp": "now",  # Memory system will replace with actual timestamp
            "project_id": project_id,
            "agent_id": agent_id,
            "operation": operation or "unknown_operation"
        })
        
        # Log to memory
        result = memory_writer(
            project_id=project_id,
            tag="agent_error_log",
            value=error_details
        )
        
        logger.info(f"✅ Logged {error_details['category']} error to memory: {str(e)}")
        return result
    except Exception as log_error:
        logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
        return {
            "status": "error",
            "message": f"Failed to log error to memory: {str(log_error)}",
            "error": str(log_error)
        }

def is_retryable_error(e: Exception) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        e: The exception to check
        
    Returns:
        Boolean indicating whether the error is retryable
    """
    # Get the error category
    category = classify_error(e)
    
    # Define retryable categories
    retryable_categories = [
        "RateLimitError",
        "NetworkError",
        "ServiceUnavailableError"
    ]
    
    # Check if the category is retryable
    return category in retryable_categories
