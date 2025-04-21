# Recursive Loop Flow Implementation Documentation

## Overview

This document describes the implementation of the recursive loop flow logic in the Promethios backend. The system now has the capability to:

1. Automatically reflect after execution
2. Evaluate loop alignment and bias
3. Report back to the Orchestrator
4. Decide whether to rerun the loop or finalize it

## Components

### 1. Orchestrator Loop Complete Endpoint

**File**: `/app/routes/orchestrator_routes.py`

This endpoint accepts post-execution signals and kicks off the system reflection process:

```python
@router.post("/orchestrator/loop-complete")
async def loop_complete(request: LoopCompleteRequest):
    """
    Handle post-execution signals and kick off system reflection.
    """
    # Process loop reflection
    reflection_result = await process_loop_reflection(request.loop_id)
    
    # Evaluate whether to rerun the loop
    rerun_decision = await evaluate_rerun_decision(
        request.loop_id, 
        reflection_result["alignment_score"],
        reflection_result["drift_score"],
        reflection_result["summary_valid"]
    )
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "reflection_result": reflection_result,
        "rerun_decision": rerun_decision
    }
```

The endpoint triggers:
- `/run-critic`
- `/pessimist-check`
- `/ceo-review`
- `/drift-summary`

### 2. Post Loop Summary Handler

**File**: `/app/modules/post_loop_summary_handler.py`

This module:
- Gathers outputs from all reflection agents
- Calculates alignment scores, bias deltas, and identifies belief conflicts
- Writes summary to memory under `loop_summary[loop_id]`
- Returns a reflection result with alignment score, drift score, and validity assessment

Key function:
```python
async def process_loop_reflection(loop_id: str) -> Dict[str, Any]:
    """
    Process loop reflection by gathering outputs from all reflection agents.
    """
    # Call all reflection agents in parallel
    critic_result, pessimist_result, ceo_result, drift_result = await asyncio.gather(
        call_run_critic(loop_id),
        call_pessimist_check(loop_id),
        call_ceo_review(loop_id),
        call_drift_summary(loop_id)
    )
    
    # Calculate aggregate alignment score
    alignment_score = (critic_score * 0.3) + (pessimist_confidence * 0.2) + (ceo_alignment * 0.5)
    
    # Store the result in memory
    memory_key = f"loop_summary[{loop_id}]"
    await write_to_memory(memory_key, reflection_result)
    
    return {
        "alignment_score": reflection_result["alignment_score"],
        "drift_score": reflection_result["drift_score"],
        "summary_valid": reflection_result["summary_valid"]
    }
```

### 3. Rerun Decision Engine

**File**: `/app/modules/rerun_decision_engine.py`

This module:
- Evaluates whether to rerun a loop based on configurable thresholds
- Generates new loop IDs for reruns
- Creates new loop traces with rerun information
- Finalizes loops when no rerun is needed

Rerun conditions:
- `alignment_score < 0.75` → Trigger rerun
- `drift_score > 0.25` → Trigger rerun
- No issues → Mark loop as finalized

When rerunning:
- Increment loop ID: `loop_001_r1`
- Copy prior loop trace
- Pass `"depth": "deep"`

### 4. Loop Trace Schema

**File**: `/app/schemas/loop_trace.py`

The schema has been updated to include:
- `rerun_of`: Reference to the original loop ID
- `rerun_reason`: Why the loop was rerun
- `rerun_depth`: How many reruns deep
- `alignment_score`: Calculated alignment score
- `drift_score`: Calculated drift score
- `summary_valid`: Whether the summary is valid

## Flow Diagram

```
Loop Execution → /orchestrator/loop-complete → Process Reflection → Evaluate Rerun Decision
                                                      ↓                       ↓
                                              Call Reflection Agents    Check Thresholds
                                                      ↓                       ↓
                                              Calculate Scores      → Rerun or Finalize Loop
                                                      ↓                       ↓
                                              Store in Memory        Generate New Loop ID
```

## Testing

The implementation includes a test script (`/app/tests/test_recursive_loop_flow.py`) that tests:
- Loop reflection process
- Rerun decision logic with different alignment and drift scores
- Generation of new loop IDs for reruns

## Configuration

Rerun thresholds are configurable in the `rerun_decision_engine.py` module:
- `alignment_threshold`: 0.75
- `drift_threshold`: 0.25
- `max_reruns`: 3

## Integration

The new components are integrated into the main application in `app/main.py`, which includes the new orchestrator router.

## Future Improvements

1. Replace mock API calls with actual calls to reflection agents
2. Implement proper memory storage instead of mock functions
3. Add more comprehensive error handling
4. Create a configuration file for rerun thresholds
5. Add logging for better debugging and monitoring
