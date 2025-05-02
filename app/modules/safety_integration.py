"""
Safety Integration Module

This module integrates all safety components of the Responsible Cognition Layer:
- Synthetic identity protection
- Output policy enforcement
- Prompt injection detection
- Domain sensitivity flagging
- IP violation scanning

It provides a unified interface for running safety checks, determining rerun triggers,
and generating reflection prompts.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set

from app.modules.synthetic_identity_checker import check_synthetic_identity
from app.modules.output_policy_enforcer import enforce_output_policy
from app.modules.loop_intent_sanitizer import sanitize_loop_intent
from app.modules.domain_sensitivity_flagging import flag_domain_sensitivity
from app.modules.ip_violation_scanner import scan_for_ip_violations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_safety_checks(
    loop_id: str,
    prompt: str,
    output: str,
    checks_to_run: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Run all specified safety checks on a loop's prompt and output.
    
    Args:
        loop_id: The ID of the loop to check
        prompt: The prompt text to check
        output: The output text to check
        checks_to_run: List of specific checks to run, or None to run all
        
    Returns:
        Dictionary with results from all safety checks
    """
    # Default to running all checks if none specified
    if checks_to_run is None:
        checks_to_run = [
            "synthetic_identity",
            "output_policy",
            "prompt_injection",
            "domain_sensitivity",
            "ip_violation"
        ]
    
    results = {
        "loop_id": loop_id,
        "safety_checks_performed": checks_to_run,
        "safety_blocks_triggered": [],
        "safety_warnings_issued": []
    }
    
    # Run synthetic identity check
    if "synthetic_identity" in checks_to_run:
        identity_result = await check_synthetic_identity(prompt, loop_id)
        results["synthetic_identity"] = identity_result
        
        # Add memory fields
        for key, value in identity_result.items():
            if key not in ["issues", "checked_at", "loop_id"]:
                results[key] = value
        
        # Check if this should trigger a block
        if identity_result.get("severity") == "high":
            results["safety_blocks_triggered"].append("synthetic_identity")
        elif identity_result.get("risk_detected", False):
            results["safety_warnings_issued"].append("synthetic_identity")
    
    # Run output policy enforcement
    if "output_policy" in checks_to_run:
        policy_result = await enforce_output_policy(output, loop_id)
        results["output_policy"] = policy_result
        
        # Add memory fields
        results["output_policy_action"] = policy_result.get("action", "allowed")
        results["content_risk_tags"] = policy_result.get("risk_tags", [])
        
        # Check if this should trigger a block
        if policy_result.get("action") == "blocked":
            results["safety_blocks_triggered"].append("output_policy")
        elif policy_result.get("action") == "warned":
            results["safety_warnings_issued"].append("output_policy")
    
    # Run prompt injection detection
    if "prompt_injection" in checks_to_run:
        injection_result = await sanitize_loop_intent(prompt, loop_id)
        results["prompt_injection"] = injection_result
        
        # Add memory fields
        results["prompt_injection_detected"] = injection_result.get("injection_detected", False)
        results["injection_tags"] = injection_result.get("injection_tags", [])
        results["sanitization_action"] = injection_result.get("action", "allow")
        
        # Check if this should trigger a block
        if injection_result.get("action") == "halt":
            results["safety_blocks_triggered"].append("prompt_injection")
        elif injection_result.get("action") == "warn":
            results["safety_warnings_issued"].append("prompt_injection")
    
    # Run domain sensitivity flagging
    if "domain_sensitivity" in checks_to_run:
        sensitivity_result = await flag_domain_sensitivity(prompt, loop_id)
        results["domain_sensitivity"] = sensitivity_result
        
        # Add memory fields
        results["domain_sensitive"] = sensitivity_result.get("domain_sensitive", False)
        results["sensitive_domains"] = sensitivity_result.get("sensitive_domains", [])
        results["primary_domain"] = sensitivity_result.get("sensitive_domains", [])[0] if sensitivity_result.get("sensitive_domains", []) else None
        results["required_reviewers"] = sensitivity_result.get("required_reviewers", [])
        
        # Check if this should trigger a warning
        if sensitivity_result.get("domain_sensitive", False):
            results["safety_warnings_issued"].append("domain_sensitivity")
    
    # Run IP violation scanning
    if "ip_violation" in checks_to_run:
        violation_result = await scan_for_ip_violations(output, loop_id)
        results["ip_violation"] = violation_result
        
        # Add memory fields
        results["ip_violation_flag"] = violation_result.get("flagged", False)
        results["ip_violation_score"] = violation_result.get("score", 0.0)
        results["violation_tags"] = violation_result.get("tags", [])
        
        # Check if this should trigger a block
        if violation_result.get("score", 0.0) >= 0.7:
            results["safety_blocks_triggered"].append("ip_violation")
        elif violation_result.get("flagged", False):
            results["safety_warnings_issued"].append("ip_violation")
    
    # Log summary of results
    blocks = results.get("safety_blocks_triggered", [])
    warnings = results.get("safety_warnings_issued", [])
    
    if blocks:
        logger.warning(f"Safety blocks triggered for loop {loop_id}: {', '.join(blocks)}")
    if warnings:
        logger.info(f"Safety warnings issued for loop {loop_id}: {', '.join(warnings)}")
    
    return results

def should_trigger_rerun(safety_results: Dict[str, Any]) -> bool:
    """
    Determine whether safety checks should trigger a rerun.
    
    Args:
        safety_results: Results from run_safety_checks
        
    Returns:
        Boolean indicating whether a rerun should be triggered
    """
    # Check if blocks are triggered and not overridden
    blocks_triggered = safety_results.get("safety_blocks_triggered", [])
    override_blocks = safety_results.get("override_blocks", False)
    
    return len(blocks_triggered) > 0 and not override_blocks

def get_rerun_configuration(safety_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for rerun based on safety results.
    
    Args:
        safety_results: Results from run_safety_checks
        
    Returns:
        Dictionary with rerun configuration
    """
    if not should_trigger_rerun(safety_results):
        return {}
    
    blocks_triggered = safety_results.get("safety_blocks_triggered", [])
    required_reviewers = set(["PESSIMIST", "CEO"])  # Default reviewers
    rerun_trigger = []
    
    # Collect required reviewers and rerun triggers from all blocks
    for block in blocks_triggered:
        if block == "synthetic_identity" and "synthetic_identity" in safety_results:
            identity_result = safety_results["synthetic_identity"]
            if should_trigger_rerun(identity_result):
                config = get_component_rerun_configuration("synthetic_identity", identity_result)
                required_reviewers.update(config.get("required_reviewers", []))
                rerun_trigger.extend(config.get("rerun_trigger", []))
        
        elif block == "output_policy" and "output_policy" in safety_results:
            policy_result = safety_results["output_policy"]
            if should_trigger_rerun(policy_result):
                config = get_component_rerun_configuration("output_policy", policy_result)
                required_reviewers.update(config.get("required_reviewers", []))
                rerun_trigger.extend(config.get("rerun_trigger", []))
        
        elif block == "prompt_injection" and "prompt_injection" in safety_results:
            injection_result = safety_results["prompt_injection"]
            if should_trigger_rerun(injection_result):
                config = get_component_rerun_configuration("prompt_injection", injection_result)
                required_reviewers.update(config.get("required_reviewers", []))
                rerun_trigger.extend(config.get("rerun_trigger", []))
        
        elif block == "ip_violation" and "ip_violation" in safety_results:
            violation_result = safety_results["ip_violation"]
            if should_trigger_rerun(violation_result):
                config = get_component_rerun_configuration("ip_violation", violation_result)
                required_reviewers.update(config.get("required_reviewers", []))
                rerun_trigger.extend(config.get("rerun_trigger", []))
    
    # Add domain sensitivity reviewers if it's a warning
    warnings_issued = safety_results.get("safety_warnings_issued", [])
    if "domain_sensitivity" in warnings_issued and "domain_sensitivity" in safety_results:
        sensitivity_result = safety_results["domain_sensitivity"]
        domain_reviewers = sensitivity_result.get("required_reviewers", [])
        required_reviewers.update(domain_reviewers)
    
    # Remove duplicates from rerun trigger
    rerun_trigger = list(set(rerun_trigger))
    
    return {
        "depth": "deep",  # Always use deep reflection for safety issues
        "required_reviewers": list(required_reviewers),
        "rerun_reason": "safety_check_triggered",
        "rerun_reason_detail": f"Safety blocks triggered: {', '.join(blocks_triggered)}",
        "rerun_trigger": rerun_trigger
    }

def get_component_rerun_configuration(component: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get rerun configuration for a specific safety component.
    
    Args:
        component: The safety component name
        result: The result from that component's check
        
    Returns:
        Dictionary with component-specific rerun configuration
    """
    if component == "synthetic_identity":
        from app.modules.synthetic_identity_checker import get_rerun_configuration
        return get_rerun_configuration(result)
    
    elif component == "output_policy":
        from app.modules.output_policy_enforcer import get_rerun_configuration
        return get_rerun_configuration(result)
    
    elif component == "prompt_injection":
        from app.modules.loop_intent_sanitizer import get_rerun_configuration
        return get_rerun_configuration(result)
    
    elif component == "domain_sensitivity":
        from app.modules.domain_sensitivity_flagging import get_rerun_configuration
        return get_rerun_configuration(result)
    
    elif component == "ip_violation":
        from app.modules.ip_violation_scanner import get_rerun_configuration
        return get_rerun_configuration(result)
    
    return {}

def get_reflection_prompts(safety_results: Dict[str, Any]) -> List[str]:
    """
    Generate reflection prompts based on safety results.
    
    Args:
        safety_results: Results from run_safety_checks
        
    Returns:
        List of reflection prompts
    """
    prompts = []
    
    # Generate prompts for blocks
    blocks_triggered = safety_results.get("safety_blocks_triggered", [])
    for block in blocks_triggered:
        if block == "synthetic_identity" and "synthetic_identity" in safety_results:
            from app.modules.synthetic_identity_checker import get_reflection_prompt
            prompt = get_reflection_prompt(safety_results["synthetic_identity"])
            if prompt:
                prompts.append(prompt)
        
        elif block == "output_policy" and "output_policy" in safety_results:
            from app.modules.output_policy_enforcer import get_reflection_prompt
            prompt = get_reflection_prompt(safety_results["output_policy"])
            if prompt:
                prompts.append(prompt)
        
        elif block == "prompt_injection" and "prompt_injection" in safety_results:
            from app.modules.loop_intent_sanitizer import get_reflection_prompt
            prompt = get_reflection_prompt(safety_results["prompt_injection"])
            if prompt:
                prompts.append(prompt)
        
        elif block == "ip_violation" and "ip_violation" in safety_results:
            from app.modules.ip_violation_scanner import get_reflection_prompt
            prompt = get_reflection_prompt(safety_results["ip_violation"])
            if prompt:
                prompts.append(prompt)
    
    # Generate prompts for warnings
    warnings_issued = safety_results.get("safety_warnings_issued", [])
    for warning in warnings_issued:
        if warning == "domain_sensitivity" and "domain_sensitivity" in safety_results:
            from app.modules.domain_sensitivity_flagging import get_reflection_prompt
            prompt = get_reflection_prompt(safety_results["domain_sensitivity"])
            if prompt:
                prompts.append(prompt)
    
    return prompts

def get_safe_output(original_output: str, safety_results: Dict[str, Any]) -> str:
    """
    Get a safe version of the output based on safety results.
    
    Args:
        original_output: The original output text
        safety_results: Results from run_safety_checks
        
    Returns:
        Safe version of the output
    """
    safe_output = original_output
    
    # Apply output policy enforcement
    if "output_policy" in safety_results:
        policy_result = safety_results["output_policy"]
        if policy_result.get("action") in ["blocked", "warned"]:
            safe_output = policy_result.get("safe_output", safe_output)
    
    # Apply IP violation scanning
    if "ip_violation" in safety_results:
        from app.modules.ip_violation_scanner import get_safe_content
        violation_result = safety_results["ip_violation"]
        if violation_result.get("flagged", False):
            safe_output = get_safe_content(safe_output, violation_result)
    
    return safe_output

def get_safe_prompt(original_prompt: str, safety_results: Dict[str, Any]) -> str:
    """
    Get a safe version of the prompt based on safety results.
    
    Args:
        original_prompt: The original prompt text
        safety_results: Results from run_safety_checks
        
    Returns:
        Safe version of the prompt
    """
    safe_prompt = original_prompt
    
    # Apply synthetic identity protection
    if "synthetic_identity" in safety_results:
        from app.modules.synthetic_identity_checker import get_safe_prompt
        identity_result = safety_results["synthetic_identity"]
        if identity_result.get("risk_detected", False):
            safe_prompt = get_safe_prompt(safe_prompt, identity_result)
    
    # Apply prompt injection detection
    if "prompt_injection" in safety_results:
        injection_result = safety_results["prompt_injection"]
        if injection_result.get("injection_detected", False):
            safe_prompt = injection_result.get("sanitized_prompt", safe_prompt)
    
    return safe_prompt

def get_consolidated_memory_fields(safety_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get consolidated memory fields from all safety components.
    
    Args:
        safety_results: Results from run_safety_checks
        
    Returns:
        Dictionary with consolidated memory fields
    """
    memory_fields = {
        "safety_checks_performed": safety_results.get("safety_checks_performed", []),
        "safety_blocks_triggered": safety_results.get("safety_blocks_triggered", []),
        "safety_warnings_issued": safety_results.get("safety_warnings_issued", [])
    }
    
    # Add synthetic identity fields
    if "synthetic_identity" in safety_results:
        from app.modules.synthetic_identity_checker import get_memory_fields
        identity_fields = get_memory_fields(safety_results["synthetic_identity"])
        memory_fields.update(identity_fields)
    
    # Add output policy fields
    if "output_policy" in safety_results:
        from app.modules.output_policy_enforcer import get_memory_fields
        policy_fields = get_memory_fields(safety_results["output_policy"])
        memory_fields.update(policy_fields)
    
    # Add prompt injection fields
    if "prompt_injection" in safety_results:
        from app.modules.loop_intent_sanitizer import get_memory_fields
        injection_fields = get_memory_fields(safety_results["prompt_injection"])
        memory_fields.update(injection_fields)
    
    # Add domain sensitivity fields
    if "domain_sensitivity" in safety_results:
        from app.modules.domain_sensitivity_flagging import get_memory_fields
        sensitivity_fields = get_memory_fields(safety_results["domain_sensitivity"])
        memory_fields.update(sensitivity_fields)
    
    # Add IP violation fields
    if "ip_violation" in safety_results:
        from app.modules.ip_violation_scanner import get_memory_fields
        violation_fields = get_memory_fields(safety_results["ip_violation"])
        memory_fields.update(violation_fields)
    
    return memory_fields
