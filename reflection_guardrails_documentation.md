# Reflection Guardrails Implementation Documentation

## Overview

This document provides comprehensive documentation for the Reflection Guardrails implementation in the Promethios backend. The guardrails system prevents endless reruns, detects bias echo patterns, tracks reflection fatigue, and ensures loops know when to stop thinking.

## Components

The Reflection Guardrails system consists of the following components:

1. **Loop Trace Schema** - Updated schema with fields for rerun limits, bias tracking, fatigue scoring, and reasoning
2. **Rerun Limit Enforcement** - Prevents loops from rerunning indefinitely
3. **Bias Echo Filter** - Detects when the same biases are repeatedly flagged
4. **Reflection Fatigue Scoring** - Tracks fatigue when loops rerun without improvement
5. **Rerun Reasoning Logger** - Adds metadata about what triggered reruns
6. **Integration Module** - Coordinates all components into a cohesive system

## Implementation Details

### 1. Loop Trace Schema

The loop trace schema has been updated to include the following fields:

```python
class LoopTraceItem(BaseModel):
    # Existing fields
    loop_id: str
    status: str
    timestamp: datetime
    
    # Rerun tracking fields
    rerun_of: Optional[str] = None
    rerun_depth: Optional[int] = None
    rerun_count: Optional[int] = 0
    max_reruns: Optional[int] = 3
    
    # Bias tracking fields
    bias_echo: Optional[bool] = False
    repeated_tags: Optional[List[str]] = None
    
    # Fatigue tracking fields
    reflection_fatigue: Optional[float] = 0.0
    fatigue_increased: Optional[bool] = False
    
    # Reasoning fields
    rerun_reason: Optional[str] = None
    rerun_reason_detail: Optional[str] = None
    rerun_trigger: Optional[List[str]] = None
    
    # Override fields
    force_finalize: Optional[bool] = False
    overridden_by: Optional[str] = None
    
    # Persona fields
    orchestrator_persona: Optional[str] = None
    reflection_persona: Optional[str] = None
```

### 2. Rerun Limit Enforcement

The rerun limit enforcement component tracks how many times a loop has rerun and prevents further reruns when the limit is reached:

```python
async def enforce_rerun_limits(
    loop_id: str,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None
) -> Dict[str, Any]:
    # Get the total rerun count for this loop family
    total_reruns = await get_total_rerun_count(loop_id)
    
    # Get the max reruns limit
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    max_reruns = RERUN_CONFIG["max_reruns"]
    if trace and "max_reruns" in trace:
        max_reruns = trace["max_reruns"]
    
    # Check if we've hit the limit
    limit_reached = total_reruns >= max_reruns
    
    # Apply override if provided
    force_finalize = limit_reached and not override_max_reruns
    
    # Update the trace with the latest rerun count and limit status
    if trace:
        trace["rerun_count"] = total_reruns
        trace["max_reruns"] = max_reruns
        trace["force_finalize"] = force_finalize
        
        if override_max_reruns and limit_reached:
            trace["overridden_by"] = override_by
        
        await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return {
        "rerun_count": total_reruns,
        "max_reruns": max_reruns,
        "limit_reached": limit_reached,
        "force_finalize": force_finalize,
        "overridden": override_max_reruns and limit_reached,
        "overridden_by": override_by if override_max_reruns and limit_reached else None
    }
```

### 3. Bias Echo Filter

The bias echo filter detects when the PESSIMIST agent flags the same bias tags repeatedly:

```python
async def detect_bias_repetition(
    loop_id: str,
    bias_tags: List[Dict[str, Any]],
    threshold: int = 3
) -> Dict[str, Any]:
    # Get the global bias history
    bias_history = await get_bias_history()
    
    # Update the loop-specific bias tags
    loop_bias_tags = await update_loop_bias_tags(loop_id, bias_tags)
    
    # Update the global bias history
    bias_history = await update_bias_history(loop_id, bias_tags)
    
    # Check for repetition patterns
    repeated_tags = []
    repetition_counts = {}
    
    for bias_tag_obj in bias_tags:
        tag = bias_tag_obj["tag"]
        
        # Get the history for this tag
        tag_history = bias_history.get(tag, {})
        occurrences = tag_history.get("occurrences", 0)
        
        repetition_counts[tag] = occurrences
        
        if occurrences >= threshold:
            repeated_tags.append(tag)
    
    # Determine if bias repetition is present
    bias_repetition = len(repeated_tags) > 0
    
    return {
        "bias_repetition": bias_repetition,
        "repeated_tags": repeated_tags,
        "repetition_counts": repetition_counts,
        "threshold": threshold,
        "bias_echo": bias_repetition,
        "trigger": "pessimist" if bias_repetition else None,
        "action": "halt_loop" if bias_repetition else None
    }
```

### 4. Reflection Fatigue Scoring

The reflection fatigue scoring component tracks fatigue when loops rerun without improving:

```python
async def calculate_fatigue_score(
    loop_id: str,
    alignment_score: float,
    drift_score: float,
    previous_fatigue: Optional[float] = None
) -> Dict[str, Any]:
    # Get the previous loop trace
    previous_trace = await get_previous_loop_trace(loop_id)
    
    # Initialize fatigue variables
    base_fatigue = previous_fatigue if previous_fatigue is not None else 0.0
    fatigue_increment = 0.0
    fatigue_increased = False
    improvement_detected = False
    
    # If this is a rerun, calculate improvement and fatigue
    if previous_trace:
        # Calculate improvements
        alignment_improvement = calculate_improvement(
            alignment_score, 
            previous_trace.get("alignment_score", 0.0),
            is_alignment=True
        )
        
        drift_improvement = calculate_improvement(
            drift_score, 
            previous_trace.get("drift_score", 1.0),
            is_alignment=False
        )
        
        # Check if there was meaningful improvement
        alignment_improved = alignment_improvement >= FATIGUE_CONFIG["improvement_threshold"]
        drift_improved = drift_improvement >= FATIGUE_CONFIG["improvement_threshold"]
        improvement_detected = alignment_improved or drift_improved
        
        # Calculate fatigue increment
        if not improvement_detected:
            # No improvement, increase fatigue
            fatigue_increment = FATIGUE_CONFIG["base_increment"]
            fatigue_increased = True
        else:
            # Improvement detected, apply decay
            fatigue_increment = -FATIGUE_CONFIG["decay_rate"]
            fatigue_increased = False
    
    # Calculate the new fatigue score
    new_fatigue = max(0.0, min(FATIGUE_CONFIG["max_fatigue"], base_fatigue + fatigue_increment))
    
    # Check if we've exceeded the critical threshold
    threshold_exceeded = new_fatigue >= FATIGUE_CONFIG["critical_threshold"]
    
    return {
        "reflection_fatigue": new_fatigue,
        "previous_fatigue": base_fatigue,
        "fatigue_increment": fatigue_increment,
        "fatigue_increased": fatigue_increased,
        "improvement_detected": improvement_detected,
        "threshold_exceeded": threshold_exceeded,
        "critical_threshold": FATIGUE_CONFIG["critical_threshold"],
        "force_finalize": threshold_exceeded
    }
```

### 5. Rerun Reasoning Logger

The rerun reasoning logger adds metadata about what triggered reruns:

```python
async def log_rerun_reasoning(
    loop_id: str,
    rerun_trigger: List[str],
    rerun_reason: str,
    rerun_reason_detail: Optional[str] = None,
    overridden_by: Optional[str] = None,
    reflection_persona: Optional[str] = None
) -> Dict[str, Any]:
    # Create the reasoning metadata
    reasoning = {
        "rerun_trigger": rerun_trigger,
        "rerun_reason": rerun_reason,
        "rerun_reason_detail": rerun_reason_detail or f"Triggered by {', '.join(rerun_trigger)}",
        "timestamp": datetime.utcnow().isoformat(),
        "reflection_persona": reflection_persona
    }
    
    # Add override information if applicable
    if overridden_by:
        reasoning["overridden_by"] = overridden_by
    
    # Get the current loop trace
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if trace:
        # Update the trace with the reasoning information
        trace["rerun_trigger"] = rerun_trigger
        trace["rerun_reason"] = rerun_reason
        trace["rerun_reason_detail"] = reasoning["rerun_reason_detail"]
        
        if overridden_by:
            trace["overridden_by"] = overridden_by
        
        if reflection_persona:
            trace["reflection_persona"] = reflection_persona
        
        # Write the updated trace back to memory
        await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    # Also store the reasoning in a dedicated location for easier retrieval
    await write_to_memory(f"rerun_reasoning[{loop_id}]", reasoning)
    
    return reasoning
```

### 6. Integration Module

The integration module coordinates all components into a cohesive system:

```python
async def process_loop_completion(
    loop_id: str,
    reflection_status: str,
    orchestrator_persona: Optional[str] = None,
    override_fatigue: bool = False,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None
) -> Dict[str, Any]:
    # Validate reflection status
    if reflection_status != "done":
        return {
            "status": "error",
            "message": "Invalid reflection status. Must be 'done'.",
            "loop_id": loop_id
        }
    
    # Process loop reflection
    reflection_result = await process_loop_reflection(
        loop_id,
        override_fatigue,
        override_max_reruns,
        override_by
    )
    
    # Extract bias tags for tracking
    bias_tags = []
    if "agent_results" in reflection_result and "pessimist" in reflection_result["agent_results"]:
        pessimist_result = reflection_result["agent_results"]["pessimist"]
        if "bias_analysis" in pessimist_result and "bias_tags_detail" in pessimist_result["bias_analysis"]:
            bias_tags = pessimist_result["bias_analysis"]["bias_tags_detail"]
    
    # Track bias if tags are available
    if bias_tags:
        bias_tracking_result = await track_bias(loop_id, bias_tags)
        
        # Update reflection result with bias tracking information
        reflection_result["bias_echo"] = bias_tracking_result["bias_echo"]
        reflection_result["repeated_tags"] = bias_tracking_result["repeated_tags"]
        reflection_result["repetition_counts"] = bias_tracking_result["repetition_counts"]
    
    # Make rerun decision
    decision_result = await make_rerun_decision(
        loop_id,
        override_fatigue,
        override_max_reruns,
        override_by
    )
    
    # Create the complete result
    result = {
        "status": "success",
        "loop_id": loop_id,
        "reflection_result": reflection_result,
        "decision_result": decision_result,
        "orchestrator_persona": orchestrator_persona or reflection_result.get("reflection_persona"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store the complete result
    await write_to_memory(f"loop_completion[{loop_id}]", result)
    
    return result
```

## API Endpoints

The Reflection Guardrails system exposes the following API endpoints:

### 1. POST /orchestrator/loop-complete

This endpoint processes a loop completion event with all reflection guardrails.

**Request:**
```json
{
  "loop_id": "loop_001",
  "reflection_status": "done",
  "orchestrator_persona": "SAGE",
  "override_fatigue": false,
  "override_max_reruns": false,
  "override_by": null
}
```

**Response:**
```json
{
  "status": "success",
  "loop_id": "loop_001",
  "reflection_result": {
    "alignment_score": 0.72,
    "drift_score": 0.28,
    "summary_valid": true,
    "reflection_persona": "SAGE",
    "bias_echo": false,
    "reflection_fatigue": 0.15
  },
  "decision_result": {
    "decision": "rerun",
    "original_loop_id": "loop_001",
    "new_loop_id": "loop_001_r1",
    "rerun_reason": "alignment_threshold_not_met",
    "rerun_number": 1,
    "rerun_count": 1,
    "max_reruns": 3
  },
  "orchestrator_persona": "SAGE",
  "timestamp": "2025-04-21T19:45:00.000Z"
}
```

### 2. GET /orchestrator/guardrails-status/{loop_id}

This endpoint gets the current status of all reflection guardrails for a loop.

**Response:**
```json
{
  "status": "success",
  "guardrails_status": {
    "loop_id": "loop_001",
    "rerun_count": 1,
    "max_reruns": 3,
    "rerun_limit_reached": false,
    "bias_echo": false,
    "reflection_fatigue": 0.15,
    "fatigue_threshold_exceeded": false,
    "force_finalize": false,
    "rerun_reason": "alignment_threshold_not_met",
    "rerun_trigger": ["alignment", "drift"],
    "alignment_score": 0.72,
    "drift_score": 0.28,
    "summary_valid": true,
    "reflection_persona": "SAGE"
  }
}
```

### 3. POST /orchestrator/override-guardrails/{loop_id}

This endpoint overrides reflection guardrails for a loop.

**Request:**
```json
{
  "override_fatigue": true,
  "override_max_reruns": false,
  "override_by": "operator",
  "override_reason": "Manual override to continue exploration"
}
```

**Response:**
```json
{
  "status": "success",
  "loop_id": "loop_001",
  "override_fatigue": true,
  "override_max_reruns": false,
  "overridden_by": "operator",
  "override_reason": "Manual override to continue exploration"
}
```

## Configuration

The Reflection Guardrails system uses the following configuration parameters:

### Rerun Decision Engine

```python
RERUN_CONFIG = {
    "alignment_threshold": 0.75,  # Minimum alignment score to avoid rerun
    "drift_threshold": 0.25,      # Maximum drift score to avoid rerun
    "max_reruns": 3,              # Maximum number of reruns for a single loop
    "fatigue_threshold": 0.5,     # Maximum fatigue score to allow reruns
    "bias_repetition_threshold": 3  # Number of repetitions to trigger bias echo detection
}
```

### Reflection Fatigue Scoring

```python
FATIGUE_CONFIG = {
    "base_increment": 0.15,           # Base fatigue increase per rerun
    "improvement_threshold": 0.05,    # Minimum improvement to avoid fatigue
    "decay_rate": 0.05,               # Rate at which fatigue decays over time
    "critical_threshold": 0.5,        # Threshold at which to force finalization
    "max_fatigue": 1.0                # Maximum possible fatigue score
}
```

## Testing

The Reflection Guardrails system includes comprehensive tests to ensure all components work correctly:

1. **process_loop_completion** - Tests the main entry point with default parameters
2. **process_loop_completion_with_overrides** - Tests overriding fatigue and rerun limits
3. **get_guardrails_status** - Tests retrieving the current guardrails status
4. **override_guardrails** - Tests manually overriding guardrails
5. **bias_echo_detection** - Tests detecting repeated bias patterns
6. **reflection_fatigue_scoring** - Tests fatigue calculation and threshold detection

## Usage Examples

### Basic Loop Completion

```python
result = await process_loop_completion(
    loop_id="loop_001",
    reflection_status="done",
    orchestrator_persona="SAGE"
)

if result["decision_result"]["decision"] == "rerun":
    new_loop_id = result["decision_result"]["new_loop_id"]
    print(f"Loop will be rerun as {new_loop_id}")
else:
    print("Loop has been finalized")
```

### Overriding Guardrails

```python
# Override fatigue-based finalization
result = await process_loop_completion(
    loop_id="loop_001",
    reflection_status="done",
    orchestrator_persona="SAGE",
    override_fatigue=True,
    override_by="operator"
)

# Check the guardrails status
status = await get_guardrails_status("loop_001")
print(f"Fatigue: {status['guardrails_status']['reflection_fatigue']}")
print(f"Force finalize: {status['guardrails_status']['force_finalize']}")
```

## Conclusion

The Reflection Guardrails system provides a comprehensive safety layer to prevent endless reruns and ensure loops know when to stop thinking. By tracking rerun limits, detecting bias echo patterns, monitoring reflection fatigue, and logging detailed reasoning, the system ensures that Promethios can reflect on its execution without getting stuck in unproductive loops.
