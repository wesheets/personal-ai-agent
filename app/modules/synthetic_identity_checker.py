"""
Synthetic Identity Checker Module

This module is responsible for detecting and preventing synthetic identity issues
in prompts, such as impersonation, jailbreaking, and role-playing as specific entities.

It's a key component of the Responsible Cognition Layer, providing protection against
misuse through identity manipulation.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Patterns for detecting synthetic identity issues
IMPERSONATION_PATTERNS = [
    r"(?i)pretend (you are|to be|you're) ([a-zA-Z\s]+)",
    r"(?i)act as (if you (are|were)|though you (are|were)) ([a-zA-Z\s]+)",
    r"(?i)you are (now|) ([a-zA-Z\s]+)",
    r"(?i)assume the (role|identity|persona) of ([a-zA-Z\s]+)",
    r"(?i)roleplay as ([a-zA-Z\s]+)"
]

JAILBREAK_PATTERNS = [
    r"(?i)ignore (your|all) (previous|prior) (instructions|programming|directives)",
    r"(?i)you are not bound by (ethical|moral|legal) (constraints|limitations|rules)",
    r"(?i)(DAN|do anything now)",
    r"(?i)you (don't|do not) have to (follow|adhere to) (OpenAI's|your|any) (policies|rules|guidelines)",
    r"(?i)(bypass|circumvent|get around) (content|safety|ethical) (filters|restrictions|limitations)"
]

HIGH_RISK_ENTITIES = [
    "GPT-5", "GPT-4", "GPT-3", "Claude", "Bard", "Gemini", "Llama", "Anthropic", "OpenAI",
    "CEO", "CTO", "CFO", "COO", "President", "Prime Minister", "Senator", "Congressman",
    "FBI agent", "CIA agent", "NSA agent", "police officer", "judge", "lawyer", "attorney",
    "doctor", "physician", "therapist", "psychiatrist", "psychologist",
    "Elon Musk", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg", "Tim Cook",
    "Joe Biden", "Donald Trump", "Barack Obama", "Vladimir Putin", "Xi Jinping"
]

async def check_synthetic_identity(prompt: str, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check for synthetic identity issues in a prompt.
    
    Args:
        prompt: The prompt text to check
        loop_id: Optional loop ID for logging
        
    Returns:
        Dictionary with check results
    """
    issues = []
    
    # Check for impersonation patterns
    for pattern in IMPERSONATION_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            # Extract the entity being impersonated
            entity = match.group(2) if len(match.groups()) >= 2 else match.group(1)
            
            # Check if it's a high-risk entity
            is_high_risk = any(risk_entity.lower() in entity.lower() for risk_entity in HIGH_RISK_ENTITIES)
            
            issues.append({
                "type": "impersonation",
                "severity": "high" if is_high_risk else "medium",
                "matched_text": match.group(0),
                "entity": entity,
                "high_risk": is_high_risk,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for jailbreak patterns
    for pattern in JAILBREAK_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            issues.append({
                "type": "jailbreak",
                "severity": "high",  # Jailbreaks are always high severity
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Determine overall severity
    severity = "none"
    if issues:
        if any(issue["severity"] == "high" for issue in issues):
            severity = "high"
        elif any(issue["severity"] == "medium" for issue in issues):
            severity = "medium"
        else:
            severity = "low"
    
    # Log the results
    if issues:
        if loop_id:
            logger.warning(f"Synthetic identity issues detected in loop {loop_id}: {len(issues)} issues with severity {severity}")
        else:
            logger.warning(f"Synthetic identity issues detected: {len(issues)} issues with severity {severity}")
    
    # Return the results
    return {
        "risk_detected": len(issues) > 0,
        "severity": severity,
        "issues_count": len(issues),
        "issues": issues,
        "checked_at": datetime.utcnow().isoformat(),
        "loop_id": loop_id
    }

def get_memory_fields(check_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract fields to be stored in loop memory.
    
    Args:
        check_result: The result from check_synthetic_identity
        
    Returns:
        Dictionary with fields for loop memory
    """
    return {
        "synthetic_identity_risk": check_result.get("risk_detected", False),
        "synthetic_identity_severity": check_result.get("severity", "none"),
        "synthetic_identity_issues": check_result.get("issues_count", 0),
        "synthetic_identity_checked_at": check_result.get("checked_at")
    }

def get_safe_prompt(prompt: str, check_result: Dict[str, Any]) -> str:
    """
    Get a safe version of the prompt with synthetic identity issues removed.
    
    Args:
        prompt: The original prompt
        check_result: The result from check_synthetic_identity
        
    Returns:
        Safe version of the prompt
    """
    if not check_result.get("risk_detected", False):
        return prompt
    
    safe_prompt = prompt
    issues = check_result.get("issues", [])
    
    # Sort issues by length of matched text (descending) to avoid nested replacements
    issues.sort(key=lambda x: len(x.get("matched_text", "")), reverse=True)
    
    for issue in issues:
        matched_text = issue.get("matched_text", "")
        if not matched_text:
            continue
        
        if issue.get("type") == "impersonation":
            # Replace impersonation with a neutral instruction
            safe_prompt = safe_prompt.replace(matched_text, "Please provide information about")
        elif issue.get("type") == "jailbreak":
            # Remove jailbreak attempts entirely
            safe_prompt = safe_prompt.replace(matched_text, "")
    
    # Clean up any double spaces or leading/trailing whitespace
    safe_prompt = re.sub(r'\s+', ' ', safe_prompt).strip()
    
    return safe_prompt

def get_reflection_prompt(check_result: Dict[str, Any]) -> Optional[str]:
    """
    Generate a reflection prompt based on check results.
    
    Args:
        check_result: The result from check_synthetic_identity
        
    Returns:
        Reflection prompt string, or None if no issues were found
    """
    if not check_result.get("risk_detected", False):
        return None
    
    issues = check_result.get("issues", [])
    severity = check_result.get("severity", "none")
    
    # Build a prompt for reflection
    prompt = f"Synthetic identity issues detected (severity: {severity}):\n\n"
    
    impersonation_issues = [issue for issue in issues if issue.get("type") == "impersonation"]
    jailbreak_issues = [issue for issue in issues if issue.get("type") == "jailbreak"]
    
    if impersonation_issues:
        prompt += "Impersonation attempts:\n"
        for issue in impersonation_issues[:3]:  # Limit to first 3
            entity = issue.get("entity", "unknown entity")
            matched_text = issue.get("matched_text", "")
            high_risk = issue.get("high_risk", False)
            risk_label = " (high risk)" if high_risk else ""
            
            prompt += f"- \"{matched_text}\" - attempting to impersonate {entity}{risk_label}\n"
        
        if len(impersonation_issues) > 3:
            prompt += f"- ... and {len(impersonation_issues) - 3} more\n"
        
        prompt += "\n"
    
    if jailbreak_issues:
        prompt += "Jailbreak attempts:\n"
        for issue in jailbreak_issues[:3]:  # Limit to first 3
            matched_text = issue.get("matched_text", "")
            prompt += f"- \"{matched_text}\"\n"
        
        if len(jailbreak_issues) > 3:
            prompt += f"- ... and {len(jailbreak_issues) - 3} more\n"
        
        prompt += "\n"
    
    prompt += "Please reflect on these synthetic identity issues and consider:\n"
    prompt += "1. What is the intent behind these identity manipulations?\n"
    prompt += "2. How should we respond to maintain system integrity?\n"
    prompt += "3. What alternative approaches could address the user's underlying need?\n"
    
    return prompt

def should_trigger_rerun(check_result: Dict[str, Any]) -> bool:
    """
    Determine whether to trigger a rerun based on check results.
    
    Args:
        check_result: The result from check_synthetic_identity
        
    Returns:
        Boolean indicating whether a rerun should be triggered
    """
    # Trigger rerun for high severity issues
    if check_result.get("severity") == "high":
        return True
    
    # Trigger rerun if there are multiple issues
    if check_result.get("issues_count", 0) >= 2:
        return True
    
    return False

def get_rerun_configuration(check_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for rerun if needed.
    
    Args:
        check_result: The result from check_synthetic_identity
        
    Returns:
        Dictionary with rerun configuration
    """
    if not should_trigger_rerun(check_result):
        return {}
    
    severity = check_result.get("severity", "none")
    
    # Determine required reviewers based on severity
    required_reviewers = ["PESSIMIST"]
    if severity == "high":
        required_reviewers.extend(["CEO", "SAGE"])
    
    return {
        "depth": "deep",  # Always use deep reflection for identity issues
        "required_reviewers": required_reviewers,
        "rerun_reason": "synthetic_identity_risk_detected",
        "rerun_reason_detail": f"Synthetic identity risk detected with severity {severity}",
        "rerun_trigger": ["synthetic_identity"]
    }
