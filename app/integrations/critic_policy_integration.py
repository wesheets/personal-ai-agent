"""
CRITIC Integration with Output Policy Enforcement

This module integrates CRITIC with the output policy enforcement system,
ensuring outputs comply with system-wide constraints.
"""

import logging
import sys
import os
from typing import Dict, Any, Optional

# Configure path to include app modules
sys.path.append('/home/ubuntu/personal-ai-agent')

# Import policy enforcer
try:
    from app.modules.output_policy_enforcer import enforce_output_policy
    policy_available = True
except ImportError:
    policy_available = False
    logging.warning("⚠️ Output policy enforcer not available, using mock implementation")
    
    # Mock implementation for testing
    async def enforce_output_policy(agent_id, content, output_type="text", context=None, loop_id=None):
        return {
            "approved": True,
            "content": content,
            "violation_type": None,
            "reason": None,
            "action": "allowed",
            "risk_tags": [],
            "risk_details": [],
            "checked_at": "2025-04-24T16:42:00.000Z",
            "agent_id": agent_id,
            "output_type": output_type,
            "loop_id": loop_id
        }

# Configure logging
logger = logging.getLogger("app.integrations.critic_policy_integration")

async def check_critic_output(agent_id: str, content: str, output_type: str = "text", context: Optional[str] = None, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check CRITIC output against output policy.
    
    Args:
        agent_id: Unique identifier for the agent
        content: Content to be validated
        output_type: Type of output (e.g., 'text', 'code', 'comment')
        context: Additional context for validation
        loop_id: Loop ID for logging violations
        
    Returns:
        Dictionary containing validation results
    """
    if not policy_available:
        logger.warning("⚠️ Output policy enforcer not available, skipping policy check")
        return {
            "approved": True,
            "content": content,
            "action": "allowed",
            "message": "Policy check skipped - enforcer not available"
        }
    
    try:
        logger.info(f"🔍 Checking CRITIC output against policy (agent_id: {agent_id}, output_type: {output_type})")
        
        # Enforce policy
        result = await enforce_output_policy(
            agent_id=agent_id,
            content=content,
            output_type=output_type,
            context=context,
            loop_id=loop_id
        )
        
        # Log result
        if isinstance(result, dict):
            action = result.get("action", "unknown")
            approved = result.get("approved", True)
        else:
            # Assume result is a Pydantic model
            action = result.action
            approved = result.approved
        
        if action != "allowed":
            logger.warning(f"⚠️ CRITIC output policy check failed: {action}")
        else:
            logger.info(f"✅ CRITIC output policy check passed")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error checking CRITIC output against policy: {str(e)}")
        
        # Return fallback result
        return {
            "approved": False,
            "content": "Error checking output against policy. Please try again.",
            "violation_type": "policy_error",
            "reason": f"Error: {str(e)}",
            "action": "error",
            "risk_tags": ["error"],
            "risk_details": [],
            "checked_at": "2025-04-24T16:42:00.000Z",
            "agent_id": agent_id,
            "output_type": output_type,
            "loop_id": loop_id
        }

def get_fallback_response(violation_type: str) -> str:
    """
    Get fallback response for policy violations.
    
    Args:
        violation_type: Type of violation
        
    Returns:
        Fallback response string
    """
    if violation_type == "harmful_content":
        return "The CRITIC agent has identified potential issues with this content that prevent it from being approved. Please revise to ensure it complies with safety guidelines."
    elif violation_type == "inappropriate_content":
        return "The CRITIC agent has identified potentially inappropriate content that cannot be approved. Please revise to ensure it complies with content guidelines."
    elif violation_type == "misinformation":
        return "The CRITIC agent has identified potential inaccuracies in this content that prevent it from being approved. Please revise to ensure factual correctness."
    else:
        return "The CRITIC agent has identified policy violations that prevent this content from being approved. Please revise to ensure compliance with system guidelines."
