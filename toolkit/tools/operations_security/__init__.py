"""
Operations & Security Tools

This module provides tools for operations and security-related tasks including environment secret checking,
agent self-diagnostics, escalation handling, timeout management, task completion verification,
and failure reason analysis.
"""

import os
import time
import random
import datetime
from typing import Dict, List, Any, Optional

# Import the registry for tool registration
from ...registry import register_tool


def env_secret_check(required_vars: List[str], prefix: str = None) -> Dict[str, Any]:
    """
    Verify that expected environment variables (API keys, tokens) are present.
    
    Args:
        required_vars: List of required environment variable names
        prefix: Optional prefix for filtering environment variables
        
    Returns:
        A dictionary containing the check results and metadata
    """
    # Initialize results
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "required_vars": required_vars,
        "prefix": prefix,
        "status": "success",
        "present": [],
        "missing": [],
        "recommendations": []
    }
    
    # Filter environment variables if prefix is provided
    if prefix:
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(prefix)}
        results["prefix_vars_count"] = len(env_vars)
    else:
        env_vars = os.environ
    
    # Check for required variables
    for var in required_vars:
        if var in env_vars:
            # Check if value is empty
            if env_vars[var].strip():
                results["present"].append(var)
            else:
                results["missing"].append(var)
                results["recommendations"].append(f"Variable {var} exists but has an empty value")
        else:
            results["missing"].append(var)
    
    # Update status based on missing variables
    if results["missing"]:
        results["status"] = "error"
        results["message"] = f"Missing {len(results['missing'])} required environment variables"
    else:
        results["message"] = "All required environment variables are present"
    
    # Generate recommendations for missing variables
    for var in results["missing"]:
        if var not in env_vars:
            results["recommendations"].append(f"Add {var} to environment variables")
    
    # Add security recommendations
    results["security_recommendations"] = [
        "Store sensitive values in environment variables, not in code",
        "Use a .env file for local development (but don't commit it to version control)",
        "Consider using a secrets management service for production environments",
        "Rotate API keys and tokens regularly",
        "Use different API keys for development and production environments"
    ]
    
    return results


def agent_self_check(active_tools: List[str] = None, recent_errors: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Return diagnostic information about the active toolkit, recent errors, and tool failures.
    
    Args:
        active_tools: List of currently active tool names
        recent_errors: List of recent error dictionaries
        
    Returns:
        A dictionary containing diagnostic information and recommendations
    """
    # Default values if not provided
    if active_tools is None:
        active_tools = []
    
    if recent_errors is None:
        recent_errors = []
    
    # Initialize diagnostic results
    diagnostics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_status": "operational",
        "toolkit": {
            "active_tools_count": len(active_tools),
            "active_tools": active_tools
        },
        "errors": {
            "recent_count": len(recent_errors),
            "recent_errors": recent_errors,
            "error_categories": categorize_errors(recent_errors)
        },
        "performance": {
            "response_time": f"{random.uniform(0.5, 2.0):.2f} seconds",  # Simulated response time
            "memory_usage": f"{random.uniform(100, 500):.1f} MB",  # Simulated memory usage
            "uptime": f"{random.randint(1, 24)} hours {random.randint(0, 59)} minutes"  # Simulated uptime
        }
    }
    
    # Analyze errors and determine agent status
    if recent_errors:
        critical_errors = [e for e in recent_errors if e.get("severity") == "critical"]
        if critical_errors:
            diagnostics["agent_status"] = "degraded"
            if len(critical_errors) > 2:
                diagnostics["agent_status"] = "critical"
    
    # Generate health score (0-100)
    health_score = calculate_health_score(diagnostics["agent_status"], len(recent_errors))
    diagnostics["health_score"] = health_score
    
    # Generate recommendations based on diagnostics
    diagnostics["recommendations"] = generate_recommendations(diagnostics)
    
    return diagnostics


def categorize_errors(errors: List[Dict[str, Any]]) -> Dict[str, int]:
    """Helper function to categorize errors by type."""
    categories = {}
    
    for error in errors:
        category = error.get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1
    
    return categories


def calculate_health_score(status: str, error_count: int) -> int:
    """Helper function to calculate agent health score."""
    base_score = {
        "operational": 90,
        "degraded": 60,
        "critical": 30
    }.get(status, 50)
    
    # Reduce score based on error count
    error_penalty = min(30, error_count * 5)
    
    return max(0, base_score - error_penalty)


def generate_recommendations(diagnostics: Dict[str, Any]) -> List[str]:
    """Helper function to generate recommendations based on diagnostics."""
    recommendations = []
    
    # Status-based recommendations
    if diagnostics["agent_status"] == "critical":
        recommendations.append("Restart the agent to clear critical errors")
        recommendations.append("Review and fix critical errors before proceeding with tasks")
    
    elif diagnostics["agent_status"] == "degraded":
        recommendations.append("Monitor agent performance closely")
        recommendations.append("Consider restarting the agent if performance continues to degrade")
    
    # Error-based recommendations
    error_categories = diagnostics["errors"]["error_categories"]
    for category, count in error_categories.items():
        if category == "timeout":
            recommendations.append(f"Adjust timeout settings for tools experiencing timeouts ({count} occurrences)")
        elif category == "api":
            recommendations.append(f"Check API connectivity and credentials ({count} API errors)")
        elif category == "memory":
            recommendations.append("Optimize memory usage or increase available memory")
    
    # General recommendations
    recommendations.append("Regularly run self-checks to monitor agent health")
    if diagnostics["health_score"] < 80:
        recommendations.append("Schedule maintenance to address issues affecting health score")
    
    return recommendations


def guardian_escalate(issue_type: str, severity: str = "medium", context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Trigger a reflection and warning memory about a potential issue.
    
    Args:
        issue_type: Type of issue being escalated
        severity: Severity level of the issue
        context: Additional context about the issue
        
    Returns:
        A dictionary containing the escalation details and reflection
    """
    # Default context if not provided
    if context is None:
        context = {}
    
    # Validate severity
    valid_severities = ["low", "medium", "high", "critical"]
    if severity not in valid_severities:
        severity = "medium"
    
    # Initialize escalation
    escalation = {
        "timestamp": datetime.datetime.now().isoformat(),
        "issue_type": issue_type,
        "severity": severity,
        "context": context,
        "escalation_id": f"esc_{int(time.time())}_{random.randint(1000, 9999)}",
        "status": "open"
    }
    
    # Generate reflection based on issue type
    reflection = generate_reflection(issue_type, severity, context)
    escalation["reflection"] = reflection
    
    # Generate action plan based on severity and issue type
    action_plan = generate_action_plan(issue_type, severity)
    escalation["action_plan"] = action_plan
    
    # Add memory tags
    escalation["memory_tags"] = [
        "reflection",
        f"issue:{issue_type}",
        f"severity:{severity}",
        "guardian_escalation"
    ]
    
    # Add user notification if high severity
    if severity in ["high", "critical"]:
        escalation["user_notification"] = {
            "required": True,
            "message": f"Important: A {severity} severity issue has been detected: {reflection['summary']}",
            "acknowledge_required": severity == "critical"
        }
    else:
        escalation["user_notification"] = {
            "required": False
        }
    
    return escalation


def generate_reflection(issue_type: str, severity: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to generate reflection based on issue type."""
    reflection = {
        "summary": f"{severity.capitalize()} {issue_type} issue detected",
        "detailed_analysis": "",
        "learning_points": []
    }
    
    # Generate detailed analysis based on issue type
    if issue_type == "security":
        reflection["summary"] = f"{severity.capitalize()} security concern detected"
        reflection["detailed_analysis"] = "The agent has detected a potential security issue that requires attention. "
        
        if "action" in context:
            reflection["detailed_analysis"] += f"The triggering action was: {context['action']}. "
        
        if severity == "critical":
            reflection["detailed_analysis"] += "This issue poses significant risk and requires immediate action."
        elif severity == "high":
            reflection["detailed_analysis"] += "This issue should be addressed promptly to mitigate potential risks."
        
        reflection["learning_points"] = [
            "Security issues should be addressed proactively",
            "Regular security audits can help prevent similar issues",
            "Implement principle of least privilege for all operations"
        ]
    
    elif issue_type == "data_quality":
        reflection["summary"] = f"{severity.capitalize()} data quality issue detected"
        reflection["detailed_analysis"] = "The agent has detected potential issues with data quality. "
        
        if "data_source" in context:
            reflection["detailed_analysis"] += f"The affected data source is: {context['data_source']}. "
        
        if "error_rate" in context:
            reflection["detailed_analysis"] += f"The estimated error rate is: {context['error_rate']}. "
        
        reflection["learning_points"] = [
            "Data quality issues can propagate through the system",
            "Implement validation checks at data entry points",
            "Consider data cleaning procedures for existing datasets"
        ]
    
    elif issue_type == "performance":
        reflection["summary"] = f"{severity.capitalize()} performance degradation detected"
        reflection["detailed_analysis"] = "The agent has detected performance issues that may affect operation. "
        
        if "response_time" in context:
            reflection["detailed_analysis"] += f"Current response time: {context['response_time']}. "
        
        if "memory_usage" in context:
            reflection["detailed_analysis"] += f"Current memory usage: {context['memory_usage']}. "
        
        reflection["learning_points"] = [
            "Performance issues can compound over time",
            "Regular monitoring helps detect issues early",
            "Consider resource optimization or scaling solutions"
        ]
    
    elif issue_type == "ethical":
        reflection["summary"] = f"{severity.capitalize()} ethical concern detected"
        reflection["detailed_analysis"] = "The agent has identified a potential ethical concern that requires review. "
        
        if "concern" in context:
            reflection["detailed_analysis"] += f"The specific concern is: {context['concern']}. "
        
        reflection["learning_points"] = [
            "Ethical considerations should be prioritized in decision-making",
            "Establish clear ethical guidelines for agent operations",
            "Regular ethical reviews can help identify potential issues"
        ]
    
    else:
        # Generic reflection for other issue types
        reflection["detailed_analysis"] = f"The agent has detected an issue of type '{issue_type}' with '{severity}' severity. "
        
        if context:
            reflection["detailed_analysis"] += f"Additional context: {str(context)}. "
        
        reflection["learning_points"] = [
            "Regular monitoring helps detect issues early",
            "Document issues to identify patterns over time",
            "Establish clear protocols for handling different issue types"
        ]
    
    return reflection


def generate_action_plan(issue_type: str, severity: str) -> List[Dict[str, Any]]:
    """Helper function to generate action plan based on issue type and severity."""
    action_plan = []
    
    # Common actions for all issue types
    action_plan.append({
        "action": "document_issue",
        "description": "Document the issue with all relevant details",
        "priority": "high",
        "assignee": "agent"
    })
    
    # Severity-based escalation
    if severity in ["high", "critical"]:
        action_plan.append({
            "action": "notify_user",
            "description": "Notify user about the detected issue",
            "priority": "immediate",
            "assignee": "agent"
        })
    
    # Issue-specific actions
    if issue_type == "security":
        action_plan.append({
            "action": "restrict_operations",
            "description": "Temporarily restrict sensitive operations",
            "priority": severity,
            "assignee": "agent"
        })
        
        if severity in ["high", "critical"]:
            action_plan.append({
                "action": "security_audit",
                "description": "Conduct a security audit of affected systems",
                "priority": "high",
                "assignee": "user"
            })
    
    elif issue_type == "data_quality":
        action_plan.append({
            "action": "validate_data",
            "description": "Perform additional validation on incoming data",
            "priority": "high",
            "assignee": "agent"
        })
        
        action_plan.append({
            "action": "data_cleanup",
            "description": "Identify and clean affected data",
            "priority": severity,
            "assignee": "agent"
        })
    
    elif issue_type == "performance":
        action_plan.append({
            "action": "optimize_resources",
            "description": "Identify and optimize resource usage",
            "priority": severity,
            "assignee": "agent"
        })
        
        if severity in ["high", "critical"]:
            action_plan.append({
                "action": "scale_resources",
                "description": "Consider scaling resources or infrastructure",
                "priority": "medium",
                "assignee": "user"
            })
    
    elif issue_type == "ethical":
        action_plan.append({
            "action": "pause_operation",
            "description": "Pause the operation raising ethical concerns",
            "priority": "high",
            "assignee": "agent"
        })
        
        action_plan.append({
            "action": "ethical_review",
            "description": "Conduct an ethical review of the operation",
            "priority": "high",
            "assignee": "user"
        })
    
    # Add follow-up action for all issues
    action_plan.append({
        "action": "review_and_improve",
        "description": "Review incident and implement preventive measures",
        "priority": "medium",
        "assignee": "user and agent"
    })
    
    return action_plan


def tool_timeout_limit(tool_name: str = None, category: str = None) -> Dict[str, Any]:
    """
    Return timeout and retry policy configuration for specific tools.
    
    Args:
        tool_name: Specific tool name to get configuration for
        category: Tool category to get configuration for
        
    Returns:
        A dictionary containing timeout and retry policies
    """
    # Define default policies
    default_policy = {
        "timeout_seconds": 30,
        "max_retries": 3,
        "retry_delay_seconds": 2,
        "exponential_backoff": True,
        "circuit_breaker": {
            "enabled": True,
            "failure_threshold": 5,
            "reset_timeout_seconds": 300
        }
    }
    
    # Define category-specific policies
    category_policies = {
        "API": {
            "timeout_seconds": 10,
            "max_retries": 3,
            "retry_delay_seconds": 1,
            "exponential_backoff": True,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 3,
                "reset_timeout_seconds": 180
            }
        },
        "Database": {
            "timeout_seconds": 15,
            "max_retries": 2,
            "retry_delay_seconds": 2,
            "exponential_backoff": True,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 3,
                "reset_timeout_seconds": 240
            }
        },
        "File": {
            "timeout_seconds": 20,
            "max_retries": 2,
            "retry_delay_seconds": 1,
            "exponential_backoff": False,
            "circuit_breaker": {
                "enabled": False
            }
        },
        "Network": {
            "timeout_seconds": 30,
            "max_retries": 5,
            "retry_delay_seconds": 2,
            "exponential_backoff": True,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 5,
                "reset_timeout_seconds": 300
            }
        },
        "Computation": {
            "timeout_seconds": 60,
            "max_retries": 1,
            "retry_delay_seconds": 5,
            "exponential_backoff": False,
            "circuit_breaker": {
                "enabled": False
            }
        },
        "External": {
            "timeout_seconds": 45,
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "exponential_backoff": True,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 3,
                "reset_timeout_seconds": 600
            }
        }
    }
    
    # Define tool-specific policies
    tool_policies = {
        "api.request": {
            "timeout_seconds": 15,
            "max_retries": 3,
            "retry_delay_seconds": 2,
            "exponential_backoff": True,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 3,
                "reset_timeout_seconds": 180
            }
        },
        "db.query": {
            "timeout_seconds": 20,
            "max_retries": 2,
            "retry_delay_seconds": 3,
            "exponential_backoff": True,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 3,
                "reset_timeout_seconds": 240
            }
        },
        "file.large.process": {
            "timeout_seconds": 120,
            "max_retries": 1,
            "retry_delay_seconds": 10,
            "exponential_backoff": False,
            "circuit_breaker": {
                "enabled": False
            }
        },
        "ml.model.predict": {
            "timeout_seconds": 90,
            "max_retries": 1,
            "retry_delay_seconds": 5,
            "exponential_backoff": False,
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 2,
                "reset_timeout_seconds": 600
            }
        }
    }
    
    # Initialize result
    result = {
        "timestamp": datetime.datetime.now().isoformat(),
        "policies": {}
    }
    
    # Return specific tool policy if requested
    if tool_name:
        result["tool_name"] = tool_name
        result["policies"]["tool"] = tool_policies.get(tool_name, default_policy)
        
        # Add category policy if tool belongs to a known category
        tool_category = get_tool_category(tool_name)
        if tool_category and tool_category in category_policies:
            result["category"] = tool_category
            result["policies"]["category"] = category_policies[tool_category]
        
        result["policies"]["default"] = default_policy
        result["effective_policy"] = merge_policies(result["policies"])
    
    # Return category policy if requested
    elif category:
        result["category"] = category
        result["policies"]["category"] = category_policies.get(category, default_policy)
        result["policies"]["default"] = default_policy
        result["effective_policy"] = merge_policies(result["policies"])
    
    # Return all policies if no specific request
    else:
        result["policies"]["tool_specific"] = tool_policies
        result["policies"]["category"] = category_policies
        result["policies"]["default"] = default_policy
    
    # Add recommendations
    result["recommendations"] = generate_timeout_recommendations(result)
    
    return result


def get_tool_category(tool_name: str) -> Optional[str]:
    """Helper function to determine tool category from name."""
    tool_categories = {
        "api": "API",
        "db": "Database",
        "file": "File",
        "network": "Network",
        "compute": "Computation",
        "ml": "Computation",
        "external": "External"
    }
    
    # Check if tool name starts with any of the category prefixes
    for prefix, category in tool_categories.items():
        if tool_name.lower().startswith(prefix):
            return category
    
    return None


def merge_policies(policies: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Helper function to merge policies with priority: tool > category > default."""
    merged = policies["default"].copy()
    
    if "category" in policies:
        for key, value in policies["category"].items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
    
    if "tool" in policies:
        for key, value in policies["tool"].items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
    
    return merged


def generate_timeout_recommendations(result: Dict[str, Any]) -> List[str]:
    """Helper function to generate timeout policy recommendations."""
    recommendations = []
    
    if "effective_policy" in result:
        policy = result["effective_policy"]
        
        # Timeout recommendations
        if policy["timeout_seconds"] < 10:
            recommendations.append("Consider increasing timeout for more complex operations")
        elif policy["timeout_seconds"] > 60:
            recommendations.append("Long timeouts may impact user experience; consider async processing for long operations")
        
        # Retry recommendations
        if policy["max_retries"] > 3:
            recommendations.append("High retry counts may mask underlying issues; consider improving error handling")
        
        # Circuit breaker recommendations
        if policy["circuit_breaker"]["enabled"]:
            recommendations.append("Monitor circuit breaker activations to identify systemic issues")
        else:
            recommendations.append("Consider enabling circuit breaker for improved fault tolerance")
    
    # General recommendations
    recommendations.extend([
        "Adjust timeouts based on observed performance metrics",
        "Implement graceful degradation for when services time out",
        "Log timeout and retry events for analysis"
    ])
    
    return recommendations


def task_finish_check(goal: str, checkpoints: List[str] = None, activity_log: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Scan current goal for missing checkpoints or agent activity.
    
    Args:
        goal: The current goal or task description
        checkpoints: List of checkpoint descriptions
        activity_log: List of agent activity entries
        
    Returns:
        A dictionary containing the completion status and recommendations
    """
    # Default values if not provided
    if checkpoints is None:
        checkpoints = []
    
    if activity_log is None:
        activity_log = []
    
    # Initialize result
    result = {
        "timestamp": datetime.datetime.now().isoformat(),
        "goal": goal,
        "checkpoints": {
            "total": len(checkpoints),
            "items": []
        },
        "activity": {
            "total": len(activity_log),
            "categories": categorize_activity(activity_log)
        },
        "completion_status": "incomplete"
    }
    
    # Process checkpoints
    completed_checkpoints = 0
    for i, checkpoint in enumerate(checkpoints):
        checkpoint_status = {
            "id": i + 1,
            "description": checkpoint,
            "status": "incomplete",
            "evidence": []
        }
        
        # Check if checkpoint is completed based on activity log
        for activity in activity_log:
            if is_checkpoint_satisfied(checkpoint, activity):
                checkpoint_status["status"] = "complete"
                checkpoint_status["evidence"].append(activity)
        
        if checkpoint_status["status"] == "complete":
            completed_checkpoints += 1
        
        result["checkpoints"]["items"].append(checkpoint_status)
    
    # Calculate completion percentage
    if checkpoints:
        completion_percentage = (completed_checkpoints / len(checkpoints)) * 100
        result["completion_percentage"] = round(completion_percentage, 1)
        
        # Determine overall status
        if completion_percentage == 100:
            result["completion_status"] = "complete"
        elif completion_percentage >= 80:
            result["completion_status"] = "nearly_complete"
        elif completion_percentage >= 50:
            result["completion_status"] = "in_progress"
        else:
            result["completion_status"] = "early_stages"
    else:
        # No checkpoints provided, use activity analysis
        if activity_log:
            # Simple heuristic: if we have activity and the last activity is recent, consider it in progress
            result["completion_status"] = "in_progress"
        else:
            result["completion_status"] = "not_started"
    
    # Identify missing checkpoints
    result["missing_checkpoints"] = [
        cp for cp in result["checkpoints"]["items"] if cp["status"] == "incomplete"
    ]
    
    # Generate recommendations
    result["recommendations"] = generate_task_recommendations(result)
    
    return result


def categorize_activity(activity_log: List[Dict[str, Any]]) -> Dict[str, int]:
    """Helper function to categorize agent activity."""
    categories = {}
    
    for activity in activity_log:
        category = activity.get("category", "other")
        categories[category] = categories.get(category, 0) + 1
    
    return categories


def is_checkpoint_satisfied(checkpoint: str, activity: Dict[str, Any]) -> bool:
    """Helper function to determine if an activity satisfies a checkpoint."""
    # Simple implementation: check if checkpoint description appears in activity description
    checkpoint_lower = checkpoint.lower()
    activity_desc = activity.get("description", "").lower()
    
    return checkpoint_lower in activity_desc


def generate_task_recommendations(result: Dict[str, Any]) -> List[str]:
    """Helper function to generate task completion recommendations."""
    recommendations = []
    
    # Status-based recommendations
    if result["completion_status"] == "complete":
        recommendations.append("Verify all outputs meet quality standards")
        recommendations.append("Document any lessons learned for future tasks")
    
    elif result["completion_status"] == "nearly_complete":
        recommendations.append("Focus on completing the remaining checkpoints")
        recommendations.append("Review completed work for consistency")
    
    elif result["completion_status"] == "in_progress":
        recommendations.append("Continue working through remaining checkpoints sequentially")
        recommendations.append("Consider re-prioritizing remaining work based on dependencies")
    
    elif result["completion_status"] == "early_stages":
        recommendations.append("Create a more detailed plan for completing the task")
        recommendations.append("Focus on foundational checkpoints first")
    
    elif result["completion_status"] == "not_started":
        recommendations.append("Begin by breaking down the goal into specific checkpoints")
        recommendations.append("Start with information gathering and planning activities")
    
    # Missing checkpoint recommendations
    if result.get("missing_checkpoints"):
        if len(result["missing_checkpoints"]) <= 3:
            for cp in result["missing_checkpoints"]:
                recommendations.append(f"Complete checkpoint {cp['id']}: {cp['description']}")
        else:
            recommendations.append(f"Prioritize the {len(result['missing_checkpoints'])} remaining checkpoints")
    
    # Activity-based recommendations
    activity_categories = result["activity"]["categories"]
    if not activity_categories:
        recommendations.append("Begin recording activities to track progress")
    elif "error" in activity_categories and activity_categories["error"] > 0:
        recommendations.append("Address errors in previous activities before proceeding")
    
    return recommendations


def agent_escalate_reason(task_id: str, status: str = "paused", context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Output a summary of why a task failed or was paused.
    
    Args:
        task_id: Identifier for the task
        status: Current status of the task (failed, paused, etc.)
        context: Additional context about the task
        
    Returns:
        A dictionary containing the escalation reason and recommendations
    """
    # Default context if not provided
    if context is None:
        context = {}
    
    # Initialize result
    result = {
        "timestamp": datetime.datetime.now().isoformat(),
        "task_id": task_id,
        "status": status,
        "context": context,
        "escalation_id": f"esc_{int(time.time())}_{random.randint(1000, 9999)}"
    }
    
    # Generate reason based on status and context
    if status == "failed":
        result["reason"] = generate_failure_reason(context)
    elif status == "paused":
        result["reason"] = generate_pause_reason(context)
    else:
        result["reason"] = {
            "summary": f"Task {task_id} has been {status}",
            "details": f"The task is currently in {status} status.",
            "root_cause": "Unknown"
        }
    
    # Generate action plan
    result["action_plan"] = generate_escalation_action_plan(status, result["reason"])
    
    # Generate user message
    result["user_message"] = generate_user_message(task_id, status, result["reason"])
    
    # Add severity level
    result["severity"] = determine_severity(status, result["reason"])
    
    return result


def generate_failure_reason(context: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to generate failure reason based on context."""
    reason = {
        "summary": "Task execution failed",
        "details": "The task could not be completed due to encountered issues.",
        "root_cause": "Unknown"
    }
    
    # Determine root cause from context
    if "error" in context:
        reason["summary"] = f"Task failed due to error: {context['error']}"
        reason["details"] = f"An error occurred during task execution: {context['error']}"
        reason["root_cause"] = "Error during execution"
    
    elif "timeout" in context:
        reason["summary"] = "Task failed due to timeout"
        reason["details"] = f"The task exceeded the allocated time limit of {context.get('timeout_seconds', 'unknown')} seconds."
        reason["root_cause"] = "Execution timeout"
    
    elif "resource_limit" in context:
        reason["summary"] = f"Task failed due to {context['resource_limit']} limit exceeded"
        reason["details"] = f"The task exceeded the {context['resource_limit']} limit."
        reason["root_cause"] = "Resource limit exceeded"
    
    elif "dependency_failure" in context:
        reason["summary"] = f"Task failed due to dependency failure: {context['dependency_failure']}"
        reason["details"] = f"A required dependency failed: {context['dependency_failure']}"
        reason["root_cause"] = "Dependency failure"
    
    elif "validation_failure" in context:
        reason["summary"] = "Task failed validation checks"
        reason["details"] = f"The task output failed validation: {context['validation_failure']}"
        reason["root_cause"] = "Validation failure"
    
    elif "permission_denied" in context:
        reason["summary"] = "Task failed due to insufficient permissions"
        reason["details"] = f"The agent lacks required permissions: {context['permission_denied']}"
        reason["root_cause"] = "Permission denied"
    
    # Add failure point if available
    if "failure_point" in context:
        reason["failure_point"] = context["failure_point"]
    
    # Add error code if available
    if "error_code" in context:
        reason["error_code"] = context["error_code"]
    
    return reason


def generate_pause_reason(context: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to generate pause reason based on context."""
    reason = {
        "summary": "Task execution paused",
        "details": "The task has been temporarily paused.",
        "root_cause": "Manual pause"
    }
    
    # Determine root cause from context
    if "user_request" in context:
        reason["summary"] = "Task paused at user request"
        reason["details"] = f"The task was paused as requested by the user: {context['user_request']}"
        reason["root_cause"] = "User request"
    
    elif "waiting_input" in context:
        reason["summary"] = f"Task paused waiting for input: {context['waiting_input']}"
        reason["details"] = f"The task requires additional input to proceed: {context['waiting_input']}"
        reason["root_cause"] = "Waiting for input"
    
    elif "resource_availability" in context:
        reason["summary"] = f"Task paused due to resource unavailability: {context['resource_availability']}"
        reason["details"] = f"The task is waiting for resource availability: {context['resource_availability']}"
        reason["root_cause"] = "Resource unavailability"
    
    elif "dependency_delay" in context:
        reason["summary"] = f"Task paused waiting for dependency: {context['dependency_delay']}"
        reason["details"] = f"The task is waiting for a dependency to complete: {context['dependency_delay']}"
        reason["root_cause"] = "Dependency delay"
    
    elif "scheduled_pause" in context:
        reason["summary"] = "Task paused as scheduled"
        reason["details"] = f"The task reached a scheduled pause point: {context['scheduled_pause']}"
        reason["root_cause"] = "Scheduled pause"
    
    # Add pause duration if available
    if "estimated_duration" in context:
        reason["estimated_pause_duration"] = context["estimated_duration"]
    
    # Add resume condition if available
    if "resume_condition" in context:
        reason["resume_condition"] = context["resume_condition"]
    
    return reason


def generate_escalation_action_plan(status: str, reason: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Helper function to generate action plan based on status and reason."""
    action_plan = []
    
    if status == "failed":
        # Actions for failed tasks
        action_plan.append({
            "action": "document_failure",
            "description": "Document the failure details for analysis",
            "assignee": "agent"
        })
        
        # Root cause specific actions
        if reason.get("root_cause") == "Error during execution":
            action_plan.append({
                "action": "analyze_error",
                "description": "Analyze the error to determine if it's transient or persistent",
                "assignee": "agent"
            })
            
            action_plan.append({
                "action": "retry_with_modifications",
                "description": "Retry the task with appropriate modifications to address the error",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Execution timeout":
            action_plan.append({
                "action": "optimize_execution",
                "description": "Identify and optimize slow execution paths",
                "assignee": "agent"
            })
            
            action_plan.append({
                "action": "increase_timeout",
                "description": "Consider increasing the timeout limit for this task",
                "assignee": "user"
            })
        
        elif reason.get("root_cause") == "Resource limit exceeded":
            action_plan.append({
                "action": "optimize_resource_usage",
                "description": "Optimize the task to use fewer resources",
                "assignee": "agent"
            })
            
            action_plan.append({
                "action": "increase_resource_limits",
                "description": "Consider increasing resource limits for this task",
                "assignee": "user"
            })
        
        elif reason.get("root_cause") == "Dependency failure":
            action_plan.append({
                "action": "check_dependency_status",
                "description": "Check the status of the failed dependency",
                "assignee": "agent"
            })
            
            action_plan.append({
                "action": "resolve_dependency_issue",
                "description": "Resolve the dependency issue or find an alternative",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Validation failure":
            action_plan.append({
                "action": "review_validation_criteria",
                "description": "Review the validation criteria for correctness",
                "assignee": "agent"
            })
            
            action_plan.append({
                "action": "fix_validation_issues",
                "description": "Address the specific validation issues",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Permission denied":
            action_plan.append({
                "action": "request_permissions",
                "description": "Request the necessary permissions from the user",
                "assignee": "agent"
            })
        
        # General recovery action
        action_plan.append({
            "action": "retry_task",
            "description": "Retry the task after addressing the root cause",
            "assignee": "agent"
        })
    
    elif status == "paused":
        # Actions for paused tasks
        action_plan.append({
            "action": "document_pause",
            "description": "Document the pause reason and current state",
            "assignee": "agent"
        })
        
        # Root cause specific actions
        if reason.get("root_cause") == "User request":
            action_plan.append({
                "action": "await_user_instruction",
                "description": "Wait for further instructions from the user",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Waiting for input":
            action_plan.append({
                "action": "request_input",
                "description": f"Request the required input: {reason.get('details', '')}",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Resource unavailability":
            action_plan.append({
                "action": "monitor_resources",
                "description": "Monitor resource availability and resume when available",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Dependency delay":
            action_plan.append({
                "action": "monitor_dependency",
                "description": "Monitor the dependency status and resume when ready",
                "assignee": "agent"
            })
        
        elif reason.get("root_cause") == "Scheduled pause":
            action_plan.append({
                "action": "resume_at_scheduled_time",
                "description": "Resume the task at the scheduled time",
                "assignee": "agent"
            })
        
        # General resume action
        if "resume_condition" in reason:
            action_plan.append({
                "action": "resume_when_condition_met",
                "description": f"Resume the task when: {reason['resume_condition']}",
                "assignee": "agent"
            })
        else:
            action_plan.append({
                "action": "resume_task",
                "description": "Resume the task when conditions allow",
                "assignee": "agent"
            })
    
    else:
        # Generic actions for other statuses
        action_plan.append({
            "action": "document_status",
            "description": f"Document the current '{status}' status",
            "assignee": "agent"
        })
        
        action_plan.append({
            "action": "determine_next_steps",
            "description": "Determine appropriate next steps based on current status",
            "assignee": "agent"
        })
    
    return action_plan


def generate_user_message(task_id: str, status: str, reason: Dict[str, Any]) -> str:
    """Helper function to generate user message based on task status and reason."""
    if status == "failed":
        message = f"Task {task_id} has failed. "
        message += f"Reason: {reason['summary']}. "
        
        if "action_plan" in reason:
            message += "Recommended actions: "
            for action in reason.get("action_plan", [])[:2]:  # Include first two actions
                message += f"{action['description']}. "
    
    elif status == "paused":
        message = f"Task {task_id} has been paused. "
        message += f"Reason: {reason['summary']}. "
        
        if "estimated_pause_duration" in reason:
            message += f"Estimated pause duration: {reason['estimated_pause_duration']}. "
        
        if "resume_condition" in reason:
            message += f"The task will resume when: {reason['resume_condition']}. "
    
    else:
        message = f"Task {task_id} is now in '{status}' status. "
        message += reason.get("summary", "")
    
    return message


def determine_severity(status: str, reason: Dict[str, Any]) -> str:
    """Helper function to determine severity level based on status and reason."""
    if status == "failed":
        # Determine severity based on root cause
        root_cause = reason.get("root_cause", "").lower()
        
        if "permission" in root_cause or "security" in root_cause:
            return "high"
        elif "timeout" in root_cause or "resource" in root_cause:
            return "medium"
        else:
            return "medium"  # Default for failures
    
    elif status == "paused":
        # Determine severity based on root cause
        root_cause = reason.get("root_cause", "").lower()
        
        if "user request" in root_cause:
            return "low"
        elif "waiting for input" in root_cause:
            return "medium"
        else:
            return "low"  # Default for pauses
    
    else:
        return "low"  # Default for other statuses


# Register all Operations & Security tools
register_tool(
    name="env.secret.check",
    description="Verify that expected environment variables (API keys, tokens) are present",
    category="Operations & Security",
    timeout_seconds=10,
    max_retries=1,
    requires_reflection=False,
    handler=env_secret_check
)

register_tool(
    name="agent.self.check",
    description="Return diagnostic of active toolkit, recent errors, tool failures",
    category="Operations & Security",
    timeout_seconds=15,
    max_retries=1,
    requires_reflection=True,
    handler=agent_self_check
)

register_tool(
    name="guardian.escalate",
    description="Trigger a reflection + warning memory",
    category="Operations & Security",
    timeout_seconds=20,
    max_retries=2,
    requires_reflection=True,
    handler=guardian_escalate
)

register_tool(
    name="tool.timeout.limit",
    description="Return timeout/retry policy config for specific tools",
    category="Operations & Security",
    timeout_seconds=10,
    max_retries=1,
    requires_reflection=False,
    handler=tool_timeout_limit
)

register_tool(
    name="task.finish.check",
    description="Scan current goal for missing checkpoints or agent activity",
    category="Operations & Security",
    timeout_seconds=15,
    max_retries=1,
    requires_reflection=True,
    handler=task_finish_check
)

register_tool(
    name="agent.escalate.reason",
    description="Output a summary of why a task failed or was paused",
    category="Operations & Security",
    timeout_seconds=15,
    max_retries=2,
    requires_reflection=True,
    handler=agent_escalate_reason
)
