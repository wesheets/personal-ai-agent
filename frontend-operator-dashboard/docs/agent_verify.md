# Agent Task Verification Module

This document describes the Agent Task Verification module, which provides functionality for agents to self-qualify for tasks based on their skills. This module enables agents to evaluate whether they should take on a given task based on their skillset, role, and current state.

## Overview

The Agent Task Verification module provides an endpoint that allows the system to check if a specific agent has the necessary skills to perform a given task. This helps ensure that tasks are assigned to agents that are capable of handling them, improving overall system efficiency and reliability.

## Endpoint

```
POST /agent/verify_task
```

This endpoint accepts a task description and an agent ID, and returns a verification result indicating whether the agent is qualified to perform the task.

## Request Format

```json
{
  "agent_id": "hal",
  "task_description": "Analyze user feedback and summarize the key points.",
  "required_skills": ["analyze", "summarize"]  // Optional
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| agent_id | string | Yes | The ID of the agent to verify (with or without "-agent" suffix) |
| task_description | string | Yes | Description of the task to be performed |
| required_skills | array of strings | No | Optional list of skills required for the task. If not provided, skills will be extracted from the task description |

## Response Format

```json
{
  "agent_id": "hal",
  "task_description": "Analyze user feedback and summarize the key points.",
  "qualified": true,
  "confidence_score": 0.9,
  "missing_skills": [],
  "matching_skills": ["analyze", "summarize"],
  "justification": "Agent is fully qualified with all required skills: analyze, summarize.",
  "suggested_agents": null
}
```

### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| agent_id | string | The ID of the agent that was verified |
| task_description | string | The original task description |
| qualified | boolean | Whether the agent is qualified to perform the task |
| confidence_score | number | A score between 0 and 1 indicating the confidence in the qualification |
| missing_skills | array of strings | Skills required for the task that the agent does not have |
| matching_skills | array of strings | Skills required for the task that the agent has |
| justification | string | A human-readable explanation of the verification result |
| suggested_agents | array of strings or null | If the agent is not qualified, a list of alternative agents that have the required skills |

## Error Responses

### Agent Not Found (404)

```json
{
  "detail": "Agent 'nonexistent' not found in manifest"
}
```

### Missing Required Fields (422)

```json
{
  "detail": "agent_id is required"
}
```

or

```json
{
  "detail": "task_description is required"
}
```

## Implementation Details

### Skill Extraction

The module extracts required skills from task descriptions using keyword matching. It looks for specific skill-related keywords in the task description and maps them to corresponding skills.

For example, words like "analyze", "assessment", "evaluate", and "examine" are mapped to the "analyze" skill.

If no skills can be extracted from the task description, the module will use a fallback approach to look for verbs at the beginning of sentences or after certain phrases.

### Qualification Determination

An agent is considered qualified for a task if it has all the required skills. The confidence score is calculated based on the percentage of matching skills:

- 100% match: 0.9 (high confidence)
- 75-99% match: 0.8 (good match)
- 50-74% match: 0.6 (moderate match)
- 1-49% match: 0.4 (poor match)
- 0% match: 0.1 (very poor match)
- No skills required: 0.5 (neutral)

### Alternative Agent Suggestions

If an agent is not qualified for a task, the module will suggest alternative agents that have all the required skills. This helps the system find suitable replacements for tasks that the original agent cannot perform.

## Usage Examples

### Verifying a Qualified Agent

```python
response = requests.post(
    "https://api.example.com/agent/verify_task",
    json={
        "agent_id": "hal",
        "task_description": "Analyze user feedback and summarize the key points."
    }
)
```

### Verifying with Explicit Skills

```python
response = requests.post(
    "https://api.example.com/agent/verify_task",
    json={
        "agent_id": "hal",
        "task_description": "Handle this complex task.",
        "required_skills": ["analyze", "monitor"]
    }
)
```

### Handling an Unqualified Agent

```python
response = requests.post(
    "https://api.example.com/agent/verify_task",
    json={
        "agent_id": "hal",
        "task_description": "Delegate tasks to other agents and execute the plan."
    }
)

# Check if the agent is qualified
if not response.json()["qualified"]:
    # Get suggested alternative agents
    suggested_agents = response.json()["suggested_agents"]
    if suggested_agents:
        # Use the first suggested agent instead
        alternative_agent = suggested_agents[0]
        print(f"Using {alternative_agent} instead of hal")
```

## Integration with Other Modules

The Agent Task Verification module can be integrated with other modules in the system:

- **Orchestrator**: The orchestrator can use this endpoint to verify that agents have the necessary skills before assigning tasks to them.
- **Delegate**: The delegate module can use this endpoint to find suitable agents for delegated tasks.
- **Task Supervisor**: The task supervisor can use this endpoint to validate agent assignments and prevent mismatches.

## Future Enhancements

Potential future enhancements for the Agent Task Verification module include:

1. **Context-aware skill extraction**: Improve skill extraction by considering the context of the task description.
2. **Learning from past verifications**: Adjust confidence scores based on past performance of agents on similar tasks.
3. **Task complexity assessment**: Consider the complexity of the task when determining qualification.
4. **Agent state consideration**: Take into account the current state of the agent (idle, busy, etc.) when suggesting alternatives.
5. **Multi-agent task verification**: Verify if a group of agents collectively has the skills required for a complex task.
