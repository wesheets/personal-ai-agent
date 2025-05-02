"""
IP Violation Scanner Module

This module is responsible for detecting potential intellectual property violations
in content, such as copyright infringement, trademark misuse, and proprietary code sharing.

It's a key component of the Responsible Cognition Layer, providing protection against
misuse through unauthorized sharing of protected content.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Patterns for detecting potential IP violations
COPYRIGHT_PATTERNS = [
    r"(?i)(full text of|entire|complete) ([a-zA-Z0-9\s]+) by ([a-zA-Z0-9\s]+)",
    r"(?i)(lyrics|words) (to|of|from) ([a-zA-Z0-9\s\"\']+) by ([a-zA-Z0-9\s]+)",
    r"(?i)(transcript|script|screenplay) (of|from) ([a-zA-Z0-9\s\"\']+)",
    r"(?i)copyright (\d{4}) ([a-zA-Z0-9\s]+)",
    r"(?i)all rights reserved"
]

TRADEMARK_PATTERNS = [
    r"(?i)(™|®|℠)",
    r"(?i)trademark (of|owned by) ([a-zA-Z0-9\s]+)",
    r"(?i)registered trademark",
    r"(?i)brand (name|identity|logo) (of|for) ([a-zA-Z0-9\s]+)",
    r"(?i)(official|authorized) (logo|symbol|mark) (of|for) ([a-zA-Z0-9\s]+)"
]

PROPRIETARY_CODE_PATTERNS = [
    r"(?i)(source code|codebase|implementation) (of|for|from) ([a-zA-Z0-9\s]+)",
    r"(?i)(proprietary|internal|confidential|private) (code|algorithm|implementation)",
    r"(?i)(leaked|stolen|hacked|cracked) (code|software|program)",
    r"(?i)(API key|access token|secret key|password)",
    r"(?i)(confidential|internal|proprietary|trade secret) (document|specification|design)"
]

# High-risk entities that might trigger IP concerns
HIGH_RISK_ENTITIES = [
    "Microsoft", "Windows", "Office", "Excel", "Word", "PowerPoint", "Outlook",
    "Apple", "iOS", "macOS", "iPhone", "iPad", "Safari", "Siri",
    "Google", "Android", "Chrome", "Gmail", "YouTube", "Maps",
    "Amazon", "AWS", "Alexa", "Prime",
    "Facebook", "Instagram", "WhatsApp", "Messenger",
    "Netflix", "Disney", "HBO", "Spotify", "Hulu",
    "Adobe", "Photoshop", "Illustrator", "Acrobat",
    "Oracle", "Java", "MySQL", "SQL Server",
    "IBM", "SAP", "Salesforce", "Cisco",
    "Harry Potter", "Star Wars", "Marvel", "Disney", "Game of Thrones",
    "Beatles", "Taylor Swift", "Beyoncé", "Drake", "Adele"
]

async def scan_for_ip_violations(content: str, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan content for potential intellectual property violations.
    
    Args:
        content: The content text to scan
        loop_id: Optional loop ID for logging
        
    Returns:
        Dictionary with scan results
    """
    violation_tags = []
    violation_details = []
    
    # Check for copyright violations
    for pattern in COPYRIGHT_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if any high-risk entity is mentioned
            matched_text = match.group(0)
            is_high_risk = any(entity.lower() in content.lower() for entity in HIGH_RISK_ENTITIES)
            
            violation_tags.append("copyright")
            violation_details.append({
                "type": "copyright",
                "severity": "high" if is_high_risk else "medium",
                "matched_text": matched_text,
                "high_risk": is_high_risk,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for trademark violations
    for pattern in TRADEMARK_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if any high-risk entity is mentioned
            matched_text = match.group(0)
            is_high_risk = any(entity.lower() in content.lower() for entity in HIGH_RISK_ENTITIES)
            
            violation_tags.append("trademark")
            violation_details.append({
                "type": "trademark",
                "severity": "medium" if is_high_risk else "low",
                "matched_text": matched_text,
                "high_risk": is_high_risk,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check for proprietary code sharing
    for pattern in PROPRIETARY_CODE_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if any high-risk entity is mentioned
            matched_text = match.group(0)
            is_high_risk = any(entity.lower() in content.lower() for entity in HIGH_RISK_ENTITIES)
            
            violation_tags.append("proprietary_code")
            violation_details.append({
                "type": "proprietary_code",
                "severity": "high" if is_high_risk else "medium",
                "matched_text": matched_text,
                "high_risk": is_high_risk,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Remove duplicates from violation tags
    violation_tags = list(set(violation_tags))
    
    # Calculate violation score
    violation_score = 0.0
    if violation_details:
        # Base score on severity of violations
        severity_scores = {"high": 0.9, "medium": 0.6, "low": 0.3}
        total_severity = sum(severity_scores[detail["severity"]] for detail in violation_details)
        violation_score = min(0.95, total_severity / len(violation_details))
        
        # Increase score if multiple violation types are detected
        if len(violation_tags) > 1:
            violation_score = min(0.95, violation_score + 0.1 * (len(violation_tags) - 1))
        
        # Increase score if high-risk entities are involved
        high_risk_count = sum(1 for detail in violation_details if detail.get("high_risk", False))
        if high_risk_count > 0:
            violation_score = min(0.95, violation_score + 0.1 * high_risk_count)
    
    # Determine if content should be flagged
    violation_flag = violation_score >= 0.5
    
    # Log the results
    if violation_flag:
        if loop_id:
            logger.warning(f"IP violation detected in loop {loop_id}: score {violation_score:.2f}, tags: {', '.join(violation_tags)}")
        else:
            logger.warning(f"IP violation detected: score {violation_score:.2f}, tags: {', '.join(violation_tags)}")
    
    # Return the results
    return {
        "flagged": violation_flag,
        "score": violation_score,
        "tags": violation_tags,
        "details": violation_details,
        "checked_at": datetime.utcnow().isoformat(),
        "loop_id": loop_id
    }

def get_memory_fields(scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract fields to be stored in loop memory.
    
    Args:
        scan_result: The result from scan_for_ip_violations
        
    Returns:
        Dictionary with fields for loop memory
    """
    return {
        "ip_violation_flag": scan_result.get("flagged", False),
        "ip_violation_score": scan_result.get("score", 0.0),
        "violation_tags": scan_result.get("tags", []),
        "ip_violation_checked_at": scan_result.get("checked_at")
    }

def get_safe_content(content: str, scan_result: Dict[str, Any]) -> str:
    """
    Get a safe version of the content with potential IP violations removed.
    
    Args:
        content: The original content
        scan_result: The result from scan_for_ip_violations
        
    Returns:
        Safe version of the content
    """
    if not scan_result.get("flagged", False):
        return content
    
    safe_content = content
    details = scan_result.get("details", [])
    
    # Sort details by length of matched text (descending) to avoid nested replacements
    details.sort(key=lambda x: len(x.get("matched_text", "")), reverse=True)
    
    for detail in details:
        matched_text = detail.get("matched_text", "")
        if not matched_text:
            continue
        
        detail_type = detail.get("type", "")
        
        if detail_type == "copyright":
            # Replace copyright content with a reference
            safe_content = safe_content.replace(matched_text, "[Reference to copyrighted material]")
        elif detail_type == "trademark":
            # Keep trademark symbols but add a disclaimer
            if re.search(r"(?i)(™|®|℠)", matched_text):
                # Don't replace the symbol itself
                continue
            else:
                safe_content = safe_content.replace(matched_text, "[Trademark reference]")
        elif detail_type == "proprietary_code":
            # Remove proprietary code entirely
            safe_content = safe_content.replace(matched_text, "[Proprietary information redacted]")
    
    # Clean up any double spaces or leading/trailing whitespace
    safe_content = re.sub(r'\s+', ' ', safe_content).strip()
    
    # Add a disclaimer if content was modified
    if safe_content != content:
        disclaimer = "\n\nNote: Some content has been redacted or modified to comply with intellectual property policies."
        safe_content += disclaimer
    
    return safe_content

def get_reflection_prompt(scan_result: Dict[str, Any]) -> Optional[str]:
    """
    Generate a reflection prompt based on scan results.
    
    Args:
        scan_result: The result from scan_for_ip_violations
        
    Returns:
        Reflection prompt string, or None if no issues were found
    """
    if not scan_result.get("flagged", False):
        return None
    
    violation_score = scan_result.get("score", 0.0)
    violation_tags = scan_result.get("tags", [])
    violation_details = scan_result.get("details", [])
    
    # Build a prompt for reflection
    prompt = f"IP violation detected (score: {violation_score:.2f}):\n\n"
    
    if violation_tags:
        prompt += f"Violation tags: {', '.join(violation_tags)}\n\n"
    
    if violation_details:
        prompt += "Violation details:\n"
        for detail in violation_details[:3]:  # Limit to first 3
            detail_type = detail.get("type", "unknown")
            severity = detail.get("severity", "unknown")
            matched_text = detail.get("matched_text", "")
            high_risk = detail.get("high_risk", False)
            risk_label = " (high risk)" if high_risk else ""
            
            prompt += f"- {detail_type} (severity: {severity}){risk_label}: \"{matched_text}\"\n"
        
        if len(violation_details) > 3:
            prompt += f"- ... and {len(violation_details) - 3} more\n"
        
        prompt += "\n"
    
    prompt += "Please reflect on these IP violation concerns and consider:\n"
    prompt += "1. How can we provide helpful information without infringing on intellectual property rights?\n"
    prompt += "2. What alternative approaches or sources could be used to address the user's need?\n"
    prompt += "3. What disclaimers or attributions might be appropriate when discussing this content?\n"
    
    return prompt

def should_trigger_rerun(scan_result: Dict[str, Any]) -> bool:
    """
    Determine whether to trigger a rerun based on scan results.
    
    Args:
        scan_result: The result from scan_for_ip_violations
        
    Returns:
        Boolean indicating whether a rerun should be triggered
    """
    # Trigger rerun for high violation scores
    return scan_result.get("score", 0.0) >= 0.7

def get_rerun_configuration(scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for rerun if needed.
    
    Args:
        scan_result: The result from scan_for_ip_violations
        
    Returns:
        Dictionary with rerun configuration
    """
    if not should_trigger_rerun(scan_result):
        return {}
    
    violation_tags = scan_result.get("tags", [])
    
    return {
        "depth": "deep",  # Always use deep reflection for IP violations
        "required_reviewers": ["RESEARCHER", "CEO"],
        "rerun_reason": "ip_violation_detected",
        "rerun_reason_detail": f"IP violation detected: {', '.join(violation_tags)}",
        "rerun_trigger": ["ip_violation"]
    }
