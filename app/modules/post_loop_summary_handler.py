"""
Post Loop Summary Handler Module

This module is responsible for gathering outputs from all reflection agents,
calculating alignment and bias scores, and storing the results in memory.

It now includes:
- Reflection guardrails (rerun limit, bias echo, fatigue scoring, rerun reasoning)
- Responsible Cognition Layer (safety architecture) integration
"""

from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
from app.utils.persona_utils import get_current_persona
from app.modules.pessimist_agent import pessimist_check
from app.modules.reflection_fatigue_scoring import process_reflection_fatigue
from app.modules.rerun_reasoning_logger import log_rerun_reasoning, log_finalization_reasoning, add_reasoning_to_summary
from app.modules.safety_integration import run_safety_checks, get_consolidated_memory_fields, should_trigger_rerun, get_rerun_configuration, get_reflection_prompts

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
    
    # Get the loop summary for analysis
    summary = await read_from_memory(f"loop_summary_text[{loop_id}]") or "Default summary text"
    
    # Call the pessimist agent to check for bias
    return await pessimist_check(loop_id, summary)

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

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "loop_summary_text[loop_001]":
        return "This is a summary of loop_001's execution and findings."
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

async def process_loop_reflection(
    loop_id: str,
    override_fatigue: bool = False,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None,
    safety_checks: List[str] = ["all"],
    override_safety_blocks: bool = False
) -> Dict[str, Any]:
    """
    Process loop reflection by gathering outputs from all reflection agents.
    
    This function:
    1. Runs safety checks on prompt and output
    2. Calls all reflection agents (critic, pessimist, CEO, drift)
    3. Aggregates their outputs
    4. Calculates alignment score, bias delta, and belief conflict flags
    5. Checks for bias echo patterns
    6. Calculates reflection fatigue
    7. Stores the result to memory with rerun reasoning
    8. Returns the reflection result
    
    Args:
        loop_id: The ID of the loop to process
        override_fatigue: Whether to override fatigue-based finalization
        override_max_reruns: Whether to override max reruns limit
        override_by: Who performed the override
        safety_checks: List of safety checks to run
        override_safety_blocks: Whether to override safety blocks
        
    Returns:
        Dict containing the reflection result with alignment_score, drift_score, and summary_valid
    """
    # Get the current persona for this loop
    persona = get_current_persona(loop_id)
    
    # Get the prompt and output for safety checks
    prompt = await read_from_memory(f"loop_prompt[{loop_id}]") or ""
    output = await read_from_memory(f"loop_output[{loop_id}]") or ""
    
    # Run safety checks
    safety_results = await run_safety_checks(
        loop_id,
        prompt,
        output,
        safety_checks,
        override_safety_blocks,
        override_by if override_safety_blocks else None
    )
    
    # Get safety memory fields
    safety_memory_fields = get_consolidated_memory_fields(safety_results)
    
    # Check if safety checks should trigger a rerun
    safety_rerun = should_trigger_rerun(safety_results)
    safety_rerun_config = get_rerun_configuration(safety_results) if safety_rerun else {}
    
    # Get reflection prompts for safety issues
    safety_reflection_prompts = get_reflection_prompts(safety_results)
    
    # Call all reflection agents in parallel with persona context
    critic_result, pessimist_result, ceo_result, drift_result = await asyncio.gather(
        call_run_critic(loop_id, persona),
        call_pessimist_check(loop_id, persona),
        call_ceo_review(loop_id, persona),
        call_drift_summary(loop_id, persona)
    )
    
    # Extract relevant scores
    critic_score = critic_result["critique"]["overall_score"]
    
    # Extract pessimist data including bias echo detection
    pessimist_confidence = 0.65  # Default value
    bias_echo = False
    bias_tags = []
    bias_repetition_count = {}
    
    if "bias_analysis" in pessimist_result:
        bias_analysis = pessimist_result["bias_analysis"]
        # Add type safety checks for bias_analysis
        if isinstance(bias_analysis, dict):
            bias_echo = bias_analysis.get("bias_echo", False)
            bias_tags = bias_analysis.get("bias_tags", [])
            bias_repetition_count = bias_analysis.get("repetition_counts", {})
    
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
    
    # Process reflection fatigue
    fatigue_result = await process_reflection_fatigue(
        loop_id,
        alignment_score,
        drift_score,
        override_fatigue
    )
    
    # Add type safety check for fatigue_result
    threshold_exceeded = False
    if isinstance(fatigue_result, dict):
        threshold_exceeded = fatigue_result.get("threshold_exceeded", False)
    
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
        },
        # Add guardrail information
        "bias_echo": bias_echo,
        "bias_tags": bias_tags,
        "bias_repetition_count": bias_repetition_count,
        "reflection_fatigue": fatigue_result["reflection_fatigue"] if isinstance(fatigue_result, dict) else 0.0,
        "fatigue_increased": fatigue_result["fatigue_increased"] if isinstance(fatigue_result, dict) else False,
        "threshold_exceeded": threshold_exceeded,
        # Add safety information
        **safety_memory_fields
    }
    
    # Determine rerun triggers
    rerun_trigger = []
    if alignment_score < 0.75:
        rerun_trigger.append("alignment")
    if drift_score > 0.25:
        rerun_trigger.append("drift")
    if not summary_valid:
        rerun_trigger.append("validity")
    if bias_echo:
        rerun_trigger.append("pessimist")
    
    # Add safety rerun triggers if any
    if safety_rerun:
        rerun_trigger.extend(safety_rerun_config.get("rerun_trigger", []))
    
    # Determine rerun reason
    rerun_reason = None
    if safety_rerun:
        rerun_reason = safety_rerun_config.get("rerun_reason")
    elif bias_echo:
        rerun_reason = "bias_echo_detected"
    elif threshold_exceeded and not override_fatigue:
        rerun_reason = "fatigue_threshold_exceeded"
    elif not summary_valid:
        rerun_reason = "summary_invalid"
    elif alignment_score < 0.75:
        rerun_reason = "alignment_threshold_not_met"
    elif drift_score > 0.25:
        rerun_reason = "drift_threshold_exceeded"
    
    # Add rerun reasoning to the result
    if rerun_reason:
        rerun_reasoning = await log_rerun_reasoning(
            loop_id,
            rerun_trigger,
            rerun_reason,
            safety_rerun_config.get("rerun_reason_detail", f"Triggered by {', '.join(rerun_trigger)}"),
            override_by if override_fatigue or override_max_reruns or override_safety_blocks else None,
            persona
        )
        reflection_result["rerun_reasoning"] = rerun_reasoning
    else:
        # Log finalization reasoning
        finalize_reasoning = await log_finalization_reasoning(
            loop_id,
            "no_issues_detected",
            [],
            "All metrics within acceptable thresholds",
            persona
        )
        reflection_result["finalize_reasoning"] = finalize_reasoning
    
    # Store the result in memory
    memory_key = f"loop_summary[{loop_id}]"
    await write_to_memory(memory_key, reflection_result)
    
    # Add reasoning to the summary
    if rerun_reason:
        await add_reasoning_to_summary(
            loop_id,
            memory_key,
            "rerun",
            reflection_result["rerun_reasoning"]
        )
    else:
        await add_reasoning_to_summary(
            loop_id,
            memory_key,
            "finalize",
            reflection_result["finalize_reasoning"]
        )
    
    # Add safety reflection prompts to the summary if any
    if safety_reflection_prompts:
        for component, prompt in safety_reflection_prompts.items():
            await write_to_memory(f"safety_reflection_prompt[{loop_id}][{component}]", prompt)
    
    return {
        "alignment_score": reflection_result["alignment_score"],
        "drift_score": reflection_result["drift_score"],
        "summary_valid": reflection_result["summary_valid"],
        "reflection_persona": reflection_result["reflection_persona"],
        "bias_echo": reflection_result["bias_echo"],
        "reflection_fatigue": reflection_result["reflection_fatigue"],
        "rerun_trigger": rerun_trigger if rerun_trigger else None,
        "rerun_reason": rerun_reason,
        "safety_checks_performed": safety_memory_fields.get("safety_checks_performed", []),
        "safety_blocks_triggered": safety_memory_fields.get("safety_blocks_triggered", []),
        "safety_warnings_issued": safety_memory_fields.get("safety_warnings_issued", [])
    }
