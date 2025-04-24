"""
SAGE Agent Module

This module provides the implementation for the SAGE agent,
which summarizes loop beliefs and logs structured belief maps.
"""
import logging
import traceback
import datetime
import json
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("agents.sage")

# Import memory functions if available
try:
    from app.modules.orchestrator_memory import write_memory
    memory_available = True
except ImportError:
    memory_available = False
    logger.warning("⚠️ Memory module not available, using mock implementation")
    
    # Mock implementation for testing
    async def write_memory(agent_id, memory_type, tag, value):
        logger.info(f"Mock memory write: {agent_id}, {memory_type}, {tag}, {len(str(value))} chars")
        return {"status": "success", "message": "Mock memory write successful"}

def run_sage_agent(project_id: str, task: str = None, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the SAGE agent to generate a system summary for the given project.
    
    This function can be called with just project_id or with additional parameters.
    
    Args:
        project_id: The project identifier
        task: The task to execute (optional)
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the summary or execution result
    """
    try:
        # Log the function call
        logger.info(f"Running SAGE agent for project: {project_id}")
        print(f"🟪 SAGE agent generating summary for {project_id}")
        
        # Initialize tools if None
        if tools is None:
            tools = []
        
        # Generate summary
        summary = f"This is a system-generated summary of recent activities for project {project_id}"
        
        # If task is provided, include it in the output
        if task:
            logger.info(f"SAGE agent executing task: {task}")
            print(f"🟩 SAGE agent executing task '{task}' on project '{project_id}'")
            return {
                "status": "success",
                "output": f"SAGE agent executed task '{task}'",
                "summary": summary,
                "task": task,
                "tools": tools,
                "project_id": project_id
            }
        else:
            # Return just the summary when called with only project_id
            return {
                "status": "success",
                "summary": summary,
                "project_id": project_id
            }
    except Exception as e:
        error_msg = f"Error running SAGE agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "task": task if task else "generate_summary",
            "tools": tools if tools else []
        }

async def review_loop_summary(loop_id: str, summary_text: str) -> Dict[str, Any]:
    """
    Review a loop summary to extract key beliefs and their confidence levels.
    
    This function analyzes the summary text to identify key beliefs,
    assigns confidence scores and emotional weights, and logs the results.
    
    Args:
        loop_id: Unique identifier for the loop
        summary_text: Summary text to analyze for beliefs
        
    Returns:
        Dict containing belief scores and reflection
    """
    try:
        logger.info(f"SAGE reviewing loop summary for loop: {loop_id}")
        print(f"🟪 SAGE agent analyzing beliefs for loop: {loop_id}")
        
        # Extract key beliefs from summary
        # In a real implementation, this would use more sophisticated NLP
        # For now, we'll use a simple approach to extract key points
        
        # Sample beliefs extraction logic
        beliefs = []
        
        # Split summary into sentences and analyze each one
        sentences = summary_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Simple heuristic: longer sentences likely contain beliefs
            if len(sentence) > 30:
                # Generate confidence based on sentence structure
                confidence = min(0.5 + (len(sentence) / 200), 0.95)
                
                # Simple sentiment analysis for emotional weight
                positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'improve', 'efficient']
                negative_words = ['bad', 'poor', 'negative', 'fail', 'issue', 'problem', 'error', 'slow']
                
                emotional_weight = 0.0
                for word in positive_words:
                    if word in sentence.lower():
                        emotional_weight += 0.2
                
                for word in negative_words:
                    if word in sentence.lower():
                        emotional_weight -= 0.2
                
                # Clamp emotional weight to [-1, 1]
                emotional_weight = max(-1.0, min(1.0, emotional_weight))
                
                # Add belief to list
                beliefs.append({
                    "belief": sentence,
                    "confidence": round(confidence, 2),
                    "emotional_weight": round(emotional_weight, 2) if emotional_weight != 0 else None
                })
        
        # If no beliefs were extracted, add a default one
        if not beliefs:
            beliefs.append({
                "belief": "Insufficient information to extract clear beliefs from summary",
                "confidence": 0.3,
                "emotional_weight": None
            })
        
        # Generate reflection based on beliefs
        reflection = generate_reflection(beliefs)
        
        # Prepare result
        result = {
            "belief_scores": beliefs,
            "reflection_text": reflection,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "loop_id": loop_id
        }
        
        # Log to memory if available
        if memory_available:
            memory_tag = f"sage_summary_{loop_id}"
            memory_result = await write_memory(
                agent_id="sage",
                memory_type="loop",
                tag=memory_tag,
                value=json.dumps(result)
            )
            logger.info(f"Memory write result: {memory_result}")
        else:
            logger.warning("Memory module not available, skipping memory write")
        
        return result
    
    except Exception as e:
        error_msg = f"Error in SAGE review: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "loop_id": loop_id
        }

def generate_reflection(beliefs: List[Dict[str, Any]]) -> str:
    """
    Generate a reflection based on the extracted beliefs.
    
    Args:
        beliefs: List of belief dictionaries with confidence and emotional weight
        
    Returns:
        Reflection text summarizing the beliefs
    """
    if not beliefs:
        return "No clear beliefs could be extracted from the summary."
    
    # Count beliefs by emotional weight
    positive_beliefs = [b for b in beliefs if b.get("emotional_weight", 0) > 0]
    negative_beliefs = [b for b in beliefs if b.get("emotional_weight", 0) < 0]
    neutral_beliefs = [b for b in beliefs if b.get("emotional_weight", 0) == 0 or b.get("emotional_weight") is None]
    
    # Sort beliefs by confidence
    high_confidence = [b for b in beliefs if b.get("confidence", 0) > 0.7]
    
    # Generate reflection
    reflection_parts = []
    
    # Overall tone
    if len(positive_beliefs) > len(negative_beliefs):
        reflection_parts.append("The summary suggests a generally positive outlook.")
    elif len(negative_beliefs) > len(positive_beliefs):
        reflection_parts.append("The summary suggests some concerns or challenges.")
    else:
        reflection_parts.append("The summary presents a balanced perspective.")
    
    # High confidence beliefs
    if high_confidence:
        reflection_parts.append(f"With high confidence, we can assert that: {high_confidence[0]['belief']}")
    
    # Additional insights
    if len(beliefs) > 1:
        reflection_parts.append(f"Additional insights include: {beliefs[1]['belief']}")
    
    # Recommendations based on emotional weight
    if negative_beliefs:
        reflection_parts.append("Areas that may need attention include addressing the negative aspects identified in the summary.")
    
    # Join all parts
    reflection = " ".join(reflection_parts)
    
    return reflection
