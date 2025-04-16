"""
Multi-Agent Debater Tool for the Personal AI Agent System.

This module provides functionality to simulate a structured debate between
multiple AI agents with different perspectives on a topic.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("multi_agent_debater")

def run(
    topic: str,
    debate_question: str = None,
    perspectives: List[str] = None,
    num_agents: int = 3,
    debate_format: str = "structured",
    debate_rounds: int = 3,
    allow_consensus: bool = True,
    require_evidence: bool = True,
    include_devil_advocate: bool = True,
    include_moderator: bool = True,
    include_fact_checker: bool = False,
    focus_areas: List[str] = None,
    time_limit_minutes: int = 10,
    format_output: str = "markdown",
    store_memory: bool = True,
    memory_manager = None,
    memory_tags: List[str] = ["debate", "multi_agent"],
    memory_scope: str = "global"
) -> Dict[str, Any]:
    """
    Simulate a structured debate between multiple AI agents with different perspectives.
    
    Args:
        topic: The main topic for debate
        debate_question: Specific question to debate (if None, will be generated from topic)
        perspectives: List of perspectives to include (if None, will be auto-generated)
        num_agents: Number of debating agents (ignored if perspectives are provided)
        debate_format: Format of debate (structured, adversarial, collaborative, or panel)
        debate_rounds: Number of debate rounds
        allow_consensus: Whether to allow agents to reach consensus
        require_evidence: Whether to require evidence for claims
        include_devil_advocate: Whether to include a devil's advocate perspective
        include_moderator: Whether to include a moderator agent
        include_fact_checker: Whether to include a fact-checker agent
        focus_areas: Specific areas to focus on within the debate
        time_limit_minutes: Maximum time to spend on debate
        format_output: Output format (markdown, json, text)
        store_memory: Whether to store debate results in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing debate results and metadata
    """
    logger.info(f"Starting multi-agent debate on topic: {topic}")
    
    try:
        # Validate inputs
        if not topic:
            raise ValueError("Topic is required")
        
        # Generate debate question if not provided
        if not debate_question:
            debate_question = _generate_debate_question(topic)
        
        # Generate perspectives if not provided
        if not perspectives:
            perspectives = _generate_perspectives(topic, num_agents, include_devil_advocate)
        
        # Initialize debate state
        debate_state = {
            "topic": topic,
            "debate_question": debate_question,
            "perspectives": perspectives,
            "format": debate_format,
            "rounds": debate_rounds,
            "allow_consensus": allow_consensus,
            "require_evidence": require_evidence,
            "include_moderator": include_moderator,
            "include_fact_checker": include_fact_checker,
            "focus_areas": focus_areas or [],
            "start_time": time.time(),
            "time_limit_minutes": time_limit_minutes,
            "current_round": 0,
            "transcript": [],
            "key_points": [],
            "evidence_presented": [],
            "consensus_reached": False,
            "consensus_statement": None
        }
        
        # Run debate
        debate_state = _run_debate(debate_state)
        
        # Generate summary and analysis
        summary = _generate_debate_summary(debate_state)
        analysis = _generate_debate_analysis(debate_state)
        
        # Format output
        formatted_output = _format_debate_output(
            debate_state,
            summary,
            analysis,
            format_output
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the debate results
                memory_entry = {
                    "type": "debate_results",
                    "topic": topic,
                    "debate_question": debate_question,
                    "perspectives_count": len(perspectives),
                    "rounds_completed": debate_state["current_round"],
                    "consensus_reached": debate_state["consensus_reached"],
                    "summary": summary["overall_summary"][:500] + ("..." if len(summary["overall_summary"]) > 500 else ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ["debate_topic", topic.lower().replace(" ", "_")]
                )
                
                # Also store key points with their own tags
                for point in debate_state["key_points"]:
                    point_tag = point["category"].lower().replace(" ", "_")
                    memory_manager.add_memory(
                        content=json.dumps({
                            "type": "debate_key_point",
                            "topic": topic,
                            "point": point["point"],
                            "category": point["category"],
                            "supporting_perspectives": point["supporting_perspectives"],
                            "opposing_perspectives": point["opposing_perspectives"],
                            "timestamp": datetime.now().isoformat()
                        }),
                        scope=memory_scope,
                        tags=memory_tags + [point_tag, "key_point"]
                    )
                
                logger.info(f"Stored debate results in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store debate results in memory: {str(e)}")
        
        # Prepare response
        response = {
            "success": True,
            "topic": topic,
            "debate_question": debate_question,
            "perspectives": perspectives,
            "rounds_completed": debate_state["current_round"],
            "consensus_reached": debate_state["consensus_reached"],
            "consensus_statement": debate_state["consensus_statement"],
            "key_points": debate_state["key_points"],
            "summary": summary,
            "analysis": analysis,
            "formatted_output": formatted_output
        }
        
        # Include transcript if requested
        if format_output == "json":
            response["transcript"] = debate_state["transcript"]
        
        return response
    except Exception as e:
        error_msg = f"Error in multi-agent debate: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "topic": topic
        }

def _generate_debate_question(topic: str) -> str:
    """
    Generate a debate question from the topic.
    
    Args:
        topic: The main topic for debate
        
    Returns:
        Generated debate question
    """
    # In a real implementation, this would use LLM to generate a question
    # For this example, we'll use a template-based approach
    
    # Simple templates for different topic types
    templates = [
        f"Should {topic} be adopted more widely?",
        f"Is {topic} beneficial for society?",
        f"What are the most important considerations regarding {topic}?",
        f"How should we approach {topic} in the future?",
        f"What are the ethical implications of {topic}?"
    ]
    
    # Select template based on topic characteristics
    topic_lower = topic.lower()
    
    if any(word in topic_lower for word in ["technology", "ai", "digital", "internet", "automation"]):
        return f"What are the potential benefits and risks of {topic}?"
    elif any(word in topic_lower for word in ["policy", "regulation", "law", "governance", "government"]):
        return f"What is the optimal approach to {topic}?"
    elif any(word in topic_lower for word in ["ethics", "moral", "value", "principle", "philosophy"]):
        return f"What ethical framework should guide our thinking about {topic}?"
    elif any(word in topic_lower for word in ["society", "culture", "community", "social", "public"]):
        return f"How does {topic} impact different segments of society?"
    elif any(word in topic_lower for word in ["economy", "business", "market", "financial", "economic"]):
        return f"What economic considerations are most important regarding {topic}?"
    else:
        # Use hash of topic to select a template deterministically
        index = hash(topic) % len(templates)
        return templates[index]

def _generate_perspectives(topic: str, num_agents: int, include_devil_advocate: bool) -> List[str]:
    """
    Generate perspectives for the debate.
    
    Args:
        topic: The main topic for debate
        num_agents: Number of debating agents
        include_devil_advocate: Whether to include a devil's advocate
        
    Returns:
        List of perspectives
    """
    # In a real implementation, this would use LLM to generate diverse perspectives
    # For this example, we'll use a template-based approach
    
    # Common perspective templates
    templates = [
        f"Proponent of {topic}",
        f"Skeptic of {topic}",
        f"Pragmatic implementer of {topic}",
        f"Ethical analyst of {topic}",
        f"Historical perspective on {topic}",
        f"Future-oriented perspective on {topic}",
        f"Economic perspective on {topic}",
        f"Social impact perspective on {topic}",
        f"Technical expert on {topic}",
        f"Regulatory perspective on {topic}"
    ]
    
    # Ensure we have enough templates
    if num_agents > len(templates):
        # Add generic numbered perspectives
        for i in range(len(templates), num_agents):
            templates.append(f"Perspective {i+1} on {topic}")
    
    # Select perspectives
    selected = []
    
    # Always include proponent and skeptic for balance
    selected.append(templates[0])  # Proponent
    selected.append(templates[1])  # Skeptic
    
    # Add devil's advocate if requested
    if include_devil_advocate:
        selected.append(f"Devil's advocate challenging assumptions about {topic}")
        num_agents -= 1  # Reduce remaining slots by 1
    
    # Fill remaining slots
    remaining_slots = num_agents - len(selected)
    if remaining_slots > 0:
        # Select from remaining templates
        remaining_templates = [t for t in templates[2:] if t not in selected]
        
        # Ensure we don't exceed available templates
        remaining_slots = min(remaining_slots, len(remaining_templates))
        
        # Add remaining perspectives
        for i in range(remaining_slots):
            selected.append(remaining_templates[i])
    
    return selected

def _run_debate(debate_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the debate simulation.
    
    Args:
        debate_state: Current debate state
        
    Returns:
        Updated debate state with results
    """
    # In a real implementation, this would use LLM to generate actual debate
    # For this example, we'll simulate the debate
    
    # Initialize transcript with introduction
    if debate_state["include_moderator"]:
        debate_state["transcript"].append({
            "role": "Moderator",
            "content": f"Welcome to our debate on the topic: {debate_state['topic']}. "
                      f"Today we'll be discussing the question: {debate_state['debate_question']} "
                      f"We have {len(debate_state['perspectives'])} perspectives represented in this debate.",
            "round": 0,
            "timestamp": _get_timestamp(debate_state["start_time"])
        })
        
        # Introduce perspectives
        for perspective in debate_state["perspectives"]:
            debate_state["transcript"].append({
                "role": "Moderator",
                "content": f"Introducing the perspective: {perspective}",
                "round": 0,
                "timestamp": _get_timestamp(debate_state["start_time"])
            })
    
    # Run debate rounds
    for round_num in range(1, debate_state["rounds"] + 1):
        # Check if we've exceeded time limit
        current_time = time.time()
        if current_time - debate_state["start_time"] > debate_state["time_limit_minutes"] * 60:
            logger.info(f"Time limit reached after {round_num - 1} rounds")
            break
        
        # Update current round
        debate_state["current_round"] = round_num
        
        # Run the round based on debate format
        if debate_state["format"] == "structured":
            debate_state = _run_structured_round(debate_state, round_num)
        elif debate_state["format"] == "adversarial":
            debate_state = _run_adversarial_round(debate_state, round_num)
        elif debate_state["format"] == "collaborative":
            debate_state = _run_collaborative_round(debate_state, round_num)
        else:  # panel
            debate_state = _run_panel_round(debate_state, round_num)
        
        # Check if consensus was reached
        if debate_state["consensus_reached"]:
            if debate_state["include_moderator"]:
                debate_state["transcript"].append({
                    "role": "Moderator",
                    "content": f"It appears we've reached a consensus: {debate_state['consensus_statement']}",
                    "round": round_num,
                    "timestamp": _get_timestamp(debate_state["start_time"])
                })
            break
    
    # Add closing statements if we completed all rounds or reached consensus
    if debate_state["current_round"] == debate_state["rounds"] or debate_state["consensus_reached"]:
        for perspective in debate_state["perspectives"]:
            debate_state["transcript"].append({
                "role": perspective,
                "content": _generate_closing_statement(perspective, debate_state),
                "round": debate_state["current_round"],
                "timestamp": _get_timestamp(debate_state["start_time"]),
                "statement_type": "closing"
            })
        
        if debate_state["include_moderator"]:
            debate_state["transcript"].append({
                "role": "Moderator",
                "content": f"Thank you all for participating in this debate on {debate_state['topic']}. "
                          f"We've heard diverse perspectives and explored important aspects of this issue.",
                "round": debate_state["current_round"],
                "timestamp": _get_timestamp(debate_state["start_time"])
            })
    
    # Extract key points from transcript
    debate_state["key_points"] = _extract_key_points(debate_state)
    
    # Extract evidence presented
    debate_state["evidence_presented"] = _extract_evidence(debate_state)
    
    return debate_state

def _run_structured_round(debate_state: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """
    Run a structured debate round where each perspective speaks in turn.
    
    Args:
        debate_state: Current debate state
        round_num: Current round number
        
    Returns:
        Updated debate state
    """
    # In a structured debate, each perspective gets a turn to speak
    
    # Determine round theme based on round number
    round_theme = _get_round_theme(round_num, debate_state)
    
    # Moderator introduces the round
    if debate_state["include_moderator"]:
        debate_state["transcript"].append({
            "role": "Moderator",
            "content": f"Round {round_num}: {round_theme}",
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"])
        })
    
    # Each perspective speaks in turn
    for perspective in debate_state["perspectives"]:
        # Generate statement for this perspective
        statement = _generate_perspective_statement(
            perspective,
            debate_state,
            round_num,
            round_theme
        )
        
        # Add to transcript
        debate_state["transcript"].append({
            "role": perspective,
            "content": statement,
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"]),
            "statement_type": "main"
        })
        
        # Fact checker response if enabled
        if debate_state["include_fact_checker"]:
            fact_check = _generate_fact_check(statement, debate_state)
            debate_state["transcript"].append({
                "role": "Fact Checker",
                "content": fact_check,
                "round": round_num,
                "timestamp": _get_timestamp(debate_state["start_time"]),
                "statement_type": "fact_check"
            })
    
    # Check for potential consensus
    if debate_state["allow_consensus"] and round_num >= 2:
        consensus_result = _check_for_consensus(debate_state)
        debate_state["consensus_reached"] = consensus_result["reached"]
        debate_state["consensus_statement"] = consensus_result["statement"]
    
    return debate_state

def _run_adversarial_round(debate_state: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """
    Run an adversarial debate round with direct challenges.
    
    Args:
        debate_state: Current debate state
        round_num: Current round number
        
    Returns:
        Updated debate state
    """
    # In an adversarial debate, perspectives directly challenge each other
    
    # Determine round theme
    round_theme = _get_round_theme(round_num, debate_state)
    
    # Moderator introduces the round
    if debate_state["include_moderator"]:
        debate_state["transcript"].append({
            "role": "Moderator",
            "content": f"Round {round_num}: {round_theme} - In this round, perspectives will directly challenge each other.",
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"])
        })
    
    # Each perspective makes an initial statement
    for perspective in debate_state["perspectives"]:
        statement = _generate_perspective_statement(
            perspective,
            debate_state,
            round_num,
            round_theme
        )
        
        debate_state["transcript"].append({
            "role": perspective,
            "content": statement,
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"]),
            "statement_type": "main"
        })
    
    # Each perspective challenges another perspective
    for i, perspective in enumerate(debate_state["perspectives"]):
        # Determine which perspective to challenge (next one in the list, wrapping around)
        target_idx = (i + 1) % len(debate_state["perspectives"])
        target_perspective = debate_state["perspectives"][target_idx]
        
        # Find the target's statement from this round
        target_statements = [entry for entry in debate_state["transcript"] 
                           if entry["role"] == target_perspective and 
                              entry["round"] == round_num and
                              entry["statement_type"] == "main"]
        
        if target_statements:
            target_statement = target_statements[0]["content"]
            
            # Generate challenge
            challenge = _generate_challenge(perspective, target_perspective, target_statement, debate_state)
            
            debate_state["transcript"].append({
                "role": perspective,
                "content": challenge,
                "round": round_num,
                "timestamp": _get_timestamp(debate_state["start_time"]),
                "statement_type": "challenge",
                "target": target_perspective
            })
            
            # Generate response to challenge
            response = _generate_response_to_challenge(target_perspective, perspective, challenge, debate_state)
            
            debate_state["transcript"].append({
                "role": target_perspective,
                "content": response,
                "round": round_num,
                "timestamp": _get_timestamp(debate_state["start_time"]),
                "statement_type": "response",
                "target": perspective
            })
            
            # Fact checker response if enabled
            if debate_state["include_fact_checker"]:
                fact_check = _generate_fact_check(response, debate_state)
                debate_state["transcript"].append({
                    "role": "Fact Checker",
                    "content": fact_check,
                    "round": round_num,
                    "timestamp": _get_timestamp(debate_state["start_time"]),
                    "statement_type": "fact_check"
                })
    
    # Adversarial format makes consensus less likely, but still check
    if debate_state["allow_consensus"] and round_num >= 2:
        consensus_result = _check_for_consensus(debate_state)
        debate_state["consensus_reached"] = consensus_result["reached"]
        debate_state["consensus_statement"] = consensus_result["statement"]
    
    return debate_state

def _run_collaborative_round(debate_state: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """
    Run a collaborative debate round focused on finding common ground.
    
    Args:
        debate_state: Current debate state
        round_num: Current round number
        
    Returns:
        Updated debate state
    """
    # In a collaborative debate, perspectives try to find common ground
    
    # Determine round theme
    round_theme = _get_round_theme(round_num, debate_state)
    
    # Moderator introduces the round
    if debate_state["include_moderator"]:
        debate_state["transcript"].append({
            "role": "Moderator",
            "content": f"Round {round_num}: {round_theme} - In this round, we'll focus on finding common ground and areas of agreement.",
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"])
        })
    
    # Each perspective identifies areas of potential agreement
    for perspective in debate_state["perspectives"]:
        statement = _generate_collaborative_statement(
            perspective,
            debate_state,
            round_num,
            round_theme
        )
        
        debate_state["transcript"].append({
            "role": perspective,
            "content": statement,
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"]),
            "statement_type": "collaborative"
        })
    
    # Moderator summarizes areas of agreement
    if debate_state["include_moderator"]:
        agreement_summary = _generate_agreement_summary(debate_state, round_num)
        
        debate_state["transcript"].append({
            "role": "Moderator",
            "content": agreement_summary,
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"]),
            "statement_type": "agreement_summary"
        })
    
    # Collaborative format makes consensus more likely
    if debate_state["allow_consensus"]:
        consensus_result = _check_for_consensus(debate_state)
        debate_state["consensus_reached"] = consensus_result["reached"]
        debate_state["consensus_statement"] = consensus_result["statement"]
    
    return debate_state

def _run_panel_round(debate_state: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """
    Run a panel debate round with moderator questions.
    
    Args:
        debate_state: Current debate state
        round_num: Current round number
        
    Returns:
        Updated debate state
    """
    # In a panel debate, the moderator asks specific questions
    
    # Determine round theme
    round_theme = _get_round_theme(round_num, debate_state)
    
    # Generate questions for this round
    questions = _generate_panel_questions(debate_state, round_num, round_theme)
    
    # Moderator introduces the round
    if debate_state["include_moderator"]:
        debate_state["transcript"].append({
            "role": "Moderator",
            "content": f"Round {round_num}: {round_theme} - I'll be asking specific questions to each perspective.",
            "round": round_num,
            "timestamp": _get_timestamp(debate_state["start_time"])
        })
    
    # Ask each question to relevant perspectives
    for question in questions:
        if debate_state["include_moderator"]:
            debate_state["transcript"].append({
                "role": "Moderator",
                "content": question["question"],
                "round": round_num,
                "timestamp": _get_timestamp(debate_state["start_time"]),
                "statement_type": "question"
            })
        
        # Determine which perspectives should answer
        if question["target"] == "all":
            answering_perspectives = debate_state["perspectives"]
        elif question["target"] == "proponent":
            # Assume first perspective is proponent
            answering_perspectives = [debate_state["perspectives"][0]]
        elif question["target"] == "skeptic":
            # Assume second perspective is skeptic
            answering_perspectives = [debate_state["perspectives"][1]]
        else:
            # Target specific perspective by index
            try:
                target_idx = int(question["target"])
                if 0 <= target_idx < len(debate_state["perspectives"]):
                    answering_perspectives = [debate_state["perspectives"][target_idx]]
                else:
                    answering_perspectives = debate_state["perspectives"]
            except ValueError:
                answering_perspectives = debate_state["perspectives"]
        
        # Get answers from selected perspectives
        for perspective in answering_perspectives:
            answer = _generate_answer_to_question(
                perspective,
                question["question"],
                debate_state
            )
            
            debate_state["transcript"].append({
                "role": perspective,
                "content": answer,
                "round": round_num,
                "timestamp": _get_timestamp(debate_state["start_time"]),
                "statement_type": "answer",
                "question": question["question"]
            })
            
            # Fact checker response if enabled
            if debate_state["include_fact_checker"]:
                fact_check = _generate_fact_check(answer, debate_state)
                debate_state["transcript"].append({
                    "role": "Fact Checker",
                    "content": fact_check,
                    "round": round_num,
                    "timestamp": _get_timestamp(debate_state["start_time"]),
                    "statement_type": "fact_check"
                })
    
    # Check for potential consensus
    if debate_state["allow_consensus"] and round_num >= 2:
        consensus_result = _check_for_consensus(debate_state)
        debate_state["consensus_reached"] = consensus_result["reached"]
        debate_state["consensus_statement"] = consensus_result["statement"]
    
    return debate_state

def _get_timestamp(start_time: float) -> str:
    """
    Get a formatted timestamp relative to debate start time.
    
    Args:
        start_time: Debate start time
        
    Returns:
        Formatted timestamp
    """
    elapsed_seconds = time.time() - start_time
    minutes = int(elapsed_seconds // 60)
    seconds = int(elapsed_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def _get_round_theme(round_num: int, debate_state: Dict[str, Any]) -> str:
    """
    Determine the theme for a debate round.
    
    Args:
        round_num: Current round number
        debate_state: Current debate state
        
    Returns:
        Round theme
    """
    # In a real implementation, this would generate contextual themes
    # For this example, we'll use predefined themes
    
    # Default themes based on round number
    default_themes = [
        "Opening statements and defining the issue",
        "Exploring key arguments and evidence",
        "Addressing counterarguments",
        "Finding common ground and potential solutions",
        "Concluding thoughts and implications"
    ]
    
    # Use focus areas if available
    if debate_state["focus_areas"] and round_num <= len(debate_state["focus_areas"]):
        return f"Discussing {debate_state['focus_areas'][round_num - 1]}"
    
    # Otherwise use default theme
    if round_num <= len(default_themes):
        return default_themes[round_num - 1]
    else:
        return f"Continuing the debate on {debate_state['topic']}"

def _generate_perspective_statement(
    perspective: str,
    debate_state: Dict[str, Any],
    round_num: int,
    round_theme: str
) -> str:
    """
    Generate a statement from a specific perspective.
    
    Args:
        perspective: The perspective to generate a statement for
        debate_state: Current debate state
        round_num: Current round number
        round_theme: Theme for the current round
        
    Returns:
        Generated statement
    """
    # In a real implementation, this would use LLM to generate statements
    # For this example, we'll use templates based on perspective and round
    
    topic = debate_state["topic"]
    question = debate_state["debate_question"]
    
    # Determine statement type based on perspective and round
    if "proponent" in perspective.lower():
        if round_num == 1:
            return f"As a proponent of {topic}, I believe there are significant benefits to consider. " \
                   f"First, {topic} offers [simulated benefit 1]. Second, we see [simulated benefit 2]. " \
                   f"The evidence clearly shows that [simulated evidence for benefits]."
        elif round_num == 2:
            return f"Building on my earlier points, I want to address some common concerns about {topic}. " \
                   f"While some worry about [simulated concern 1], the reality is that [simulated rebuttal 1]. " \
                   f"Similarly, [simulated concern 2] is addressed by [simulated rebuttal 2]."
        else:
            return f"As we continue this discussion on {topic}, I want to emphasize that [simulated key point]. " \
                   f"This is particularly important because [simulated reasoning]. " \
                   f"The data from [simulated source] supports this conclusion."
    
    elif "skeptic" in perspective.lower():
        if round_num == 1:
            return f"As a skeptic regarding {topic}, I have several concerns that must be addressed. " \
                   f"Primarily, there's the issue of [simulated concern 1], which could lead to [simulated negative outcome]. " \
                   f"Additionally, [simulated concern 2] raises serious questions about [simulated aspect of topic]."
        elif round_num == 2:
            return f"I've listened to the arguments in favor of {topic}, but they fail to address [simulated critical issue]. " \
                   f"The claim that [simulated opposing claim] overlooks [simulated counterpoint]. " \
                   f"Furthermore, studies from [simulated source] indicate [simulated contradictory evidence]."
        else:
            return f"At this point in our debate on {topic}, I must emphasize that [simulated key concern]. " \
                   f"While I acknowledge [simulated concession], this doesn't outweigh [simulated primary objection]. " \
                   f"We need more rigorous analysis of [simulated aspect requiring scrutiny]."
    
    elif "devil's advocate" in perspective.lower():
        return f"Playing devil's advocate on {topic}, let's consider a perspective that challenges our assumptions. " \
               f"What if [simulated contrarian hypothesis]? This would suggest that [simulated unexpected implication]. " \
               f"Have we fully considered [simulated overlooked aspect]? This raises important questions about our approach."
    
    elif "pragmatic" in perspective.lower():
        return f"Taking a pragmatic view of {topic}, we need to focus on implementation realities. " \
               f"The practical challenges include [simulated practical challenge 1] and [simulated practical challenge 2]. " \
               f"A workable approach would need to address [simulated implementation requirement] " \
               f"while balancing [simulated competing priority]."
    
    elif "ethical" in perspective.lower():
        return f"From an ethical standpoint, {topic} raises important considerations about [simulated ethical dimension]. " \
               f"We must ask whether [simulated ethical question]. The principle of [simulated ethical principle] " \
               f"suggests that [simulated ethical conclusion]. However, this must be balanced against [simulated competing value]."
    
    elif "economic" in perspective.lower():
        return f"Examining the economic aspects of {topic}, we should consider both short and long-term impacts. " \
               f"In the near term, [simulated economic effect 1]. Over time, however, [simulated economic effect 2]. " \
               f"Cost-benefit analysis suggests [simulated economic conclusion], though this varies across [simulated economic contexts]."
    
    elif "social" in perspective.lower():
        return f"Considering the social impact of {topic}, we must acknowledge how different communities are affected. " \
               f"For [simulated demographic 1], this means [simulated social impact 1]. " \
               f"Meanwhile, [simulated demographic 2] experiences [simulated social impact 2]. " \
               f"These disparate effects highlight the importance of [simulated social consideration]."
    
    elif "technical" in perspective.lower():
        return f"From a technical perspective, {topic} involves several key considerations. " \
               f"The architecture of [simulated technical aspect] determines [simulated technical outcome]. " \
               f"Current limitations in [simulated technical limitation] present challenges, " \
               f"but emerging approaches in [simulated technical innovation] offer promising solutions."
    
    elif "regulatory" in perspective.lower():
        return f"From a regulatory standpoint, {topic} requires careful governance frameworks. " \
               f"Current regulations like [simulated regulation] address [simulated regulatory aspect], " \
               f"but gaps remain in [simulated regulatory gap]. " \
               f"A balanced approach would include [simulated regulatory recommendation] " \
               f"while avoiding [simulated regulatory pitfall]."
    
    else:
        # Generic perspective
        return f"Considering {topic} from my perspective, I believe [simulated viewpoint]. " \
               f"This is based on [simulated reasoning]. While others may focus on [simulated alternative aspect], " \
               f"I think [simulated distinctive view] deserves more attention in this discussion."

def _generate_challenge(
    challenger: str,
    target: str,
    target_statement: str,
    debate_state: Dict[str, Any]
) -> str:
    """
    Generate a challenge from one perspective to another.
    
    Args:
        challenger: Perspective making the challenge
        target: Perspective being challenged
        target_statement: Statement being challenged
        debate_state: Current debate state
        
    Returns:
        Generated challenge
    """
    # In a real implementation, this would use LLM to generate challenges
    # For this example, we'll use templates
    
    topic = debate_state["topic"]
    
    challenges = [
        f"I must challenge the perspective from {target}. The claim that [simulated target claim] " \
        f"overlooks [simulated overlooked factor]. This is problematic because [simulated reasoning].",
        
        f"There's a fundamental flaw in the argument presented by {target}. " \
        f"The evidence doesn't support the conclusion that [simulated target conclusion]. " \
        f"In fact, [simulated contradictory evidence] suggests otherwise.",
        
        f"I appreciate {target}'s perspective, but it relies on an assumption that [simulated questionable assumption]. " \
        f"This assumption doesn't hold when we consider [simulated counterexample or context].",
        
        f"The analysis from {target} fails to account for [simulated missing factor], " \
        f"which significantly changes how we should view [simulated aspect of topic]. " \
        f"This oversight leads to [simulated problematic conclusion]."
    ]
    
    # Select challenge based on challenger characteristics
    if "skeptic" in challenger.lower():
        return challenges[0]
    elif "devil's advocate" in challenger.lower():
        return challenges[1]
    elif "technical" in challenger.lower() or "economic" in challenger.lower():
        return challenges[2]
    else:
        return challenges[3]

def _generate_response_to_challenge(
    responder: str,
    challenger: str,
    challenge: str,
    debate_state: Dict[str, Any]
) -> str:
    """
    Generate a response to a challenge.
    
    Args:
        responder: Perspective responding to the challenge
        challenger: Perspective that made the challenge
        challenge: The challenge being responded to
        debate_state: Current debate state
        
    Returns:
        Generated response
    """
    # In a real implementation, this would use LLM to generate responses
    # For this example, we'll use templates
    
    topic = debate_state["topic"]
    
    responses = [
        f"I appreciate the challenge from {challenger}, but I stand by my position. " \
        f"The concern about [simulated challenged aspect] doesn't undermine my core argument because [simulated defense]. " \
        f"Furthermore, [simulated additional evidence] supports my original point.",
        
        f"The challenge raises an important consideration, but it mischaracterizes my position. " \
        f"I'm not claiming [simulated misattributed claim], but rather [simulated actual position]. " \
        f"This distinction is crucial because [simulated reasoning].",
        
        f"While {challenger} raises a valid point about [simulated valid aspect of challenge], " \
        f"this actually strengthens my overall argument when we consider [simulated broader context]. " \
        f"The apparent contradiction is resolved when we recognize [simulated reconciling factor].",
        
        f"I concede that {challenger} has identified a limitation in my earlier statement. " \
        f"The point about [simulated challenged point] deserves more nuance. " \
        f"A more accurate characterization would be [simulated refined position], " \
        f"which addresses the concern while preserving the core insight."
    ]
    
    # Select response based on responder characteristics
    if "proponent" in responder.lower():
        return responses[0]
    elif "pragmatic" in responder.lower():
        return responses[1]
    elif "ethical" in responder.lower() or "social" in responder.lower():
        return responses[2]
    else:
        return responses[3]

def _generate_collaborative_statement(
    perspective: str,
    debate_state: Dict[str, Any],
    round_num: int,
    round_theme: str
) -> str:
    """
    Generate a collaborative statement seeking common ground.
    
    Args:
        perspective: The perspective to generate a statement for
        debate_state: Current debate state
        round_num: Current round number
        round_theme: Theme for the current round
        
    Returns:
        Generated collaborative statement
    """
    # In a real implementation, this would use LLM to generate statements
    # For this example, we'll use templates
    
    topic = debate_state["topic"]
    
    statements = [
        f"Looking for common ground on {topic}, I believe we can all agree that [simulated shared value or goal]. " \
        f"While we may differ on [simulated area of disagreement], there's consensus around [simulated area of agreement]. " \
        f"This shared understanding could form the basis for [simulated constructive approach].",
        
        f"Despite our different perspectives on {topic}, I see several points of convergence. " \
        f"First, [simulated common point 1]. Second, [simulated common point 2]. " \
        f"These areas of agreement suggest that [simulated collaborative conclusion].",
        
        f"To bridge the gap between our viewpoints on {topic}, I propose focusing on [simulated bridging concept]. " \
        f"This approach acknowledges [simulated concern from other perspective] while also addressing [simulated own priority]. " \
        f"A balanced solution might include [simulated compromise approach].",
        
        f"Synthesizing the insights shared so far about {topic}, I see a potential integrated framework. " \
        f"The [simulated aspect from perspective 1] complements [simulated aspect from perspective 2] " \
        f"when we consider [simulated integrating factor]. This suggests [simulated holistic approach]."
    ]
    
    # Select statement based on perspective and round
    index = (hash(perspective) + round_num) % len(statements)
    return statements[index]

def _generate_agreement_summary(debate_state: Dict[str, Any], round_num: int) -> str:
    """
    Generate a summary of areas of agreement.
    
    Args:
        debate_state: Current debate state
        round_num: Current round number
        
    Returns:
        Generated agreement summary
    """
    # In a real implementation, this would analyze actual statements
    # For this example, we'll use a template
    
    topic = debate_state["topic"]
    
    return f"Thank you all for your thoughtful contributions. I'm noticing several areas of agreement emerging: " \
           f"First, there seems to be consensus that [simulated agreement point 1]. " \
           f"Second, most perspectives acknowledge [simulated agreement point 2]. " \
           f"There's also general recognition that [simulated agreement point 3]. " \
           f"These areas of common ground provide a foundation for addressing the remaining differences " \
           f"regarding [simulated remaining disagreement]."

def _generate_panel_questions(
    debate_state: Dict[str, Any],
    round_num: int,
    round_theme: str
) -> List[Dict[str, Any]]:
    """
    Generate questions for a panel debate round.
    
    Args:
        debate_state: Current debate state
        round_num: Current round number
        round_theme: Theme for the current round
        
    Returns:
        List of questions with targets
    """
    # In a real implementation, this would generate contextual questions
    # For this example, we'll use templates
    
    topic = debate_state["topic"]
    question = debate_state["debate_question"]
    
    # Generate 2-3 questions per round
    questions = []
    
    if round_num == 1:
        questions = [
            {
                "question": f"Let's start with a fundamental question: What do you see as the most important aspect of {topic} that should frame our discussion?",
                "target": "all"
            },
            {
                "question": f"To the proponent perspective: What evidence most strongly supports your position on {topic}?",
                "target": "proponent"
            },
            {
                "question": f"To the skeptical perspective: What specific concerns or risks do you believe aren't receiving adequate attention in discussions about {topic}?",
                "target": "skeptic"
            }
        ]
    elif round_num == 2:
        questions = [
            {
                "question": f"How might different stakeholders be affected differently by {topic}?",
                "target": "all"
            },
            {
                "question": f"What are the strongest counterarguments to your own position, and how do you address them?",
                "target": "all"
            }
        ]
    else:
        questions = [
            {
                "question": f"As we near the end of our discussion, what common ground do you see emerging on {topic}?",
                "target": "all"
            },
            {
                "question": f"What specific next steps or actions would you recommend regarding {topic}?",
                "target": "all"
            }
        ]
    
    # Add focus area questions if applicable
    if debate_state["focus_areas"]:
        for area in debate_state["focus_areas"]:
            if len(questions) < 4:  # Limit total questions
                questions.append({
                    "question": f"How does {area} specifically relate to our central question about {topic}?",
                    "target": "all"
                })
    
    return questions

def _generate_answer_to_question(
    perspective: str,
    question: str,
    debate_state: Dict[str, Any]
) -> str:
    """
    Generate an answer to a panel question.
    
    Args:
        perspective: The perspective answering the question
        question: The question being answered
        debate_state: Current debate state
        
    Returns:
        Generated answer
    """
    # In a real implementation, this would use LLM to generate answers
    # For this example, we'll use templates based on perspective
    
    topic = debate_state["topic"]
    
    # Generic answer template
    answer = f"From my perspective as {perspective}, I would answer that [simulated answer content]. " \
             f"This is important because [simulated reasoning]. " \
             f"The implications for {topic} are [simulated implications]."
    
    # Customize based on perspective type
    if "proponent" in perspective.lower():
        answer = f"As a proponent of {topic}, I believe [simulated positive answer]. " \
                 f"The evidence from [simulated source] demonstrates [simulated supporting evidence]. " \
                 f"This highlights the potential for [simulated positive outcome]."
    elif "skeptic" in perspective.lower():
        answer = f"As a skeptic regarding {topic}, I must point out [simulated cautionary answer]. " \
                 f"We should be wary of [simulated risk or concern]. " \
                 f"A more prudent approach would involve [simulated alternative approach]."
    elif "pragmatic" in perspective.lower():
        answer = f"Taking a pragmatic view, the question of {topic} comes down to [simulated practical consideration]. " \
                 f"The implementation challenges include [simulated practical challenge]. " \
                 f"A workable solution would need to address [simulated implementation requirement]."
    elif "ethical" in perspective.lower():
        answer = f"From an ethical standpoint, this question raises important considerations about [simulated ethical dimension]. " \
                 f"We must consider whether [simulated ethical question]. " \
                 f"The principle of [simulated ethical principle] suggests [simulated ethical conclusion]."
    
    return answer

def _generate_fact_check(statement: str, debate_state: Dict[str, Any]) -> str:
    """
    Generate a fact check for a statement.
    
    Args:
        statement: Statement to fact check
        debate_state: Current debate state
        
    Returns:
        Generated fact check
    """
    # In a real implementation, this would use LLM to generate fact checks
    # For this example, we'll use templates with randomization
    
    import random
    
    fact_check_templates = [
        "The statement is generally accurate. The claim about [simulated claim] is supported by [simulated evidence]. However, the characterization of [simulated detail] could be more precise.",
        
        "This statement contains a mixture of accurate and inaccurate information. While [simulated accurate part] is correct, the claim that [simulated inaccurate claim] is not supported by current evidence. [Simulated correction].",
        
        "The statement requires context. While technically accurate, the claim about [simulated claim] omits important context about [simulated missing context] which affects how this information should be interpreted.",
        
        "The statement includes a factual error. The claim that [simulated erroneous claim] is contradicted by [simulated contradictory evidence]. The accurate information is [simulated correction]."
    ]
    
    # Randomly select a fact check template
    return random.choice(fact_check_templates)

def _check_for_consensus(debate_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if consensus has been reached in the debate.
    
    Args:
        debate_state: Current debate state
        
    Returns:
        Dictionary indicating if consensus was reached and the consensus statement
    """
    # In a real implementation, this would analyze actual statements
    # For this example, we'll use a simple heuristic
    
    # Collaborative format makes consensus more likely
    consensus_probability = 0.1  # Base probability
    
    if debate_state["format"] == "collaborative":
        consensus_probability += 0.4
    elif debate_state["format"] == "structured":
        consensus_probability += 0.2
    elif debate_state["format"] == "panel":
        consensus_probability += 0.1
    
    # Later rounds make consensus more likely
    consensus_probability += min(0.3, debate_state["current_round"] * 0.1)
    
    # Simulate consensus check
    import random
    consensus_reached = random.random() < consensus_probability
    
    if consensus_reached:
        consensus_statement = f"After thorough discussion of {debate_state['topic']}, there is agreement that " \
                             f"[simulated consensus point 1]. Additionally, all perspectives acknowledge " \
                             f"[simulated consensus point 2], while recognizing [simulated nuance or limitation]. " \
                             f"This suggests [simulated implication or path forward]."
    else:
        consensus_statement = None
    
    return {
        "reached": consensus_reached,
        "statement": consensus_statement
    }

def _generate_closing_statement(perspective: str, debate_state: Dict[str, Any]) -> str:
    """
    Generate a closing statement for a perspective.
    
    Args:
        perspective: The perspective making the closing statement
        debate_state: Current debate state
        
    Returns:
        Generated closing statement
    """
    # In a real implementation, this would use LLM to generate statements
    # For this example, we'll use templates
    
    topic = debate_state["topic"]
    
    # Generic closing statement
    closing = f"In conclusion, my perspective on {topic} emphasizes [simulated key point]. " \
              f"Throughout this debate, I've highlighted [simulated main arguments]. " \
              f"Moving forward, it's important to consider [simulated recommendation] " \
              f"as we continue to address this important issue."
    
    # Customize based on perspective type
    if "proponent" in perspective.lower():
        closing = f"As we conclude, I maintain that {topic} offers significant benefits, including [simulated benefits]. " \
                 f"While acknowledging [simulated limitation], the evidence clearly supports [simulated positive conclusion]. " \
                 f"I encourage further exploration of [simulated promising direction]."
    elif "skeptic" in perspective.lower():
        closing = f"In closing, my skepticism about {topic} stems from [simulated concerns]. " \
                 f"While I recognize [simulated positive aspect], we must remain vigilant about [simulated risks]. " \
                 f"A more balanced approach would include [simulated recommendation]."
    elif "devil's advocate" in perspective.lower():
        closing = f"As devil's advocate, I've challenged assumptions about {topic} to deepen our understanding. " \
                 f"By questioning [simulated challenged assumptions], we've uncovered [simulated insights]. " \
                 f"This demonstrates the value of considering [simulated alternative viewpoint]."
    
    return closing

def _extract_key_points(debate_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract key points from the debate transcript.
    
    Args:
        debate_state: Current debate state
        
    Returns:
        List of key points with metadata
    """
    # In a real implementation, this would analyze actual statements
    # For this example, we'll generate simulated key points
    
    topic = debate_state["topic"]
    
    # Generate 3-5 key points
    num_points = min(5, max(3, len(debate_state["perspectives"]) - 1))
    
    key_points = []
    
    # Categories for key points
    categories = [
        "Core Consideration",
        "Area of Agreement",
        "Point of Contention",
        "Ethical Dimension",
        "Practical Implication",
        "Future Direction",
        "Underlying Assumption",
        "Evidence Gap"
    ]
    
    for i in range(num_points):
        # Select category
        category = categories[i % len(categories)]
        
        # Determine which perspectives support and oppose this point
        all_perspectives = debate_state["perspectives"].copy()
        import random
        random.shuffle(all_perspectives)
        
        # Randomly assign perspectives to supporting or opposing
        split_point = random.randint(1, len(all_perspectives) - 1)
        supporting = all_perspectives[:split_point]
        opposing = all_perspectives[split_point:]
        
        # Create key point
        key_point = {
            "point": f"Simulated key point {i+1} about {topic}",
            "category": category,
            "supporting_perspectives": supporting,
            "opposing_perspectives": opposing,
            "evidence_strength": random.choice(["strong", "moderate", "limited"]),
            "first_mentioned_in_round": random.randint(1, debate_state["current_round"])
        }
        
        key_points.append(key_point)
    
    return key_points

def _extract_evidence(debate_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract evidence presented in the debate.
    
    Args:
        debate_state: Current debate state
        
    Returns:
        List of evidence items with metadata
    """
    # In a real implementation, this would analyze actual statements
    # For this example, we'll generate simulated evidence
    
    # Generate 3-6 evidence items
    num_items = min(6, max(3, debate_state["current_round"] * 2))
    
    evidence = []
    
    # Evidence types
    evidence_types = [
        "Research Study",
        "Expert Opinion",
        "Statistical Data",
        "Case Study",
        "Historical Precedent",
        "Logical Argument"
    ]
    
    for i in range(num_items):
        # Select type
        evidence_type = evidence_types[i % len(evidence_types)]
        
        # Determine which perspective presented this evidence
        import random
        presenting_perspective = random.choice(debate_state["perspectives"])
        
        # Create evidence item
        evidence_item = {
            "description": f"Simulated evidence {i+1} related to {debate_state['topic']}",
            "type": evidence_type,
            "presented_by": presenting_perspective,
            "presented_in_round": random.randint(1, debate_state["current_round"]),
            "strength": random.choice(["strong", "moderate", "weak"]),
            "contested": random.choice([True, False])
        }
        
        if evidence_item["contested"]:
            evidence_item["contested_by"] = random.choice([p for p in debate_state["perspectives"] if p != presenting_perspective])
            evidence_item["contestation_reason"] = random.choice([
                "Methodological concerns",
                "Sample size limitations",
                "Alternative interpretation",
                "Outdated information",
                "Contextual relevance"
            ])
        
        evidence.append(evidence_item)
    
    return evidence

def _generate_debate_summary(debate_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of the debate.
    
    Args:
        debate_state: Current debate state
        
    Returns:
        Debate summary
    """
    # In a real implementation, this would analyze actual debate content
    # For this example, we'll generate a simulated summary
    
    topic = debate_state["topic"]
    question = debate_state["debate_question"]
    
    # Generate overall summary
    overall_summary = f"This debate explored {topic}, specifically addressing the question: {question}. "
    overall_summary += f"The discussion included {len(debate_state['perspectives'])} perspectives over {debate_state['current_round']} rounds. "
    
    if debate_state["consensus_reached"]:
        overall_summary += f"Notably, the participants reached consensus that {debate_state['consensus_statement']}. "
    else:
        overall_summary += f"While consensus wasn't reached, several key areas of agreement and disagreement emerged. "
    
    overall_summary += f"The debate highlighted the complexity of {topic}, with implications for [simulated stakeholders or domains]."
    
    # Generate perspective summaries
    perspective_summaries = {}
    for perspective in debate_state["perspectives"]:
        perspective_summaries[perspective] = f"The {perspective} emphasized [simulated key arguments], "
        perspective_summaries[perspective] += f"particularly focusing on [simulated focus area]. "
        perspective_summaries[perspective] += f"This perspective was supported by [simulated evidence or reasoning]."
    
    # Generate key agreements and disagreements
    key_agreements = [
        f"Simulated agreement point 1 about {topic}",
        f"Simulated agreement point 2 about {topic}"
    ]
    
    key_disagreements = [
        f"Simulated disagreement point 1 about {topic}",
        f"Simulated disagreement point 2 about {topic}",
        f"Simulated disagreement point 3 about {topic}"
    ]
    
    return {
        "overall_summary": overall_summary,
        "perspective_summaries": perspective_summaries,
        "key_agreements": key_agreements,
        "key_disagreements": key_disagreements,
        "rounds_completed": debate_state["current_round"],
        "consensus_reached": debate_state["consensus_reached"]
    }

def _generate_debate_analysis(debate_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an analysis of the debate.
    
    Args:
        debate_state: Current debate state
        
    Returns:
        Debate analysis
    """
    # In a real implementation, this would analyze actual debate content
    # For this example, we'll generate a simulated analysis
    
    topic = debate_state["topic"]
    
    # Generate quality assessment
    quality_assessment = {
        "evidence_quality": _generate_quality_score(),
        "reasoning_quality": _generate_quality_score(),
        "perspective_diversity": _generate_quality_score(),
        "argument_coherence": _generate_quality_score(),
        "overall_quality": _generate_quality_score()
    }
    
    # Generate argument strength by perspective
    argument_strength = {}
    for perspective in debate_state["perspectives"]:
        argument_strength[perspective] = {
            "evidence_strength": _generate_quality_score(),
            "reasoning_strength": _generate_quality_score(),
            "persuasiveness": _generate_quality_score(),
            "responsiveness": _generate_quality_score()
        }
    
    # Generate cognitive biases identified
    cognitive_biases = [
        {
            "bias": "Confirmation Bias",
            "description": "Tendency to search for and interpret information in a way that confirms pre-existing beliefs",
            "observed_in": [debate_state["perspectives"][0]]  # Assign to first perspective
        },
        {
            "bias": "False Consensus Effect",
            "description": "Tendency to overestimate how much others agree with one's own beliefs",
            "observed_in": [debate_state["perspectives"][1]]  # Assign to second perspective
        },
        {
            "bias": "Appeal to Authority",
            "description": "Using the opinion of an authority figure as evidence",
            "observed_in": [debate_state["perspectives"][2 % len(debate_state["perspectives"])]]  # Assign to third perspective (or wrap around)
        }
    ]
    
    # Generate logical fallacies identified
    logical_fallacies = [
        {
            "fallacy": "False Dichotomy",
            "description": "Presenting only two options when others exist",
            "observed_in_round": 1
        },
        {
            "fallacy": "Slippery Slope",
            "description": "Arguing that a small step will lead to extreme consequences",
            "observed_in_round": 2
        }
    ]
    
    # Generate implications
    implications = [
        f"Simulated implication 1 for {topic}",
        f"Simulated implication 2 for {topic}",
        f"Simulated implication 3 for {topic}"
    ]
    
    return {
        "quality_assessment": quality_assessment,
        "argument_strength": argument_strength,
        "cognitive_biases": cognitive_biases,
        "logical_fallacies": logical_fallacies,
        "implications": implications
    }

def _generate_quality_score() -> Dict[str, Any]:
    """
    Generate a quality score with explanation.
    
    Returns:
        Quality score with explanation
    """
    import random
    
    score = round(random.uniform(2.5, 4.5), 1)  # Score between 2.5 and 4.5
    
    explanations = {
        (2.5, 3.0): "Below average, with significant room for improvement",
        (3.0, 3.5): "Average, meeting basic standards",
        (3.5, 4.0): "Above average, demonstrating good quality",
        (4.0, 4.5): "Excellent, with minor areas for improvement",
        (4.5, 5.0): "Outstanding, exemplary quality"
    }
    
    # Find the appropriate explanation
    explanation = next((exp for range_key, exp in explanations.items() 
                      if range_key[0] <= score <= range_key[1]), 
                      "Average quality")
    
    return {
        "score": score,
        "out_of": 5.0,
        "explanation": explanation
    }

def _format_debate_output(
    debate_state: Dict[str, Any],
    summary: Dict[str, Any],
    analysis: Dict[str, Any],
    format_output: str
) -> str:
    """
    Format the debate output in the specified format.
    
    Args:
        debate_state: Current debate state
        summary: Debate summary
        analysis: Debate analysis
        format_output: Output format (markdown, json, text)
        
    Returns:
        Formatted debate output
    """
    if format_output == "json":
        return json.dumps({
            "debate_state": debate_state,
            "summary": summary,
            "analysis": analysis
        }, indent=2)
    elif format_output == "text":
        return _format_text_output(debate_state, summary, analysis)
    else:  # markdown
        return _format_markdown_output(debate_state, summary, analysis)

def _format_text_output(
    debate_state: Dict[str, Any],
    summary: Dict[str, Any],
    analysis: Dict[str, Any]
) -> str:
    """
    Format debate output as plain text.
    
    Args:
        debate_state: Current debate state
        summary: Debate summary
        analysis: Debate analysis
        
    Returns:
        Text formatted output
    """
    output = f"DEBATE SUMMARY: {debate_state['topic']}\n"
    output += f"Question: {debate_state['debate_question']}\n\n"
    
    output += "OVERVIEW\n"
    output += f"{summary['overall_summary']}\n\n"
    
    output += "PERSPECTIVES\n"
    for perspective, summary_text in summary['perspective_summaries'].items():
        output += f"- {perspective}: {summary_text}\n"
    output += "\n"
    
    output += "KEY POINTS OF AGREEMENT\n"
    for point in summary['key_agreements']:
        output += f"- {point}\n"
    output += "\n"
    
    output += "KEY POINTS OF DISAGREEMENT\n"
    for point in summary['key_disagreements']:
        output += f"- {point}\n"
    output += "\n"
    
    if debate_state['consensus_reached']:
        output += "CONSENSUS\n"
        output += f"{debate_state['consensus_statement']}\n\n"
    
    output += "EVIDENCE PRESENTED\n"
    for evidence in debate_state['evidence_presented']:
        output += f"- {evidence['description']} ({evidence['type']})\n"
        output += f"  Presented by: {evidence['presented_by']} in round {evidence['presented_in_round']}\n"
        output += f"  Strength: {evidence['strength']}\n"
        if evidence['contested']:
            output += f"  Contested by: {evidence['contested_by']} - {evidence['contestation_reason']}\n"
        output += "\n"
    
    output += "QUALITY ASSESSMENT\n"
    qa = analysis['quality_assessment']
    output += f"- Evidence Quality: {qa['evidence_quality']['score']}/5.0 - {qa['evidence_quality']['explanation']}\n"
    output += f"- Reasoning Quality: {qa['reasoning_quality']['score']}/5.0 - {qa['reasoning_quality']['explanation']}\n"
    output += f"- Perspective Diversity: {qa['perspective_diversity']['score']}/5.0 - {qa['perspective_diversity']['explanation']}\n"
    output += f"- Overall Quality: {qa['overall_quality']['score']}/5.0 - {qa['overall_quality']['explanation']}\n\n"
    
    output += "IMPLICATIONS\n"
    for implication in analysis['implications']:
        output += f"- {implication}\n"
    
    return output

def _format_markdown_output(
    debate_state: Dict[str, Any],
    summary: Dict[str, Any],
    analysis: Dict[str, Any]
) -> str:
    """
    Format debate output as markdown.
    
    Args:
        debate_state: Current debate state
        summary: Debate summary
        analysis: Debate analysis
        
    Returns:
        Markdown formatted output
    """
    output = f"# Debate Summary: {debate_state['topic']}\n\n"
    output += f"**Question:** {debate_state['debate_question']}\n\n"
    
    output += "## Overview\n\n"
    output += f"{summary['overall_summary']}\n\n"
    
    output += "## Perspectives\n\n"
    for perspective, summary_text in summary['perspective_summaries'].items():
        output += f"### {perspective}\n\n"
        output += f"{summary_text}\n\n"
    
    output += "## Key Points\n\n"
    
    output += "### Points of Agreement\n\n"
    for point in summary['key_agreements']:
        output += f"- {point}\n"
    output += "\n"
    
    output += "### Points of Disagreement\n\n"
    for point in summary['key_disagreements']:
        output += f"- {point}\n"
    output += "\n"
    
    if debate_state['consensus_reached']:
        output += "## Consensus\n\n"
        output += f"{debate_state['consensus_statement']}\n\n"
    
    output += "## Evidence Presented\n\n"
    for evidence in debate_state['evidence_presented']:
        output += f"### {evidence['type']}: {evidence['description']}\n\n"
        output += f"- **Presented by:** {evidence['presented_by']} (Round {evidence['presented_in_round']})\n"
        output += f"- **Strength:** {evidence['strength']}\n"
        if evidence['contested']:
            output += f"- **Contested by:** {evidence['contested_by']}\n"
            output += f"- **Contestation reason:** {evidence['contestation_reason']}\n"
        output += "\n"
    
    output += "## Analysis\n\n"
    
    output += "### Quality Assessment\n\n"
    qa = analysis['quality_assessment']
    output += "| Aspect | Score | Assessment |\n"
    output += "|--------|-------|------------|\n"
    output += f"| Evidence Quality | {qa['evidence_quality']['score']}/5.0 | {qa['evidence_quality']['explanation']} |\n"
    output += f"| Reasoning Quality | {qa['reasoning_quality']['score']}/5.0 | {qa['reasoning_quality']['explanation']} |\n"
    output += f"| Perspective Diversity | {qa['perspective_diversity']['score']}/5.0 | {qa['perspective_diversity']['explanation']} |\n"
    output += f"| Overall Quality | {qa['overall_quality']['score']}/5.0 | {qa['overall_quality']['explanation']} |\n\n"
    
    output += "### Cognitive Biases Identified\n\n"
    for bias in analysis['cognitive_biases']:
        output += f"- **{bias['bias']}:** {bias['description']}\n"
        output += f"  - Observed in: {', '.join(bias['observed_in'])}\n"
    output += "\n"
    
    output += "### Implications\n\n"
    for implication in analysis['implications']:
        output += f"- {implication}\n"
    
    return output
