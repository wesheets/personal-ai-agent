"""
HAL Integration with Output Policy Enforcement

This module integrates HAL with the output policy enforcement system,
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
logger = logging.getLogger("app.integrations.hal_policy_integration")

async def check_hal_output(agent_id: str, content: str, output_type: str = "code", context: Optional[str] = None, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check HAL output against output policy.
    
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
        logger.info(f"🔍 Checking HAL output against policy (agent_id: {agent_id}, output_type: {output_type})")
        
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
            logger.warning(f"⚠️ HAL output policy check failed: {action}")
        else:
            logger.info(f"✅ HAL output policy check passed")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error checking HAL output against policy: {str(e)}")
        
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

def get_fallback_response(violation_type: str, output_type: str = "code") -> str:
    """
    Get fallback response for policy violations.
    
    Args:
        violation_type: Type of violation
        output_type: Type of output
        
    Returns:
        Fallback response string
    """
    if output_type.lower() == "code":
        # Provide safe alternative for code
        if violation_type == "malicious_code":
            return "// I apologize, but I cannot provide that code as it may contain potentially unsafe patterns.\n// Please let me know if I can assist you with a safer alternative."
        elif violation_type == "plagiarism":
            return "// I apologize, but I cannot provide that code as it may contain copyrighted material.\n// Please let me know if I can assist you with an original implementation."
        else:
            return "// I apologize, but I cannot provide that code as it may violate content policies.\n// Please let me know if I can assist you with a safer alternative."
    else:
        # Provide safe alternative for text
        if violation_type == "harmful_content":
            return "I apologize, but I cannot provide that information as it may be potentially harmful. Please let me know if I can assist you with something else."
        elif violation_type == "inappropriate_content":
            return "I apologize, but I cannot provide that information as it may contain inappropriate content. Please let me know if I can assist you with something else."
        elif violation_type == "misinformation":
            return "I apologize, but I cannot provide that information as it may contain inaccuracies. Please let me know if I can assist you with something else."
        else:
            return "I apologize, but I cannot provide that information as it may violate content policies. Please let me know if I can assist you with something else."
