# Promethios Tiered Orchestrator Depth Modes Documentation

## Overview

The Tiered Orchestrator Depth Modes feature extends the Cognitive Control Layer of Promethios with a sophisticated mode-based execution system. This feature provides different execution modes for the orchestrator based on task complexity, sensitivity, and resource requirements, allowing for more efficient and appropriate handling of various tasks.

This documentation covers the architecture, components, and usage of the Tiered Orchestrator Depth Modes feature.

## Architecture

The Tiered Orchestrator Depth Modes feature consists of several interconnected components:

1. **Tiered Orchestrator** - Core module that manages different execution modes
2. **Depth Controller Integration** - Maps orchestrator modes to reflection depths
3. **Loop Map Visualizer** - Provides visual representation of loop execution paths
4. **Live Memory Inspection** - Enables real-time access to memory state during execution

These components work together to provide a comprehensive mode-based execution framework that adapts to different task requirements.

## Orchestrator Modes

The Tiered Orchestrator supports four distinct execution modes:

### 1. FAST Mode

**Purpose**: Quick execution with minimal reflection and validation for simple, straightforward tasks.

**Characteristics**:
- Shallow reflection depth
- Minimal agent involvement (HAL, NOVA, CEO only)
- Basic safety checks
- Short memory retention
- Limited to 2 loops maximum
- Timeout multiplier: 0.7x (faster execution)
- Visualization: Minimal detail, end-only updates
- Memory inspection: Read-only access, end-only snapshots

**Best for**: Simple, non-sensitive tasks with time constraints.

### 2. BALANCED Mode

**Purpose**: Standard execution with normal reflection and validation for everyday tasks.

**Characteristics**:
- Standard reflection depth
- Moderate agent involvement (includes CRITIC, CEO)
- Basic and alignment safety checks
- Medium memory retention
- Up to 3 loops maximum
- Timeout multiplier: 1.0x (standard execution)
- Visualization: Standard detail, agent-completion updates
- Memory inspection: Read-only access, agent-completion snapshots

**Best for**: Typical day-to-day tasks with moderate complexity.

### 3. THOROUGH Mode

**Purpose**: Comprehensive execution with extensive reflection and validation for complex or sensitive tasks.

**Characteristics**:
- Deep reflection depth
- Extensive agent involvement (includes SAGE, PESSIMIST, CRITIC, CEO)
- Comprehensive safety checks (basic, alignment, bias, drift)
- Long memory retention
- Up to 5 loops maximum
- Timeout multiplier: 1.5x (more thorough execution)
- Visualization: Detailed, real-time updates
- Memory inspection: Read-write access, real-time snapshots

**Best for**: Complex tasks, sensitive domains, or situations requiring high accuracy.

### 4. RESEARCH Mode

**Purpose**: Deep exploration mode with maximum reflection and validation for research, exploration, or highly sensitive tasks.

**Characteristics**:
- Deep reflection depth with additional research-specific settings
- Maximum agent involvement (all available agents)
- Exhaustive safety checks (includes hallucination and copyright checks)
- Permanent memory retention
- Up to 7 loops maximum
- Timeout multiplier: 2.0x (most thorough execution)
- Visualization: Comprehensive with uncertainty tracking
- Memory inspection: Admin access, real-time snapshots, time travel enabled

**Best for**: Research tasks, deep exploration, highly sensitive domains, or situations requiring maximum accuracy and transparency.

## Core Components

### 1. Tiered Orchestrator Module

The Tiered Orchestrator Module is implemented in `tiered_orchestrator.py` and serves as the central component for managing execution modes.

#### Key Functions:

- `determine_optimal_mode(task_description, complexity, sensitivity, time_constraint)` - Determines the optimal mode based on task characteristics
- `get_mode_config(mode)` - Returns the configuration for a specific mode
- `enrich_loop_with_mode(loop_data, mode)` - Enriches a loop with mode-specific information
- `adjust_agent_plan_for_mode(agent_plan, mode)` - Adjusts an agent plan based on the specified mode

#### Usage Example:

```python
from app.modules.tiered_orchestrator import determine_optimal_mode, enrich_loop_with_mode

# Determine optimal mode for a task
task_description = "Create a medical diagnosis system"
mode = determine_optimal_mode(task_description, sensitivity=0.9)
print(f"Recommended mode: {mode}")

# Enrich a loop with mode information
enriched_loop = enrich_loop_with_mode(loop_data, mode)
```

### 2. Depth Controller Integration

The Depth Controller Integration maps orchestrator modes to reflection depths and is implemented through the integration between `tiered_orchestrator.py` and `depth_controller.py`.

#### Key Functions:

- `get_depth_for_mode(mode)` - Returns the corresponding depth level for a specific mode
- `get_agents_for_mode(mode)` - Returns the list of agents required for a specific mode
- `get_reflection_config_for_mode(mode)` - Returns reflection configuration for a specific mode

#### Usage Example:

```python
from app.modules.tiered_orchestrator import get_depth_for_mode, get_agents_for_mode

# Get depth for a mode
depth = get_depth_for_mode("thorough")
print(f"Depth for THOROUGH mode: {depth}")

# Get agents for a mode
agents = get_agents_for_mode("balanced")
print(f"Agents for BALANCED mode: {', '.join(agents)}")
```

### 3. Loop Map Visualizer

The Loop Map Visualizer is implemented in `loop_map_visualizer.py` and provides visual representation of loop execution paths, agent interactions, and memory state transitions.

#### Key Functions:

- `create_visualizer(loop_id, mode, color_scheme)` - Creates a loop map visualizer for a loop
- `generate_map_from_trace(loop_trace)` - Generates a loop map from a loop trace
- `generate_html(loop_map)` - Generates HTML visualization from a loop map
- `should_update_visualization(event_type)` - Determines if visualization should be updated for a given event type

#### Visualization Formats:

- **JSON** - Raw data structure for API consumption
- **HTML** - Interactive visualization with D3.js
- **SVG** - Static visualization for embedding
- **PNG** - Image format for sharing
- **DOT** - GraphViz format for further processing

#### Usage Example:

```python
from app.modules.loop_map_visualizer import create_visualizer, visualize_loop

# Create a visualizer for a loop
visualizer = create_visualizer("loop_001", "thorough", "default")

# Generate visualization
visualization = visualize_loop("loop_001", loop_trace, "thorough", "html")

# Save visualization to file
with open("loop_visualization.html", "w") as f:
    f.write(visualization["visualization"])
```

### 4. Live Memory Inspection

The Live Memory Inspection is implemented in `live_memory_inspection.py` and provides real-time access to the memory state of running loops.

#### Key Functions:

- `create_memory_inspector(loop_id, mode)` - Creates a memory inspector for a loop
- `get_memory_state(filter_options)` - Gets the current memory state for a loop
- `get_memory_value(key)` - Gets a specific memory value by key
- `should_snapshot_memory(mode, event_type)` - Determines if memory should be snapshotted for a given mode and event type

#### Memory Access Levels:

- **READ_ONLY** - Can only read memory values (FAST, BALANCED modes)
- **READ_WRITE** - Can read and write memory values (THOROUGH mode)
- **ADMIN** - Full access including deletion and time travel (RESEARCH mode)

#### Usage Example:

```python
from app.modules.live_memory_inspection import create_memory_inspector, inspect_memory

# Create a memory inspector for a loop
inspector = create_memory_inspector("loop_001", "research")

# Get memory state
memory_state = await inspector.get_memory_state()

# Get specific memory value
memory_value = await inspector.get_memory_value("task_description")

# Check if memory should be snapshotted
should_snapshot = should_snapshot_memory("balanced", "agent_completion")
```

## Integration with Orchestrator

The Tiered Orchestrator Depth Modes feature is integrated with the main orchestrator through the `orchestrator_integration.py` module, which now includes mode-based functionality.

### Key Functions:

- `integrate_with_orchestrator_and_mode(loop_id, loop_data, mode=None)` - Integrates all components for a loop with mode-specific settings
- `determine_mode_for_task(task_description, **kwargs)` - Determines the appropriate mode for a task
- `change_mode_during_execution(loop_id, loop_data, new_mode, reason)` - Changes the mode during loop execution

### Usage Example:

```python
from app.modules.orchestrator_integration import integrate_with_orchestrator_and_mode, determine_mode_for_task

# Determine mode for a task
task_description = "Analyze financial data for fraud patterns"
mode = determine_mode_for_task(task_description)

# Prepare a loop with cognitive controls and mode-specific settings
prepared_loop = integrate_with_orchestrator_and_mode("loop_001", loop_data, mode)
```

## API Endpoints

The Tiered Orchestrator Depth Modes feature is exposed through several API endpoints in the `orchestrator_routes.py` module.

### Key Endpoints:

#### 1. `/orchestrator/determine-mode`

Determines the optimal mode for a task based on its description and characteristics.

```python
@router.post("/orchestrator/determine-mode")
async def determine_mode_endpoint(request: DetermineModeRequest):
    """
    Determine the optimal orchestrator mode for a task.
    """
    mode = determine_optimal_mode(
        request.task_description,
        complexity=request.complexity,
        sensitivity=request.sensitivity,
        time_constraint=request.time_constraint,
        user_preference=request.user_preference
    )
    
    return {
        "status": "success",
        "task_description": request.task_description,
        "recommended_mode": mode,
        "mode_description": get_mode_description(mode),
        "mode_config": get_mode_config(mode),
        "processed_at": datetime.utcnow().isoformat()
    }
```

#### 2. `/orchestrator/validate-loop-with-mode`

Validates a loop against core requirements and enriches it with mode-specific settings.

```python
@router.post("/orchestrator/validate-loop-with-mode")
async def validate_loop_with_mode_endpoint(request: LoopValidateWithModeRequest):
    """
    Validate a loop against core requirements and enrich with mode-specific settings.
    """
    # Determine mode if not provided
    mode = request.mode
    if not mode:
        mode = determine_optimal_mode(request.loop_data.get("task_description", ""))
    
    # Apply cognitive controls and mode-specific settings to the loop
    prepared_loop = integrate_with_orchestrator_and_mode(request.loop_id, request.loop_data, mode)
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "mode": mode,
        "mode_description": get_mode_description(mode),
        "validation_result": prepared_loop.get("validation_status", {}),
        "prepared_loop": prepared_loop,
        "processed_by": "tiered_orchestrator",
        "processed_at": datetime.utcnow().isoformat()
    }
```

#### 3. `/orchestrator/change-mode`

Changes the mode of an existing loop during execution.

```python
@router.post("/orchestrator/change-mode")
async def change_mode_endpoint(request: ChangeModeRequest):
    """
    Change the mode of an existing loop during execution.
    """
    # Get current loop data
    loop_data = await get_loop_data(request.loop_id)
    
    # Change mode
    updated_loop = change_mode_during_execution(
        request.loop_id,
        loop_data,
        request.new_mode,
        request.reason
    )
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "old_mode": loop_data.get("mode"),
        "new_mode": request.new_mode,
        "reason": request.reason,
        "updated_loop": updated_loop,
        "processed_at": datetime.utcnow().isoformat()
    }
```

#### 4. `/orchestrator/visualize-loop`

Generates a visualization of a loop's execution path.

```python
@router.post("/orchestrator/visualize-loop")
async def visualize_loop_endpoint(request: VisualizeLoopRequest):
    """
    Generate a visualization of a loop's execution path.
    """
    # Get loop trace
    loop_trace = await get_loop_trace(request.loop_id)
    
    # Generate visualization
    visualization = visualize_loop(
        request.loop_id,
        loop_trace,
        request.mode,
        request.format,
        request.color_scheme
    )
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "mode": request.mode,
        "format": request.format,
        "visualization": visualization,
        "processed_at": datetime.utcnow().isoformat()
    }
```

#### 5. `/orchestrator/inspect-memory`

Provides access to the memory state of a running loop.

```python
@router.post("/orchestrator/inspect-memory")
async def inspect_memory_endpoint(request: InspectMemoryRequest):
    """
    Provide access to the memory state of a running loop.
    """
    # Create memory inspector
    inspector = create_memory_inspector(request.loop_id, request.mode)
    
    # Get memory state
    memory_state = await inspector.get_memory_state(request.filter_options)
    
    return {
        "status": "success",
        "loop_id": request.loop_id,
        "mode": request.mode,
        "memory_state": memory_state,
        "processed_at": datetime.utcnow().isoformat()
    }
```

## Workflow

The typical workflow for the Tiered Orchestrator Depth Modes feature is as follows:

1. **Mode Determination** - The optimal mode is determined based on task characteristics
2. **Loop Creation** - A new loop is created with a prompt, orchestrator persona, and plan
3. **Mode Enrichment** - The loop is enriched with mode-specific information
4. **Depth Mapping** - The mode is mapped to the appropriate reflection depth
5. **Loop Execution** - The loop is executed according to the plan with mode-specific settings
6. **Visualization** - The loop execution path is visualized according to mode-specific settings
7. **Memory Inspection** - The memory state is inspected according to mode-specific settings
8. **Mode Adaptation** - The mode may be changed during execution based on new information

## Best Practices

1. **Use Appropriate Modes** - Choose the appropriate mode for the task at hand
2. **Consider Task Characteristics** - Consider task complexity, sensitivity, and time constraints when determining the mode
3. **Allow Mode Adaptation** - Allow the system to adapt the mode during execution based on new information
4. **Use Visualizations** - Use visualizations to understand loop execution paths
5. **Inspect Memory** - Use memory inspection to debug and analyze loop execution

## Troubleshooting

### Common Issues

1. **Inappropriate Mode Selection**
   - Check task complexity, sensitivity, and time constraints
   - Consider user preferences
   - Allow the system to adapt the mode during execution

2. **Visualization Issues**
   - Check browser compatibility for HTML visualizations
   - Ensure loop trace contains all required information
   - Try different visualization formats

3. **Memory Inspection Issues**
   - Check access level for the current mode
   - Ensure memory keys exist
   - Consider using filters to reduce data volume

## Conclusion

The Tiered Orchestrator Depth Modes feature provides a sophisticated mode-based execution system for the Promethios AI agent platform. By adapting to different task requirements, it helps create a more efficient and appropriate AI system that can handle a wide range of tasks with varying complexity, sensitivity, and time constraints.

For more information, please refer to the source code and unit tests in the repository.
