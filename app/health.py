"""
Health check endpoint for Railway deployment.

This module provides a simple health check endpoint that returns a 200 OK response
when the application is running properly. This is used by Railway to determine
if the deployment is healthy.
"""

from fastapi import APIRouter

# Create a router for health check endpoints
health_router = APIRouter(tags=["Health"])

@health_router.get("/health")
async def health_check():
    """
    Simple health check endpoint that returns a 200 OK response.
    Used by Railway to verify the application is running properly.
    """
    return {"status": "ok"}
