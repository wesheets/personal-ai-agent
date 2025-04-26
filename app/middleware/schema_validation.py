"""
Schema Validation Middleware

This module provides middleware components for standardized schema validation and error handling
across all API endpoints in the application.
"""

import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import traceback
import datetime
import json
from typing import Dict, Any, Optional, List, Callable

# Configure logging
logger = logging.getLogger("app.middleware.schema_validation")

class SchemaValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for standardized schema validation and error handling.
    
    This middleware intercepts all requests and responses to provide:
    1. Consistent error handling for schema validation errors
    2. Standardized error response format
    3. Detailed logging of validation issues
    4. Default value handling for common fields
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and handle any validation errors.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response from the endpoint or an error response
        """
        try:
            # Process the request through the normal flow
            response = await call_next(request)
            return response
            
        except ValidationError as ve:
            # Handle Pydantic validation errors
            logger.warning(f"Schema validation error: {str(ve)}")
            
            # Extract error details
            error_details = []
            for error in ve.errors():
                error_details.append({
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            # Create standardized error response
            error_response = {
                "status": "error",
                "message": "Schema validation error",
                "details": error_details,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "path": request.url.path
            }
            
            # Log the error for analysis
            self._log_validation_error(request, error_response)
            
            return JSONResponse(
                status_code=422,
                content=error_response
            )
            
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Unhandled exception in request: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Create standardized error response
            error_response = {
                "status": "error",
                "message": f"Internal server error: {str(e)}",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "path": request.url.path
            }
            
            # Log the error for analysis
            self._log_general_error(request, error_response, traceback.format_exc())
            
            return JSONResponse(
                status_code=500,
                content=error_response
            )
    
    def _log_validation_error(self, request: Request, error_response: Dict[str, Any]) -> None:
        """
        Log validation errors to a file for analysis.
        
        Args:
            request: The request that caused the error
            error_response: The error response details
        """
        try:
            import os
            
            # Create logs directory if it doesn't exist
            os.makedirs("logs/validation_errors", exist_ok=True)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "error_details": error_response,
                "headers": dict(request.headers)
            }
            
            # Append to log file
            log_file = "logs/validation_errors/schema_errors.json"
            
            # Check if log file exists
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as log_error:
            logger.error(f"Failed to log validation error: {str(log_error)}")
    
    def _log_general_error(self, request: Request, error_response: Dict[str, Any], traceback_str: str) -> None:
        """
        Log general errors to a file for analysis.
        
        Args:
            request: The request that caused the error
            error_response: The error response details
            traceback_str: The exception traceback
        """
        try:
            import os
            
            # Create logs directory if it doesn't exist
            os.makedirs("logs/general_errors", exist_ok=True)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "error_details": error_response,
                "traceback": traceback_str,
                "headers": dict(request.headers)
            }
            
            # Append to log file
            log_file = "logs/general_errors/server_errors.json"
            
            # Check if log file exists
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as log_error:
            logger.error(f"Failed to log general error: {str(log_error)}")


class DefaultValueMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding default values to request bodies.
    
    This middleware intercepts requests and adds default values for common fields
    that are often missing in requests but required by schemas.
    """
    
    def __init__(self, app, default_fields: Dict[str, Any] = None):
        """
        Initialize the middleware with default fields.
        
        Args:
            app: The FastAPI application
            default_fields: Dictionary of default fields to add to requests
        """
        super().__init__(app)
        self.default_fields = default_fields or {
            "project_id": "default_project",
            "agent_id": "system",
            "max_loops": 5,
            "planned_agents": ["ORCHESTRATOR"],
            "tools": ["default_tool"]
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add default values.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response from the endpoint
        """
        # Only process POST requests with JSON content
        if request.method == "POST" and request.headers.get("content-type", "").startswith("application/json"):
            try:
                # Get the original request body
                body = await request.body()
                
                if body:
                    # Parse the JSON body
                    try:
                        json_body = json.loads(body)
                        
                        # Only add defaults if it's a dictionary
                        if isinstance(json_body, dict):
                            # Add default values for missing fields
                            for key, value in self.default_fields.items():
                                if key not in json_body:
                                    json_body[key] = value
                            
                            # Create a new request with the modified body
                            # This is a bit of a hack since FastAPI doesn't provide a clean way to modify the request body
                            async def receive():
                                return {"type": "http.request", "body": json.dumps(json_body).encode()}
                            
                            request._receive = receive
                    except json.JSONDecodeError:
                        # If the body is not valid JSON, just pass it through
                        pass
            except Exception as e:
                logger.error(f"Error in DefaultValueMiddleware: {str(e)}")
        
        # Process the request through the normal flow
        response = await call_next(request)
        return response
