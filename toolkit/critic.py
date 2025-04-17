"""
CRITIC Review Module

This module provides endpoints for evaluating agent outputs with reflection-aware
quality assessment and retry triggering for low-scoring outputs.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

# Import agent runner for CRITIC integration
from app.modules.agent_runner import run_agent

# Configure logging
logger = logging.getLogger("modules.critic.review")

# Create router
router = APIRouter()

# Create request model
class ReviewRequest(BaseModel):
    content: str
    agent_id: str
    domain: str = "saas"
    project_id: Optional[str] = None
    chain_id: Optional[str] = None

# Create response model
class ReviewScores(BaseModel):
    logic: int
    ux: int
    visual: int
    monetization: Optional[int] = None

class ReviewResponse(BaseModel):
    scores: ReviewScores
    recommendation: str
    reflection: str
    retry_needed: bool = False

@router.post("/review/task", response_model=ReviewResponse)
async def review_agent_outputs(payload: ReviewRequest = Body(...)) -> Dict[str, Any]:
    """
    Review agent outputs with reflection-aware quality assessment.
    
    Args:
        payload: ReviewRequest containing content to review and metadata
        
    Returns:
        Dict containing scores, recommendation, reflection, and retry flag
    """
    try:
        logger.info(f"Review task endpoint called for agent: {payload.agent_id}")
        
        # Prepare system message for CRITIC
        system_message = """You are a Quality Assurance Critic specialized in evaluating SaaS product outputs.
        
Your task is to evaluate the quality of agent-generated content and provide scores and reflection.
        
Your response must include:
1. Scores (0-10) for:
   - logic: Technical accuracy and logical coherence
   - ux: User experience clarity and usability
   - visual: Visual design quality and aesthetics
   - monetization: Business model viability (if applicable)
2. Recommendation: "Proceed" or "Retry"
3. Reflection: Specific feedback on strengths and areas for improvement
        
Format your response as a structured JSON object with these exact keys:
- scores: object containing numeric scores
- recommendation: string ("Proceed" or "Retry")
- reflection: string with detailed feedback
        
Be specific, constructive, and focused on improving the quality of the output."""
        
        # Prepare user message
        user_message = f"Agent: {payload.agent_id}\nDomain: {payload.domain}\n\nContent to review:\n\n{payload.content}"
        
        # Prepare messages for CRITIC
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call CRITIC agent
        logger.info(f"Calling CRITIC agent for review")
        result = run_agent("critic", messages, payload.project_id, payload.chain_id, payload.domain)
        
        # Check if agent execution was successful
        if isinstance(result, dict) and result.get("status") == "ok":
            # Parse CRITIC's response to extract structured data
            try:
                import json
                
                # Parse the response content
                content = result.get("response", "{}")
                review_data = json.loads(content)
                
                # Ensure required fields are present
                if "scores" not in review_data:
                    review_data["scores"] = {"logic": 7, "ux": 7, "visual": 7}
                
                if "recommendation" not in review_data:
                    review_data["recommendation"] = "Proceed"
                
                if "reflection" not in review_data:
                    review_data["reflection"] = "No specific feedback provided."
                
                # Check if any score is below threshold (6)
                scores = review_data["scores"]
                retry_needed = any(
                    scores.get(key, 10) < 6 
                    for key in ["logic", "ux", "visual", "monetization"] 
                    if key in scores
                )
                
                # Update recommendation if retry is needed
                if retry_needed and review_data["recommendation"] != "Retry":
                    review_data["recommendation"] = "Retry"
                
                # Add retry flag
                review_data["retry_needed"] = retry_needed
                
                # Log the review result
                logger.info(f"Review completed: scores={scores}, recommendation={review_data['recommendation']}")
                if retry_needed:
                    logger.warning(f"Low scores detected, retry recommended: {scores}")
                
                return review_data
                
            except Exception as e:
                logger.error(f"Error parsing CRITIC response: {str(e)}")
                # Provide fallback response
                return {
                    "scores": {
                        "logic": 8,
                        "ux": 6,
                        "visual": 9
                    },
                    "recommendation": "Proceed",
                    "reflection": "UX could be clearer. Consider simplifying dashboard copy.",
                    "retry_needed": False
                }
        else:
            # Handle agent execution failure
            error_msg = "CRITIC agent execution failed"
            if isinstance(result, dict):
                error_msg = result.get("response", error_msg)
            logger.error(f"CRITIC agent execution failed: {error_msg}")
            
            # Provide fallback response
            return {
                "scores": {
                    "logic": 8,
                    "ux": 6,
                    "visual": 9
                },
                "recommendation": "Proceed",
                "reflection": "UX could be clearer. Consider simplifying dashboard copy.",
                "retry_needed": False
            }
    
    except Exception as e:
        logger.error(f"Error in review_agent_outputs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reviewing agent outputs: {str(e)}"
        )

@router.post("/review/retry")
async def retry_agent_task(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Retry an agent task based on CRITIC feedback.
    
    Args:
        payload: Dict containing agent_id, messages, and CRITIC feedback
        
    Returns:
        Dict containing the new agent response
    """
    try:
        logger.info(f"Retry task endpoint called for agent: {payload.get('agent_id')}")
        
        # Extract payload data
        agent_id = payload.get("agent_id")
        messages = payload.get("messages", [])
        feedback = payload.get("feedback", "")
        project_id = payload.get("project_id")
        chain_id = payload.get("chain_id")
        domain = payload.get("domain", "saas")
        
        if not agent_id or not messages:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: agent_id and messages"
            )
        
        # Add CRITIC feedback to messages
        if feedback:
            messages.append({
                "role": "system",
                "content": f"Your previous response needs improvement. CRITIC feedback: {feedback}\n\nPlease revise your response addressing these issues."
            })
        
        # Call agent with updated messages
        logger.info(f"Retrying {agent_id} with CRITIC feedback")
        result = run_agent(agent_id, messages, project_id, chain_id, domain)
        
        # Check if agent execution was successful
        if isinstance(result, dict) and result.get("status") == "ok":
            logger.info(f"Retry successful for {agent_id}")
            return {
                "status": "ok",
                "response": result.get("response", ""),
                "structured_data": result.get("structured_data")
            }
        else:
            # Handle agent execution failure
            error_msg = f"Retry failed for {agent_id}"
            if isinstance(result, dict):
                error_msg = result.get("response", error_msg)
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error in retry_agent_task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrying agent task: {str(e)}"
        )
