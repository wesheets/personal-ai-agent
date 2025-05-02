"""
Retry Handler Module

This module provides a reusable retry mechanism with exponential backoff
for handling transient failures in API calls, memory operations, and other
potentially unstable operations.
"""

import time
import logging
import functools
import asyncio
from typing import Callable, Tuple, Type, Any, Optional, List, Dict, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_with_backoff(retries=3, backoff=2):
    """
    Decorator factory for retrying async functions with exponential backoff.
    
    Args:
        retries: Maximum number of retries (default: 3)
        backoff: Backoff factor for retry delay (default: 2)
        
    Returns:
        Decorator function that adds retry logic to the decorated function
    """
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    # If this is the last attempt, re-raise the exception
                    if attempt == retries - 1:
                        logger.error(f"❌ All {retries} retry attempts failed: {str(e)}")
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = backoff * (2 ** attempt)
                    
                    # Log the retry attempt
                    logger.warning(f"⚠️ Attempt {attempt + 1}/{retries} failed: {str(e)}. Retrying in {delay:.2f}s...")
                    print(f"⚠️ Retry {attempt + 1}/{retries}: {str(e)}. Waiting {delay:.2f}s...")
                    
                    # Wait before retrying
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            raise Exception(f"Function {fn.__name__} failed after {retries} retries.")
        return wrapper
    return decorator

# Legacy function - kept for backward compatibility with direct function calls
def _legacy_retry_with_backoff(
    fn: Callable, 
    retries: int = 3, 
    backoff: float = 1.5, 
    allowed_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Legacy retry function with exponential backoff.
    
    This function is kept for backward compatibility with direct function calls.
    New code should use the decorator factory version of retry_with_backoff.
    
    Args:
        fn: The function to retry
        retries: Maximum number of retries (default: 3)
        backoff: Backoff factor for retry delay (default: 1.5)
        allowed_exceptions: Tuple of exception types to catch and retry (default: all exceptions)
        
    Returns:
        The result of the function call
        
    Raises:
        The last exception encountered if all retries fail
    """
    logger.warning("Using deprecated direct call to retry_with_backoff. Use as decorator instead.")
    for attempt in range(retries):
        try:
            return fn()
        except allowed_exceptions as e:
            # If this is the last attempt, re-raise the exception
            if attempt == retries - 1:
                logger.error(f"❌ All {retries} retry attempts failed: {str(e)}")
                raise e
            
            # Calculate delay with exponential backoff
            delay = backoff ** attempt
            
            # Log the retry attempt
            logger.warning(f"⚠️ Attempt {attempt + 1}/{retries} failed: {str(e)}. Retrying in {delay:.2f}s...")
            print(f"⚠️ Retry {attempt + 1}/{retries}: {str(e)}. Waiting {delay:.2f}s...")
            
            # Wait before retrying
            time.sleep(delay)

def retry_async_with_backoff(
    fn: Callable, 
    retries: int = 3, 
    backoff: float = 1.5, 
    allowed_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    This is a wrapper for async functions that need to be retried.
    The actual retry logic is handled by the wrapped function.
    
    Args:
        fn: The async function to retry
        retries: Maximum number of retries (default: 3)
        backoff: Backoff factor for retry delay (default: 1.5)
        allowed_exceptions: Tuple of exception types to catch and retry (default: all exceptions)
        
    Returns:
        The result of the async function call
        
    Raises:
        The last exception encountered if all retries fail
    """
    async def async_retry_wrapper(*args, **kwargs):
        for attempt in range(retries):
            try:
                return await fn(*args, **kwargs)
            except allowed_exceptions as e:
                # If this is the last attempt, re-raise the exception
                if attempt == retries - 1:
                    logger.error(f"❌ All {retries} async retry attempts failed: {str(e)}")
                    raise e
                
                # Calculate delay with exponential backoff
                delay = backoff ** attempt
                
                # Log the retry attempt
                logger.warning(f"⚠️ Async attempt {attempt + 1}/{retries} failed: {str(e)}. Retrying in {delay:.2f}s...")
                print(f"⚠️ Async retry {attempt + 1}/{retries}: {str(e)}. Waiting {delay:.2f}s...")
                
                # Wait before retrying
                await asyncio.sleep(delay)
    
    return async_retry_wrapper

def retry_decorator(
    retries: int = 3, 
    backoff: float = 1.5, 
    allowed_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        retries: Maximum number of retries (default: 3)
        backoff: Backoff factor for retry delay (default: 1.5)
        allowed_exceptions: Tuple of exception types to catch and retry (default: all exceptions)
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def _retry_func():
                return func(*args, **kwargs)
            return _legacy_retry_with_backoff(_retry_func, retries, backoff, allowed_exceptions)
        return wrapper
    return decorator

def async_retry_decorator(
    retries: int = 3, 
    backoff: float = 1.5, 
    allowed_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        retries: Maximum number of retries (default: 3)
        backoff: Backoff factor for retry delay (default: 1.5)
        allowed_exceptions: Tuple of exception types to catch and retry (default: all exceptions)
        
    Returns:
        Decorated async function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except allowed_exceptions as e:
                    # If this is the last attempt, re-raise the exception
                    if attempt == retries - 1:
                        logger.error(f"❌ All {retries} async retry attempts failed: {str(e)}")
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = backoff ** attempt
                    
                    # Log the retry attempt
                    logger.warning(f"⚠️ Async attempt {attempt + 1}/{retries} failed: {str(e)}. Retrying in {delay:.2f}s...")
                    print(f"⚠️ Async retry {attempt + 1}/{retries}: {str(e)}. Waiting {delay:.2f}s...")
                    
                    # Wait before retrying
                    import asyncio
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
