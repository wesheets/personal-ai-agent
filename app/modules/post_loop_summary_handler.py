"""
Post Loop Summary Handler Module

This module is responsible for gathering outputs from all reflection agents,
calculating alignment and bias scores, and storing the results in memory.
"""

from typing import Dict, Any, List, Optional
import json
import asyncio
from app.utils.persona_utils import get_current_persona

# Mock functions for API calls to reflection agents
# In a real implementation, these would make actual API calls
async def call_run_critic(loop_id: str, persona: str) -> Dict[str, Any]:
    """Call the run-critic endpoint to get critic feedback."""
    # Simulate API call
    await asyncio.sleep(0.1)
    return {
        "loop_id": loop_id,
        "reflection_persona": persona,
        "critique": {
            "strengths": ["Thorough analysis", "Clear reasoning"],
            "weaknesses": ["Could consider more edge cases"],
            "overall_score": 0.85
        }
    }

async def call_pessimist_check(loop_id: str, persona: str) -> Dict[str, Any]:
    """Call the pessimist-check endpoint to get pessimistic evaluation."""
    # Simulate API call
    await asyncio.sleep(0.1)
    return {
        "loop_id": loop_id,
        "reflection_persona": persona,
        "pessimist_view": {
            "concerns": ["Potential bias in data sources", "Limited scope"],
            "risk_assessment": "medium",
            "confidence_score": 0.65
        }
    }

async def call_ceo_review(loop_id: str, persona: str) -> Dict[str, Any]:
    """Call the ceo-review endpoint to get executive perspective."""
    # Simulate API call
    await asyncio.sleep(0.1)
    return {
        "loop_id": loop_id,
        "reflection_persona": persona,
        "executive_review": {
            "strategic_alignment": "high",
            "business_impact": "positive",
            "recommendation": "proceed",
            "alignment_score": 0.78
        }
    }

async def call_drift_summary(loop_id: str, persona: str) -> Dict[str, Any]:
    """Call the drift-summary endpoint to get drift analysis."""
    # Simulate API call
    await asyncio.sleep(0.1)
    return {
        "loop_id": loop_id,
        "reflection_persona": persona,
        "drift_analysis": {
            "drift_detected": "minor",
            "drift_score": 0.26,
            "areas": ["knowledge application", "reasoning approach"],
            "recommendation": "monitor"
        }
    }

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

async def process_loop_reflection(loop_id: str) -> Dict[str, Any]:
    """
    Process loop reflection by gathering outputs from all reflection agents.
    
    This function:
    1. Calls all reflection agents (critic, pessimist, CEO, drift)
    2. Aggregates their outputs
    3. Calculates alignment score, bias delta, and belief conflict flags
    4. Stores the result to memory
    5. Returns the reflection result
    
    Args:
        loop_id: The ID of the loop to process
        
    Returns:
        Dict containing the reflection result with alignment_score, drift_score, and summary_valid
    """
    # Get the current persona for this loop
    persona = get_current_persona(loop_id)
    
    # Call all reflection agents in parallel with persona context
    critic_result, pessimist_result, ceo_result, drift_result = await asyncio.gather(
        call_run_critic(loop_id, persona),
        call_pessimist_check(loop_id, persona),
        call_ceo_review(loop_id, persona),
        call_drift_summary(loop_id, persona)
    )
    
    # Extract relevant scores
    critic_score = critic_result["critique"]["overall_score"]
    pessimist_confidence = pessimist_result["pessimist_view"]["confidence_score"]
    ceo_alignment = ceo_result["executive_review"]["alignment_score"]
    drift_score = drift_result["drift_analysis"]["drift_score"]
    
    # Calculate aggregate alignment score (weighted average)
    alignment_score = (critic_score * 0.3) + (pessimist_confidence * 0.2) + (ceo_alignment * 0.5)
    
    # Determine if there are any belief conflicts
    belief_conflict_flags = []
    
    if critic_score > 0.8 and pessimist_confidence < 0.6:
        belief_conflict_flags.append("critic_pessimist_disagreement")
    
    if ceo_alignment > 0.8 and drift_score > 0.3:
        belief_conflict_flags.append("alignment_drift_conflict")
    
    # Determine if summary is valid
    summary_valid = alignment_score >= 0.7 and drift_score <= 0.3 and len(belief_conflict_flags) == 0
    
    # Create the reflection result
    reflection_result = {
        "alignment_score": round(alignment_score, 2),
        "drift_score": drift_score,
        "summary_valid": summary_valid,
        "belief_conflict_flags": belief_conflict_flags,
        "reflection_persona": persona,  # Include persona in reflection result
        "agent_results": {
            "critic": critic_result,
            "pessimist": pessimist_result,
            "ceo": ceo_result,
            "drift": drift_result
        }
    }
    
    # Store the result in memory
    memory_key = f"loop_summary[{loop_id}]"
    await write_to_memory(memory_key, reflection_result)
    
    return {
        "alignment_score": reflection_result["alignment_score"],
        "drift_score": reflection_result["drift_score"],
        "summary_valid": reflection_result["summary_valid"],
        "reflection_persona": reflection_result["reflection_persona"]  # Include persona in return value
    }
