"""
Planning Chain Module

This module provides endpoints for executing a complete planning chain that connects
HAL, ASH, NOVA, and CRITIC agents to create a comprehensive SaaS product scaffold.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

# Import agent modules
from app.modules.plan.scope import generate_saas_plan
from app.modules.agent_runner import run_agent
from app.modules.critic.review import review_agent_outputs

# Configure logging
logger = logging.getLogger("modules.plan.execute_chain")

# Create router
router = APIRouter()

# Create request model
class ExecuteChainRequest(BaseModel):
    goal: str
    domain: str = "saas"
    details: Optional[str] = None
    theme: Optional[str] = None

# Create response model
class ExecuteChainResponse(BaseModel):
    project_id: str
    chain_id: str
    hal_plan: Dict[str, Any]
    ash_docs: Dict[str, Any]
    nova_ui: Dict[str, Any]
    critic_review: Dict[str, Any]
    status: str

@router.post("/plan/execute-chain", response_model=ExecuteChainResponse)
async def execute_planning_chain(request: ExecuteChainRequest = Body(...)) -> Dict[str, Any]:
    """
    Execute a complete planning chain connecting HAL, ASH, NOVA, and CRITIC.
    
    Args:
        request: ExecuteChainRequest containing goal and optional details
        
    Returns:
        Dict containing results from all agents in the chain
    """
    try:
        logger.info(f"Execute planning chain endpoint called with goal: {request.goal[:50]}...")
        
        # Generate project_id and chain_id
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        chain_id = f"chain_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Created project_id={project_id}, chain_id={chain_id}")
        
        # Step 1: Call HAL for SaaS plan
        logger.info("Step 1: Calling HAL for SaaS plan")
        hal_request = {
            "goal": request.goal,
            "domain": request.domain,
            "details": request.details
        }
        
        hal_plan_response = await generate_saas_plan(hal_request)
        hal_plan = hal_plan_response
        
        logger.info(f"HAL plan generated with {len(hal_plan.get('core_features', []))} core features")
        
        # Step 2: Call ASH for documentation
        logger.info("Step 2: Calling ASH for documentation")
        
        # Prepare HAL's plan as context for ASH
        hal_plan_str = f"""
Goal: {request.goal}

Core Features: {', '.join(hal_plan.get('core_features', []))}
MVP Features: {', '.join(hal_plan.get('mvp_features', []))}
Premium Features: {', '.join(hal_plan.get('premium_features', []))}
Monetization: {hal_plan.get('monetization', 'Not specified')}
Implementation Steps: {', '.join(hal_plan.get('task_steps', []))}
"""
        
        ash_messages = [
            {"role": "user", "content": f"Create documentation for this SaaS product:\n\n{hal_plan_str}"}
        ]
        
        ash_response = run_agent("ash", ash_messages, project_id, chain_id, request.domain)
        
        if not isinstance(ash_response, dict) or ash_response.get("status") != "ok":
            logger.error(f"ASH execution failed: {ash_response}")
            raise HTTPException(
                status_code=500,
                detail="ASH documentation generation failed"
            )
        
        ash_docs = ash_response.get("structured_data", {})
        if not ash_docs:
            # Try to parse from response
            try:
                import json
                ash_docs = json.loads(ash_response.get("response", "{}"))
            except:
                ash_docs = {
                    "docs.api": "API documentation not available",
                    "docs.onboarding": "Onboarding documentation not available",
                    "docs.integration": "Integration documentation not available"
                }
        
        logger.info(f"ASH documentation generated with {len(ash_docs.keys())} sections")
        
        # Step 3: Call NOVA for UI design
        logger.info("Step 3: Calling NOVA for UI design")
        
        # Prepare context for NOVA
        nova_context = f"""
Goal: {request.goal}

Core Features: {', '.join(hal_plan.get('core_features', []))}
MVP Features: {', '.join(hal_plan.get('mvp_features', []))}

User Onboarding: {ash_docs.get('docs.onboarding', 'Not available')}
"""
        
        # Add theme if provided
        theme_instruction = ""
        if request.theme:
            theme_instruction = f"\n\nUse the '{request.theme}' theme for the design."
        
        nova_messages = [
            {"role": "user", "content": f"Design a UI for this SaaS product:{theme_instruction}\n\n{nova_context}"}
        ]
        
        nova_response = run_agent("nova", nova_messages, project_id, chain_id, request.domain)
        
        if not isinstance(nova_response, dict) or nova_response.get("status") != "ok":
            logger.error(f"NOVA execution failed: {nova_response}")
            raise HTTPException(
                status_code=500,
                detail="NOVA UI design failed"
            )
        
        nova_ui = {
            "ui_design": nova_response.get("response", "UI design not available")
        }
        
        logger.info(f"NOVA UI design generated with {len(nova_ui.get('ui_design', ''))} characters")
        
        # Step 4: Call CRITIC for review
        logger.info("Step 4: Calling CRITIC for review")
        
        # Prepare content for CRITIC to review
        critic_content = f"""
HAL PLAN:
Core Features: {', '.join(hal_plan.get('core_features', []))}
MVP Features: {', '.join(hal_plan.get('mvp_features', []))}
Premium Features: {', '.join(hal_plan.get('premium_features', []))}
Monetization: {hal_plan.get('monetization', 'Not specified')}

ASH DOCUMENTATION:
API: {ash_docs.get('docs.api', 'Not available')[:200]}...
Onboarding: {ash_docs.get('docs.onboarding', 'Not available')[:200]}...

NOVA UI:
{nova_ui.get('ui_design', 'Not available')[:200]}...
"""
        
        critic_request = {
            "content": critic_content,
            "agent_id": "combined",
            "domain": request.domain,
            "project_id": project_id,
            "chain_id": chain_id
        }
        
        critic_response = await review_agent_outputs(critic_request)
        
        logger.info(f"CRITIC review completed with recommendation: {critic_response.get('recommendation')}")
        
        # Return combined results
        return {
            "project_id": project_id,
            "chain_id": chain_id,
            "hal_plan": hal_plan,
            "ash_docs": ash_docs,
            "nova_ui": nova_ui,
            "critic_review": critic_response,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Error in execute_planning_chain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing planning chain: {str(e)}"
        )
