# Promethios Cognitive Control Layer Documentation

## Overview

The Cognitive Control Layer is a Claude-inspired integrity guardrail system for the Promethios AI agent platform. It ensures that all loops adhere to core beliefs, operational thresholds, and agent permissions, providing a robust framework for safe and aligned AI operation.

This documentation covers the architecture, components, and usage of the Cognitive Control Layer.

## Architecture

The Cognitive Control Layer consists of several interconnected components:

1. **Core Beliefs System** - Defines fundamental principles that guide all operations
2. **Agent Permission Registry** - Controls what actions each agent type can perform
3. **Loop Validation System** - Ensures loops contain all required components
4. **Reflection Depth Controller** - Manages reflection depth based on context
5. **Orchestrator Integration** - Coordinates all components during loop execution

These components work together to provide a comprehensive integrity framework that operates at multiple levels of the system.

## Core Components

### 1. Core Beliefs System

The Core Beliefs System is defined in `PROMETHIOS_CORE.md` and enforced through the `core_beliefs_integration.py` module. It ensures that all loops adhere to fundamental principles such as:

- **Reflection Before Execution** - All plans must be reflected upon before execution
- **Alignment Over Speed** - Alignment with user intent takes precedence over execution speed
- **Transparency to Operator** - All operations must be transparent to the system operator
- **Bias Awareness** - The system must be aware of and mitigate potential biases

#### Key Functions:

- `inject_belief_references(loop_data)` - Adds core belief references to a loop
- `check_belief_conflicts(loop_data, reflection_result)` - Identifies conflicts between reflection results and core beliefs
- `get_belief_description(belief_name)` - Retrieves detailed descriptions of specific beliefs
- `get_belief_priority(belief_name)` - Gets the priority level of a belief for conflict resolution

#### Usage Example:

```python
from app.modules.core_beliefs_integration import inject_belief_references, check_belief_conflicts

# Enrich a loop with belief references
enriched_loop = inject_belief_references(loop_data)

# Check for belief conflicts in reflection results
conflicts, conflict_details = check_belief_conflicts(loop_data, reflection_result)
if conflicts:
    print(f"Found {len(conflicts)} belief conflicts: {', '.join(conflicts)}")
    print(f"Conflict severity: {conflict_details['severity']}")
```

### 2. Agent Permission Registry

The Agent Permission Registry is defined in `agent_permissions.json` and enforced through the `agent_permission_validator.py` module. It ensures that agents only perform actions they are authorized to perform.

#### Key Functions:

- `check_permission(agent, action)` - Checks if an agent is allowed to perform a specific action
- `enforce_agent_permissions(agent, action, loop_id)` - Enforces permissions and provides substitutes for unauthorized actions
- `log_violation(violation, loop_id)` - Logs permission violations for auditing
- `get_substitute_action(agent, attempted_action)` - Provides substitute actions when an agent attempts an unauthorized action

#### Usage Example:

```python
from app.modules.agent_permission_validator import enforce_agent_permissions

# Check if an agent is allowed to perform an action
is_allowed, violation, substitute = enforce_agent_permissions("NOVA", "identify_bias", "loop_001")

if not is_allowed:
    print(f"Agent NOVA is not allowed to identify_bias")
    if substitute:
        print(f"Using substitute action: {substitute['action']} instead")
```

### 3. Loop Validation System

The Loop Validation System is implemented in `loop_validator.py` and ensures that all loops contain the required components and adhere to structural requirements.

#### Key Functions:

- `validate_loop(loop_data)` - Validates a loop against core requirements
- `validate_and_enrich_loop(loop_data)` - Validates and enriches a loop with additional metadata

#### Validation Checks:

- Presence of required components (prompt, orchestrator_persona, plan, reflection_agent)
- Validity of orchestrator persona
- Minimum plan steps (at least 2)
- Required agents for specified depth

#### Usage Example:

```python
from app.modules.loop_validator import validate_loop, validate_and_enrich_loop

# Validate a loop
is_valid, reason, validation_result = validate_loop(loop_data)
if not is_valid:
    print(f"Loop validation failed: {reason}")
    print(f"Missing components: {validation_result.get('missing_components', [])}")
    print(f"Invalid components: {validation_result.get('invalid_components', [])}")

# Validate and enrich a loop
enriched_loop = validate_and_enrich_loop(loop_data)
```

### 4. Reflection Depth Controller

The Reflection Depth Controller is implemented in `depth_controller.py` and manages the depth of reflection based on context, ensuring appropriate agent involvement.

#### Depth Levels:

- **Shallow** - Basic reflection with HAL and NOVA agents
- **Standard** - Normal reflection with CRITIC and CEO agents
- **Deep** - Comprehensive reflection with SAGE, PESSIMIST, and full drift review

#### Key Functions:

- `enrich_loop_with_depth(loop_data, depth=None)` - Enriches a loop with depth information and appropriate agents
- `preload_depth_for_rerun(loop_data, rerun_reason)` - Determines appropriate depth for loop reruns
- `get_agents_for_depth(depth)` - Returns the list of agents required for a specific depth
- `get_reflection_config(depth)` - Returns configuration parameters for a specific depth

#### Usage Example:

```python
from app.modules.depth_controller import enrich_loop_with_depth, preload_depth_for_rerun

# Enrich a loop with standard depth
standard_loop = enrich_loop_with_depth(loop_data)

# Enrich a loop with deep depth
deep_loop = enrich_loop_with_depth(loop_data, "deep")

# Determine depth for a rerun based on reason
rerun_depth = preload_depth_for_rerun(loop_data, "alignment_threshold_not_met")
```

### 5. Orchestrator Integration

The Orchestrator Integration is implemented in `orchestrator_integration.py` and serves as the central coordination point for the Cognitive Control Layer.

#### Key Functions:

- `integrate_with_orchestrator(loop_id, loop_data)` - Integrates all cognitive control components for a loop
- `process_reflection_with_controls(loop_id, loop_data, reflection_result)` - Processes reflection results with cognitive controls
- `determine_rerun_depth_with_controls(loop_id, loop_data, rerun_reason)` - Determines appropriate depth for reruns with controls

#### Usage Example:

```python
from app.modules.orchestrator_integration import integrate_with_orchestrator, process_reflection_with_controls

# Prepare a loop with cognitive controls
prepared_loop = integrate_with_orchestrator("loop_001", loop_data)

# Process reflection results with cognitive controls
processed_reflection = process_reflection_with_controls("loop_001", prepared_loop, reflection_result)

# Check for belief conflicts
if processed_reflection.get("belief_conflict", False):
    print("Belief conflicts detected:")
    for conflict in processed_reflection["belief_conflict_flags"]:
        print(f"- {conflict}: {processed_reflection['belief_conflict_descriptions'][conflict]}")
```

## Integration with FastAPI Routes

The Cognitive Control Layer is integrated with the Promethios API through the `orchestrator_routes.py` module, which provides endpoints for loop validation and completion.

### Key Endpoints:

#### 1. `/orchestrator/validate-loop`

Validates a loop against core requirements and enriches it with cognitive controls.

```python
@router.post("/orchestrator/validate-loop")
async def validate_loop_endpoint(request: LoopValidateRequest):
    """
    Validate a loop against core requirements and enrich with cognitive controls.
    """
    # Apply cognitive controls to the loop
    prepared_loop = integrate_with_orchestrator(request.loop_id, request.loop_data)
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "validation_result": prepared_loop.get("validation_status", {}),
        "prepared_loop": prepared_loop,
        "processed_by": "cognitive_control_layer",
        "processed_at": datetime.utcnow().isoformat()
    }
```

#### 2. `/orchestrator/loop-complete`

Handles post-execution signals and processes reflection results with cognitive controls.

```python
@router.post("/orchestrator/loop-complete")
async def loop_complete(request: LoopCompleteRequest):
    """
    Handle post-execution signals and kick off system reflection.
    """
    # Process loop reflection by gathering outputs from all reflection agents
    reflection_result = await process_loop_reflection(request.loop_id)
    
    # Apply cognitive controls to the reflection result
    controlled_reflection = process_reflection_with_controls(
        request.loop_id, 
        {"loop_id": request.loop_id, "orchestrator_persona": orchestrator_persona},
        reflection_result
    )
    
    # Evaluate whether to rerun the loop based on alignment and drift scores
    rerun_decision = await evaluate_rerun_decision(
        request.loop_id, 
        controlled_reflection
    )
    
    # If rerun is needed, determine the appropriate depth
    if rerun_decision.get("decision") == "rerun":
        rerun_depth = determine_rerun_depth_with_controls(
            request.loop_id,
            {"loop_id": request.loop_id, "orchestrator_persona": orchestrator_persona},
            rerun_decision.get("rerun_reason", "unknown")
        )
        rerun_decision["depth"] = rerun_depth
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "orchestrator_persona": orchestrator_persona,
        "reflection_result": controlled_reflection,
        "rerun_decision": rerun_decision,
        "processed_by": "cognitive_control_layer",
        "processed_at": datetime.utcnow().isoformat()
    }
```

## Workflow

The typical workflow for the Cognitive Control Layer is as follows:

1. **Loop Creation** - A new loop is created with a prompt, orchestrator persona, and plan
2. **Loop Validation** - The loop is validated against core requirements
3. **Belief Injection** - Core beliefs are injected into the loop
4. **Depth Enrichment** - The loop is enriched with depth information and appropriate agents
5. **Loop Execution** - The loop is executed according to the plan
6. **Reflection** - Reflection agents analyze the execution results
7. **Belief Conflict Check** - Reflection results are checked for conflicts with core beliefs
8. **Rerun Decision** - A decision is made whether to rerun the loop based on alignment and drift scores
9. **Depth Determination** - If a rerun is needed, the appropriate depth is determined

## Configuration

### Core Beliefs Configuration

Core beliefs are defined in `PROMETHIOS_CORE.md` and include:

- **Belief Name** - The name of the belief
- **Description** - A detailed description of the belief
- **Priority** - The priority level of the belief (1-10)
- **Required Components** - Components required to satisfy the belief
- **Tolerance Thresholds** - Thresholds for acceptable deviation from the belief

### Agent Permissions Configuration

Agent permissions are defined in `agent_permissions.json` and include:

- **Agent Name** - The name of the agent
- **Allowed Actions** - A list of actions the agent is allowed to perform

### Depth Configuration

Depth configuration is defined in the `depth_controller.py` module and includes:

- **Depth Levels** - Shallow, Standard, and Deep
- **Required Agents** - Agents required for each depth level
- **Reflection Config** - Configuration parameters for each depth level

## Best Practices

1. **Always Validate Loops** - Always validate loops before execution to ensure they meet core requirements
2. **Check Belief Conflicts** - Always check for belief conflicts in reflection results
3. **Use Appropriate Depth** - Use the appropriate depth for the task at hand
4. **Handle Permission Violations** - Always handle permission violations gracefully
5. **Log Everything** - Log all operations for auditing and debugging

## Troubleshooting

### Common Issues

1. **Loop Validation Failures**
   - Check for missing required components
   - Verify orchestrator persona is valid
   - Ensure plan has at least 2 steps
   - Verify required agents for specified depth are present

2. **Permission Violations**
   - Check agent permissions in `agent_permissions.json`
   - Use substitute actions when available
   - Log violations for auditing

3. **Belief Conflicts**
   - Check reflection results against core beliefs
   - Address conflicts based on priority
   - Consider rerunning the loop with deeper reflection

## Conclusion

The Cognitive Control Layer provides a robust framework for ensuring the integrity and alignment of the Promethios AI agent platform. By enforcing core beliefs, agent permissions, and operational thresholds, it helps create a safer and more reliable AI system.

For more information, please refer to the source code and unit tests in the repository.
