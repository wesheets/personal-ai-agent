"""
Schema Validation Middleware Initialization

This module initializes the schema validation middleware and integrates it with the main application.
"""

import logging
from fastapi import FastAPI
from app.middleware.schema_validation import SchemaValidationMiddleware, DefaultValueMiddleware
from app.utils.schema_validation import validate_request_body, create_error_response

# Configure logging
logger = logging.getLogger("app.middleware.__init__")

# Create empty __init__.py to make the directory a proper Python package
