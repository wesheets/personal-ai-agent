# Agent Creation Module

## Overview

The Agent Creation Module enables the system (or users) to create new agents based on the output of `agent_creation_suggestions[]` from the `/orchestrator/scope` endpoint. This completes the workflow loop:

```
scope → detect gap → suggest agent → create agent → present
```

The module allows for dynamic expansion of the agent ecosystem by creating new agents with specific skills and tone profiles to fill capability gaps identified during project scoping.

## Endpoint

```
POST /agent/create
```

## Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agent_name | string | Yes | Name for the new agent (with or without "-agent" suffix) |
| skills | array | Yes | List of skills the agent possesses |
| tone_profile | object | Yes | Agent's tone characteristics |
| description | string | Yes | Brief description of the agent's purpose |

### Tone Profile Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| style | string | Yes | Writing/communication style (e.g., "gentle", "formal") |
| emotion | string | Yes | Emotional tone (e.g., "empathetic", "neutral") |
| vibe | string | Yes | Overall presence (e.g., "grief companion", "strategic-advisor") |
| persona | string | Yes | Character description |

### Example Request

```json
{
  "agent_name": "echo",
  "skills": ["emotional_analysis", "summarize"],
  "tone_profile": {
    "style": "gentle",
    "emotion": "empathetic",
    "vibe": "grief companion",
    "persona": "Echo is a reflective presence for healing work"
  },
  "description": "Tone-aware agent for emotional memory processing"
}
```

## Response Schema

### Success Response

```json
{
  "status": "success",
  "agent_id": "echo",
  "message": "Agent echo successfully created and registered."
}
```

### Error Response: Duplicate Agent

```json
{
  "status": "error",
  "agent_id": "echo",
  "message": "Agent 'echo' already exists."
}
```

### Error Response: Missing Fields (422 Unprocessable Entity)

```json
{
  "detail": "agent_name is required"
}
```

or

```json
{
  "detail": "At least one skill is required"
}
```

## Implementation Details

### Agent Validation

The module validates the agent input schema to ensure:
- `agent_name` is provided
- At least one skill is specified
- All required tone profile fields are present

### Agent Registration

When a valid agent is submitted:
1. The module checks for duplicates by agent name
2. If no duplicate exists, it creates a new agent entry with:
   - The provided name, skills, tone profile, and description
   - Default version (0.1.0)
   - Default status ("experimental")
   - Generated entrypoint path based on the agent name

3. The new agent is appended to the `agent_manifest.json` file
4. A success response is returned with the agent ID

### Duplicate Prevention

The module prevents duplicate agents by:
1. Checking if an agent with the same name already exists in the manifest
2. Returning an error response if a duplicate is found
3. Handling agent names with or without the "-agent" suffix

### Optional Schema Fallbacks

While the current implementation requires all fields, future enhancements could include:
- Default tone profiles for missing tone information
- Skill inference based on agent name and description
- Auto-generation of persona based on other tone profile elements

## Connection to Agent Creation Suggestions

This endpoint is designed to work with the `agent_creation_suggestions[]` array returned by the `/orchestrator/scope` endpoint. When a project scope analysis detects skill gaps, it suggests new agents that can be created using this endpoint.

### Example Workflow

1. Call `/orchestrator/scope` with a project goal
2. Receive response with `agent_creation_suggestions[]`
3. For each suggestion, call `/agent/create` with the suggested parameters
4. Verify the new agent was created successfully
5. Use `/agent/present` to view the new agent's self-presentation

## Validation Rules

- No duplicate agent_id: Each agent must have a unique name
- Skills required: At least one skill must be specified
- Complete tone profile: All tone profile fields must be provided
- Valid agent name: Agent names should be lowercase, alphanumeric with hyphens

## Usage Examples

### Creating a New Agent from Scope Suggestions

```javascript
// After receiving scope results with agent suggestions
const scopeResult = await fetch('/orchestrator/scope', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    goal: "Build an emotional journaling system",
    project_id: "emotional-journal"
  })
});

const scopeData = await scopeResult.json();

// For each suggested agent
for (const suggestion of scopeData.agent_creation_suggestions) {
  // Create the suggested agent
  const createResult = await fetch('/agent/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_name: suggestion.name,
      skills: suggestion.skills,
      tone_profile: suggestion.tone_profile,
      description: suggestion.reason
    })
  });
  
  const createData = await createResult.json();
  console.log(`Agent creation result: ${createData.status}`);
}
```

### Manual Agent Creation

```bash
curl -X POST http://localhost:8000/agent/create \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "echo",
    "skills": ["emotional_analysis", "summarize"],
    "tone_profile": {
      "style": "gentle",
      "emotion": "empathetic",
      "vibe": "grief companion",
      "persona": "Echo is a reflective presence for healing work"
    },
    "description": "Tone-aware agent for emotional memory processing"
  }'
```

## Future Enhancements

Potential future enhancements to the Agent Creation module include:

- Support for agent template selection
- Automatic stub file creation for the agent implementation
- Integration with a training pipeline for new agents
- Validation of skills against a master skills registry
- Support for agent relationships and dependencies
- Agent versioning and update mechanisms
