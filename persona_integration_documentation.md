# Persona Integration Documentation

## Overview

This document describes the implementation of persona integration throughout the Promethios backend. The system now has the capability to:

1. Switch between different personas for loop execution
2. Track persona context in all loop phases
3. Auto-attach persona to loop traces
4. Preload persona for deep loops
5. Include persona information in reflection results

## Components

### 1. Persona Routes

**File**: `/app/routes/persona_routes.py`

#### `/persona/switch` Endpoint

This endpoint allows switching the active persona for a specific loop:

```python
@router.post("/persona/switch")
async def switch_persona(request: PersonaSwitchRequest):
    """
    Change active persona for a specific loop.
    """
    # Validate persona against allowed list
    if request.persona not in VALID_PERSONAS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid persona. Must be one of: {', '.join(VALID_PERSONAS)}"
        )
    
    # Write to memory
    persona_state = {
        "loop_id": request.loop_id,
        "orchestrator_persona": request.persona,
        "switched_by": "operator",
        "operator_id": request.operator_id,
        "timestamp": timestamp,
        "persona_switch_reason": "manual"
    }
    
    # Update memory with persona state
    update_project_memory(request.loop_id, "orchestrator_persona", request.persona)
    # ...
```

#### `/persona/current` Endpoint

This endpoint returns the current persona for a specific loop or the system default:

```python
@router.get("/persona/current")
async def get_current_persona(loop_id: Optional[str] = None):
    """
    Return current orchestrator_persona for the specified loop or the system default.
    """
    current_persona = "SAGE"  # Default persona
    
    if loop_id:
        try:
            # Try to get the current persona from memory for the specified loop
            loop_trace = get_project_memory(loop_id)
            if "orchestrator_persona" in loop_trace:
                current_persona = loop_trace["orchestrator_persona"]
        except KeyError:
            # If loop doesn't exist in memory, use default
            pass
    
    # ...
```

### 2. Loop Trace Schema

**File**: `/app/schemas/loop_trace.py`

The schema has been updated to include persona-related fields:

```python
class LoopTraceItem(BaseModel):
    # ...
    
    # Fields for persona tracking
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Active persona during loop execution")
    persona_switch_reason: Optional[str] = Field(default="default", description="Reason for persona selection")
    reflection_persona: Optional[str] = None

class LoopReflectionResult(BaseModel):
    # ...
    reflection_persona: Optional[str] = Field(default="SAGE", description="Persona used for reflection")

class LoopCompleteRequest(BaseModel):
    # ...
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Persona to use for reflection")

class RerunDecision(BaseModel):
    # ...
    orchestrator_persona: Optional[str] = Field(default="SAGE", description="Persona to use for rerun")
```

### 3. Persona Utilities

**File**: `/app/utils/persona_utils.py`

This module provides utility functions for persona validation and management:

```python
# Define valid personas
VALID_PERSONAS = ["SAGE", "ARCHITECT", "RESEARCHER", "RITUALIST", "INVENTOR"]

def validate_persona(persona: str) -> bool:
    """
    Validate if a persona is in the allowed list.
    """
    return persona in VALID_PERSONAS

def get_current_persona(loop_id: Optional[str] = None) -> str:
    """
    Get the current persona for a specific loop or the default.
    """
    # ...

def set_persona_for_loop(loop_id: str, persona: str, reason: str = "auto") -> bool:
    """
    Set the persona for a specific loop.
    """
    # ...

def preload_persona_for_deep_loop(loop_id: str, rerun_depth: int) -> str:
    """
    Preload persona for a deep loop.
    
    If no persona is set and depth is "deep" (rerun_depth > 0),
    default to SAGE.
    """
    # ...
```

### 4. Loop-Critical Routes

**File**: `/app/routes/agent_routes.py`

All loop-critical routes have been updated to accept and return persona context:

```python
@router.post("/analyze-prompt")
async def analyze_prompt(data: Dict[str, Any]):
    """
    Thought Partner prompt analysis.
    """
    # ...
    
    # Get the current persona for this loop
    orchestrator_persona = data.get("orchestrator_persona")
    if not orchestrator_persona:
        orchestrator_persona = get_current_persona(loop_id)
    
    # ...
    return {
        # ...
        "orchestrator_persona": orchestrator_persona,
        "status": "success"
    }
```

Similar updates have been made to:
- `/generate-variants`
- `/plan-and-execute`
- `/run-critic`
- `/pessimist-check`
- `/ceo-review`
- `/drift-summary`

### 5. Post Loop Summary Handler

**File**: `/app/modules/post_loop_summary_handler.py`

The post loop summary handler now includes persona context in reflection results:

```python
async def process_loop_reflection(loop_id: str) -> Dict[str, Any]:
    """
    Process loop reflection by gathering outputs from all reflection agents.
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
    
    # ...
    
    # Create the reflection result
    reflection_result = {
        # ...
        "reflection_persona": persona,  # Include persona in reflection result
        # ...
    }
    
    # ...
    
    return {
        # ...
        "reflection_persona": reflection_result["reflection_persona"]  # Include persona in return value
    }
```

### 6. Rerun Decision Engine

**File**: `/app/modules/rerun_decision_engine.py`

The rerun decision engine now preloads persona for deep loops:

```python
async def evaluate_rerun_decision(
    loop_id: str, 
    alignment_score: float, 
    drift_score: float,
    summary_valid: bool
) -> Dict[str, Any]:
    """
    Evaluate whether to rerun a loop based on alignment and drift scores.
    """
    # ...
    
    # If rerun is needed, prepare the new loop
    if rerun_needed:
        # ...
        
        if current_trace:
            # Get the current persona or preload for deep loop
            orchestrator_persona = preload_persona_for_deep_loop(loop_id, current_rerun_num + 1)
            
            # Create a new trace for the rerun
            new_trace = {
                # ...
                "orchestrator_persona": orchestrator_persona,  # Include persona in rerun
                # ...
            }
            
            # ...
            
            return {
                # ...
                "orchestrator_persona": orchestrator_persona  # Include persona in response
            }
    
    # ...
    
    return {
        # ...
        "orchestrator_persona": orchestrator_persona  # Include persona in response
    }
```

### 7. Orchestrator Routes

**File**: `/app/routes/orchestrator_routes.py`

The orchestrator routes now include persona context:

```python
@router.post("/orchestrator/loop-complete")
async def loop_complete(request: LoopCompleteRequest):
    """
    Handle post-execution signals and kick off system reflection.
    """
    # ...
    
    # Get the current persona for this loop if not provided
    orchestrator_persona = request.orchestrator_persona
    if not orchestrator_persona:
        orchestrator_persona = get_current_persona(request.loop_id)
    
    # ...
    
    return {
        # ...
        "orchestrator_persona": orchestrator_persona,
        # ...
    }
```

## Flow Diagram

```
Operator → /persona/switch → Set Persona in Memory
                                   ↓
Loop Execution → Loop-Critical Routes → Include Persona in Responses
                                   ↓
                        Store Persona in Loop Trace
                                   ↓
Loop Complete → Reflection Agents → Include Persona in Reflection
                                   ↓
                  Rerun Decision → Preload Persona for Deep Loops
```

## Testing

The implementation includes a test script (`/app/tests/test_persona_integration.py`) that tests:
- Persona validation
- Persona memory operations
- Persona preloading for deep loops
- Complete persona integration flow

## Configuration

Valid personas are defined in the `persona_utils.py` module:
- `SAGE`
- `ARCHITECT`
- `RESEARCHER`
- `RITUALIST`
- `INVENTOR`

## Benefits

This implementation provides several key benefits:

1. **No more chasing flags**: Persona context is automatically tracked throughout the system
2. **No retrofitting personas into memory**: Every loop has persona context from the beginning
3. **Identity-aware loops**: Every loop knows which persona it's using
4. **Perspective-based thinking**: Promethios can now think from different perspectives
5. **Alignment as architecture**: The system is designed with alignment built in

## Future Improvements

1. Implement persona-specific reflection strategies
2. Add persona switching based on task complexity
3. Create a persona history view for tracking persona usage over time
4. Implement persona-specific memory retrieval
5. Add persona-based response formatting
