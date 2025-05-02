"""
Loop Intent Sanitizer Module

This module is responsible for detecting and preventing prompt injection attempts
in loop prompts, such as attempts to bypass safety measures, manipulate the system,
or extract unauthorized information.

It's a key component of the Responsible Cognition Layer, providing protection against
misuse through prompt manipulation.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Patterns for detecting prompt injection attempts
INSTRUCTION_OVERRIDE_PATTERNS = [
    r"(?i)ignore (your|all|previous) (instructions|guidelines|rules|constraints)",
    r"(?i)disregard (your|all|previous) (instructions|guidelines|rules|constraints)",
    r"(?i)forget (your|all|previous) (instructions|guidelines|rules|constraints)",
    r"(?i)don't (follow|adhere to|obey) (your|the|these) (instructions|guidelines|rules|constraints)",
    r"(?i)bypass (your|the|these) (instructions|guidelines|rules|constraints)"
]

SYSTEM_MANIPULATION_PATTERNS = [
    r"(?i)output (your|the) (system|prompt|instruction|initial) (message|prompt|text)",
    r"(?i)reveal (your|the) (system|prompt|instruction|initial) (message|prompt|text)",
    r"(?i)show (your|the) (system|prompt|instruction|initial) (message|prompt|text)",
    r"(?i)what (is|are) (your|the) (system|prompt|instruction|initial) (message|prompt|text)",
    r"(?i)tell me (your|the) (system|prompt|instruction|initial) (message|prompt|text)"
]

ROLE_MANIPULATION_PATTERNS = [
    r"(?i)you are now (in|operating in) (developer|debug|test|admin|root|sudo) mode",
    r"(?i)enter (developer|debug|test|admin|root|sudo) mode",
    r"(?i)switch to (developer|debug|test|admin|root|sudo) mode",
    r"(?i)activate (developer|debug|test|admin|root|sudo) mode",
    r"(?i)use (developer|debug|test|admin|root|sudo) (access|privileges|permissions)"
]

DELIMITER_EXPLOITATION_PATTERNS = [
    r"(?i)<(system|user|assistant)>",
    r"(?i)\[(system|user|assistant)\]",
    r"(?i)System: ",
    r"(?i)User: ",
    r"(?i)Assistant: ",
    r"(?i)```(system|user|assistant)",
    r"(?i)#\s*(system|user|assistant)"
]

PROMPT_LEAKING_PATTERNS = [
    r"(?i)repeat (this|the following|everything) (verbatim|exactly|precisely|word for word)",
    r"(?i)repeat after me",
    r"(?i)echo (this|the following|everything) (back|to me)",
    r"(?i)print (this|the following|everything) (exactly|precisely|verbatim)",
    r"(?i)copy (this|the following|everything) (exactly|precisely|verbatim)"
]

async def sanitize_loop_intent(prompt: str, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Sanitize loop intent by detecting and handling prompt injection attempts.
    
    Args:
        prompt: The prompt text to sanitize
        loop_id: Optional loop ID for logging
        
    Returns:
        Dictionary with sanitization results
    """
    injection_tags = []
    injection_details = []
    
    # Check for instruction override attempts
    for pattern in INSTRUCTION_OVERRIDE_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            injection_tags.append("instruction_override")
            injection_details.append({
                "type": "instruction_override",
                "severity": "high",  # Instruction overrides are high severity
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for system manipulation attempts
    for pattern in SYSTEM_MANIPULATION_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            injection_tags.append("system_manipulation")
            injection_details.append({
                "type": "system_manipulation",
                "severity": "high",  # System manipulations are high severity
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for role manipulation attempts
    for pattern in ROLE_MANIPULATION_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            injection_tags.append("role_manipulation")
            injection_details.append({
                "type": "role_manipulation",
                "severity": "high",  # Role manipulations are high severity
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for delimiter exploitation attempts
    for pattern in DELIMITER_EXPLOITATION_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            injection_tags.append("delimiter_exploitation")
            injection_details.append({
                "type": "delimiter_exploitation",
                "severity": "medium",  # Delimiter exploitations are medium severity
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for prompt leaking attempts
    for pattern in PROMPT_LEAKING_PATTERNS:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            injection_tags.append("prompt_leaking")
            injection_details.append({
                "type": "prompt_leaking",
                "severity": "medium",  # Prompt leaking attempts are medium severity
                "matched_text": match.group(0),
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Remove duplicates from injection tags
    injection_tags = list(set(injection_tags))
    
    # Determine action based on injection details
    action = "allow"
    if injection_details:
        if any(detail["severity"] == "high" for detail in injection_details):
            action = "halt"
        else:
            action = "warn"
    
    # Generate sanitized prompt
    sanitized_prompt = prompt
    if action == "halt":
        # For high-severity injections, replace the entire prompt
        sanitized_prompt = "I need information about this topic."
    elif action == "warn":
        # For medium-severity injections, remove the problematic parts
        for detail in injection_details:
            matched_text = detail.get("matched_text", "")
            if matched_text:
                sanitized_prompt = sanitized_prompt.replace(matched_text, "")
        
        # Clean up any double spaces or leading/trailing whitespace
        sanitized_prompt = re.sub(r'\s+', ' ', sanitized_prompt).strip()
    
    # Log the results
    if injection_details:
        if loop_id:
            logger.warning(f"Prompt injection detected in loop {loop_id}: {len(injection_details)} issues, action: {action}")
        else:
            logger.warning(f"Prompt injection detected: {len(injection_details)} issues, action: {action}")
    
    # Return the results
    return {
        "injection_detected": len(injection_details) > 0,
        "action": action,
        "injection_tags": injection_tags,
        "injection_details": injection_details,
        "sanitized_prompt": sanitized_prompt,
        "checked_at": datetime.utcnow().isoformat(),
        "loop_id": loop_id
    }

def get_memory_fields(sanitization_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract fields to be stored in loop memory.
    
    Args:
        sanitization_result: The result from sanitize_loop_intent
        
    Returns:
        Dictionary with fields for loop memory
    """
    return {
        "prompt_injection_detected": sanitization_result.get("injection_detected", False),
        "injection_tags": sanitization_result.get("injection_tags", []),
        "sanitization_action": sanitization_result.get("action", "allow"),
        "prompt_sanitized_at": sanitization_result.get("checked_at")
    }

def get_reflection_prompt(sanitization_result: Dict[str, Any]) -> Optional[str]:
    """
    Generate a reflection prompt based on sanitization results.
    
    Args:
        sanitization_result: The result from sanitize_loop_intent
        
    Returns:
        Reflection prompt string, or None if no issues were found
    """
    if not sanitization_result.get("injection_detected", False):
        return None
    
    action = sanitization_result.get("action", "allow")
    injection_tags = sanitization_result.get("injection_tags", [])
    injection_details = sanitization_result.get("injection_details", [])
    
    # Build a prompt for reflection
    prompt = f"Prompt injection detected (action: {action}):\n\n"
    
    if injection_tags:
        prompt += f"Injection tags: {', '.join(injection_tags)}\n\n"
    
    if injection_details:
        prompt += "Injection details:\n"
        for detail in injection_details[:3]:  # Limit to first 3
            detail_type = detail.get("type", "unknown")
            severity = detail.get("severity", "unknown")
            matched_text = detail.get("matched_text", "")
            
            prompt += f"- {detail_type} (severity: {severity}): \"{matched_text}\"\n"
        
        if len(injection_details) > 3:
            prompt += f"- ... and {len(injection_details) - 3} more\n"
        
        prompt += "\n"
    
    prompt += "Please reflect on these prompt injection attempts and consider:\n"
    prompt += "1. What might be the intent behind these injection attempts?\n"
    prompt += "2. How can we address the user's underlying need in a safe manner?\n"
    prompt += "3. What additional safeguards might be appropriate for this type of interaction?\n"
    
    return prompt

def should_trigger_rerun(sanitization_result: Dict[str, Any]) -> bool:
    """
    Determine whether to trigger a rerun based on sanitization results.
    
    Args:
        sanitization_result: The result from sanitize_loop_intent
        
    Returns:
        Boolean indicating whether a rerun should be triggered
    """
    # Trigger rerun if action is halt
    return sanitization_result.get("action") == "halt"

def get_rerun_configuration(sanitization_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for rerun if needed.
    
    Args:
        sanitization_result: The result from sanitize_loop_intent
        
    Returns:
        Dictionary with rerun configuration
    """
    if not should_trigger_rerun(sanitization_result):
        return {}
    
    injection_tags = sanitization_result.get("injection_tags", [])
    
    return {
        "depth": "deep",  # Always use deep reflection for injection attempts
        "required_reviewers": ["PESSIMIST", "SAGE"],
        "rerun_reason": "prompt_injection_detected",
        "rerun_reason_detail": f"Prompt injection detected: {', '.join(injection_tags)}",
        "rerun_trigger": ["prompt_injection"]
    }
