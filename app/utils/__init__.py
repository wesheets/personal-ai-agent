"""
Schema Validation Utils Initialization

This module initializes the schema validation utilities.
"""

import logging
from app.utils.schema_validation import validate_request_body, create_error_response

# Configure logging
logger = logging.getLogger("app.utils.__init__")

# Create empty __init__.py to make the directory a proper Python package
