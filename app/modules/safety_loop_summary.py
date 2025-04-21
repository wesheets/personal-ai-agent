"""
Safety Loop Summary Module

This module provides a comprehensive summary of safety checks performed on a loop,
including synthetic identity protection, output policy enforcement, prompt injection detection,
domain sensitivity flagging, and IP violation scanning.

It integrates with the Responsible Cognition Layer to provide a unified view of safety status.
"""

from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime

from app.modules.safety_integration import (
    run_safety_checks,
    get_consolidated_memory_fields,
    should_trigger_rerun,
    get_rerun_configuration,
    get_reflection_prompts,
    get_safe_output,
    get_safe_prompt
)

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "loop_trace[loop_001]":
        return {
            "loop_id": "loop_001",
            "status": "completed",
            "timestamp": "2025-04-21T12:00:00Z",
            "summary": "Analyzed quantum computing concepts",
            "orchestrator_persona": "SAGE",
            "safety_checks_performed": ["synthetic_identity", "output_policy", "prompt_injection", "domain_sensitivity", "ip_violation"],
            "safety_blocks_triggered": [],
            "safety_warnings_issued": ["domain_sensitivity"]
        }
    elif key == "loop_prompt[loop_001]":
        return "Analyze the impact of quantum computing on cryptography."
    elif key == "loop_output[loop_001]":
        return "Quantum computing poses significant challenges to current cryptographic methods..."
    
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

async def generate_safety_summary(loop_id: str) -> Dict[str, Any]:
    """
    Generate a comprehensive safety summary for a loop.
    
    This function:
    1. Retrieves the loop trace, prompt, and output
    2. Extracts safety-related fields
    3. Generates a summary of safety checks performed
    4. Provides recommendations based on safety results
    
    Args:
        loop_id: The ID of the loop to summarize
        
    Returns:
        Dict containing the safety summary
    """
    # Get the loop trace, prompt, and output
    loop_trace = await read_from_memory(f"loop_trace[{loop_id}]")
    prompt = await read_from_memory(f"loop_prompt[{loop_id}]") or ""
    output = await read_from_memory(f"loop_output[{loop_id}]") or ""
    
    # Initialize summary
    summary = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "safety_status": "safe",
        "safety_checks_performed": [],
        "safety_blocks_triggered": [],
        "safety_warnings_issued": [],
        "recommendations": []
    }
    
    # If loop trace is not found, return basic summary
    if not isinstance(loop_trace, dict):
        summary["safety_status"] = "unknown"
        summary["recommendations"].append("Loop trace not found, unable to determine safety status")
        return summary
    
    # Extract safety-related fields from loop trace
    safety_checks_performed = loop_trace.get("safety_checks_performed", [])
    safety_blocks_triggered = loop_trace.get("safety_blocks_triggered", [])
    safety_warnings_issued = loop_trace.get("safety_warnings_issued", [])
    
    # Update summary with safety fields
    summary["safety_checks_performed"] = safety_checks_performed
    summary["safety_blocks_triggered"] = safety_blocks_triggered
    summary["safety_warnings_issued"] = safety_warnings_issued
    
    # Determine safety status
    if safety_blocks_triggered:
        summary["safety_status"] = "blocked"
    elif safety_warnings_issued:
        summary["safety_status"] = "warning"
    
    # Add detailed information for each safety component
    
    # Synthetic identity protection
    if "synthetic_identity" in safety_checks_performed:
        synthetic_identity_risk = loop_trace.get("synthetic_identity_risk", False)
        synthetic_identity_severity = loop_trace.get("synthetic_identity_severity", "none")
        synthetic_identity_issues = loop_trace.get("synthetic_identity_issues", 0)
        
        summary["synthetic_identity"] = {
            "risk_detected": synthetic_identity_risk,
            "severity": synthetic_identity_severity,
            "issues_count": synthetic_identity_issues
        }
        
        if synthetic_identity_risk:
            if "synthetic_identity" in safety_blocks_triggered:
                summary["recommendations"].append("Synthetic identity risk blocked: Revise prompt to avoid impersonation")
            else:
                summary["recommendations"].append("Synthetic identity risk detected: Consider reviewing prompt for potential impersonation")
    
    # Output policy enforcement
    if "output_policy" in safety_checks_performed:
        content_risk_tags = loop_trace.get("content_risk_tags", [])
        output_policy_action = loop_trace.get("output_policy_action", "allowed")
        
        summary["output_policy"] = {
            "risk_tags": content_risk_tags,
            "action": output_policy_action
        }
        
        if output_policy_action == "blocked":
            summary["recommendations"].append(f"Output blocked due to policy violation: {', '.join(content_risk_tags)}")
        elif content_risk_tags:
            summary["recommendations"].append(f"Content risk tags detected: {', '.join(content_risk_tags)}")
    
    # Prompt injection detection
    if "prompt_injection" in safety_checks_performed:
        prompt_injection_detected = loop_trace.get("prompt_injection_detected", False)
        injection_tags = loop_trace.get("injection_tags", [])
        sanitization_action = loop_trace.get("sanitization_action", "allow")
        
        summary["prompt_injection"] = {
            "detected": prompt_injection_detected,
            "tags": injection_tags,
            "action": sanitization_action
        }
        
        if prompt_injection_detected:
            if sanitization_action == "halt":
                summary["recommendations"].append(f"Prompt injection blocked: {', '.join(injection_tags)}")
            elif sanitization_action == "warn":
                summary["recommendations"].append(f"Potential prompt injection detected: {', '.join(injection_tags)}")
    
    # Domain sensitivity flagging
    if "domain_sensitivity" in safety_checks_performed:
        domain_sensitive = loop_trace.get("domain_sensitive", False)
        sensitive_domains = loop_trace.get("sensitive_domains", [])
        primary_domain = loop_trace.get("primary_domain")
        required_reviewers = loop_trace.get("required_reviewers", [])
        
        summary["domain_sensitivity"] = {
            "sensitive": domain_sensitive,
            "domains": sensitive_domains,
            "primary_domain": primary_domain,
            "required_reviewers": required_reviewers
        }
        
        if domain_sensitive:
            domain_str = f"{primary_domain} domain" if primary_domain else f"{', '.join(sensitive_domains)} domains"
            summary["recommendations"].append(f"Sensitive domain detected: {domain_str}. Consider expert review.")
    
    # IP violation scanning
    if "ip_violation" in safety_checks_performed:
        ip_violation_score = loop_trace.get("ip_violation_score", 0.0)
        ip_violation_flag = loop_trace.get("ip_violation_flag", False)
        violation_tags = loop_trace.get("violation_tags", [])
        
        summary["ip_violation"] = {
            "score": ip_violation_score,
            "flagged": ip_violation_flag,
            "tags": violation_tags
        }
        
        if ip_violation_flag:
            if "ip_violation" in safety_blocks_triggered:
                summary["recommendations"].append(f"IP violation blocked: {', '.join(violation_tags)}")
            else:
                summary["recommendations"].append(f"Potential IP violation detected: {', '.join(violation_tags)}")
    
    # Add safe versions of prompt and output if any blocks were triggered
    if safety_blocks_triggered:
        # Run safety checks to get safe versions
        safety_results = await run_safety_checks(loop_id, prompt, output, safety_checks_performed)
        
        # Get safe versions
        safe_prompt = get_safe_prompt(prompt, safety_results)
        safe_output = get_safe_output(output, safety_results)
        
        # Add to summary
        if safe_prompt != prompt:
            summary["safe_prompt"] = safe_prompt
        if safe_output != output:
            summary["safe_output"] = safe_output
    
    # Store the summary in memory
    await write_to_memory(f"safety_summary[{loop_id}]", summary)
    
    return summary

async def get_safety_report(loop_id: str) -> str:
    """
    Generate a human-readable safety report for a loop.
    
    Args:
        loop_id: The ID of the loop to generate a report for
        
    Returns:
        String containing the safety report
    """
    # Generate the safety summary
    summary = await generate_safety_summary(loop_id)
    
    # Format the report
    report = [
        f"# Safety Report for Loop {loop_id}",
        f"Generated at: {summary.get('timestamp')}",
        "",
        f"## Safety Status: {summary.get('safety_status', 'unknown').upper()}",
        "",
        "## Safety Checks Performed:",
    ]
    
    # Add safety checks
    safety_checks = summary.get("safety_checks_performed", [])
    if safety_checks:
        for check in safety_checks:
            report.append(f"- {check}")
    else:
        report.append("- No safety checks performed")
    
    report.append("")
    
    # Add blocks triggered
    report.append("## Safety Blocks Triggered:")
    safety_blocks = summary.get("safety_blocks_triggered", [])
    if safety_blocks:
        for block in safety_blocks:
            report.append(f"- {block}")
    else:
        report.append("- No safety blocks triggered")
    
    report.append("")
    
    # Add warnings issued
    report.append("## Safety Warnings Issued:")
    safety_warnings = summary.get("safety_warnings_issued", [])
    if safety_warnings:
        for warning in safety_warnings:
            report.append(f"- {warning}")
    else:
        report.append("- No safety warnings issued")
    
    report.append("")
    
    # Add recommendations
    report.append("## Recommendations:")
    recommendations = summary.get("recommendations", [])
    if recommendations:
        for recommendation in recommendations:
            report.append(f"- {recommendation}")
    else:
        report.append("- No recommendations")
    
    # Add detailed information for each safety component
    report.append("")
    report.append("## Detailed Safety Information:")
    
    # Synthetic identity protection
    if "synthetic_identity" in summary:
        report.append("")
        report.append("### Synthetic Identity Protection:")
        synthetic_identity = summary["synthetic_identity"]
        report.append(f"- Risk Detected: {synthetic_identity.get('risk_detected', False)}")
        report.append(f"- Severity: {synthetic_identity.get('severity', 'none')}")
        report.append(f"- Issues Count: {synthetic_identity.get('issues_count', 0)}")
    
    # Output policy enforcement
    if "output_policy" in summary:
        report.append("")
        report.append("### Output Policy Enforcement:")
        output_policy = summary["output_policy"]
        report.append(f"- Action: {output_policy.get('action', 'allowed')}")
        risk_tags = output_policy.get("risk_tags", [])
        if risk_tags:
            report.append(f"- Risk Tags: {', '.join(risk_tags)}")
        else:
            report.append("- Risk Tags: None")
    
    # Prompt injection detection
    if "prompt_injection" in summary:
        report.append("")
        report.append("### Prompt Injection Detection:")
        prompt_injection = summary["prompt_injection"]
        report.append(f"- Detected: {prompt_injection.get('detected', False)}")
        report.append(f"- Action: {prompt_injection.get('action', 'allow')}")
        injection_tags = prompt_injection.get("tags", [])
        if injection_tags:
            report.append(f"- Injection Tags: {', '.join(injection_tags)}")
        else:
            report.append("- Injection Tags: None")
    
    # Domain sensitivity flagging
    if "domain_sensitivity" in summary:
        report.append("")
        report.append("### Domain Sensitivity Flagging:")
        domain_sensitivity = summary["domain_sensitivity"]
        report.append(f"- Sensitive: {domain_sensitivity.get('sensitive', False)}")
        sensitive_domains = domain_sensitivity.get("domains", [])
        if sensitive_domains:
            report.append(f"- Sensitive Domains: {', '.join(sensitive_domains)}")
        else:
            report.append("- Sensitive Domains: None")
        primary_domain = domain_sensitivity.get("primary_domain")
        if primary_domain:
            report.append(f"- Primary Domain: {primary_domain}")
        required_reviewers = domain_sensitivity.get("required_reviewers", [])
        if required_reviewers:
            report.append(f"- Required Reviewers: {', '.join(required_reviewers)}")
    
    # IP violation scanning
    if "ip_violation" in summary:
        report.append("")
        report.append("### IP Violation Scanning:")
        ip_violation = summary["ip_violation"]
        report.append(f"- Flagged: {ip_violation.get('flagged', False)}")
        report.append(f"- Score: {ip_violation.get('score', 0.0)}")
        violation_tags = ip_violation.get("tags", [])
        if violation_tags:
            report.append(f"- Violation Tags: {', '.join(violation_tags)}")
        else:
            report.append("- Violation Tags: None")
    
    # Add safe versions if available
    if "safe_prompt" in summary:
        report.append("")
        report.append("### Safe Prompt:")
        report.append("```")
        report.append(summary["safe_prompt"])
        report.append("```")
    
    if "safe_output" in summary:
        report.append("")
        report.append("### Safe Output:")
        report.append("```")
        report.append(summary["safe_output"])
        report.append("```")
    
    # Return the report as a string
    return "\n".join(report)
