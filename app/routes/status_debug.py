"""
Status Debug Routes Module

This module provides a simple health check endpoint for Render deployment.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/debug/status")
def status_check():
    """
    Simple health check endpoint that returns a 200 OK response.
    Used by Render to verify the application is running properly.
    
    Returns:
        dict: A simple status message
    """
    return {"status": "ok"}
