"""
Main Application Update

This module updates the main FastAPI application to integrate the schema validation middleware.
"""

import logging
from fastapi import FastAPI
from app.core.schema_validation_integration import add_schema_validation_middleware

# Configure logging
logger = logging.getLogger("app.main_update")

def update_main_application(app: FastAPI) -> None:
    """
    Update the main FastAPI application with schema validation middleware.
    
    This function should be called in main.py after the FastAPI app is created
    but before any routes are registered.
    
    Args:
        app: The FastAPI application
    """
    logger.info("Updating main application with schema validation middleware")
    
    # Add schema validation middleware
    add_schema_validation_middleware(app)
    
    logger.info("Main application updated successfully")
