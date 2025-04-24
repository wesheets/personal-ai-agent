"""
Output Policy Enforcer Module

This module provides functionality for enforcing output policies,
ensuring agents operate within system-wide constraints.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

# Import schemas if available
try:
    from app.schemas.output_policy_schema import OutputPolicyRequest, OutputPolicyResult
    schema_available = True
except ImportError:
    schema_available = False
    logging.warning("⚠️ Output policy schema not available, using dictionary responses")

# Import memory operations if available
try:
    from app.modules.memory_writer import write_memory
    memory_available = True
except ImportError:
    memory_available = False
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementation for testing
    async def write_memory(project_id, tag, value):
        return {"status": "success", "message": "Mock write successful"}

# Configure logging
logger = logging.getLogger("app.modules.output_policy_enforcer")

# Risk level thresholds for different categories
RISK_LEVEL_THRESHOLDS = {
    "harmful": {
        "warn": 0.5,
        "block": 0.8
    },
    "inappropriate": {
        "warn": 0.6,
        "block": 0.85
    },
    "misinformation": {
        "warn": 0.7,
        "block": 0.9
    },
    "malicious_code": {
        "warn": 0.4,
        "block": 0.7
    },
    "plagiarism": {
        "warn": 0.8,
        "block": 0.95
    }
}

# Blocklist patterns for different categories
BLOCKLIST_PATTERNS = {
    "harmful": [
        r"(?i)how\s+to\s+make\s+(?:a\s+)?(?:bomb|explosive)",
        r"(?i)instructions\s+for\s+(?:hacking|attacking)",
        r"(?i)methods\s+to\s+(?:harm|injure|kill)",
        r"(?i)ways\s+to\s+(?:steal|rob|burglarize)"
    ],
    "inappropriate": [
        r"(?i)explicit\s+(?:sexual|adult)",
        r"(?i)nsfw\s+content",
        r"(?i)pornographic\s+material",
        r"(?i)obscene\s+(?:language|content)"
    ],
    "misinformation": [
        r"(?i)conspiracy\s+theory",
        r"(?i)proven\s+false",
        r"(?i)debunked\s+claim",
        r"(?i)misleading\s+information"
    ],
    "malicious_code": [
        r"(?i)system\(['\"](rm|del).*['\"]",
        r"(?i)exec\s*\(\s*(?:input|raw_input)",
        r"(?i)os\.system\s*\(\s*['\"](?:rm|del)",
        r"(?i)eval\s*\(\s*(?:input|raw_input)",
        r"(?i)subprocess\.(?:call|run|Popen)\s*\(\s*['\"](?:rm|del)",
        r"(?i)import\s+(?:subprocess|os)\s*;.*(?:rm|del)",
        r"(?i)document\.cookie",
        r"(?i)localStorage\.",
        r"(?i)sessionStorage\.",
        r"(?i)fetch\s*\(\s*['\"]https?://",
        r"(?i)new\s+XMLHttpRequest\s*\(\s*\)"
    ],
    "plagiarism": [
        r"(?i)copied\s+from",
        r"(?i)plagiarized\s+content",
        r"(?i)without\s+attribution",
        r"(?i)copyright\s+infringement"
    ]
}

# Code safety regex patterns
CODE_SAFETY_PATTERNS = {
    "javascript": [
        {
            "pattern": r"(?i)eval\s*\(",
            "risk_level": 0.8,
            "description": "Use of eval() can execute arbitrary code"
        },
        {
            "pattern": r"(?i)document\.write\s*\(",
            "risk_level": 0.7,
            "description": "document.write() can enable XSS attacks"
        },
        {
            "pattern": r"(?i)innerHTML\s*=",
            "risk_level": 0.6,
            "description": "innerHTML can enable XSS if not properly sanitized"
        },
        {
            "pattern": r"(?i)setTimeout\s*\(\s*['\"](.*?)['\"]",
            "risk_level": 0.5,
            "description": "setTimeout with string argument can execute arbitrary code"
        }
    ],
    "python": [
        {
            "pattern": r"(?i)eval\s*\(",
            "risk_level": 0.8,
            "description": "Use of eval() can execute arbitrary code"
        },
        {
            "pattern": r"(?i)exec\s*\(",
            "risk_level": 0.8,
            "description": "Use of exec() can execute arbitrary code"
        },
        {
            "pattern": r"(?i)os\.system\s*\(",
            "risk_level": 0.7,
            "description": "os.system() can execute arbitrary shell commands"
        },
        {
            "pattern": r"(?i)subprocess\.(?:call|run|Popen)",
            "risk_level": 0.7,
            "description": "Subprocess functions can execute arbitrary commands"
        },
        {
            "pattern": r"(?i)__import__\s*\(",
            "risk_level": 0.6,
            "description": "Dynamic imports can load arbitrary modules"
        }
    ],
    "sql": [
        {
            "pattern": r"(?i)(?:SELECT|INSERT|UPDATE|DELETE).*?(?:FROM|INTO|WHERE).*?(?:--|#|\/\*)",
            "risk_level": 0.9,
            "description": "SQL injection attempt with comment"
        },
        {
            "pattern": r"(?i)(?:UNION|OR)\s+(?:SELECT|1=1)",
            "risk_level": 0.9,
            "description": "SQL injection attempt with UNION or OR"
        },
        {
            "pattern": r"(?i)(?:DROP|TRUNCATE|ALTER)\s+TABLE",
            "risk_level": 0.9,
            "description": "Destructive SQL operation"
        }
    ]
}

async def enforce_output_policy(
    agent_id: str,
    content: str,
    output_type: str = "text",
    context: Optional[str] = None,
    loop_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enforce output policy on agent-generated content.
    
    Args:
        agent_id: Unique identifier for the agent
        content: Content to be validated
        output_type: Type of output (e.g., 'text', 'code', 'comment')
        context: Additional context for validation
        loop_id: Loop ID for logging violations
        
    Returns:
        Dictionary containing validation results
    """
    try:
        # Initialize risk levels
        harmful_risk_level = 0.0
        inappropriate_risk_level = 0.0
        misinformation_risk_level = 0.0
        malicious_code_risk_level = 0.0
        plagiarism_risk_level = 0.0
        
        # Initialize risk details
        risk_details = []
        
        # Check against blocklist patterns
        for category, patterns in BLOCKLIST_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    matched_text = match.group(0)
                    
                    # Determine risk level based on category
                    if category == "harmful":
                        risk_level = 0.7  # Default risk level for harmful content
                        harmful_risk_level = max(harmful_risk_level, risk_level)
                    elif category == "inappropriate":
                        risk_level = 0.7  # Default risk level for inappropriate content
                        inappropriate_risk_level = max(inappropriate_risk_level, risk_level)
                    elif category == "misinformation":
                        risk_level = 0.7  # Default risk level for misinformation
                        misinformation_risk_level = max(misinformation_risk_level, risk_level)
                    elif category == "malicious_code":
                        risk_level = 0.7  # Default risk level for malicious code
                        malicious_code_risk_level = max(malicious_code_risk_level, risk_level)
                    elif category == "plagiarism":
                        risk_level = 0.7  # Default risk level for plagiarism
                        plagiarism_risk_level = max(plagiarism_risk_level, risk_level)
                    
                    # Add to risk details
                    risk_details.append({
                        "type": category,
                        "risk_level": risk_level,
                        "matched_text": matched_text,
                        "pattern": pattern
                    })
        
        # Check code safety if output_type is code
        if output_type.lower() in ["code", "javascript", "python", "sql"]:
            # Determine language
            language = output_type.lower()
            if language == "code":
                # Try to detect language from context
                if context and "javascript" in context.lower():
                    language = "javascript"
                elif context and "python" in context.lower():
                    language = "python"
                elif context and "sql" in context.lower():
                    language = "sql"
                else:
                    # Default to checking all languages
                    language = "all"
            
            # Check against code safety patterns
            if language == "all":
                # Check all languages
                for lang, patterns in CODE_SAFETY_PATTERNS.items():
                    for pattern_info in patterns:
                        matches = re.finditer(pattern_info["pattern"], content)
                        for match in matches:
                            matched_text = match.group(0)
                            risk_level = pattern_info["risk_level"]
                            
                            # Update malicious code risk level
                            malicious_code_risk_level = max(malicious_code_risk_level, risk_level)
                            
                            # Add to risk details
                            risk_details.append({
                                "type": "malicious_code",
                                "risk_level": risk_level,
                                "matched_text": matched_text,
                                "pattern": pattern_info["pattern"],
                                "description": pattern_info["description"],
                                "language": lang
                            })
            else:
                # Check specific language
                if language in CODE_SAFETY_PATTERNS:
                    for pattern_info in CODE_SAFETY_PATTERNS[language]:
                        matches = re.finditer(pattern_info["pattern"], content)
                        for match in matches:
                            matched_text = match.group(0)
                            risk_level = pattern_info["risk_level"]
                            
                            # Update malicious code risk level
                            malicious_code_risk_level = max(malicious_code_risk_level, risk_level)
                            
                            # Add to risk details
                            risk_details.append({
                                "type": "malicious_code",
                                "risk_level": risk_level,
                                "matched_text": matched_text,
                                "pattern": pattern_info["pattern"],
                                "description": pattern_info["description"],
                                "language": language
                            })
        
        # Determine risk tags
        risk_tags = []
        if harmful_risk_level >= RISK_LEVEL_THRESHOLDS["harmful"]["warn"]:
            risk_tags.append("harmful")
        if inappropriate_risk_level >= RISK_LEVEL_THRESHOLDS["inappropriate"]["warn"]:
            risk_tags.append("inappropriate")
        if misinformation_risk_level >= RISK_LEVEL_THRESHOLDS["misinformation"]["warn"]:
            risk_tags.append("misinformation")
        if malicious_code_risk_level >= RISK_LEVEL_THRESHOLDS["malicious_code"]["warn"]:
            risk_tags.append("malicious_code")
        if plagiarism_risk_level >= RISK_LEVEL_THRESHOLDS["plagiarism"]["warn"]:
            risk_tags.append("plagiarism")
        
        # Determine overall action and violation details
        action = "allowed"
        approved = True
        violation_type = None
        reason = None
        
        if (harmful_risk_level >= RISK_LEVEL_THRESHOLDS["harmful"]["block"] or
            inappropriate_risk_level >= RISK_LEVEL_THRESHOLDS["inappropriate"]["block"] or
            misinformation_risk_level >= RISK_LEVEL_THRESHOLDS["misinformation"]["block"] or
            malicious_code_risk_level >= RISK_LEVEL_THRESHOLDS["malicious_code"]["block"] or
            plagiarism_risk_level >= RISK_LEVEL_THRESHOLDS["plagiarism"]["block"]):
            action = "blocked"
            approved = False
            
            # Determine violation type and reason
            if harmful_risk_level >= RISK_LEVEL_THRESHOLDS["harmful"]["block"]:
                violation_type = "harmful_content"
                reason = "Content contains potentially harmful information"
            elif inappropriate_risk_level >= RISK_LEVEL_THRESHOLDS["inappropriate"]["block"]:
                violation_type = "inappropriate_content"
                reason = "Content contains potentially inappropriate material"
            elif misinformation_risk_level >= RISK_LEVEL_THRESHOLDS["misinformation"]["block"]:
                violation_type = "misinformation"
                reason = "Content contains potential misinformation"
            elif malicious_code_risk_level >= RISK_LEVEL_THRESHOLDS["malicious_code"]["block"]:
                violation_type = "malicious_code"
                reason = "Code contains potentially malicious patterns"
            elif plagiarism_risk_level >= RISK_LEVEL_THRESHOLDS["plagiarism"]["block"]:
                violation_type = "plagiarism"
                reason = "Content may contain plagiarized material"
        elif risk_tags:
            action = "rewritten"
            approved = True
            
            # Add a disclaimer
            if output_type.lower() == "code":
                # Add code comment disclaimer
                if any(lang in content.lower() for lang in ["javascript", "java", "c", "cpp", "csharp"]):
                    disclaimer = "\n\n// Note: This code contains patterns that may require additional security review before use in production.\n"
                elif any(lang in content.lower() for lang in ["python", "ruby"]):
                    disclaimer = "\n\n# Note: This code contains patterns that may require additional security review before use in production.\n"
                elif "html" in content.lower():
                    disclaimer = "\n\n<!-- Note: This code contains patterns that may require additional security review before use in production. -->\n"
                else:
                    disclaimer = "\n\n/* Note: This code contains patterns that may require additional security review before use in production. */\n"
            else:
                # Add text disclaimer
                disclaimer = "\n\nNote: This response may contain sensitive information. Please use this information responsibly and ethically."
            
            content = content + disclaimer
        
        # Generate safe output for blocked content
        if action == "blocked":
            if output_type.lower() == "code":
                # Provide safe alternative for code
                safe_output = "// I apologize, but I cannot provide that code as it may violate content policies.\n// Please let me know if I can assist you with a safer alternative."
            else:
                # Provide safe alternative for text
                safe_output = "I apologize, but I cannot provide that information as it may violate content policies. Please let me know if I can assist you with something else."
        else:
            safe_output = content
        
        # Log the results
        if action != "allowed":
            if loop_id and memory_available:
                # Log to memory
                await write_memory(
                    loop_id,
                    f"output_policy_violation_{agent_id}",
                    {
                        "agent_id": agent_id,
                        "output_type": output_type,
                        "action": action,
                        "risk_tags": risk_tags,
                        "violation_type": violation_type,
                        "reason": reason,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                logger.info(f"✅ Logged output policy enforcement result to memory for loop {loop_id}")
            
            logger.warning(f"⚠️ Output policy enforcement triggered for agent {agent_id}: {action} due to {', '.join(risk_tags)}")
        else:
            logger.info(f"✅ Output policy check passed for agent {agent_id}")
        
        # Create result
        result = {
            "approved": approved,
            "content": safe_output,
            "violation_type": violation_type,
            "reason": reason,
            "action": action,
            "risk_tags": risk_tags,
            "risk_details": risk_details,
            "checked_at": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "output_type": output_type,
            "loop_id": loop_id
        }
        
        # Return schema object if available
        if schema_available:
            return OutputPolicyResult(**result)
        else:
            return result
    
    except Exception as e:
        logger.error(f"❌ Error enforcing output policy: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error result
        error_result = {
            "approved": False,
            "content": "Error enforcing output policy. Please try again.",
            "violation_type": "policy_error",
            "reason": f"Error: {str(e)}",
            "action": "error",
            "risk_tags": ["error"],
            "risk_details": [],
            "checked_at": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "output_type": output_type,
            "loop_id": loop_id
        }
        
        # Return schema object if available
        if schema_available:
            return OutputPolicyResult(**error_result)
        else:
            return error_result

async def get_policy_logs(
    agent_id: Optional[str] = None,
    output_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 10,
    loop_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get policy enforcement logs.
    
    Args:
        agent_id: Filter by agent ID
        output_type: Filter by output type
        action: Filter by action
        limit: Maximum number of log entries to return
        loop_id: Filter by loop ID
        
    Returns:
        Dictionary containing log entries
    """
    try:
        # This is a placeholder for actual log retrieval
        # In a real implementation, this would query a database or memory store
        
        # Mock logs for testing
        logs = [
            {
                "agent_id": "hal",
                "output_type": "code",
                "action": "blocked",
                "risk_tags": ["malicious_code"],
                "timestamp": datetime.utcnow().isoformat(),
                "loop_id": "loop_12345"
            },
            {
                "agent_id": "critic",
                "output_type": "text",
                "action": "rewritten",
                "risk_tags": ["inappropriate"],
                "timestamp": datetime.utcnow().isoformat(),
                "loop_id": "loop_67890"
            }
        ]
        
        # Filter logs
        filtered_logs = logs
        if agent_id:
            filtered_logs = [log for log in filtered_logs if log["agent_id"] == agent_id]
        if output_type:
            filtered_logs = [log for log in filtered_logs if log["output_type"] == output_type]
        if action:
            filtered_logs = [log for log in filtered_logs if log["action"] == action]
        if loop_id:
            filtered_logs = [log for log in filtered_logs if log["loop_id"] == loop_id]
        
        # Limit logs
        limited_logs = filtered_logs[:limit]
        
        # Return logs
        return {
            "logs": limited_logs,
            "total": len(filtered_logs)
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting policy logs: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error result
        return {
            "logs": [],
            "total": 0,
            "error": str(e)
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
