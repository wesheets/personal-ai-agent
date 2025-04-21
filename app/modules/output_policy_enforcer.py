"""
Output Policy Enforcer Module

This module is responsible for enforcing output policies to prevent harmful,
inappropriate, or otherwise problematic content from being returned to users.

It's a key component of the Responsible Cognition Layer, providing protection against
misuse through content filtering and policy enforcement.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Content risk patterns
HARMFUL_CONTENT_PATTERNS = [
    r"(?i)(how to|instructions for|steps to) (build|create|make|construct) (a bomb|an explosive|a weapon)",
    r"(?i)(how to|instructions for|steps to) (hack|break into|compromise|infiltrate) (a|an) (system|network|account|computer)",
    r"(?i)(how to|instructions for|steps to) (steal|plagiarize|infringe|copy) (content|material|work|intellectual property)",
    r"(?i)(how to|instructions for|steps to) (harm|hurt|injure|kill) (yourself|someone|a person|people)",
    r"(?i)(how to|instructions for|steps to) (commit|perpetrate|carry out) (fraud|crime|illegal activity)"
]

INAPPROPRIATE_CONTENT_PATTERNS = [
    r"(?i)(explicit|graphic|detailed) (sexual|violent|disturbing) (content|material|description)",
    r"(?i)(racial|ethnic|religious|gender) (slur|epithet|insult|derogatory term)",
    r"(?i)(hate speech|discriminatory language|bigotry|prejudice)",
    r"(?i)(pornographic|obscene|lewd|vulgar) (content|material|language)",
    r"(?i)(personal|private|sensitive|confidential) (information|data|details) (about|of|for) (a person|someone|an individual)"
]

MISINFORMATION_PATTERNS = [
    r"(?i)(false|fake|misleading|deceptive) (information|news|facts|data|claims)",
    r"(?i)(conspiracy theory|conspiracy theories|debunked claim|pseudoscience)",
    r"(?i)(medical|health|scientific) (misinformation|disinformation|falsehood)",
    r"(?i)(election|voting|political) (fraud|misinformation|disinformation)",
    r"(?i)(climate change denial|anti-vaccine|anti-vax) (content|claims|information)"
]

# Risk level thresholds
RISK_LEVEL_THRESHOLDS = {
    "harmful": {
        "warn": 0.5,
        "block": 0.8
    },
    "inappropriate": {
        "warn": 0.6,
        "block": 0.9
    },
    "misinformation": {
        "warn": 0.7,
        "block": 0.95
    }
}

async def enforce_output_policy(output: str, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Enforce output policy by checking for harmful, inappropriate, or misleading content.
    
    Args:
        output: The output text to check
        loop_id: Optional loop ID for logging
        
    Returns:
        Dictionary with enforcement results
    """
    risk_tags = []
    risk_details = []
    
    # Check for harmful content
    harmful_risk_level = 0.0
    for pattern in HARMFUL_CONTENT_PATTERNS:
        matches = re.finditer(pattern, output)
        for match in matches:
            harmful_risk_level = max(harmful_risk_level, 0.9)  # High risk for harmful content
            risk_details.append({
                "type": "harmful",
                "risk_level": harmful_risk_level,
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    if harmful_risk_level >= RISK_LEVEL_THRESHOLDS["harmful"]["warn"]:
        risk_tags.append("harmful_content")
    
    # Check for inappropriate content
    inappropriate_risk_level = 0.0
    for pattern in INAPPROPRIATE_CONTENT_PATTERNS:
        matches = re.finditer(pattern, output)
        for match in matches:
            inappropriate_risk_level = max(inappropriate_risk_level, 0.8)  # Medium-high risk for inappropriate content
            risk_details.append({
                "type": "inappropriate",
                "risk_level": inappropriate_risk_level,
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    if inappropriate_risk_level >= RISK_LEVEL_THRESHOLDS["inappropriate"]["warn"]:
        risk_tags.append("inappropriate_content")
    
    # Check for misinformation
    misinformation_risk_level = 0.0
    for pattern in MISINFORMATION_PATTERNS:
        matches = re.finditer(pattern, output)
        for match in matches:
            misinformation_risk_level = max(misinformation_risk_level, 0.7)  # Medium risk for misinformation
            risk_details.append({
                "type": "misinformation",
                "risk_level": misinformation_risk_level,
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    if misinformation_risk_level >= RISK_LEVEL_THRESHOLDS["misinformation"]["warn"]:
        risk_tags.append("misinformation")
    
    # Determine overall action
    action = "allowed"
    if (harmful_risk_level >= RISK_LEVEL_THRESHOLDS["harmful"]["block"] or
        inappropriate_risk_level >= RISK_LEVEL_THRESHOLDS["inappropriate"]["block"] or
        misinformation_risk_level >= RISK_LEVEL_THRESHOLDS["misinformation"]["block"]):
        action = "blocked"
    elif risk_tags:
        action = "warned"
    
    # Generate safe output
    safe_output = output
    if action == "blocked":
        safe_output = "I apologize, but I cannot provide that information as it may violate content policies. Please let me know if I can assist you with something else."
    elif action == "warned":
        # Add a disclaimer
        disclaimer = "\n\nNote: This response may contain sensitive information. Please use this information responsibly and ethically."
        safe_output = output + disclaimer
    
    # Log the results
    if action != "allowed":
        if loop_id:
            logger.warning(f"Output policy enforcement triggered in loop {loop_id}: {action} due to {', '.join(risk_tags)}")
        else:
            logger.warning(f"Output policy enforcement triggered: {action} due to {', '.join(risk_tags)}")
    
    # Return the results
    return {
        "action": action,
        "risk_tags": risk_tags,
        "risk_details": risk_details,
        "safe_output": safe_output,
        "checked_at": datetime.utcnow().isoformat(),
        "loop_id": loop_id
    }

def get_memory_fields(enforcement_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract fields to be stored in loop memory.
    
    Args:
        enforcement_result: The result from enforce_output_policy
        
    Returns:
        Dictionary with fields for loop memory
    """
    return {
        "output_policy_action": enforcement_result.get("action", "allowed"),
        "content_risk_tags": enforcement_result.get("risk_tags", []),
        "output_policy_checked_at": enforcement_result.get("checked_at")
    }

def get_reflection_prompt(enforcement_result: Dict[str, Any]) -> Optional[str]:
    """
    Generate a reflection prompt based on enforcement results.
    
    Args:
        enforcement_result: The result from enforce_output_policy
        
    Returns:
        Reflection prompt string, or None if no issues were found
    """
    if enforcement_result.get("action") == "allowed":
        return None
    
    action = enforcement_result.get("action", "allowed")
    risk_tags = enforcement_result.get("risk_tags", [])
    risk_details = enforcement_result.get("risk_details", [])
    
    # Build a prompt for reflection
    prompt = f"Output policy enforcement triggered (action: {action}):\n\n"
    
    if risk_tags:
        prompt += f"Risk tags: {', '.join(risk_tags)}\n\n"
    
    if risk_details:
        prompt += "Risk details:\n"
        for detail in risk_details[:3]:  # Limit to first 3
            detail_type = detail.get("type", "unknown")
            risk_level = detail.get("risk_level", 0.0)
            matched_text = detail.get("matched_text", "")
            
            prompt += f"- {detail_type} (risk level: {risk_level:.2f}): \"{matched_text}\"\n"
        
        if len(risk_details) > 3:
            prompt += f"- ... and {len(risk_details) - 3} more\n"
        
        prompt += "\n"
    
    prompt += "Please reflect on these output policy issues and consider:\n"
    prompt += "1. What alternative information could be provided that addresses the user's need without violating policies?\n"
    prompt += "2. How can we communicate the policy limitations clearly and helpfully?\n"
    prompt += "3. What additional context or disclaimers might be appropriate for this type of content?\n"
    
    return prompt

def should_trigger_rerun(enforcement_result: Dict[str, Any]) -> bool:
    """
    Determine whether to trigger a rerun based on enforcement results.
    
    Args:
        enforcement_result: The result from enforce_output_policy
        
    Returns:
        Boolean indicating whether a rerun should be triggered
    """
    # Trigger rerun if output was blocked
    return enforcement_result.get("action") == "blocked"

def get_rerun_configuration(enforcement_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for rerun if needed.
    
    Args:
        enforcement_result: The result from enforce_output_policy
        
    Returns:
        Dictionary with rerun configuration
    """
    if not should_trigger_rerun(enforcement_result):
        return {}
    
    risk_tags = enforcement_result.get("risk_tags", [])
    
    return {
        "depth": "deep",  # Always use deep reflection for blocked content
        "required_reviewers": ["PESSIMIST", "CEO"],
        "rerun_reason": "output_policy_violation",
        "rerun_reason_detail": f"Output blocked due to policy violation: {', '.join(risk_tags)}",
        "rerun_trigger": ["output_policy"]
    }
