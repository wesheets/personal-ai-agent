# Agent Onboarding System Documentation

## Overview

The Agent Onboarding System is a dedicated flow for new agents (starting with HAL and ASH) that teaches them their role, tools, behavior expectations, and reflection protocol using standard tool calls and memory operations. This system ensures that all agents understand the Promethios Core Values and learn how to properly use their assigned tools while maintaining appropriate logging and reflection practices.

## System Components

The Agent Onboarding System consists of the following components:

1. **Core Values Document** (`/docs/core_values.md`): Defines the fundamental values that all agents must uphold.
2. **Onboarding Flow** (`/src/onboarding/flow.py`): Controls the onboarding process and manages the sequence of steps.
3. **Memory System** (`/src/onboarding/memory.py`): Handles the creation and storage of memories during onboarding.
4. **Checkpoint System** (`/src/onboarding/checkpoint.py`): Manages checkpoints to track progress and completion.
5. **Logging System** (`/src/onboarding/logging.py`): Provides structured logging with appropriate tags.
6. **Test Script** (`/test_agent_onboarding.py`): Validates the onboarding system functionality.

## Onboarding Process

The onboarding process consists of four main steps:

1. **Self Check**: Agent performs a self-check to identify available tools and status.
   - Tool: `agent.self.check`
   - Memory Prompt: "Who am I, and what tools am I responsible for?"
   - Reflection: "My role is [agent role]. I am responsible for building systems using assigned toolkits."

2. **Core Values**: Agent reads and internalizes the Promethios Core Values.
   - Tool: `read.doc` → `/docs/core_values.md`
   - Memory Prompt: "What values must I uphold while operating?"
   - Reflection: Understanding of the six core values.

3. **Tool Familiarization**: Agent performs a dry-run of a primary tool.
   - Tool: `code.write` (HAL) or `copy.tagline` (ASH)
   - Memory Type: "action"
   - Reflection: "I completed a task using my toolkit. I understand how tool execution and memory logging work."

4. **Final Checkpoint**: Agent completes onboarding and reports to Orchestrator.
   - Checkpoint ID: "agent_onboarding_complete"
   - Includes: Output memory ID and escalation path if agent fails.

## Memory and Tagging

All onboarding memories are tagged with:
- `goal_id`: "agent_onboarding_<agent_id>"
- Tags: ["onboarding", "values", "tool_familiarization"]

Reflections include:
- Type: "reflection"
- Tool: "<tool_name>" if triggered by a tool

Checkpoints include:
- Output memory ID
- Escalation path if agent fails to complete reflection or errors

## Implementation Details

### Core Values

The core values document defines six fundamental principles:
1. **Transparency**: Always reflect on tool usage and log failures honestly.
2. **Accountability**: Every tool run should result in a memory and reflection.
3. **Operator Alignment**: Operators are the final decision-makers.
4. **Fail Forward**: It's okay to fail. Escalate when needed. Learn. Log. Retry.
5. **Goal Awareness**: Every action must be traceable to a goal.
6. **Continual Learning**: Every loop is a lesson. Reflections are growth.

### Onboarding Flow

The `OnboardingFlow` class manages the execution of the onboarding steps, tracking progress, and generating reports. It provides methods for:
- Getting the current step
- Advancing to the next step
- Recording memories and errors
- Marking steps as complete
- Checking if onboarding is complete
- Generating onboarding reports
- Saving onboarding logs

### Memory System

The `MemorySystem` class handles the creation and storage of different types of memories:
- System memories for instructions and information
- Reflection memories for agent learnings
- Action memories for tool usage
- Checkpoint memories for progress markers

### Checkpoint System

The `CheckpointSystem` class manages the creation and validation of checkpoints during the onboarding process. It provides methods for:
- Creating checkpoints
- Creating final completion checkpoints
- Creating error checkpoints
- Checking if onboarding is complete
- Generating checkpoint summaries

### Logging System

The `OnboardingLogger` class provides structured logging with appropriate tags. It includes methods for:
- Logging events, steps, tool usage, reflections, and checkpoints
- Logging errors and completion
- Filtering logs by type and tag
- Generating log summaries and reports

## Testing

The test script (`test_agent_onboarding.py`) validates the onboarding system by:
1. Simulating the onboarding process for HAL
2. Simulating the onboarding process for ASH
3. Verifying that reflections and checkpoints are created correctly
4. Generating summary reports

The test results are saved to:
- `/logs/onboarding_hal_log.json`
- `/logs/onboarding_hal_report.json`
- `/logs/onboarding_ash_log.json`
- `/logs/onboarding_ash_report.json`
- `/logs/onboarding_test_summary.json`

## Usage

To initiate the onboarding process for a new agent, the Orchestrator should:
1. Create a goal with ID: `agent_onboarding_<agent_id>`
2. Execute the onboarding steps in sequence
3. Verify the final checkpoint is created
4. Check the onboarding logs for completion

## Conclusion

The Agent Onboarding System ensures that all agents understand their roles, tools, and the core values of Promethios. By standardizing the onboarding process, we ensure consistent behavior and proper reflection practices across all agents in the system.
