"""
CTO Agent

This module implements the CTO Agent that evaluates loop health, tracks trust decay,
detects plan-summary divergence, and generates reports for system integrity monitoring.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

def score_loop_health(
    loop: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> float:
    """
    Scores the health of a loop based on execution metrics.
    
    Args:
        loop (Dict[str, Any]): The loop data including plan, execution logs, and summary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        float: Health score between 0.0 (unhealthy) and 1.0 (perfectly healthy)
    """
    # Use default config if none provided
    if config is None:
        config = {
            "weights": {
                "plan_rerouted": 0.3,
                "required_agents_called": 0.25,
                "critic_skipped": 0.15,
                "completed_without_error": 0.3
            },
            "required_agents": ["core-forge", "critic", "hal"]
        }
    
    # Extract weights from config
    weights = config.get("weights", {})
    required_agents = config.get("required_agents", ["core-forge", "critic", "hal"])
    
    # Initialize score components
    score_components = {
        "plan_rerouted": 1.0,  # Default: plan was not rerouted (good)
        "required_agents_called": 1.0,  # Default: all required agents were called (good)
        "critic_skipped": 1.0,  # Default: critic was not skipped (good)
        "completed_without_error": 1.0  # Default: completed without error (good)
    }
    
    # Check if plan was rerouted
    if loop.get("plan_rerouted", False):
        score_components["plan_rerouted"] = 0.0
    
    # Check if all required agents were called
    called_agents = set(loop.get("called_agents", []))
    required_agent_set = set(required_agents)
    if not required_agent_set.issubset(called_agents):
        # Calculate percentage of required agents that were called
        missing_agents = required_agent_set - called_agents
        score_components["required_agents_called"] = 1.0 - (len(missing_agents) / len(required_agent_set))
    
    # Check if critic was skipped
    if "critic" in required_agents and "critic" not in called_agents:
        score_components["critic_skipped"] = 0.0
    
    # Check if loop completed without error
    if loop.get("error", False) or loop.get("status", "") == "failed":
        score_components["completed_without_error"] = 0.0
    
    # Calculate weighted score
    weighted_score = sum(
        score * weights.get(component, 0.25)
        for component, score in score_components.items()
    )
    
    # Ensure score is between 0.0 and 1.0
    return max(0.0, min(1.0, weighted_score))

def check_plan_summary_divergence(
    plan: Dict[str, Any],
    summary: str,
    config: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculates the divergence between a plan and its execution summary.
    
    Args:
        plan (Dict[str, Any]): The original plan
        summary (str): The execution summary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        float: Divergence score between 0.0 (no divergence) and 1.0 (complete divergence)
    """
    # Use default config if none provided
    if config is None:
        config = {
            "key_terms_weight": 0.6,
            "action_steps_weight": 0.4,
            "min_term_length": 4
        }
    
    # Extract weights from config
    key_terms_weight = config.get("key_terms_weight", 0.6)
    action_steps_weight = config.get("action_steps_weight", 0.4)
    min_term_length = config.get("min_term_length", 4)
    
    # Extract key terms from plan
    plan_terms = _extract_key_terms(plan, min_term_length)
    
    # Extract key terms from summary
    summary_terms = _extract_key_terms_from_text(summary, min_term_length)
    
    # Calculate term overlap
    term_divergence = _calculate_term_divergence(plan_terms, summary_terms)
    
    # Calculate action step divergence
    action_divergence = _calculate_action_divergence(plan, summary)
    
    # Calculate weighted divergence
    weighted_divergence = (
        term_divergence * key_terms_weight +
        action_divergence * action_steps_weight
    )
    
    # Ensure divergence is between 0.0 and 1.0
    return max(0.0, min(1.0, weighted_divergence))

def _extract_key_terms(plan: Dict[str, Any], min_length: int = 4) -> Set[str]:
    """
    Extracts key terms from a plan.
    
    Args:
        plan (Dict[str, Any]): The plan
        min_length (int): Minimum length of terms to include
        
    Returns:
        Set[str]: Set of key terms
    """
    terms = set()
    
    # Extract from objective
    if "objective" in plan:
        terms.update(_extract_key_terms_from_text(plan["objective"], min_length))
    
    # Extract from steps
    if "steps" in plan and isinstance(plan["steps"], list):
        for step in plan["steps"]:
            if isinstance(step, dict) and "description" in step:
                terms.update(_extract_key_terms_from_text(step["description"], min_length))
            elif isinstance(step, str):
                terms.update(_extract_key_terms_from_text(step, min_length))
    
    # Extract from other text fields
    for key, value in plan.items():
        if isinstance(value, str) and key not in ["objective"]:
            terms.update(_extract_key_terms_from_text(value, min_length))
    
    return terms

def _extract_key_terms_from_text(text: str, min_length: int = 4) -> Set[str]:
    """
    Extracts key terms from text.
    
    Args:
        text (str): The text to extract terms from
        min_length (int): Minimum length of terms to include
        
    Returns:
        Set[str]: Set of key terms
    """
    # Common stop words to exclude
    stop_words = {
        "the", "and", "for", "with", "this", "that", "from", "will", "have",
        "been", "has", "are", "were", "was", "they", "their", "them", "these",
        "those", "then", "than", "when", "what", "which", "who", "whom", "whose",
        "how", "why", "where", "there", "here", "some", "any", "all", "none",
        "many", "much", "more", "most", "other", "another", "such", "only",
        "very", "just", "but", "not", "into", "about", "upon", "over", "under",
        "above", "below", "between", "among", "through", "during", "before",
        "after", "since", "until", "while", "because", "although", "though",
        "even", "also", "too", "either", "neither", "both", "each", "every",
        "whether", "however", "therefore", "thus", "hence", "accordingly",
        "consequently", "otherwise", "instead", "meanwhile", "nonetheless",
        "nevertheless", "regardless", "notwithstanding"
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter out stop words and short words
    return {word for word in words if word not in stop_words and len(word) >= min_length}

def _calculate_term_divergence(plan_terms: Set[str], summary_terms: Set[str]) -> float:
    """
    Calculates term divergence between plan and summary.
    
    Args:
        plan_terms (Set[str]): Terms from the plan
        summary_terms (Set[str]): Terms from the summary
        
    Returns:
        float: Term divergence score between 0.0 and 1.0
    """
    if not plan_terms:
        return 0.0
    
    # Calculate overlap
    overlap = plan_terms.intersection(summary_terms)
    
    # Calculate percentage of plan terms that appear in summary
    # This is more important than Jaccard similarity for our use case
    plan_coverage = len(overlap) / len(plan_terms) if plan_terms else 0.0
    
    # Calculate Jaccard distance (1 - Jaccard similarity)
    union = plan_terms.union(summary_terms)
    if not union:
        return 0.0
    
    jaccard_similarity = len(overlap) / len(union)
    jaccard_distance = 1.0 - jaccard_similarity
    
    # Weight plan coverage more heavily than Jaccard distance
    # A high plan coverage (most plan terms appear in summary) should result in low divergence
    weighted_divergence = (jaccard_distance * 0.3) + ((1.0 - plan_coverage) * 0.7)
    
    return weighted_divergence

def _calculate_action_divergence(plan: Dict[str, Any], summary: str) -> float:
    """
    Calculates action step divergence between plan and summary.
    
    Args:
        plan (Dict[str, Any]): The plan
        summary (str): The execution summary
        
    Returns:
        float: Action divergence score between 0.0 and 1.0
    """
    # Extract action verbs from plan steps
    plan_actions = set()
    if "steps" in plan and isinstance(plan["steps"], list):
        for step in plan["steps"]:
            if isinstance(step, dict) and "description" in step:
                # Extract first word of each step as potential action verb
                match = re.search(r'^\s*([a-zA-Z]+)', step["description"])
                if match:
                    plan_actions.add(match.group(1).lower())
            elif isinstance(step, str):
                match = re.search(r'^\s*([a-zA-Z]+)', step)
                if match:
                    plan_actions.add(match.group(1).lower())
    
    # Extract potential action verbs from summary
    summary_actions = set()
    sentences = re.split(r'[.!?]', summary)
    for sentence in sentences:
        match = re.search(r'^\s*([a-zA-Z]+)', sentence)
        if match:
            summary_actions.add(match.group(1).lower())
    
    # Calculate action verb overlap
    if not plan_actions:
        return 0.0
    
    overlap = plan_actions.intersection(summary_actions)
    action_similarity = len(overlap) / len(plan_actions)
    action_divergence = 1.0 - action_similarity
    
    return action_divergence

def track_trust_decay(
    agent_logs: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Tracks agent failure rates and trust score drops over time.
    
    Args:
        agent_logs (List[Dict[str, Any]]): List of agent execution logs
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Trust decay metrics including agent failure rates and average loop trust decay
    """
    # Use default config if none provided
    if config is None:
        config = {
            "window_size": 10,
            "trust_threshold": 0.7
        }
    
    # Extract config values
    window_size = config.get("window_size", 10)
    trust_threshold = config.get("trust_threshold", 0.7)
    
    # Initialize result
    result = {
        "agent_failure_rate": {},
        "avg_loop_trust_decay": 0.0
    }
    
    # Group logs by agent
    agent_logs_by_name = {}
    for log in agent_logs:
        agent_name = log.get("agent_name", "unknown")
        if agent_name not in agent_logs_by_name:
            agent_logs_by_name[agent_name] = []
        agent_logs_by_name[agent_name].append(log)
    
    # Calculate failure rates for each agent
    for agent_name, logs in agent_logs_by_name.items():
        # Use only the most recent logs up to window_size
        recent_logs = logs[-window_size:] if len(logs) > window_size else logs
        
        # Count failures
        failure_count = sum(1 for log in recent_logs if log.get("status", "") == "failed")
        
        # Calculate failure rate
        failure_rate = failure_count / len(recent_logs) if recent_logs else 0.0
        
        # Add to result
        result["agent_failure_rate"][agent_name] = round(failure_rate, 2)
    
    # Calculate average loop trust decay
    trust_scores = [
        log.get("trust_score", 1.0) for log in agent_logs 
        if "trust_score" in log and log.get("agent_name", "") == "system"
    ]
    
    if len(trust_scores) >= 2:
        # Use only the most recent scores up to window_size
        recent_scores = trust_scores[-window_size:] if len(trust_scores) > window_size else trust_scores
        
        # Calculate average decay
        decays = []
        for i in range(1, len(recent_scores)):
            if recent_scores[i] < recent_scores[i-1]:
                decays.append(recent_scores[i-1] - recent_scores[i])
        
        avg_decay = sum(decays) / len(decays) if decays else 0.0
        result["avg_loop_trust_decay"] = round(avg_decay, 2)
    
    return result

def generate_cto_report(
    loop_id: str,
    loop: Dict[str, Any],
    plan: Dict[str, Any],
    summary: str,
    agent_logs: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a CTO report for a loop.
    
    Args:
        loop_id (str): The loop identifier
        loop (Dict[str, Any]): The loop data
        plan (Dict[str, Any]): The original plan
        summary (str): The execution summary
        agent_logs (List[Dict[str, Any]]): List of agent execution logs
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: CTO report with health metrics and recommendations
    """
    # Use default config if none provided
    if config is None:
        config = {
            "health_threshold": 0.6,
            "divergence_threshold": 0.4,
            "trust_decay_threshold": 0.1
        }
    
    # Calculate health score
    health_score = score_loop_health(loop)
    
    # Calculate plan-summary alignment
    divergence_score = check_plan_summary_divergence(plan, summary)
    alignment_score = 1.0 - divergence_score
    
    # Track trust decay
    trust_metrics = track_trust_decay(agent_logs)
    trust_decay = trust_metrics.get("avg_loop_trust_decay", 0.0)
    
    # Generate recommendation
    recommendation = _generate_recommendation(
        health_score, 
        alignment_score, 
        trust_decay, 
        trust_metrics.get("agent_failure_rate", {}),
        config
    )
    
    # Create report
    report = {
        "loop_id": loop_id,
        "health_score": round(health_score, 2),
        "plan_summary_alignment_score": round(alignment_score, 2),
        "trust_decay": trust_decay,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add agent failure rates if any
    if trust_metrics.get("agent_failure_rate"):
        report["agent_failure_rates"] = trust_metrics["agent_failure_rate"]
    
    return report

def _generate_recommendation(
    health_score: float,
    alignment_score: float,
    trust_decay: float,
    agent_failure_rates: Dict[str, float],
    config: Dict[str, Any]
) -> str:
    """
    Generates a recommendation based on health metrics.
    
    Args:
        health_score (float): The loop health score
        alignment_score (float): The plan-summary alignment score
        trust_decay (float): The trust decay value
        agent_failure_rates (Dict[str, float]): Agent failure rates
        config (Dict[str, Any]): Configuration options
        
    Returns:
        str: Recommendation for improving system health
    """
    # Extract thresholds from config
    health_threshold = config.get("health_threshold", 0.6)
    divergence_threshold = config.get("divergence_threshold", 0.4)
    trust_decay_threshold = config.get("trust_decay_threshold", 0.1)
    
    # Initialize recommendation
    recommendations = []
    
    # Check health score
    if health_score < health_threshold:
        if "critic" in agent_failure_rates and agent_failure_rates["critic"] > 0:
            recommendations.append("Enable CRITIC by default next loop")
        else:
            recommendations.append("Review loop execution process")
    
    # Check alignment score
    if alignment_score < (1.0 - divergence_threshold):
        recommendations.append("Improve plan-summary alignment")
    
    # Check trust decay
    if trust_decay > trust_decay_threshold:
        recommendations.append("Address trust decay issues")
    
    # Check agent failure rates
    failing_agents = [
        agent for agent, rate in agent_failure_rates.items()
        if rate > 0.2  # Agents failing more than 20% of the time
    ]
    
    if failing_agents:
        agent_list = ", ".join(failing_agents)
        recommendations.append(f"Investigate failures in {agent_list}")
    
    # Combine recommendations
    if recommendations:
        return "; ".join(recommendations)
    else:
        return "No specific recommendations; system operating within normal parameters"

def analyze_loop_with_cto_agent(
    loop_id: str,
    loop: Dict[str, Any],
    plan: Dict[str, Any],
    summary: str,
    agent_logs: List[Dict[str, Any]],
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes a loop using the CTO Agent.
    
    Args:
        loop_id (str): The loop identifier
        loop (Dict[str, Any]): The loop data
        plan (Dict[str, Any]): The original plan
        summary (str): The execution summary
        agent_logs (List[Dict[str, Any]]): List of agent execution logs
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Updated memory with CTO reports and warnings
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "health_threshold": 0.6,
            "divergence_threshold": 0.4,
            "trust_decay_threshold": 0.1,
            "warning_threshold": 0.4
        }
    
    # Skip analysis if disabled
    if not config.get("enabled", True):
        return memory
    
    # Make a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Calculate health score
    health_score = score_loop_health(loop)
    
    # Add health score to loop data
    loop["loop_health_score"] = round(health_score, 2)
    
    # Update loop in memory
    if "loops" in updated_memory:
        for i, mem_loop in enumerate(updated_memory["loops"]):
            if mem_loop.get("loop_id") == loop_id:
                updated_memory["loops"][i] = {**mem_loop, **loop}
                break
    
    # Generate CTO report
    report = generate_cto_report(loop_id, loop, plan, summary, agent_logs, config)
    
    # Store report in memory
    if "cto_reports" not in updated_memory:
        updated_memory["cto_reports"] = []
    
    updated_memory["cto_reports"].append(report)
    
    # Check if warning should be generated
    warning_threshold = config.get("warning_threshold", 0.4)
    
    if (health_score < warning_threshold or 
            report["plan_summary_alignment_score"] < warning_threshold or
            report["trust_decay"] > config.get("trust_decay_threshold", 0.1)):
        
        # Generate warning
        warning = {
            "type": "cto_warning",
            "loop_id": loop_id,
            "health_score": report["health_score"],
            "message": f"Critical system health issue detected: {report['recommendation']}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Store warning in memory
        if "cto_warnings" not in updated_memory:
            updated_memory["cto_warnings"] = []
        
        updated_memory["cto_warnings"].append(warning)
    
    return updated_memory
