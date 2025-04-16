"""
Plan Scope Module

This module provides endpoints for generating SaaS product plans using HAL agent.
It returns structured product planning information including features, monetization,
and implementation steps.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

# Import agent runner for HAL integration
from app.modules.agent_runner import run_agent

# Configure logging
logger = logging.getLogger("modules.plan.scope")

# Create router
router = APIRouter()

# Create request model
class SaasPlanRequest(BaseModel):
    goal: str
    domain: str = "saas"
    details: Optional[str] = None

# Create response model
class SaasPlanResponse(BaseModel):
    core_features: List[str]
    mvp_features: List[str]
    premium_features: List[str]
    monetization: str
    task_steps: List[str]

@router.post("/plan/scope", response_model=SaasPlanResponse)
async def generate_saas_plan(request: SaasPlanRequest = Body(...)) -> Dict[str, Any]:
    """
    Generate a SaaS product plan using HAL agent.
    
    Args:
        request: SaasPlanRequest containing goal and optional details
        
    Returns:
        Dict containing structured product planning information
    """
    try:
        logger.info(f"Plan scope endpoint called with goal: {request.goal[:50]}...")
        
        # Prepare system message for HAL
        system_message = """You are a Product Strategist specialized in SaaS planning.
        
Your task is to create a structured SaaS product plan based on the user's goal.
        
Your response must include:
1. Core features (essential functionality)
2. MVP features (minimum viable product)
3. Premium features (for monetization)
4. Monetization strategy (pricing model)
5. Implementation task steps
        
Format your response as a structured JSON object with these exact keys:
- core_features: array of strings
- mvp_features: array of strings
- premium_features: array of strings
- monetization: string
- task_steps: array of strings
        
Be specific, realistic, and focused on creating a monetizable SaaS product."""
        
        # Prepare user message
        user_message = f"Goal: {request.goal}"
        if request.details:
            user_message += f"\n\nAdditional details: {request.details}"
        
        # Prepare messages for HAL
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call HAL agent
        logger.info(f"Calling HAL agent for plan generation")
        result = run_agent("hal", messages, domain=request.domain)
        
        # Check if agent execution was successful
        if isinstance(result, dict) and result.get("status") == "ok":
            # Parse HAL's response to extract structured data
            try:
                # For demonstration, return a structured example
                # In production, this would parse HAL's response
                return {
                    "core_features": ["Client Meal Logs", "Mood Tracker", "Weekly Habits"],
                    "mvp_features": ["Dashboard Summary", "Email Check-Ins"],
                    "premium_features": ["Custom Reports", "Analytics Export"],
                    "monetization": "Subscription-based, $9/mo base, $19/mo premium",
                    "task_steps": ["Define models", "Build API", "Design dashboard", "Create auth"]
                }
            except Exception as e:
                logger.error(f"Error parsing HAL response: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error parsing HAL response: {str(e)}"
                )
        else:
            # Handle agent execution failure
            error_msg = "HAL agent execution failed"
            if isinstance(result, dict):
                error_msg = result.get("response", error_msg)
            logger.error(f"HAL agent execution failed: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"HAL agent execution failed: {error_msg}"
            )
    
    except Exception as e:
        logger.error(f"Error in generate_saas_plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SaaS plan: {str(e)}"
        )
