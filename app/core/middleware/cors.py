"""
Custom CORS middleware for the Personal AI Agent system.

This module provides a reusable, self-contained CORS middleware implementation
that addresses common issues with origin matching and header sanitization.
"""
import re
import os
import logging
from typing import List, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response

# Configure logging
logger = logging.getLogger("cors")

# Default to False, can be enabled via environment variable
CORS_DEBUG = os.environ.get("CORS_DEBUG", "false").lower() == "true"

def normalize_origin(origin: str) -> str:
    """
    Normalize origin by stripping trailing slashes and converting to lowercase.
    
    Args:
        origin: The origin URL to normalize
        
    Returns:
        Normalized origin string
    """
    if not origin:
        return ""
    # Remove trailing slash if present and convert to lowercase
    normalized = origin.rstrip("/").lower()
    return normalized

def sanitize_origin_for_header(origin: str) -> str:
    """
    Sanitize origin for use in Access-Control-Allow-Origin header.
    Removes any trailing semicolons, commas, or other invalid characters.
    
    Args:
        origin: The origin URL to sanitize
        
    Returns:
        Sanitized origin string
    """
    if not origin:
        return ""
    
    # Remove any trailing semicolons, commas, or other invalid characters
    sanitized = origin.strip().replace(";", "").rstrip(",")
    
    if CORS_DEBUG:
        logger.info(f"✅ Sanitized Origin Header: '{sanitized}'")
    
    return sanitized

class CustomCORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware that uses strict string equality for origin matching
    and properly sanitizes headers to prevent injection issues.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        expose_headers: List[str] = None,
        max_age: int = 600,
    ) -> None:
        """
        Initialize the CustomCORSMiddleware.
        
        Args:
            app: The ASGI application
            allow_origins: List of allowed origins
            allow_methods: List of allowed HTTP methods
            allow_headers: List of allowed HTTP headers
            allow_credentials: Whether to allow credentials
            expose_headers: List of headers to expose
            max_age: Maximum age of preflight requests in seconds
        """
        super().__init__(app)
        
        # Initialize with safe defaults
        self.allow_origins = allow_origins or []
        self.normalized_origins = [normalize_origin(origin) for origin in self.allow_origins]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        
        logger.info(f"🔒 CustomCORSMiddleware initialized with {len(self.allow_origins)} origins")
        if CORS_DEBUG:
            logger.info(f"🔒 Allowed origins: {self.allow_origins}")
            logger.info(f"🔒 Normalized origins: {self.normalized_origins}")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add CORS headers to the response.
        
        Args:
            request: The incoming request
            call_next: The next middleware in the chain
            
        Returns:
            The response with CORS headers
        """
        # Get the origin from the request headers
        origin = request.headers.get("origin")
        
        # If no origin, just proceed with the request
        if not origin:
            if CORS_DEBUG:
                logger.info("🔒 No origin header in request, skipping CORS processing")
            return await call_next(request)
        
        # Normalize the request origin
        normalized_request_origin = normalize_origin(origin)
        if CORS_DEBUG:
            logger.info(f"🔒 CustomCORSMiddleware: Request Origin: {origin}")
            logger.info(f"🔒 CustomCORSMiddleware: Normalized Request Origin: {normalized_request_origin}")
            logger.info(f"🔍 CORS Debug: Comparing request origin '{normalized_request_origin}' to allowed origins")
            logger.info(f"🔍 CORS Debug: Full list of normalized allowed origins: {self.normalized_origins}")
        
        # Check if the normalized origin matches any of our normalized allowed origins
        # Using strict string equality instead of regex matching
        matching_origin = None
        for idx, norm_allowed in enumerate(self.normalized_origins):
            if CORS_DEBUG:
                logger.info(f"🔍 CORS Debug: Comparing '{normalized_request_origin}' == '{norm_allowed}'")
            
            # Use strict string equality for validation
            if normalized_request_origin == norm_allowed:
                # Get the original format but ensure it's sanitized
                matching_origin = sanitize_origin_for_header(self.allow_origins[idx])
                if CORS_DEBUG:
                    logger.info(f"🔒 CustomCORSMiddleware: Origin Match: ✅ Allowed (exact match with {norm_allowed})")
                    logger.info(f"✅ Sanitized Origin Header: '{matching_origin}'")
                break
            elif CORS_DEBUG:
                logger.info(f"🔍 CORS Debug: No match: '{normalized_request_origin}' != '{norm_allowed}'")
        
        # If no match found, return 403 Forbidden instead of using fallback
        if not matching_origin:
            logger.warning(f"🚫 CustomCORSMiddleware: No matching origin found for request: {origin}")
            return Response("Forbidden Origin", status_code=403)
        
        # If it's an OPTIONS request, return a response with CORS headers
        if request.method == "OPTIONS":
            if CORS_DEBUG:
                logger.info(f"🔒 CustomCORSMiddleware: OPTIONS request, returning CORS headers")
            headers = self._get_cors_headers(matching_origin)
            if CORS_DEBUG:
                logger.info(f"🔒 CustomCORSMiddleware: OPTIONS headers: {headers}")
            return Response(
                content="",
                status_code=200,
                headers=headers,
            )
        
        # For other requests, proceed with the request and add CORS headers to the response
        response = await call_next(request)
        
        # Add CORS headers to the response
        if matching_origin:
            if CORS_DEBUG:
                logger.info(f"🔒 CustomCORSMiddleware: Adding CORS headers to response")
            headers = self._get_cors_headers(matching_origin)
            for key, value in headers.items():
                # Explicitly log the exact header being set
                if CORS_DEBUG:
                    logger.info(f"🔒 Setting header: {key}='{value}'")
                response.headers[key] = value
            
            # Log the response headers for debugging
            if CORS_DEBUG:
                logger.info(f"🔒 CustomCORSMiddleware: Response headers: {dict(response.headers)}")
        else:
            logger.warning(f"🔒 CustomCORSMiddleware: No matching origin found, not adding CORS headers")
        
        return response
    
    def _get_cors_headers(self, origin: str) -> Dict[str, str]:
        """
        Get the CORS headers for a response.
        
        Args:
            origin: The origin to use in the Access-Control-Allow-Origin header
            
        Returns:
            Dictionary of CORS headers
        """
        # Ensure origin is sanitized
        clean_origin = sanitize_origin_for_header(origin)
        
        # Double-check for any remaining semicolons
        if ";" in clean_origin:
            logger.warning(f"⚠️ Semicolon still present after sanitization: '{clean_origin}'")
            clean_origin = clean_origin.replace(";", "")
            logger.info(f"🧹 Forcibly removed semicolon: '{clean_origin}'")
        
        headers = {
            "Access-Control-Allow-Origin": clean_origin,
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
        }
        
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        if self.max_age:
            headers["Access-Control-Max-Age"] = str(self.max_age)
        
        # Log the exact headers being returned
        if CORS_DEBUG:
            logger.info(f"🔒 CORS Headers: {headers}")
        
        return headers

def get_cors_middleware(
    allow_origins: List[str] = None,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
    allow_credentials: bool = False,
    expose_headers: List[str] = None,
    max_age: int = 600,
) -> CustomCORSMiddleware:
    """
    Factory function to create a CustomCORSMiddleware instance.
    
    Args:
        allow_origins: List of allowed origins
        allow_methods: List of allowed HTTP methods
        allow_headers: List of allowed HTTP headers
        allow_credentials: Whether to allow credentials
        expose_headers: List of headers to expose
        max_age: Maximum age of preflight requests in seconds
        
    Returns:
        CustomCORSMiddleware instance
    """
    return lambda app: CustomCORSMiddleware(
        app=app,
        allow_origins=allow_origins,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        allow_credentials=allow_credentials,
        expose_headers=expose_headers,
        max_age=max_age,
    )
