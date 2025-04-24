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

def retry_with_backoff(
    fn: Callable, 
    retries: int = 3, 
    backoff: float = 1.5, 
    allowed_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Retry a function with exponential backoff.
    
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
            return retry_with_backoff(_retry_func, retries, backoff, allowed_exceptions)
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
