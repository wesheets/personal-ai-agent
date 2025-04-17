"""
Chain runner utility for internal FastAPI requests.

This module provides a helper function to run internal chain requests
without creating circular imports with the main app.
"""

import httpx
import logging
import traceback
from typing import Dict, Any, List, Union

# Configure logging
logger = logging.getLogger("app.utils.chain_runner")

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
        logger.info(f"🔗 CHAIN RUNNER: Starting internal chain execution")
        print(f"🔗 CHAIN RUNNER: Starting internal chain execution")
        
        logger.info(f"Chain payload: {payload}")
        
        async with httpx.AsyncClient(app=app_ref, base_url="http://testserver") as client:
            logger.info(f"Sending POST request to /api/orchestrator/chain")
            print(f"Sending POST request to /api/orchestrator/chain")
            
            response = await client.post(
                "/api/orchestrator/chain", 
                json=payload,
                timeout=300.0  # 5 minute timeout for the entire chain execution
            )
            
            logger.info(f"Received response with status code: {response.status_code}")
            print(f"Received response with status code: {response.status_code}")
            
            # Check if the request was successful
            if response.status_code != 200:
                error_message = f"Chain execution failed with status {response.status_code}"
                logger.error(f"❌ {error_message}")
                logger.error(f"Response text: {response.text}")
                print(f"❌ {error_message}")
                
                return {
                    "status": "error",
                    "message": error_message,
                    "details": response.text
                }
            
            # Parse the JSON response
            try:
                result = response.json()
                logger.info(f"Successfully parsed JSON response")
                
                # Log key parts of the response
                if "chain_id" in result:
                    logger.info(f"Chain ID: {result['chain_id']}")
                
                if "steps" in result:
                    logger.info(f"Number of steps: {len(result['steps'])}")
                    for i, step in enumerate(result['steps']):
                        logger.info(f"Step {i+1}: Agent={step.get('agent')}, Status={step.get('status')}")
                
                return result
            except Exception as json_error:
                logger.error(f"❌ Failed to parse JSON response: {str(json_error)}")
                logger.error(f"Response text: {response.text}")
                print(f"❌ Failed to parse JSON response: {str(json_error)}")
                
                return {
                    "status": "error",
                    "message": f"Failed to parse chain response: {str(json_error)}",
                    "details": response.text
                }
            
    except httpx.RequestError as e:
        # Handle connection errors
        error_message = f"Connection error during chain execution: {str(e)}"
        logger.error(f"❌ {error_message}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_message}")
        
        return {
            "status": "error",
            "message": error_message,
            "error_type": "connection_error"
        }
        
    except httpx.TimeoutException as e:
        # Handle timeout errors
        error_message = f"Timeout during chain execution: {str(e)}"
        logger.error(f"❌ {error_message}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_message}")
        
        return {
            "status": "error",
            "message": error_message,
            "error_type": "timeout"
        }
        
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Unexpected error during chain execution: {str(e)}"
        logger.error(f"❌ {error_message}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_message}")
        
        return {
            "status": "error",
            "message": error_message,
            "error_type": "unexpected",
            "traceback": traceback.format_exc()
        }
