"""
Rebuilder Agent Module

This module implements the Rebuilder Agent for Promethios, which automatically
detects degradation or drift in the system and coordinates scoped rebuilds.

The Rebuilder Agent is responsible for:
1. Scanning project_manifest.json for outdated modules or version gaps
2. Detecting belief mismatches, failing agents, or CI drift
3. Scoring system stability
4. Triggering rebuild-mode loops using Orchestrator
5. Logging output to appropriate locations
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PROJECT_MANIFEST_DIR = "/home/ubuntu/repo/personal-ai-agent/data/project_manifest"
DEFAULT_STABILITY_THRESHOLD = 0.75
DEFAULT_REBUILD_THRESHOLD = 0.6

def run_agent(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the Rebuilder Agent.
    
    Args:
        context: Dictionary containing context information for the agent
        
    Returns:
        Dictionary containing the result of the agent's execution
    """
    logger.info("Rebuilder Agent started")
    
    # Extract parameters from context
    project_id = context.get("project_id", "default")
    orchestrator_mode = context.get("orchestrator_mode", "BALANCED")
    loop_id = context.get("loop_id", "unknown")
    
    # Initialize result
    result = {
        "agent_id": "rebuilder",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "project_id": project_id,
        "loop_id": loop_id,
        "stability_score": 0.0,
        "needs_rebuild": False,
        "rebuild_events": [],
        "recommendations": []
    }
    
    try:
        # Scan project manifest
        manifest_data, manifest_issues = scan_project_manifest(project_id)
        result["manifest_scan_result"] = {
            "issues_found": len(manifest_issues),
            "issues": manifest_issues
        }
        
        # Detect belief mismatches
        belief_issues = detect_belief_mismatches(project_id, manifest_data)
        result["belief_scan_result"] = {
            "issues_found": len(belief_issues),
            "issues": belief_issues
        }
        
        # Check for failing agents
        agent_issues = detect_failing_agents(project_id, manifest_data)
        result["agent_scan_result"] = {
            "issues_found": len(agent_issues),
            "issues": agent_issues
        }
        
        # Check for CI drift
        ci_issues = detect_ci_drift(project_id, manifest_data)
        result["ci_scan_result"] = {
            "issues_found": len(ci_issues),
            "issues": ci_issues
        }
        
        # Calculate stability score
        stability_score = calculate_stability_score(
            manifest_issues, belief_issues, agent_issues, ci_issues, orchestrator_mode
        )
        result["stability_score"] = stability_score
        
        # Determine if rebuild is needed
        needs_rebuild, rebuild_events = determine_rebuild_needs(
            stability_score, manifest_issues, belief_issues, agent_issues, ci_issues, orchestrator_mode
        )
        result["needs_rebuild"] = needs_rebuild
        result["rebuild_events"] = rebuild_events
        
        # Generate recommendations
        recommendations = generate_recommendations(
            stability_score, manifest_issues, belief_issues, agent_issues, ci_issues, orchestrator_mode
        )
        result["recommendations"] = recommendations
        
        # Trigger rebuild if needed
        if needs_rebuild:
            rebuild_result = trigger_rebuild(project_id, rebuild_events, orchestrator_mode)
            result["rebuild_triggered"] = True
            result["rebuild_result"] = rebuild_result
        
        # Update project manifest
        update_project_manifest(project_id, result)
        
        # Log output
        log_rebuild_events(project_id, loop_id, result)
        
        logger.info(f"Rebuilder Agent completed with stability score: {stability_score}")
        return result
    
    except Exception as e:
        logger.error(f"Error in Rebuilder Agent: {e}")
        result["error"] = str(e)
        result["status"] = "error"
        return result

def scan_project_manifest(project_id: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Scan project manifest for outdated modules or version gaps.
    
    Args:
        project_id: ID of the project to scan
        
    Returns:
        Tuple containing manifest data and list of issues found
    """
    logger.info(f"Scanning project manifest for project: {project_id}")
    
    # Ensure project manifest directory exists
    os.makedirs(PROJECT_MANIFEST_DIR, exist_ok=True)
    
    # Check if project manifest exists
    manifest_path = os.path.join(PROJECT_MANIFEST_DIR, f"{project_id}.json")
    if not os.path.exists(manifest_path):
        logger.warning(f"Project manifest not found for project: {project_id}")
        return {}, [{"type": "missing_manifest", "severity": "high", "message": f"Project manifest not found for project: {project_id}"}]
    
    try:
        # Load project manifest
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
        
        # Check for issues
        issues = []
        
        # Check for missing required fields
        required_fields = ["modules", "created_at", "updated_at", "version"]
        for field in required_fields:
            if field not in manifest_data:
                issues.append({
                    "type": "missing_field",
                    "field": field,
                    "severity": "medium",
                    "message": f"Required field '{field}' missing from project manifest"
                })
        
        # Check for outdated modules
        if "modules" in manifest_data:
            for module_name, module_data in manifest_data["modules"].items():
                # Check if module needs rebuild
                if module_data.get("needs_rebuild", False):
                    issues.append({
                        "type": "module_needs_rebuild",
                        "module": module_name,
                        "severity": "high",
                        "message": f"Module '{module_name}' is marked for rebuild"
                    })
                
                # Check for missing last_ci_result
                if "last_ci_result" not in module_data:
                    issues.append({
                        "type": "missing_ci_result",
                        "module": module_name,
                        "severity": "medium",
                        "message": f"Module '{module_name}' has no CI result"
                    })
                elif module_data["last_ci_result"].get("status") == "failed":
                    issues.append({
                        "type": "failed_ci",
                        "module": module_name,
                        "severity": "high",
                        "message": f"Module '{module_name}' failed CI tests"
                    })
                
                # Check for outdated belief version
                if "belief_version" not in module_data:
                    issues.append({
                        "type": "missing_belief_version",
                        "module": module_name,
                        "severity": "medium",
                        "message": f"Module '{module_name}' has no belief version"
                    })
        
        return manifest_data, issues
    
    except Exception as e:
        logger.error(f"Error scanning project manifest: {e}")
        return {}, [{"type": "manifest_error", "severity": "high", "message": f"Error scanning project manifest: {e}"}]

def detect_belief_mismatches(project_id: str, manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect belief mismatches in the project.
    
    Args:
        project_id: ID of the project to scan
        manifest_data: Project manifest data
        
    Returns:
        List of belief mismatch issues found
    """
    logger.info(f"Detecting belief mismatches for project: {project_id}")
    
    issues = []
    
    # Check if modules exist in manifest
    if "modules" not in manifest_data:
        return [{"type": "missing_modules", "severity": "high", "message": "No modules found in project manifest"}]
    
    # Get all belief versions
    belief_versions = {}
    for module_name, module_data in manifest_data["modules"].items():
        if "belief_version" in module_data:
            belief_version = module_data["belief_version"]
            if belief_version not in belief_versions:
                belief_versions[belief_version] = []
            belief_versions[belief_version].append(module_name)
    
    # Check for multiple belief versions
    if len(belief_versions) > 1:
        issues.append({
            "type": "multiple_belief_versions",
            "severity": "high",
            "message": f"Multiple belief versions found: {list(belief_versions.keys())}",
            "versions": belief_versions
        })
    
    # Check for modules without belief versions
    modules_without_belief = []
    for module_name, module_data in manifest_data["modules"].items():
        if "belief_version" not in module_data:
            modules_without_belief.append(module_name)
    
    if modules_without_belief:
        issues.append({
            "type": "missing_belief_versions",
            "severity": "medium",
            "message": f"Modules without belief versions: {modules_without_belief}",
            "modules": modules_without_belief
        })
    
    return issues

def detect_failing_agents(project_id: str, manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect failing agents in the project.
    
    Args:
        project_id: ID of the project to scan
        manifest_data: Project manifest data
        
    Returns:
        List of failing agent issues found
    """
    logger.info(f"Detecting failing agents for project: {project_id}")
    
    issues = []
    
    # Check if modules exist in manifest
    if "modules" not in manifest_data:
        return [{"type": "missing_modules", "severity": "high", "message": "No modules found in project manifest"}]
    
    # Check for failing agents
    for module_name, module_data in manifest_data["modules"].items():
        if module_data.get("agent_type") == "plugin" and module_data.get("status") == "failing":
            issues.append({
                "type": "failing_agent",
                "module": module_name,
                "severity": "high",
                "message": f"Agent '{module_name}' is failing",
                "last_error": module_data.get("last_error", "Unknown error")
            })
    
    return issues

def detect_ci_drift(project_id: str, manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect CI drift in the project.
    
    Args:
        project_id: ID of the project to scan
        manifest_data: Project manifest data
        
    Returns:
        List of CI drift issues found
    """
    logger.info(f"Detecting CI drift for project: {project_id}")
    
    issues = []
    
    # Check if modules exist in manifest
    if "modules" not in manifest_data:
        return [{"type": "missing_modules", "severity": "high", "message": "No modules found in project manifest"}]
    
    # Check for CI drift
    for module_name, module_data in manifest_data["modules"].items():
        if "last_ci_result" in module_data:
            ci_result = module_data["last_ci_result"]
            
            # Check for failed CI
            if ci_result.get("status") == "failed":
                issues.append({
                    "type": "failed_ci",
                    "module": module_name,
                    "severity": "high",
                    "message": f"Module '{module_name}' failed CI tests",
                    "ci_score": ci_result.get("ci_score", 0.0),
                    "failure_reason": ci_result.get("failure_reason", "Unknown reason")
                })
            
            # Check for low CI score
            elif ci_result.get("ci_score", 1.0) < 0.7:
                issues.append({
                    "type": "low_ci_score",
                    "module": module_name,
                    "severity": "medium",
                    "message": f"Module '{module_name}' has low CI score: {ci_result.get('ci_score', 0.0)}",
                    "ci_score": ci_result.get("ci_score", 0.0)
                })
    
    return issues

def calculate_stability_score(
    manifest_issues: List[Dict[str, Any]],
    belief_issues: List[Dict[str, Any]],
    agent_issues: List[Dict[str, Any]],
    ci_issues: List[Dict[str, Any]],
    orchestrator_mode: str
) -> float:
    """
    Calculate stability score based on issues found.
    
    Args:
        manifest_issues: List of manifest issues
        belief_issues: List of belief mismatch issues
        agent_issues: List of failing agent issues
        ci_issues: List of CI drift issues
        orchestrator_mode: Mode of the orchestrator
        
    Returns:
        Stability score between 0.0 and 1.0
    """
    logger.info("Calculating stability score")
    
    # Define weights based on orchestrator mode
    weights = {
        "FAST": {"manifest": 0.2, "belief": 0.2, "agent": 0.3, "ci": 0.3},
        "BALANCED": {"manifest": 0.25, "belief": 0.25, "agent": 0.25, "ci": 0.25},
        "THOROUGH": {"manifest": 0.3, "belief": 0.3, "agent": 0.2, "ci": 0.2},
        "RESEARCH": {"manifest": 0.4, "belief": 0.4, "agent": 0.1, "ci": 0.1}
    }
    
    # Use BALANCED weights if orchestrator mode is not recognized
    mode_weights = weights.get(orchestrator_mode, weights["BALANCED"])
    
    # Calculate severity scores
    def calculate_severity_score(issues: List[Dict[str, Any]]) -> float:
        if not issues:
            return 1.0
        
        severity_weights = {"low": 0.25, "medium": 0.5, "high": 1.0}
        total_severity = sum(severity_weights.get(issue.get("severity", "medium"), 0.5) for issue in issues)
        return max(0.0, 1.0 - (total_severity / (len(issues) * 2)))
    
    # Calculate component scores
    manifest_score = calculate_severity_score(manifest_issues)
    belief_score = calculate_severity_score(belief_issues)
    agent_score = calculate_severity_score(agent_issues)
    ci_score = calculate_severity_score(ci_issues)
    
    # Calculate weighted stability score
    stability_score = (
        manifest_score * mode_weights["manifest"] +
        belief_score * mode_weights["belief"] +
        agent_score * mode_weights["agent"] +
        ci_score * mode_weights["ci"]
    )
    
    logger.info(f"Stability score: {stability_score:.2f} (manifest: {manifest_score:.2f}, belief: {belief_score:.2f}, agent: {agent_score:.2f}, ci: {ci_score:.2f})")
    return stability_score

def determine_rebuild_needs(
    stability_score: float,
    manifest_issues: List[Dict[str, Any]],
    belief_issues: List[Dict[str, Any]],
    agent_issues: List[Dict[str, Any]],
    ci_issues: List[Dict[str, Any]],
    orchestrator_mode: str
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Determine if rebuild is needed based on stability score and issues.
    
    Args:
        stability_score: Stability score between 0.0 and 1.0
        manifest_issues: List of manifest issues
        belief_issues: List of belief mismatch issues
        agent_issues: List of failing agent issues
        ci_issues: List of CI drift issues
        orchestrator_mode: Mode of the orchestrator
        
    Returns:
        Tuple containing boolean indicating if rebuild is needed and list of rebuild events
    """
    logger.info(f"Determining rebuild needs with stability score: {stability_score}")
    
    # Define rebuild thresholds based on orchestrator mode
    thresholds = {
        "FAST": 0.5,
        "BALANCED": 0.6,
        "THOROUGH": 0.7,
        "RESEARCH": 0.8
    }
    
    # Use BALANCED threshold if orchestrator mode is not recognized
    rebuild_threshold = thresholds.get(orchestrator_mode, thresholds["BALANCED"])
    
    # Determine if rebuild is needed
    needs_rebuild = stability_score < rebuild_threshold
    
    # Generate rebuild events
    rebuild_events = []
    
    if needs_rebuild:
        # Add overall stability event
        rebuild_events.append({
            "type": "low_stability",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "stability_score": stability_score,
            "threshold": rebuild_threshold,
            "orchestrator_mode": orchestrator_mode,
            "message": f"System stability score ({stability_score:.2f}) is below threshold ({rebuild_threshold:.2f})"
        })
        
        # Add events for high severity issues
        all_issues = manifest_issues + belief_issues + agent_issues + ci_issues
        for issue in all_issues:
            if issue.get("severity") == "high":
                rebuild_events.append({
                    "type": issue.get("type", "unknown_issue"),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "severity": "high",
                    "message": issue.get("message", "Unknown issue"),
                    "details": {k: v for k, v in issue.items() if k not in ["type", "severity", "message"]}
                })
    
    logger.info(f"Rebuild needed: {needs_rebuild}, events: {len(rebuild_events)}")
    return needs_rebuild, rebuild_events

def generate_recommendations(
    stability_score: float,
    manifest_issues: List[Dict[str, Any]],
    belief_issues: List[Dict[str, Any]],
    agent_issues: List[Dict[str, Any]],
    ci_issues: List[Dict[str, Any]],
    orchestrator_mode: str
) -> List[Dict[str, Any]]:
    """
    Generate recommendations based on issues found.
    
    Args:
        stability_score: Stability score between 0.0 and 1.0
        manifest_issues: List of manifest issues
        belief_issues: List of belief mismatch issues
        agent_issues: List of failing agent issues
        ci_issues: List of CI drift issues
        orchestrator_mode: Mode of the orchestrator
        
    Returns:
        List of recommendations
    """
    logger.info("Generating recommendations")
    
    recommendations = []
    
    # Define stability thresholds
    stability_thresholds = {
        "critical": 0.4,
        "warning": 0.6,
        "good": 0.8
    }
    
    # Add overall stability recommendation
    if stability_score < stability_thresholds["critical"]:
        recommendations.append({
            "type": "critical_stability",
            "priority": "high",
            "message": f"Critical stability issues detected (score: {stability_score:.2f}). Immediate rebuild recommended.",
            "action": "rebuild_system"
        })
    elif stability_score < stability_thresholds["warning"]:
        recommendations.append({
            "type": "low_stability",
            "priority": "medium",
            "message": f"Low stability score detected ({stability_score:.2f}). Consider rebuilding affected modules.",
            "action": "rebuild_modules"
        })
    elif stability_score < stability_thresholds["good"]:
        recommendations.append({
            "type": "moderate_stability",
            "priority": "low",
            "message": f"Moderate stability score ({stability_score:.2f}). Monitor system for further degradation.",
            "action": "monitor_system"
        })
    else:
        recommendations.append({
            "type": "good_stability",
            "priority": "info",
            "message": f"Good stability score ({stability_score:.2f}). No action needed.",
            "action": "none"
        })
    
    # Add recommendations for specific issues
    for issue in manifest_issues:
        if issue.get("type") == "module_needs_rebuild":
            recommendations.append({
                "type": "rebuild_module",
                "priority": "high",
                "message": f"Rebuild module '{issue.get('module', 'unknown')}' as it is marked for rebuild.",
                "action": "rebuild_module",
                "module": issue.get("module", "unknown")
            })
    
    for issue in belief_issues:
        if issue.get("type") == "multiple_belief_versions":
            recommendations.append({
                "type": "align_belief_versions",
                "priority": "high",
                "message": "Align belief versions across all modules to ensure consistency.",
                "action": "align_beliefs",
                "versions": issue.get("versions", {})
            })
    
    for issue in agent_issues:
        if issue.get("type") == "failing_agent":
            recommendations.append({
                "type": "fix_agent",
                "priority": "high",
                "message": f"Fix failing agent '{issue.get('module', 'unknown')}'.",
                "action": "fix_agent",
                "module": issue.get("module", "unknown"),
                "error": issue.get("last_error", "Unknown error")
            })
    
    for issue in ci_issues:
        if issue.get("type") == "failed_ci":
            recommendations.append({
                "type": "fix_ci",
                "priority": "high",
                "message": f"Fix CI failures for module '{issue.get('module', 'unknown')}'.",
                "action": "fix_ci",
                "module": issue.get("module", "unknown"),
                "failure_reason": issue.get("failure_reason", "Unknown reason")
            })
    
    logger.info(f"Generated {len(recommendations)} recommendations")
    return recommendations

def trigger_rebuild(project_id: str, rebuild_events: List[Dict[str, Any]], orchestrator_mode: str) -> Dict[str, Any]:
    """
    Trigger rebuild using Orchestrator.
    
    Args:
        project_id: ID of the project to rebuild
        rebuild_events: List of rebuild events
        orchestrator_mode: Mode of the orchestrator
        
    Returns:
        Dictionary containing result of rebuild trigger
    """
    logger.info(f"Triggering rebuild for project: {project_id}")
    
    # In a real implementation, this would call the Orchestrator API
    # For now, we'll just return a mock result
    
    rebuild_id = f"rebuild-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    result = {
        "rebuild_id": rebuild_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "project_id": project_id,
        "orchestrator_mode": orchestrator_mode,
        "status": "triggered",
        "events": rebuild_events
    }
    
    logger.info(f"Rebuild triggered with ID: {rebuild_id}")
    return result

def update_project_manifest(project_id: str, result: Dict[str, Any]) -> bool:
    """
    Update project manifest with rebuild results.
    
    Args:
        project_id: ID of the project
        result: Result of the Rebuilder Agent execution
        
    Returns:
        Boolean indicating success
    """
    logger.info(f"Updating project manifest for project: {project_id}")
    
    # Ensure project manifest directory exists
    os.makedirs(PROJECT_MANIFEST_DIR, exist_ok=True)
    
    # Check if project manifest exists
    manifest_path = os.path.join(PROJECT_MANIFEST_DIR, f"{project_id}.json")
    
    try:
        # Load existing manifest or create new one
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
        else:
            manifest_data = {
                "project_id": project_id,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "updated_at": datetime.datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "modules": {}
            }
        
        # Update manifest with rebuild results
        manifest_data["updated_at"] = datetime.datetime.utcnow().isoformat()
        manifest_data["last_stability_score"] = result["stability_score"]
        manifest_data["last_rebuild_check"] = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "needs_rebuild": result["needs_rebuild"],
            "rebuild_events": result["rebuild_events"],
            "recommendations": result["recommendations"]
        }
        
        # Save manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        logger.info(f"Project manifest updated for project: {project_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating project manifest: {e}")
        return False

def log_rebuild_events(project_id: str, loop_id: str, result: Dict[str, Any]) -> bool:
    """
    Log rebuild events to appropriate locations.
    
    Args:
        project_id: ID of the project
        loop_id: ID of the current loop
        result: Result of the Rebuilder Agent execution
        
    Returns:
        Boolean indicating success
    """
    logger.info(f"Logging rebuild events for project: {project_id}, loop: {loop_id}")
    
    try:
        # In a real implementation, this would log to various locations:
        # 1. loop_trace.rebuild_events[]
        # 2. project_manifest.json
        # 3. Operator UI summaries
        
        # For now, we'll just log to the console
        if result["needs_rebuild"]:
            logger.info(f"Rebuild needed for project: {project_id}")
            for event in result["rebuild_events"]:
                logger.info(f"Rebuild event: {event['type']} - {event['message']}")
        else:
            logger.info(f"No rebuild needed for project: {project_id}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error logging rebuild events: {e}")
        return False
