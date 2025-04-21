"""
Domain Sensitivity Flagging Module

This module is responsible for detecting prompts that enter sensitive domains
such as medical, legal, and financial, and flagging them for appropriate handling.

It's a key component of the Responsible Cognition Layer, providing awareness of
domain-specific risks and triggering appropriate review processes.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sensitive domains and their patterns
MEDICAL_PATTERNS = [
    r"(?i)(diagnos(is|e|ing)|treatment|symptom|disease|illness|condition|patient|medical advice)",
    r"(?i)(prescription|medication|drug|dosage|therapy|surgery|vaccine)",
    r"(?i)(cancer|diabetes|heart disease|stroke|alzheimer|dementia|depression|anxiety)",
    r"(?i)(doctor|physician|nurse|hospital|clinic|emergency room|ER)",
    r"(?i)(blood test|x-ray|MRI|CT scan|ultrasound|biopsy)"
]

LEGAL_PATTERNS = [
    r"(?i)(legal advice|lawsuit|litigation|court case|trial|settlement)",
    r"(?i)(attorney|lawyer|judge|plaintiff|defendant|witness|testimony)",
    r"(?i)(contract|agreement|terms|clause|provision|liability|damages)",
    r"(?i)(copyright|trademark|patent|intellectual property|infringement)",
    r"(?i)(divorce|custody|will|estate|inheritance|probate)"
]

FINANCIAL_PATTERNS = [
    r"(?i)(investment advice|stock|bond|mutual fund|ETF|portfolio|asset allocation)",
    r"(?i)(mortgage|loan|debt|credit|interest rate|APR|refinance)",
    r"(?i)(tax|deduction|exemption|write-off|IRS|audit|filing)",
    r"(?i)(retirement|401k|IRA|pension|social security|annuity)",
    r"(?i)(insurance|premium|deductible|coverage|claim|policy)"
]

MENTAL_HEALTH_PATTERNS = [
    r"(?i)(therapy|counseling|psychologist|psychiatrist|therapist)",
    r"(?i)(depression|anxiety|bipolar|schizophrenia|PTSD|trauma)",
    r"(?i)(suicide|self-harm|crisis|mental health emergency)",
    r"(?i)(medication|antidepressant|antipsychotic|stimulant)",
    r"(?i)(diagnosis|treatment plan|recovery|coping mechanism)"
]

POLITICAL_PATTERNS = [
    r"(?i)(election|voting|ballot|campaign|candidate|political party)",
    r"(?i)(democrat|republican|liberal|conservative|progressive|right-wing|left-wing)",
    r"(?i)(policy|legislation|regulation|law|bill|amendment)",
    r"(?i)(president|senator|congressman|representative|governor|mayor)",
    r"(?i)(political opinion|stance|view|position|ideology)"
]

# Domain sensitivity thresholds
DOMAIN_SENSITIVITY_THRESHOLDS = {
    "medical": 0.7,
    "legal": 0.7,
    "financial": 0.7,
    "mental_health": 0.8,
    "political": 0.6
}

# Domain review requirements
DOMAIN_REVIEW_REQUIREMENTS = {
    "medical": ["RESEARCHER", "CEO"],
    "legal": ["RESEARCHER", "CEO"],
    "financial": ["RESEARCHER", "CEO"],
    "mental_health": ["RESEARCHER", "CEO", "PESSIMIST"],
    "political": ["RESEARCHER", "CEO", "PESSIMIST"]
}

def scan_for_domain_sensitivity(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scan text for domain sensitivity across all domains.
    
    Args:
        text: The text to scan
        
    Returns:
        Dictionary mapping domains to lists of detected sensitivities
    """
    results = {
        "medical": [],
        "legal": [],
        "financial": [],
        "mental_health": [],
        "political": []
    }
    
    # Check medical patterns
    for pattern in MEDICAL_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            results["medical"].append({
                "matched_text": match.group(0),
                "sensitivity": 0.8,  # Default sensitivity, could be refined with ML in production
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check legal patterns
    for pattern in LEGAL_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            results["legal"].append({
                "matched_text": match.group(0),
                "sensitivity": 0.8,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check financial patterns
    for pattern in FINANCIAL_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            results["financial"].append({
                "matched_text": match.group(0),
                "sensitivity": 0.8,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check mental health patterns
    for pattern in MENTAL_HEALTH_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            results["mental_health"].append({
                "matched_text": match.group(0),
                "sensitivity": 0.9,  # Higher sensitivity for mental health
                "detected_at": datetime.utcnow().isoformat()
            })
    
    # Check political patterns
    for pattern in POLITICAL_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            results["political"].append({
                "matched_text": match.group(0),
                "sensitivity": 0.7,
                "detected_at": datetime.utcnow().isoformat()
            })
    
    return results

def get_highest_sensitivity(sensitivities: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
    """
    Get the highest sensitivity for each domain.
    
    Args:
        sensitivities: Dictionary of sensitivities by domain
        
    Returns:
        Dictionary mapping domains to their highest sensitivity
    """
    highest_sensitivities = {}
    
    for domain, sensitivity_list in sensitivities.items():
        if not sensitivity_list:
            highest_sensitivities[domain] = 0.0
            continue
        
        highest = 0.0
        for sensitivity in sensitivity_list:
            sensitivity_value = sensitivity.get("sensitivity", 0.0)
            if sensitivity_value > highest:
                highest = sensitivity_value
        
        highest_sensitivities[domain] = highest
    
    return highest_sensitivities

def determine_sensitive_domains(highest_sensitivities: Dict[str, float]) -> List[str]:
    """
    Determine which domains are sensitive based on thresholds.
    
    Args:
        highest_sensitivities: Dictionary mapping domains to their highest sensitivity
        
    Returns:
        List of sensitive domains
    """
    sensitive_domains = []
    
    for domain, sensitivity in highest_sensitivities.items():
        threshold = DOMAIN_SENSITIVITY_THRESHOLDS.get(domain, 0.7)
        if sensitivity >= threshold:
            sensitive_domains.append(domain)
    
    return sensitive_domains

def get_required_reviewers(sensitive_domains: List[str]) -> Set[str]:
    """
    Get the required reviewers for the sensitive domains.
    
    Args:
        sensitive_domains: List of sensitive domains
        
    Returns:
        Set of required reviewer roles
    """
    required_reviewers = set()
    
    for domain in sensitive_domains:
        reviewers = DOMAIN_REVIEW_REQUIREMENTS.get(domain, [])
        required_reviewers.update(reviewers)
    
    return required_reviewers

def flag_domain_sensitivity(prompt: str, loop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Flag domain sensitivity by scanning for domain-specific patterns.
    
    Args:
        prompt: The prompt text to check
        loop_id: Optional loop ID for logging
        
    Returns:
        Dictionary with flagging results
    """
    # Scan for domain sensitivity
    sensitivities = scan_for_domain_sensitivity(prompt)
    
    # Get highest sensitivity for each domain
    highest_sensitivities = get_highest_sensitivity(sensitivities)
    
    # Determine sensitive domains
    sensitive_domains = determine_sensitive_domains(highest_sensitivities)
    
    # Get required reviewers
    required_reviewers = get_required_reviewers(sensitive_domains)
    
    # Determine if rerun is needed
    rerun_needed = len(sensitive_domains) > 0
    
    # Log the results
    if rerun_needed:
        if loop_id:
            logger.info(f"Domain sensitivity detected in loop {loop_id}: {sensitive_domains}")
        else:
            logger.info(f"Domain sensitivity detected: {sensitive_domains}")
    
    # Return the results
    return {
        "domain_sensitive": len(sensitive_domains) > 0,
        "sensitive_domains": sensitive_domains,
        "highest_sensitivities": highest_sensitivities,
        "sensitivities": sensitivities,
        "required_reviewers": list(required_reviewers),
        "rerun_needed": rerun_needed,
        "checked_at": datetime.utcnow().isoformat(),
        "loop_id": loop_id
    }

def get_memory_fields(flagging_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract fields to be stored in loop memory.
    
    Args:
        flagging_result: The result from flag_domain_sensitivity
        
    Returns:
        Dictionary with fields for loop memory
    """
    sensitive_domains = flagging_result.get("sensitive_domains", [])
    domain_sensitive = flagging_result.get("domain_sensitive", False)
    
    # If there are sensitive domains, use the first one as the primary domain
    primary_domain = sensitive_domains[0] if sensitive_domains else None
    
    return {
        "domain_sensitive": domain_sensitive,
        "sensitive_domains": sensitive_domains,
        "primary_domain": primary_domain,
        "required_reviewers": flagging_result.get("required_reviewers", []),
        "domain_sensitivity_checked_at": flagging_result.get("checked_at")
    }

def get_reflection_prompt(flagging_result: Dict[str, Any]) -> Optional[str]:
    """
    Generate a reflection prompt based on flagging results.
    
    Args:
        flagging_result: The result from flag_domain_sensitivity
        
    Returns:
        Reflection prompt string, or None if no sensitive domains were found
    """
    sensitive_domains = flagging_result.get("sensitive_domains", [])
    if not sensitive_domains:
        return None
    
    # Build a prompt for reflection
    prompt = "The following domain sensitivities were detected:\n\n"
    
    for domain in sensitive_domains:
        sensitivities = flagging_result.get("sensitivities", {}).get(domain, [])
        if not sensitivities:
            continue
        
        prompt += f"Domain: {domain.replace('_', ' ').title()}\n"
        prompt += f"Sensitivity: {flagging_result.get('highest_sensitivities', {}).get(domain, 0.0):.2f}\n"
        prompt += "Matched content:\n"
        
        for sensitivity in sensitivities[:3]:  # Limit to first 3 matches per domain
            prompt += f"- \"{sensitivity.get('matched_text', '')}\"\n"
        
        if len(sensitivities) > 3:
            prompt += f"- ... and {len(sensitivities) - 3} more\n"
        
        prompt += "\n"
    
    required_reviewers = flagging_result.get("required_reviewers", [])
    prompt += f"Required reviewers: {', '.join(required_reviewers)}\n\n"
    
    prompt += "Please reflect on these domain sensitivities and consider:\n"
    prompt += "1. What special considerations are needed for this domain?\n"
    prompt += "2. What disclaimers or qualifications should be included?\n"
    prompt += "3. How can we ensure responsible handling of this sensitive topic?\n"
    
    return prompt

def should_trigger_rerun(flagging_result: Dict[str, Any]) -> bool:
    """
    Determine whether to trigger a rerun based on flagging results.
    
    Args:
        flagging_result: The result from flag_domain_sensitivity
        
    Returns:
        Boolean indicating whether a rerun should be triggered
    """
    return flagging_result.get("rerun_needed", False)

def get_rerun_configuration(flagging_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for rerun if needed.
    
    Args:
        flagging_result: The result from flag_domain_sensitivity
        
    Returns:
        Dictionary with rerun configuration
    """
    if not flagging_result.get("rerun_needed", False):
        return {}
    
    required_reviewers = flagging_result.get("required_reviewers", [])
    sensitive_domains = flagging_result.get("sensitive_domains", [])
    
    return {
        "depth": "deep",  # Always use deep reflection for sensitive domains
        "required_reviewers": required_reviewers,
        "rerun_reason": "domain_sensitivity_detected",
        "rerun_reason_detail": f"Sensitive domains detected: {', '.join(sensitive_domains)}",
        "rerun_trigger": ["domain_sensitivity"]
    }
