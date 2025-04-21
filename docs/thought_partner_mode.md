# Orchestrator Thought Partner Mode

This module implements the Thought Partner Mode for the Orchestrator, enabling it to act as a Socratic co-architect by analyzing prompts, asking clarifying questions, suggesting refinements, and storing prompt memory for future reference.

## Overview

The Thought Partner Mode enhances the Orchestrator's ability to understand and refine user prompts before planning. It analyzes prompts to determine intent, confidence, emotional tone, and ambiguity, then generates Socratic-style questions to help clarify requirements.

## Features

- **Prompt Analysis**: Evaluates prompts to extract intent, confidence score, emotional tone, and ambiguous phrases
- **Reflection Questions**: Generates Socratic-style questions based on analysis results
- **Memory Integration**: Stores and retrieves prompt analysis for future reference
- **Mode Dispatcher**: Connects Thought Partner Mode to the rest of the system

## Usage

### Basic Usage

```python
from orchestrator.modes.thought_partner import analyze_prompt, generate_reflection_questions
from orchestrator.mode_dispatcher import ModeDispatcher

# Create a mode dispatcher
dispatcher = ModeDispatcher()

# Set the mode to Thought Partner
dispatcher.set_mode("thought_partner")

# Process a prompt
result = dispatcher.process_prompt(
    prompt="Build a simple dashboard with data filters",
    project_id="my-project",
    loop_id=123,
    memory={}
)

# Check the analysis and reflection questions
print(f"Intent: {result['analysis']['interpreted_intent']}")
print(f"Confidence: {result['analysis']['confidence_score']}")
print(f"Ambiguous phrases: {result['analysis']['ambiguous_phrases']}")
print(f"Questions: {result['reflection_questions']}")
```

### Toggling Sage Mode

```python
# Enable Sage Mode (automatically sets mode to Thought Partner)
dispatcher.toggle_sage_mode(True)

# Disable Sage Mode
dispatcher.toggle_sage_mode(False)
```

### Retrieving Previous Analysis

```python
# Get the latest prompt analysis for a project
previous_analysis = dispatcher.get_previous_analysis("my-project", memory)
if previous_analysis:
    print(f"Previous intent: {previous_analysis['interpreted_intent']}")
```

## Configuration

The Mode Dispatcher can be configured with custom settings:

```python
config = {
    "default_mode": "thought_partner",  # Default is "architect"
    "sage_mode_enabled": True           # Default is True
}
dispatcher = ModeDispatcher(config)
```

## Schema

The prompt analysis follows the schema defined in `schemas/prompt_analysis.schema.json`, which includes:

- `interpreted_intent`: The interpreted intent of the prompt
- `confidence_score`: Confidence score for the interpretation (0.0 to 1.0)
- `emotional_tone`: Detected emotional tone of the prompt
- `ambiguous_phrases`: List of ambiguous phrases detected in the prompt
- `reflection_questions`: Socratic-style questions generated based on the analysis
- `timestamp`: ISO 8601 timestamp when the analysis was created
- `project_id`: Identifier for the project
- `loop_id`: Identifier for the loop
- `prompt_quality_score`: Optional score indicating the quality of the prompt
- `prompt_variants`: Optional suggested variants of the prompt for clarity
- `domain_context`: Optional domain-specific context extracted from the prompt
