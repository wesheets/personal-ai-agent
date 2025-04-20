# Reflection Grader + Confidence Monitor

## Overview

The Reflection Grader is a system that evaluates agent reflections (especially from HAL, SAGE, CRITIC, and Orchestrator) and scores their quality based on multiple criteria. This gives Promethios metacognition hygiene — the ability to know when its own thoughts are weak.

## Implementation Details

### Core Components

1. **`reflection_grader.py`**: The main module that implements the grading logic
2. **Project Memory Integration**: Stores reflection scores and weak reflections in project state
3. **Debug API Endpoint**: Allows manual grading of reflections via `/api/debug/reflection/grade/{project_id}`

### Grading Criteria

The reflection grader evaluates reflections based on:

1. **Schema Compliance**: Checks if the reflection follows the expected schema structure
2. **Confidence Value**: Penalizes reflections with low confidence scores
3. **Tag Quality**: Ensures reflections include appropriate tags, especially loop references
4. **Goal Alignment**: Verifies that the reflection summary aligns with the stated goal
5. **Verbosity vs Clarity**: Checks if the reflection is too brief or excessively verbose

### Scoring System

- Starting score: 1.0
- Schema mismatch: -0.3
- Low confidence (< 0.6): -0.2
- Missing loop reference tag: -0.1
- Summary doesn't align with goal: -0.15
- Summary too brief (< 50 chars): -0.1
- Summary excessively verbose (> 1000 chars): -0.05

Reflections with scores below 0.6 are considered "weak" and are stored separately for further analysis.

## API Reference

### Module Functions

#### `grade_reflection(project_id: str) -> Dict[str, Any]`

Grades the last reflection for a project and stores the score in project state.

**Parameters:**
- `project_id`: The ID of the project

**Returns:**
- Dictionary containing:
  - `score`: The reflection quality score (0.0-1.0)
  - `issues`: List of identified issues
  - `timestamp`: When the grading occurred
  - `loop`: Current loop count
  - `reflection_id`: Unique identifier for the reflection

#### `get_reflection_scores(project_id: str) -> Dict[str, Any]`

Gets all reflection scores for a project.

**Parameters:**
- `project_id`: The ID of the project

**Returns:**
- Dictionary containing:
  - `project_id`: The project ID
  - `reflection_scores`: List of all reflection score objects
  - `count`: Number of reflection scores
  - `average_score`: Average score across all reflections

#### `get_weak_reflections(project_id: str) -> Dict[str, Any]`

Gets all weak reflections for a project.

**Parameters:**
- `project_id`: The ID of the project

**Returns:**
- Dictionary containing:
  - `project_id`: The project ID
  - `weak_reflections`: List of all weak reflection objects
  - `count`: Number of weak reflections

### API Endpoints

#### `GET /api/debug/reflection/grade/{project_id}`

Grades the last reflection for a project and returns the result.

**Parameters:**
- `project_id`: The ID of the project (path parameter)

**Response:**
- Same as the return value of `grade_reflection()`

## Integration Guide

### Orchestrator Integration

To integrate the Reflection Grader with the Orchestrator:

1. After each agent completes a reflection, call the grading endpoint:
   ```python
   response = requests.get(f"{API_BASE}/api/debug/reflection/grade/{project_id}")
   ```

2. Check the score and take appropriate action:
   ```python
   if response.json().get("score", 1.0) < 0.6:
       # Handle weak reflection
       # Options:
       # - Rerun the reflection
       # - Log a warning
       # - Adjust agent parameters
   ```

### Automatic Grading

For automatic grading after every reflection, add the following to the agent loop flow:

```python
def process_agent_reflection(project_id, agent_id, reflection):
    # Store reflection in project state
    update_project_state(project_id, {"last_reflection": reflection})
    
    # Grade the reflection
    from app.modules.reflection_grader import grade_reflection
    result = grade_reflection(project_id)
    
    # Take action based on score
    if result["score"] < 0.6:
        logger.warning(f"Weak reflection detected from {agent_id}: {result['issues']}")
        # Implement recovery logic here
```

## Testing

The `test_reflection_grader.py` script provides comprehensive tests for the Reflection Grader module, including:

1. Grading good reflections
2. Grading bad reflections
3. Retrieving reflection scores
4. Retrieving weak reflections
5. Handling multiple reflections

Run the tests with:
```
python test_reflection_grader.py
```

## Future Enhancements

1. **Adaptive Thresholds**: Adjust scoring thresholds based on historical performance
2. **Agent-Specific Grading**: Customize grading criteria for different agent types
3. **Automatic Recovery**: Implement automatic recovery strategies for weak reflections
4. **Trend Analysis**: Analyze reflection quality trends over time
5. **UI Integration**: Add reflection quality metrics to the operator dashboard

## Conclusion

The Reflection Grader + Confidence Monitor provides Promethios with metacognition hygiene — the ability to know when its own thoughts are weak. This is a critical capability for a self-improving system, as it enables the system to identify and address weaknesses in its own thinking processes.
