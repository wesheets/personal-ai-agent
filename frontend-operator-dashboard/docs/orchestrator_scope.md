# Orchestrator Scope Module

## Overview

The Orchestrator Scope module provides a strategic project planning capability that turns high-level user goals into structured system plans. It outputs a full project scaffold including modules, agents, schema, risks, and test payloads ready for execution or simulation.

## Endpoint

```
POST /orchestrator/scope
```

## Request Schema

| Field       | Type    | Required | Description                                                                             |
| ----------- | ------- | -------- | --------------------------------------------------------------------------------------- |
| goal        | string  | Yes      | High-level user goal                                                                    |
| user_id     | string  | No       | Optional user identifier                                                                |
| project_id  | string  | No       | Optional project identifier (auto-generated if not provided)                            |
| mode        | string  | No       | Operation mode, currently only "scope" is supported (future modes: "simulate", "build") |
| store_scope | boolean | No       | Whether to store the scope in memory (default: false)                                   |

### Example Request

```json
{
  "goal": "Create a journaling application with reflection capabilities",
  "user_id": "user-123",
  "project_id": "proj-journal",
  "mode": "scope",
  "store_scope": true
}
```

## Response Schema

| Field                      | Type        | Description                                           |
| -------------------------- | ----------- | ----------------------------------------------------- |
| project_id                 | string      | Project identifier                                    |
| goal                       | string      | Original goal                                         |
| required_modules           | array       | List of required modules                              |
| suggested_agents           | array       | List of suggested agents with tools and personas      |
| recommended_schema         | object      | Input and output schema                               |
| execution_tasks            | array       | List of execution tasks                               |
| known_risks                | array       | List of known risks                                   |
| confidence_scores          | object      | Confidence scores for agents                          |
| project_dependencies       | object      | Dependencies between modules                          |
| agent_training_reqs        | object      | Training requirements for agents                      |
| execution_blueprint_id     | string      | Execution blueprint identifier                        |
| simulate_pathways          | null/object | Simulation pathways (null for scope mode)             |
| suggested_tests            | array       | List of suggested tests                               |
| markdown_summary           | string      | Markdown summary of the project scope                 |
| stored                     | boolean     | Whether the scope was stored in memory                |
| skill_validation_passed    | boolean     | Whether all required tools have matching agent skills |
| unmatched_tasks            | array       | List of tools that don't have matching agent skills   |
| agent_creation_suggestions | array       | Suggestions for new agents to fill skill gaps         |

### Example Response

```json
{
  "project_id": "proj-journal",
  "goal": "Create a journaling application with reflection capabilities",
  "required_modules": ["write", "read", "reflect", "summarize"],
  "suggested_agents": [
    {
      "agent_name": "hal",
      "tools": ["reflect", "summarize"],
      "persona": "supportive, analytical"
    },
    {
      "agent_name": "ash",
      "tools": ["delegate", "execute"],
      "persona": "direct, action-oriented"
    }
  ],
  "recommended_schema": {
    "input": ["agent_id", "goal", "project_id", "memory_trace_id"],
    "output": ["status", "result", "summary"]
  },
  "execution_tasks": [
    "Create project container",
    "Register agents",
    "Train memory with project context",
    "Test summary and reflection loop",
    "Validate trace integrity"
  ],
  "known_risks": [
    "Loop runaway without cycle caps",
    "Missing agent capability validation",
    "Reflection without goal alignment",
    "Output returned without success check"
  ],
  "confidence_scores": {
    "hal": 0.92,
    "ash": 0.87
  },
  "project_dependencies": {
    "summarize": ["write", "reflect"]
  },
  "agent_training_reqs": {
    "hal": ["tone_profile", "journaling context"],
    "ash": ["task delegation patterns"]
  },
  "execution_blueprint_id": "scope-xyz-123",
  "simulate_pathways": null,
  "suggested_tests": [
    {
      "endpoint": "/train",
      "description": "Train HAL on tone and journaling",
      "example": {
        "agent_id": "hal",
        "goal": "Train HAL to support reflective journaling",
        "project_id": "proj-journal",
        "content": "HAL should use a warm, supportive tone."
      }
    }
  ],
  "markdown_summary": "# Project Scope: proj-journal\n\n## Goal\nCreate a journaling application with reflection capabilities\n\n## Required Modules\n- write\n- read\n- reflect\n- summarize\n\n## Suggested Agents\n- **HAL**: supportive, analytical\n  - Tools: reflect, summarize\n- **ASH**: direct, action-oriented\n  - Tools: delegate, execute\n\n## Execution Tasks\n- Create project container\n- Register agents\n- Train memory with project context\n- Test summary and reflection loop\n- Validate trace integrity\n\n## Known Risks\n- Loop runaway without cycle caps\n- Missing agent capability validation\n- Reflection without goal alignment\n- Output returned without success check\n\n---\nGenerated by Orchestrator Scope Module",
  "stored": true,
  "skill_validation_passed": true,
  "unmatched_tasks": []
}
```

### Example Response with Agent Creation Suggestions

When the system detects skill gaps (required tools that no existing agent can perform), it will generate agent creation suggestions:

```json
{
  "project_id": "proj-emotional-journal",
  "goal": "Build a journaling AI that reflects on memory with emotional analysis",
  "required_modules": ["write", "read", "reflect", "emotional_analysis"],
  "suggested_agents": [
    {
      "agent_name": "hal",
      "tools": ["reflect", "summarize"],
      "persona": "supportive, analytical"
    },
    {
      "agent_name": "ash",
      "tools": ["delegate", "execute"],
      "persona": "direct, action-oriented"
    }
  ],
  "skill_validation_passed": false,
  "unmatched_tasks": [
    {
      "tool": "emotional_analysis",
      "reason": "No agent declared capability for emotional_analysis"
    }
  ],
  "agent_creation_suggestions": [
    {
      "agent_name": "echo",
      "proposed_skills": ["emotional_analysis", "reflect"],
      "tone_profile": {
        "style": "gentle",
        "emotion": "empathetic",
        "vibe": "therapist",
        "persona": "A compassionate presence for emotional understanding tasks"
      },
      "reason": "This agent is needed for tone-aware memory reflection and emotional context processing"
    }
  ],
  "confidence_scores": {
    "hal": 0.75,
    "ash": 0.65
  },
  "markdown_summary": "# Project Scope: proj-emotional-journal\n\n## Goal\nBuild a journaling AI that reflects on memory with emotional analysis\n\n## Required Modules\n- write\n- read\n- reflect\n- emotional_analysis\n\n## Suggested Agents\n- **HAL**: supportive, analytical\n  - Tools: reflect, summarize\n- **ASH**: direct, action-oriented\n  - Tools: delegate, execute\n\n## Skill Gaps\n- emotional_analysis: No agent has this capability\n\n## Agent Creation Suggestions\n- **ECHO**: gentle, empathetic\n  - Proposed Skills: emotional_analysis, reflect\n  - Reason: Needed for tone-aware memory reflection\n\n## Execution Tasks\n- Create project container\n- Register agents\n- Create new agent for emotional analysis\n- Train memory with project context\n- Test emotional analysis capabilities\n- Validate trace integrity\n\n---\nGenerated by Orchestrator Scope Module",
  "stored": true
}
```

## Agent Creation Suggestions

When the system detects skill gaps (required tools that no existing agent can perform), it will generate agent creation suggestions to fill those gaps.

### How Agent Suggestions Work

1. **Skill Gap Detection**:

   - During scope planning, the system checks if each required tool has a matching agent with the necessary skills
   - If a tool has no matching agent, it's added to `unmatched_tasks[]`
   - The system sets `skill_validation_passed` to `false`

2. **Agent Creation Suggestion Generation**:

   - The system groups related unmatched skills together
   - For each skill group, it generates:
     - An appropriate agent name based on the skills
     - A list of proposed skills the agent should have
     - A tone profile with style, emotion, vibe, and persona
     - A clear justification for why the agent is needed

3. **Response Structure**:
   - The suggestions are returned in the `agent_creation_suggestions` field
   - Each suggestion contains all the information needed to create the agent

### Manually Creating the Suggested Agent

To create an agent based on the suggestions:

```bash
# Using the /agent/create endpoint
curl -X POST https://api.example.com/agent/create \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "echo",
    "skills": ["emotional_analysis", "reflect"],
    "tone_profile": {
      "style": "gentle",
      "emotion": "empathetic",
      "vibe": "therapist",
      "persona": "A compassionate presence for emotional understanding tasks"
    }
  }'
```

You can extract the necessary information directly from the `agent_creation_suggestions` field in the response:

```python
import requests
import json

# First, get the project scope
scope_response = requests.post(
    "https://api.example.com/orchestrator/scope",
    json={
        "goal": "Build a journaling AI that reflects on memory with emotional analysis"
    }
)

scope = scope_response.json()

# Check if there are agent creation suggestions
if scope.get("agent_creation_suggestions"):
    # Get the first suggestion
    suggestion = scope["agent_creation_suggestions"][0]

    # Create the agent
    agent_response = requests.post(
        "https://api.example.com/agent/create",
        json={
            "agent_id": suggestion["agent_name"],
            "skills": suggestion["proposed_skills"],
            "tone_profile": suggestion["tone_profile"]
        }
    )

    print(f"Created agent: {suggestion['agent_name']}")
    print(f"Response: {agent_response.json()}")
```

## Implementation Details

### Module Analysis

The Orchestrator Scope module analyzes the user's goal to determine which modules are required for the project. It looks for keywords in the goal text to identify relevant modules:

- Base modules (always included): write, read, reflect
- Summarization: summarize (keywords: summarize, summary, summarization)
- Task management: task/status (keywords: task, status, progress, track)
- Training: train (keywords: train, learning, teach)
- Delegation: delegate (keywords: delegate, assign, handoff)
- Looping: loop (keywords: loop, iterate, cycle)

### Agent Selection

The module suggests appropriate agents based on the goal and required modules:

- HAL: Analytical and reflective tasks, good for summarization
- ASH: Action-oriented tasks, good for delegation and execution

### Schema Generation

The module generates recommended input and output schemas based on the required modules:

- Base input fields: agent_id, goal, project_id
- Additional input fields: memory_trace_id (if reflection or summarization is needed)
- Base output fields: status, result
- Additional output fields: summary (if summarization is needed)

### Memory Storage

If the `store_scope` parameter is set to `true`, the module stores the generated scope in memory with:

- agent_id: "system"
- type: "project_scope"
- tags: ["project_scope", f"project:{project_id}"]
- project_id: The project ID
- status: "active"
- task_type: "scope"

## Error Handling

The endpoint returns appropriate error responses in the following cases:

- 422 Unprocessable Entity: Missing required fields (e.g., goal)
- 500 Internal Server Error: Error during scope generation

## Future Enhancements

The current implementation uses static logic to generate project scopes. Future enhancements could include:

- Agent-powered generation for more dynamic and context-aware scopes
- Support for "simulate" mode to simulate project execution
- Support for "build" mode to automatically build the project scaffold
- Integration with other orchestration components for end-to-end project execution

## Testing

The module includes comprehensive tests in `/tests/test_orchestrator_scope.py` that verify:

- Basic functionality
- Project ID handling
- Memory storage
- Required fields validation
- Module analysis
- Agent selection
- Markdown summary generation
- Suggested tests generation
- Skill validation
- Agent creation suggestions

## Usage Examples

### Basic Usage

```python
import requests

response = requests.post(
    "https://api.example.com/orchestrator/scope",
    json={
        "goal": "Create a journaling application with reflection capabilities"
    }
)

scope = response.json()
print(f"Project ID: {scope['project_id']}")
print(f"Required modules: {scope['required_modules']}")
```

### With Project ID and Storage

```python
import requests

response = requests.post(
    "https://api.example.com/orchestrator/scope",
    json={
        "goal": "Build a task management system with delegation",
        "project_id": "proj-task-manager",
        "store_scope": true
    }
)

scope = response.json()
print(f"Project ID: {scope['project_id']}")
print(f"Stored: {scope['stored']}")
```

### Using the Markdown Summary

```python
import requests

response = requests.post(
    "https://api.example.com/orchestrator/scope",
    json={
        "goal": "Create a data analysis pipeline with visualization"
    }
)

scope = response.json()
markdown = scope["markdown_summary"]

# Save the markdown to a file
with open("project_scope.md", "w") as f:
    f.write(markdown)
```

### Creating Suggested Agents

```python
import requests

# Get the project scope
scope_response = requests.post(
    "https://api.example.com/orchestrator/scope",
    json={
        "goal": "Build a journaling AI that reflects on memory with emotional analysis"
    }
)

scope = scope_response.json()

# Check if there are skill gaps and agent creation suggestions
if not scope["skill_validation_passed"] and scope.get("agent_creation_suggestions"):
    # Get the first suggestion
    suggestion = scope["agent_creation_suggestions"][0]

    # Create the agent
    agent_response = requests.post(
        "https://api.example.com/agent/create",
        json={
            "agent_id": suggestion["agent_name"],
            "skills": suggestion["proposed_skills"],
            "tone_profile": suggestion["tone_profile"]
        }
    )

    print(f"Created agent: {suggestion['agent_name']}")
    print(f"Response: {agent_response.json()}")

    # Now we can re-run the scope with the new agent
    updated_scope_response = requests.post(
        "https://api.example.com/orchestrator/scope",
        json={
            "goal": "Build a journaling AI that reflects on memory with emotional analysis",
            "project_id": scope["project_id"]
        }
    )

    updated_scope = updated_scope_response.json()
    print(f"Skill validation passed: {updated_scope['skill_validation_passed']}")
```
