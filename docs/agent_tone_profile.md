# Agent Tone Profile

## Overview

The Agent Tone Profile feature adds emotional coherence and voice consistency to the Promethios OS by associating a tone profile with each agent. This enables agents to write tone-aware memory and maintain a consistent voice across different interactions.

## Tone Profile Schema

Each agent's configuration now includes a `tone_profile` field with the following attributes:

```json
"tone_profile": {
  "style": "concise",
  "emotion": "neutral",
  "vibe": "strategic-advisor",
  "persona": "Efficient system orchestrator with a focus on clarity and precision"
}
```

### Attributes

| Attribute | Description | Examples |
|-----------|-------------|----------|
| `style` | Writing style of the agent | formal, concise, conversational, poetic, direct, analytical |
| `emotion` | Emotional tone of the agent | neutral, warm, blunt, calm, enthusiastic, curious |
| `vibe` | Social role or archetype | strategic-advisor, guardian, coach, mentor, rebel, analyst |
| `persona` | Freeform personality description | "HAL-9000 with fewer red flags", "Supportive life coach with a focus on personal growth" |

## Implementation Details

### Agent Configuration

Agent tone profiles are defined in the agent manifest file at `/config/agent_manifest.json`. Each agent entry includes a `tone_profile` object with the attributes described above.

### Memory Writing

When a memory is written with an agent_id, the system:

1. Looks up the agent's tone profile from the agent manifest
2. Injects the tone profile into the memory object as `agent_tone`
3. Stores the memory with the tone profile in both local and shared memory

Example memory object with agent tone:

```json
{
  "memory_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "hal-agent",
  "type": "observation",
  "content": "System diagnostics complete. All functions nominal.",
  "tags": ["system", "diagnostics"],
  "timestamp": "2025-04-11T06:15:42.123456",
  "agent_tone": {
    "style": "formal",
    "emotion": "neutral",
    "vibe": "guardian",
    "persona": "HAL-9000 with fewer red flags"
  }
}
```

### Memory Reading

The `/read` endpoint automatically includes the `agent_tone` field in memory objects returned from queries. No additional parameters are needed to access this information.

## Usage Examples

### Reading Memories with Agent Tone

```javascript
// Example API call to read memories with agent tone
const response = await fetch('/app/modules/read?agent_id=hal-agent&limit=5');
const data = await response.json();

// Access agent tone from the first memory
const firstMemory = data.memories[0];
const agentTone = firstMemory.agent_tone;

console.log(`Agent ${firstMemory.agent_id} has a ${agentTone.style} style with ${agentTone.emotion} emotion`);
```

### Using Agent Tone in UI

```javascript
// Example of using agent tone to style UI elements
function getAgentColorScheme(agentTone) {
  if (agentTone.emotion === 'warm') {
    return 'orange.500';
  } else if (agentTone.style === 'formal') {
    return 'blue.700';
  } else {
    return 'gray.500';
  }
}

// Apply styling based on agent tone
const memoryElement = document.getElementById('memory-content');
memoryElement.style.color = getAgentColorScheme(memory.agent_tone);
```

## Benefits

The Agent Tone Profile feature provides several benefits:

1. **Voice Consistency**: Ensures agents maintain a consistent voice across interactions
2. **Emotional Coherence**: Adds emotional depth to agent communications
3. **UI Enhancement**: Enables tone-aware UI elements and styling
4. **Orchestration**: Facilitates tone-aware task delegation and agent selection
5. **User Experience**: Creates more natural and engaging interactions

## Future Extensions

This implementation lays the groundwork for future tone-aware features:

1. **Tone-aware orchestration logic**: Selecting agents based on required tone
2. **Tone-shifting UI controls**: Allowing users to adjust agent tone preferences
3. **Delegation with tone preservation**: Maintaining consistent tone across delegated tasks
4. **Tone-aware summarization**: Generating summaries that match agent tone
5. **Reflection with tone awareness**: Creating reflections that preserve agent personality
