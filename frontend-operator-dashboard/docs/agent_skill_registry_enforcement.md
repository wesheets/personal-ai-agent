# Agent Skill Registry Enforcement

## Overview

This document describes the implementation of Agent Skill Registry Enforcement in the Promethios OS. This feature ensures that agents can only be assigned tasks they're qualified to perform based on their declared skills.

## Implementation Details

### 1. Agent Skills in Agent Manifest

The `agent_manifest.json` file already contains a `skills` field for each agent, listing their capabilities:

```json
{
  "hal-agent": {
    "version": "1.0.0",
    "description": "Safety and constraint monitoring system",
    "status": "active",
    "entrypoint": "app/agents/hal_agent.py",
    "tone_profile": {
      "style": "formal",
      "emotion": "neutral",
      "vibe": "guardian",
      "persona": "HAL-9000 with fewer red flags"
    },
    "skills": ["reflect", "summarize", "monitor", "analyze"]
  },
  "ash-agent": {
    "version": "0.9.0",
    "description": "Clinical analysis and protocol-driven agent",
    "status": "active",
    "entrypoint": "app/agents/ash_agent.py",
    "tone_profile": {
      "style": "precise",
      "emotion": "calm",
      "vibe": "medical-professional",
      "persona": "Methodical clinician with a focus on accuracy and protocol adherence"
    },
    "skills": ["delegate", "execute", "analyze", "protocol"]
  }
}
```

### 2. Enhanced Skill Validation in `/orchestrator/scope`

The `/orchestrator/scope` endpoint has been enhanced to validate agent skills against required tools:

#### 2.1 Tool-to-Agent Mapping

A mapping of tools to potential agents has been added to help identify which agents can handle specific tools:

```python
tool_to_agents = {
    "reflect": ["hal", "lifetree"],
    "summarize": ["hal"],
    "delegate": ["ash"],
    "execute": ["ash"],
    "write": ["memory", "hal"],
    "read": ["memory", "hal"],
    "train": ["neureal"],
    "loop": ["core-forge"],
    "task/status": ["ops"]
}
```

#### 2.2 Module Qualification Tracking

The system now tracks which required modules have a qualified agent:

```python
module_has_qualified_agent = {module: False for module in required_modules}
```

#### 2.3 Comprehensive Skill Validation

The skill validation process now:
- Checks if each agent has the skills for their assigned tools
- Tracks which modules have qualified agents
- Identifies unmatched tasks when no agent has the required skill
- Sets `skill_validation_passed` to `false` when any required module lacks a qualified agent

#### 2.4 Confidence Score Adjustment

Confidence scores are now adjusted based on skill validation:
- Agents without required skills get a confidence score of 0.0
- When overall validation fails but an agent has its own skills, its score is reduced
- Detailed logging is added to help with debugging

```python
# Adjust score based on skill validation
if not has_all_skills:
    # Set to 0.0 if agent doesn't have required skills
    initial_score = 0.0
    print(f"Agent {agent.agent_name} lacks skills for: {', '.join(missing_skills)}, setting confidence to 0.0")
elif not skill_validation_passed:
    # Reduce score if overall validation failed but this agent has its skills
    initial_score = max(initial_score * 0.7, 0.5)
    print(f"Overall skill validation failed, reducing {agent.agent_name}'s confidence to {initial_score:.2f}")
```

### 3. Response Structure

The `/orchestrator/scope` endpoint response includes:

#### 3.1 Skill Validation Status

```json
"skill_validation_passed": true
```

This field indicates whether all required tools have matching agent skills.

#### 3.2 Unmatched Tasks

```json
"unmatched_tasks": [
  {
    "tool": "summarize",
    "reason": "No agent declared capability for summarize"
  }
]
```

This field lists tools that don't have matching agent skills, including the reason.

## Testing

The implementation includes comprehensive tests in `tests/test_orchestrator_scope.py`:

- Basic skill validation testing
- Scenario where no agent can summarize
- Assertions for `skill_validation_passed` field
- Verification of unmatched tasks

## Benefits

This implementation provides several benefits:

1. **Prevents Misassignment**: Ensures agents are only assigned tasks they're qualified to perform
2. **Early Warning**: Identifies capability gaps before project execution
3. **Confidence Scoring**: Provides accurate confidence scores based on skill matching
4. **Transparency**: Clearly communicates which tasks lack qualified agents

## Future Enhancements

Potential future enhancements include:

1. **Skill Level Gradation**: Add skill levels (beginner, intermediate, expert)
2. **Dynamic Skill Learning**: Allow agents to learn new skills during operation
3. **Skill Verification**: Add verification tests to confirm agents can perform claimed skills
4. **Fallback Mechanisms**: Implement fallback strategies when no agent has a required skill
