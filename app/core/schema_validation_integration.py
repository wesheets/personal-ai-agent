"""
Schema Validation Integration

This module provides functions to integrate the schema validation middleware and utilities
into the FastAPI application.
"""

import logging
from fastapi import FastAPI
from app.middleware.schema_validation import SchemaValidationMiddleware, DefaultValueMiddleware

# Configure logging
logger = logging.getLogger("app.core.schema_validation_integration")

def add_schema_validation_middleware(app: FastAPI) -> None:
    """
    Add schema validation middleware to the FastAPI application.
    
    This function adds middleware components that provide:
    1. Standardized error handling for schema validation errors
    2. Default value handling for common fields
    
    Args:
        app: The FastAPI application
    """
    logger.info("Adding schema validation middleware to application")
    
    # Add default value middleware first (so it runs before validation)
    app.add_middleware(DefaultValueMiddleware)
    
    # Add schema validation middleware
    app.add_middleware(SchemaValidationMiddleware)
    
    logger.info("Schema validation middleware added successfully")
