# Agent Self-Presentation Module

## Overview

The Agent Self-Presentation module enables any agent (HAL, ASH, ECHO, future) to describe themselves in a structured, narrative format similar to how the Orchestrator presents information. This brings agents up to Orchestrator-level expressiveness for use in Control Room UI, system reflections, dynamic delegation, persona visualization, and TED-style runtime logs.

## Endpoint

```
POST /agent/present
```

## Request Schema

| Field    | Type   | Required | Description                                                          |
| -------- | ------ | -------- | -------------------------------------------------------------------- |
| agent_id | string | Yes      | Identifier of the agent to present (with or without "-agent" suffix) |

### Example Request

```json
{
  "agent_id": "hal"
}
```

## Response Schema

| Field            | Type   | Description                                                  |
| ---------------- | ------ | ------------------------------------------------------------ |
| agent_id         | string | Identifier of the agent                                      |
| description      | string | Brief description of the agent                               |
| skills           | array  | List of agent skills                                         |
| tone_profile     | object | Agent's tone characteristics (style, emotion, vibe, persona) |
| ideal_tasks      | array  | List of tasks the agent is well-suited for                   |
| present_markdown | string | Markdown presentation of the agent                           |
| narration_text   | string | First-person narrative description for the agent             |

### Example Response

```json
{
  "agent_id": "hal",
  "description": "Safety and constraint monitoring system",
  "skills": ["reflect", "summarize", "monitor", "analyze"],
  "tone_profile": {
    "style": "formal",
    "emotion": "neutral",
    "vibe": "guardian",
    "persona": "HAL-9000 with fewer red flags"
  },
  "ideal_tasks": [
    "Reflect on user interactions and patterns",
    "Provide thoughtful analysis of past decisions",
    "Generate concise summaries of memory traces",
    "Condense complex information into key points",
    "Monitor system performance and health"
  ],
  "present_markdown": "# HAL: Self-Presentation\n\n## Description\nSafety and constraint monitoring system\n\n## Skills\n- reflect\n- summarize\n- monitor\n- analyze\n\n## Ideal Tasks\n- Reflect on user interactions and patterns\n- Provide thoughtful analysis of past decisions\n- Generate concise summaries of memory traces\n- Condense complex information into key points\n- Monitor system performance and health\n\n## Persona\nHAL-9000 with fewer red flags\n\n## Tone Profile\n- Style: formal\n- Emotion: neutral\n- Vibe: guardian",
  "narration_text": "I am HAL. I specialize in reflect, summarize, monitor, and analyze. Safety and constraint monitoring system I maintain professional standards in all interactions."
}
```

## Error Responses

### Agent Not Found (404)

If the specified agent is not found in the agent manifest:

```json
{
  "detail": "Agent 'nonexistent' not found in manifest"
}
```

### Missing Required Field (422)

If the agent_id is not provided:

```json
{
  "detail": "agent_id is required"
}
```

## Implementation Details

### Agent Information Retrieval

The module retrieves agent information from the `agent_manifest.json` file, which contains details about all available agents including their descriptions, skills, and tone profiles.

### Ideal Tasks Generation

If ideal tasks are not explicitly defined for an agent, the module automatically generates appropriate tasks based on the agent's skills using a comprehensive skill-to-task mapping.

### Tone Profile Handling

The module handles incomplete tone profiles by filling in missing fields with system defaults:

- Default style: "neutral"
- Default emotion: "neutral"
- Default vibe: "assistant"
- Default persona: "Helpful assistant"

### Markdown Generation

The module generates a structured markdown presentation for each agent with sections for:

- Description
- Skills
- Ideal Tasks
- Persona
- Tone Profile

### Narration Text Generation

The module creates a first-person narrative description that adapts to the agent's tone profile, making each agent's self-presentation unique and aligned with their character.

## Usage in Control Room

The Agent Self-Presentation module is designed to be used in the Control Room UI to provide users with clear, structured information about available agents. When a user selects an agent in the Control Room, the system can call the `/agent/present` endpoint to retrieve and display the agent's self-presentation.

### Example Control Room Integration

```javascript
// Control Room agent selection handler
async function onAgentSelected(agentId) {
  try {
    const response = await fetch('/agent/present', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ agent_id: agentId })
    });

    if (response.status === 404) {
      displayError(`Agent ${agentId} not found`);
      return;
    }

    const agentPresentation = await response.json();

    // Display the agent's markdown presentation
    document.getElementById('agent-presentation').innerHTML = markdownToHtml(
      agentPresentation.present_markdown
    );

    // Use the narration text for text-to-speech or tooltips
    document.getElementById('agent-narration').textContent = agentPresentation.narration_text;

    // Update the agent info panel with structured data
    updateAgentInfoPanel(agentPresentation);
  } catch (error) {
    console.error('Failed to load agent presentation:', error);
    displayError('Failed to load agent information');
  }
}
```

## Fallback Behavior

If an agent is not found, the endpoint returns a structured 404 error with a clear error message. This allows the Control Room UI to display an appropriate error message to the user.

In cases where the Control Room needs to display information about an agent that doesn't exist in the manifest, it can fall back to a generic agent presentation or prompt the user to create a new agent.

## Testing

The module includes comprehensive tests in `/tests/test_agent_present.py` that verify:

- Valid agent presentation
- Error handling for missing agents
- Validation of required fields
- Markdown formatting
- Handling of agent IDs with and without suffixes
- Generation of non-empty narration text

## Future Enhancements

Potential future enhancements to the Agent Self-Presentation module include:

- Support for custom agent icons or avatars
- Integration with a text-to-speech system for narration
- Dynamic generation of example code snippets for each agent
- Performance metrics and usage statistics
- Relationship mapping between agents
- Customizable presentation templates
