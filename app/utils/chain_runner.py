"""
Chain runner utility for internal FastAPI requests.

This module provides a helper function to run internal chain requests
without creating circular imports with the main app.
"""

import httpx
from typing import Dict, Any, List, Union

async def run_internal_chain(payload: Union[List[Dict[str, Any]], Dict[str, Any]], app_ref):
    """
    Run an internal chain request without importing the global app reference.
    
    This function uses httpx.AsyncClient with the app parameter to make
    internal FastAPI requests, avoiding circular imports.
    
    Args:
        payload: The JSON payload to send to the chain endpoint
        app_ref: The FastAPI app reference (passed from request.app)
        
    Returns:
        dict: The JSON response from the chain endpoint
    """
    try:
        async with httpx.AsyncClient(app=app_ref, base_url="http://testserver") as client:
            response = await client.post(
                "/api/orchestrator/chain", 
                json=payload,
                timeout=300.0  # 5 minute timeout for the entire chain execution
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Chain execution failed with status {response.status_code}",
                    "details": response.text
                }
                
            # Return the JSON response
            return response.json()
            
    except httpx.RequestError as e:
        # Handle connection errors
        return {
            "status": "error",
            "message": f"Connection error during chain execution: {str(e)}"
        }
        
    except httpx.TimeoutException as e:
        # Handle timeout errors
        return {
            "status": "error",
            "message": f"Timeout during chain execution: {str(e)}"
        }
        
    except Exception as e:
        # Handle unexpected errors
        return {
            "status": "error",
            "message": f"Unexpected error during chain execution: {str(e)}"
        }
