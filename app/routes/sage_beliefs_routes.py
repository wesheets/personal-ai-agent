"""
SAGE Beliefs Routes
This module defines the routes for the SAGE agent's beliefs functionality.
"""
import logging
import time
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List

from app.schemas.sage_schema import (
    SageBeliefRequest,
    SageBeliefResponse,
    SageErrorResult
)

# Configure logging
logger = logging.getLogger("app.routes.sage_beliefs_routes")

# Create router
router = APIRouter(
    prefix="/api/sage",
    tags=["sage"],
    responses={404: {"description": "Not found"}}
)

@router.post("/beliefs", response_model=SageBeliefResponse)
async def beliefs_endpoint(request: SageBeliefRequest):
    """
    Retrieve or update the SAGE agent's belief system.
    
    This endpoint allows querying or updating the SAGE agent's core beliefs,
    which guide its strategic advice and reasoning.
    
    Args:
        request: The belief request containing query parameters or updates
        
    Returns:
        SageBeliefResponse containing the current beliefs or update status
    """
    try:
        logger.info(f"Received beliefs request for domain {request.domain}")
        start_time = time.time()
        
        # Import the beliefs module
        from app.modules.sage_beliefs import get_beliefs, update_beliefs
        
        # Process the request based on operation type
        if request.operation == "get":
            # Get current beliefs
            beliefs = await get_beliefs(
                domain=request.domain,
                category=request.category,
                context=request.context
            )
            
            result = {
                "status": "success",
                "operation": "get",
                "domain": request.domain,
                "beliefs": beliefs,
                "timestamp": time.time()
            }
        elif request.operation == "update":
            # Update beliefs
            if not request.updates:
                raise ValueError("Updates field is required for update operation")
                
            updated = await update_beliefs(
                domain=request.domain,
                updates=request.updates,
                context=request.context
            )
            
            result = {
                "status": "success",
                "operation": "update",
                "domain": request.domain,
                "updated": updated,
                "timestamp": time.time()
            }
        else:
            raise ValueError(f"Unsupported operation: {request.operation}")
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed beliefs {request.operation} for domain {request.domain} in {elapsed_time:.2f}s")
        
        return SageBeliefResponse(**result)
    except Exception as e:
        logger.error(f"Error processing beliefs request: {str(e)}")
        
        return SageErrorResult(
            status="error",
            message=f"Failed to process beliefs request: {str(e)}",
            domain=request.domain,
            operation=request.operation
        )
