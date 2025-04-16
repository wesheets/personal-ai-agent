"""
Belief Calibrator Tool for the Personal AI Agent System.

This module provides functionality to evaluate and calibrate confidence
in beliefs, facts, and predictions to improve accuracy.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("belief_calibrator")

def run(
    statements: Union[str, List[str]],
    domain: str = None,
    confidence_threshold: float = 0.7,
    require_evidence: bool = True,
    check_recency: bool = True,
    check_consistency: bool = True,
    check_source_quality: bool = True,
    include_alternatives: bool = True,
    include_confidence_intervals: bool = False,
    include_reasoning: bool = True,
    format_output: str = "detailed",
    store_memory: bool = True,
    memory_manager = None,
    memory_tags: List[str] = ["belief_calibration", "meta"],
    memory_scope: str = "global"
) -> Dict[str, Any]:
    """
    Evaluate and calibrate confidence in statements, facts, or predictions.
    
    Args:
        statements: Statement(s) to evaluate (string or list of strings)
        domain: Knowledge domain for context (e.g., science, history, finance)
        confidence_threshold: Threshold for high confidence classification
        require_evidence: Whether to require evidence for high confidence
        check_recency: Whether to check if information is recent/outdated
        check_consistency: Whether to check for internal consistency
        check_source_quality: Whether to evaluate source quality
        include_alternatives: Whether to include alternative viewpoints
        include_confidence_intervals: Whether to include confidence intervals
        include_reasoning: Whether to include reasoning for evaluations
        format_output: Output format (simple, detailed, or technical)
        store_memory: Whether to store calibration results in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing calibration results and metadata
    """
    logger.info(f"Calibrating beliefs in domain: {domain or 'general'}")
    
    try:
        # Convert single statement to list for consistent processing
        if isinstance(statements, str):
            statements = [statements]
        
        # Validate inputs
        if not statements:
            raise ValueError("At least one statement is required")
        
        # Process each statement
        calibration_results = []
        for statement in statements:
            result = _calibrate_statement(
                statement,
                domain,
                confidence_threshold,
                require_evidence,
                check_recency,
                check_consistency,
                check_source_quality,
                include_alternatives,
                include_confidence_intervals,
                include_reasoning
            )
            calibration_results.append(result)
        
        # Generate summary statistics
        summary = _generate_calibration_summary(calibration_results)
        
        # Format output
        formatted_output = _format_calibration_output(
            calibration_results,
            summary,
            format_output,
            include_reasoning,
            include_alternatives,
            include_confidence_intervals
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the calibration results
                memory_entry = {
                    "type": "belief_calibration",
                    "domain": domain or "general",
                    "statements_count": len(statements),
                    "high_confidence_count": summary["high_confidence_count"],
                    "low_confidence_count": summary["low_confidence_count"],
                    "uncertain_count": summary["uncertain_count"],
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ([domain] if domain else [])
                )
                
                # Also store individual high-confidence calibrations
                for result in calibration_results:
                    if result["confidence_level"] >= confidence_threshold:
                        memory_manager.add_memory(
                            content=json.dumps({
                                "type": "calibrated_belief",
                                "statement": result["statement"],
                                "confidence": result["confidence_level"],
                                "evidence": result.get("evidence", []),
                                "timestamp": datetime.now().isoformat()
                            }),
                            scope=memory_scope,
                            tags=memory_tags + ["high_confidence", domain] if domain else ["high_confidence"]
                        )
                
                logger.info(f"Stored calibration results in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store calibration results in memory: {str(e)}")
        
        # Prepare response
        response = {
            "success": True,
            "calibration_results": calibration_results,
            "summary": summary,
            "formatted_output": formatted_output
        }
        
        return response
    except Exception as e:
        error_msg = f"Error in belief calibration: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "statements": statements
        }

def _calibrate_statement(
    statement: str,
    domain: str,
    confidence_threshold: float,
    require_evidence: bool,
    check_recency: bool,
    check_consistency: bool,
    check_source_quality: bool,
    include_alternatives: bool,
    include_confidence_intervals: bool,
    include_reasoning: bool
) -> Dict[str, Any]:
    """
    Calibrate a single statement.
    
    Args:
        statement: Statement to evaluate
        domain: Knowledge domain for context
        confidence_threshold: Threshold for high confidence classification
        require_evidence: Whether to require evidence for high confidence
        check_recency: Whether to check if information is recent/outdated
        check_consistency: Whether to check for internal consistency
        check_source_quality: Whether to evaluate source quality
        include_alternatives: Whether to include alternative viewpoints
        include_confidence_intervals: Whether to include confidence intervals
        include_reasoning: Whether to include reasoning for evaluations
        
    Returns:
        Calibration result for the statement
    """
    # In a real implementation, this would use LLM to evaluate the statement
    # For this example, we'll use a simulated approach
    
    # Simulate evaluation process
    time.sleep(0.5)  # Simulate processing time
    
    # Parse statement to extract key components
    statement_type = _determine_statement_type(statement)
    
    # Simulate confidence level calculation
    confidence_level = _simulate_confidence_calculation(statement, domain)
    
    # Determine confidence category
    if confidence_level >= confidence_threshold:
        confidence_category = "high"
    elif confidence_level >= 0.4:
        confidence_category = "moderate"
    else:
        confidence_category = "low"
    
    # Simulate evidence collection
    evidence = []
    if require_evidence or confidence_level >= 0.5:
        evidence = _simulate_evidence_collection(statement, domain, 3)
    
    # Simulate recency check
    recency_issues = None
    if check_recency:
        recency_issues = _simulate_recency_check(statement, domain)
    
    # Simulate consistency check
    consistency_issues = None
    if check_consistency:
        consistency_issues = _simulate_consistency_check(statement)
    
    # Simulate source quality evaluation
    source_quality = None
    if check_source_quality and evidence:
        source_quality = _simulate_source_quality_evaluation(evidence)
    
    # Simulate alternative viewpoints
    alternatives = None
    if include_alternatives and confidence_level < 0.9:
        alternatives = _simulate_alternative_viewpoints(statement, domain)
    
    # Simulate confidence intervals
    confidence_interval = None
    if include_confidence_intervals and statement_type in ["prediction", "estimation"]:
        confidence_interval = _simulate_confidence_interval(confidence_level)
    
    # Simulate reasoning
    reasoning = None
    if include_reasoning:
        reasoning = _simulate_reasoning(
            statement,
            confidence_level,
            evidence,
            recency_issues,
            consistency_issues,
            source_quality
        )
    
    # Prepare result
    result = {
        "statement": statement,
        "statement_type": statement_type,
        "confidence_level": confidence_level,
        "confidence_category": confidence_category,
        "calibrated": True
    }
    
    if evidence:
        result["evidence"] = evidence
    
    if recency_issues:
        result["recency_issues"] = recency_issues
    
    if consistency_issues:
        result["consistency_issues"] = consistency_issues
    
    if source_quality:
        result["source_quality"] = source_quality
    
    if alternatives:
        result["alternatives"] = alternatives
    
    if confidence_interval:
        result["confidence_interval"] = confidence_interval
    
    if reasoning:
        result["reasoning"] = reasoning
    
    return result

def _determine_statement_type(statement: str) -> str:
    """
    Determine the type of statement.
    
    Args:
        statement: Statement to evaluate
        
    Returns:
        Statement type
    """
    # In a real implementation, this would use NLP to classify the statement
    # For this example, we'll use simple keyword matching
    
    statement_lower = statement.lower()
    
    if any(word in statement_lower for word in ["will", "going to", "future", "expect", "predict", "forecast"]):
        return "prediction"
    elif any(word in statement_lower for word in ["approximately", "about", "around", "estimate", "roughly"]):
        return "estimation"
    elif any(word in statement_lower for word in ["always", "never", "every", "all", "none"]):
        return "universal"
    elif any(word in statement_lower for word in ["should", "must", "ought", "best"]):
        return "normative"
    elif any(word in statement_lower for word in ["because", "cause", "effect", "result", "lead to"]):
        return "causal"
    else:
        return "factual"

def _simulate_confidence_calculation(statement: str, domain: str) -> float:
    """
    Simulate confidence level calculation.
    
    Args:
        statement: Statement to evaluate
        domain: Knowledge domain
        
    Returns:
        Simulated confidence level (0-1)
    """
    # In a real implementation, this would use LLM to calculate confidence
    # For this example, we'll use a simple heuristic
    
    # Base confidence
    confidence = 0.7
    
    # Adjust based on statement characteristics
    statement_lower = statement.lower()
    
    # Statements with hedging language get lower confidence
    if any(word in statement_lower for word in ["maybe", "perhaps", "possibly", "might", "could", "uncertain"]):
        confidence -= 0.2
    
    # Statements with strong language get higher confidence
    if any(word in statement_lower for word in ["definitely", "certainly", "absolutely", "undoubtedly"]):
        confidence += 0.15
    
    # Universal statements get lower confidence
    if any(word in statement_lower for word in ["always", "never", "every", "all", "none"]):
        confidence -= 0.25
    
    # Specific statements get higher confidence
    if any(word in statement_lower for word in ["specifically", "precisely", "exactly", "particularly"]):
        confidence += 0.1
    
    # Add some randomness
    import random
    confidence += random.uniform(-0.1, 0.1)
    
    # Ensure confidence is within bounds
    confidence = max(0.1, min(0.95, confidence))
    
    return round(confidence, 2)

def _simulate_evidence_collection(statement: str, domain: str, count: int) -> List[Dict[str, Any]]:
    """
    Simulate evidence collection for a statement.
    
    Args:
        statement: Statement to find evidence for
        domain: Knowledge domain
        count: Number of evidence items to generate
        
    Returns:
        List of evidence items
    """
    # In a real implementation, this would search for actual evidence
    # For this example, we'll generate simulated evidence
    
    evidence = []
    
    for i in range(count):
        evidence_type = ["research_paper", "expert_opinion", "statistical_data", "historical_record"][i % 4]
        
        evidence_item = {
            "type": evidence_type,
            "summary": f"Simulated evidence {i+1} supporting or relating to the statement",
            "relevance": round(0.5 + (0.4 * (count - i) / count), 2)  # Higher relevance for earlier items
        }
        
        if evidence_type == "research_paper":
            evidence_item["source"] = {
                "title": f"Research on {domain or 'general knowledge'} topic {i+1}",
                "authors": ["Researcher A", "Researcher B"],
                "year": 2020 + (i % 3),
                "journal": "Journal of Simulated Evidence"
            }
        elif evidence_type == "expert_opinion":
            evidence_item["source"] = {
                "expert": f"Dr. Expert {i+1}",
                "credentials": f"Professor of {domain or 'General Studies'}",
                "institution": "University of Simulation"
            }
        elif evidence_type == "statistical_data":
            evidence_item["source"] = {
                "dataset": f"{domain or 'General'} Statistics {2020 + (i % 3)}",
                "sample_size": 1000 * (i + 1),
                "methodology": "Simulated random sampling"
            }
        else:
            evidence_item["source"] = {
                "record": f"Historical document {i+1}",
                "year": 2000 + (i * 5),
                "archive": "Simulated Archives"
            }
        
        evidence.append(evidence_item)
    
    return evidence

def _simulate_recency_check(statement: str, domain: str) -> Optional[Dict[str, Any]]:
    """
    Simulate checking if information is recent or outdated.
    
    Args:
        statement: Statement to check
        domain: Knowledge domain
        
    Returns:
        Recency issues if any, None otherwise
    """
    # In a real implementation, this would check actual recency
    # For this example, we'll randomly determine if there are recency issues
    
    import random
    
    if random.random() < 0.3:  # 30% chance of recency issues
        return {
            "is_outdated": True,
            "last_valid": f"{2018 + random.randint(0, 3)}",
            "reason": "Simulated recency issue: newer data contradicts this statement",
            "update": "The current understanding is slightly different from this statement"
        }
    
    return None

def _simulate_consistency_check(statement: str) -> Optional[Dict[str, Any]]:
    """
    Simulate checking for internal consistency issues.
    
    Args:
        statement: Statement to check
        
    Returns:
        Consistency issues if any, None otherwise
    """
    # In a real implementation, this would check actual consistency
    # For this example, we'll randomly determine if there are consistency issues
    
    import random
    
    if random.random() < 0.2:  # 20% chance of consistency issues
        return {
            "has_inconsistency": True,
            "type": random.choice(["logical_contradiction", "term_ambiguity", "unstated_assumption"]),
            "description": "Simulated consistency issue in the statement",
            "suggestion": "Consider clarifying or reformulating the statement"
        }
    
    return None

def _simulate_source_quality_evaluation(evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulate evaluating the quality of evidence sources.
    
    Args:
        evidence: List of evidence items
        
    Returns:
        Source quality evaluation
    """
    # In a real implementation, this would evaluate actual sources
    # For this example, we'll generate a simulated evaluation
    
    # Calculate average source quality
    import random
    
    quality_scores = []
    for item in evidence:
        # Base score
        score = 0.6 + random.uniform(0, 0.3)
        
        # Adjust based on evidence type
        if item["type"] == "research_paper":
            # Adjust based on recency and journal
            year = item["source"].get("year", 2020)
            score += min(0.1, (year - 2020) * 0.02)  # More recent is better
        elif item["type"] == "expert_opinion":
            # Expert opinions get a slight penalty for subjectivity
            score -= 0.05
        elif item["type"] == "statistical_data":
            # Adjust based on sample size
            sample_size = item["source"].get("sample_size", 1000)
            score += min(0.1, (sample_size / 10000) * 0.1)  # Larger sample is better
        
        # Ensure score is within bounds
        score = max(0.3, min(0.95, score))
        quality_scores.append(score)
    
    # Calculate average and highest quality
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
    max_quality = max(quality_scores) if quality_scores else 0.5
    
    # Determine diversity of sources
    source_types = set(item["type"] for item in evidence)
    diversity_score = len(source_types) / 4  # Normalize by number of possible types
    
    return {
        "average_quality": round(avg_quality, 2),
        "highest_quality": round(max_quality, 2),
        "diversity_score": round(diversity_score, 2),
        "evaluation": _get_quality_evaluation(avg_quality)
    }

def _get_quality_evaluation(quality_score: float) -> str:
    """
    Get a textual evaluation based on quality score.
    
    Args:
        quality_score: Quality score (0-1)
        
    Returns:
        Textual evaluation
    """
    if quality_score >= 0.8:
        return "High-quality sources with strong reliability"
    elif quality_score >= 0.6:
        return "Good-quality sources with reasonable reliability"
    elif quality_score >= 0.4:
        return "Moderate-quality sources with some limitations"
    else:
        return "Lower-quality sources with significant limitations"

def _simulate_alternative_viewpoints(statement: str, domain: str) -> List[Dict[str, Any]]:
    """
    Simulate generating alternative viewpoints.
    
    Args:
        statement: Statement to generate alternatives for
        domain: Knowledge domain
        
    Returns:
        List of alternative viewpoints
    """
    # In a real implementation, this would generate actual alternatives
    # For this example, we'll generate simulated alternatives
    
    import random
    num_alternatives = random.randint(1, 2)
    
    alternatives = []
    for i in range(num_alternatives):
        confidence = round(0.3 + random.uniform(0, 0.4), 2)  # Lower confidence than main statement
        
        alternative = {
            "statement": f"Alternative viewpoint {i+1} to the original statement",
            "confidence": confidence,
            "rationale": f"Simulated rationale for alternative viewpoint {i+1}"
        }
        
        alternatives.append(alternative)
    
    return alternatives

def _simulate_confidence_interval(confidence_level: float) -> Dict[str, Any]:
    """
    Simulate generating a confidence interval.
    
    Args:
        confidence_level: Confidence level for the statement
        
    Returns:
        Confidence interval
    """
    # In a real implementation, this would calculate actual intervals
    # For this example, we'll generate a simulated interval
    
    # Width of interval is inversely related to confidence
    width = (1 - confidence_level) * 0.6
    
    lower_bound = max(0, confidence_level - width)
    upper_bound = min(1, confidence_level + width)
    
    return {
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "interpretation": f"There is a 90% chance that the true confidence level is between {lower_bound:.2f} and {upper_bound:.2f}"
    }

def _simulate_reasoning(
    statement: str,
    confidence_level: float,
    evidence: List[Dict[str, Any]],
    recency_issues: Optional[Dict[str, Any]],
    consistency_issues: Optional[Dict[str, Any]],
    source_quality: Optional[Dict[str, Any]]
) -> str:
    """
    Simulate generating reasoning for the evaluation.
    
    Args:
        statement: Statement being evaluated
        confidence_level: Calculated confidence level
        evidence: Collected evidence
        recency_issues: Identified recency issues
        consistency_issues: Identified consistency issues
        source_quality: Source quality evaluation
        
    Returns:
        Reasoning text
    """
    # In a real implementation, this would generate actual reasoning
    # For this example, we'll generate simulated reasoning
    
    reasoning = f"The statement was evaluated with a confidence level of {confidence_level:.2f}. "
    
    if evidence:
        reasoning += f"This assessment is based on {len(evidence)} pieces of evidence. "
        
        if source_quality:
            reasoning += f"The sources are of {source_quality['evaluation'].lower()}. "
    else:
        reasoning += "No specific evidence was found to support this statement. "
    
    if recency_issues:
        reasoning += "There are concerns about the recency of this information. "
        reasoning += recency_issues.get("reason", "") + " "
    
    if consistency_issues:
        reasoning += "There are internal consistency issues with this statement. "
        reasoning += consistency_issues.get("description", "") + " "
    
    if confidence_level >= 0.8:
        reasoning += "Overall, this statement appears to be highly reliable based on available information."
    elif confidence_level >= 0.6:
        reasoning += "Overall, this statement appears to be generally reliable, though with some limitations."
    elif confidence_level >= 0.4:
        reasoning += "Overall, this statement has moderate reliability and should be considered with caution."
    else:
        reasoning += "Overall, this statement has low reliability based on available information."
    
    return reasoning

def _generate_calibration_summary(calibration_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for calibration results.
    
    Args:
        calibration_results: List of calibration results
        
    Returns:
        Summary statistics
    """
    # Count by confidence category
    high_confidence = sum(1 for r in calibration_results if r["confidence_category"] == "high")
    moderate_confidence = sum(1 for r in calibration_results if r["confidence_category"] == "moderate")
    low_confidence = sum(1 for r in calibration_results if r["confidence_category"] == "low")
    
    # Count by statement type
    statement_types = {}
    for r in calibration_results:
        statement_type = r["statement_type"]
        statement_types[statement_type] = statement_types.get(statement_type, 0) + 1
    
    # Count issues
    recency_issues = sum(1 for r in calibration_results if "recency_issues" in r)
    consistency_issues = sum(1 for r in calibration_results if "consistency_issues" in r)
    
    # Calculate average confidence
    avg_confidence = sum(r["confidence_level"] for r in calibration_results) / len(calibration_results)
    
    return {
        "total_statements": len(calibration_results),
        "high_confidence_count": high_confidence,
        "moderate_confidence_count": moderate_confidence,
        "low_confidence_count": low_confidence,
        "uncertain_count": moderate_confidence + low_confidence,
        "statement_types": statement_types,
        "recency_issues_count": recency_issues,
        "consistency_issues_count": consistency_issues,
        "average_confidence": round(avg_confidence, 2)
    }

def _format_calibration_output(
    calibration_results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    format_output: str,
    include_reasoning: bool,
    include_alternatives: bool,
    include_confidence_intervals: bool
) -> str:
    """
    Format the calibration output in the specified format.
    
    Args:
        calibration_results: List of calibration results
        summary: Summary statistics
        format_output: Output format (simple, detailed, or technical)
        include_reasoning: Whether reasoning is included
        include_alternatives: Whether alternatives are included
        include_confidence_intervals: Whether confidence intervals are included
        
    Returns:
        Formatted calibration output
    """
    if format_output == "simple":
        return _format_simple_output(calibration_results, summary)
    elif format_output == "technical":
        return _format_technical_output(
            calibration_results,
            summary,
            include_reasoning,
            include_alternatives,
            include_confidence_intervals
        )
    else:  # detailed
        return _format_detailed_output(
            calibration_results,
            summary,
            include_reasoning,
            include_alternatives,
            include_confidence_intervals
        )

def _format_simple_output(
    calibration_results: List[Dict[str, Any]],
    summary: Dict[str, Any]
) -> str:
    """
    Format calibration results in simple format.
    
    Args:
        calibration_results: List of calibration results
        summary: Summary statistics
        
    Returns:
        Simple formatted output
    """
    output = f"BELIEF CALIBRATION SUMMARY\n\n"
    output += f"Evaluated {summary['total_statements']} statement(s) with an average confidence of {summary['average_confidence']:.2f}.\n\n"
    
    output += "RESULTS:\n\n"
    for i, result in enumerate(calibration_results, 1):
        output += f"{i}. \"{result['statement']}\"\n"
        output += f"   Confidence: {result['confidence_level']:.2f} ({result['confidence_category'].upper()})\n"
        
        if "recency_issues" in result:
            output += f"   Note: Information may be outdated.\n"
        
        if "consistency_issues" in result:
            output += f"   Note: Statement has internal consistency issues.\n"
        
        output += "\n"
    
    return output

def _format_detailed_output(
    calibration_results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    include_reasoning: bool,
    include_alternatives: bool,
    include_confidence_intervals: bool
) -> str:
    """
    Format calibration results in detailed format.
    
    Args:
        calibration_results: List of calibration results
        summary: Summary statistics
        include_reasoning: Whether reasoning is included
        include_alternatives: Whether alternatives are included
        include_confidence_intervals: Whether confidence intervals are included
        
    Returns:
        Detailed formatted output
    """
    output = f"BELIEF CALIBRATION DETAILED REPORT\n\n"
    
    # Summary section
    output += "SUMMARY:\n"
    output += f"- Evaluated {summary['total_statements']} statement(s)\n"
    output += f"- Average confidence: {summary['average_confidence']:.2f}\n"
    output += f"- High confidence statements: {summary['high_confidence_count']} ({summary['high_confidence_count']/summary['total_statements']*100:.1f}%)\n"
    output += f"- Moderate confidence statements: {summary['moderate_confidence_count']} ({summary['moderate_confidence_count']/summary['total_statements']*100:.1f}%)\n"
    output += f"- Low confidence statements: {summary['low_confidence_count']} ({summary['low_confidence_count']/summary['total_statements']*100:.1f}%)\n"
    
    if summary['recency_issues_count'] > 0:
        output += f"- Statements with recency issues: {summary['recency_issues_count']}\n"
    
    if summary['consistency_issues_count'] > 0:
        output += f"- Statements with consistency issues: {summary['consistency_issues_count']}\n"
    
    output += "\nDETAILED RESULTS:\n\n"
    
    # Individual results
    for i, result in enumerate(calibration_results, 1):
        output += f"STATEMENT {i}: \"{result['statement']}\"\n"
        output += f"Type: {result['statement_type'].capitalize()}\n"
        output += f"Confidence: {result['confidence_level']:.2f} ({result['confidence_category'].upper()})\n"
        
        if include_confidence_intervals and "confidence_interval" in result:
            ci = result["confidence_interval"]
            output += f"Confidence Interval: {ci['lower_bound']:.2f} to {ci['upper_bound']:.2f}\n"
        
        if "evidence" in result:
            output += f"\nEvidence ({len(result['evidence'])} sources):\n"
            for j, evidence in enumerate(result["evidence"], 1):
                output += f"- Evidence {j}: {evidence['summary']} (Relevance: {evidence['relevance']:.2f})\n"
                if "source" in evidence:
                    source = evidence["source"]
                    if "title" in source:
                        output += f"  Source: {source['title']}"
                        if "year" in source:
                            output += f" ({source['year']})"
                        output += "\n"
                    elif "expert" in source:
                        output += f"  Source: {source['expert']}, {source['credentials']}\n"
                    elif "dataset" in source:
                        output += f"  Source: {source['dataset']} (n={source['sample_size']})\n"
                    elif "record" in source:
                        output += f"  Source: {source['record']} ({source['year']})\n"
        
        if "source_quality" in result:
            sq = result["source_quality"]
            output += f"\nSource Quality: {sq['evaluation']}\n"
            output += f"- Average quality score: {sq['average_quality']:.2f}\n"
            output += f"- Source diversity: {sq['diversity_score']:.2f}\n"
        
        if "recency_issues" in result:
            ri = result["recency_issues"]
            output += f"\nRecency Issues:\n"
            output += f"- {ri['reason']}\n"
            if "update" in ri:
                output += f"- Update: {ri['update']}\n"
        
        if "consistency_issues" in result:
            ci = result["consistency_issues"]
            output += f"\nConsistency Issues:\n"
            output += f"- Type: {ci['type'].replace('_', ' ').capitalize()}\n"
            output += f"- Description: {ci['description']}\n"
            if "suggestion" in ci:
                output += f"- Suggestion: {ci['suggestion']}\n"
        
        if include_alternatives and "alternatives" in result:
            output += f"\nAlternative Viewpoints:\n"
            for j, alt in enumerate(result["alternatives"], 1):
                output += f"- Alternative {j}: \"{alt['statement']}\"\n"
                output += f"  Confidence: {alt['confidence']:.2f}\n"
                if "rationale" in alt:
                    output += f"  Rationale: {alt['rationale']}\n"
        
        if include_reasoning and "reasoning" in result:
            output += f"\nReasoning:\n{result['reasoning']}\n"
        
        output += "\n" + "-" * 50 + "\n\n"
    
    return output

def _format_technical_output(
    calibration_results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    include_reasoning: bool,
    include_alternatives: bool,
    include_confidence_intervals: bool
) -> str:
    """
    Format calibration results in technical format.
    
    Args:
        calibration_results: List of calibration results
        summary: Summary statistics
        include_reasoning: Whether reasoning is included
        include_alternatives: Whether alternatives are included
        include_confidence_intervals: Whether confidence intervals are included
        
    Returns:
        Technical formatted output
    """
    # Technical format is JSON-like
    output = "{\n"
    output += f"  \"summary\": {{\n"
    output += f"    \"total_statements\": {summary['total_statements']},\n"
    output += f"    \"average_confidence\": {summary['average_confidence']:.2f},\n"
    output += f"    \"high_confidence_count\": {summary['high_confidence_count']},\n"
    output += f"    \"moderate_confidence_count\": {summary['moderate_confidence_count']},\n"
    output += f"    \"low_confidence_count\": {summary['low_confidence_count']},\n"
    output += f"    \"recency_issues_count\": {summary['recency_issues_count']},\n"
    output += f"    \"consistency_issues_count\": {summary['consistency_issues_count']}\n"
    output += "  },\n"
    
    output += "  \"results\": [\n"
    for i, result in enumerate(calibration_results):
        output += "    {\n"
        output += f"      \"statement\": \"{result['statement']}\",\n"
        output += f"      \"statement_type\": \"{result['statement_type']}\",\n"
        output += f"      \"confidence_level\": {result['confidence_level']:.2f},\n"
        output += f"      \"confidence_category\": \"{result['confidence_category']}\",\n"
        
        if include_confidence_intervals and "confidence_interval" in result:
            ci = result["confidence_interval"]
            output += f"      \"confidence_interval\": {{\n"
            output += f"        \"lower_bound\": {ci['lower_bound']:.2f},\n"
            output += f"        \"upper_bound\": {ci['upper_bound']:.2f}\n"
            output += "      },\n"
        
        if "evidence" in result:
            output += f"      \"evidence_count\": {len(result['evidence'])},\n"
        
        if "source_quality" in result:
            sq = result["source_quality"]
            output += f"      \"source_quality\": {{\n"
            output += f"        \"average_quality\": {sq['average_quality']:.2f},\n"
            output += f"        \"diversity_score\": {sq['diversity_score']:.2f}\n"
            output += "      },\n"
        
        if "recency_issues" in result:
            output += "      \"has_recency_issues\": true,\n"
        else:
            output += "      \"has_recency_issues\": false,\n"
        
        if "consistency_issues" in result:
            output += "      \"has_consistency_issues\": true,\n"
        else:
            output += "      \"has_consistency_issues\": false,\n"
        
        if include_alternatives and "alternatives" in result:
            output += f"      \"alternatives_count\": {len(result['alternatives'])},\n"
        
        if include_reasoning and "reasoning" in result:
            # Truncate reasoning for technical format
            reasoning_preview = result['reasoning'][:100] + "..." if len(result['reasoning']) > 100 else result['reasoning']
            output += f"      \"reasoning_preview\": \"{reasoning_preview}\"\n"
        else:
            # Remove trailing comma from last item
            output = output.rstrip(",\n") + "\n"
        
        output += "    }" + ("," if i < len(calibration_results) - 1 else "") + "\n"
    
    output += "  ]\n"
    output += "}"
    
    return output
