# Pessimist Agent Documentation

## Overview

The Pessimist Agent is a specialized agent that evaluates loop summaries, flags overconfidence, and injects memory tags for tone realism and self-auditing. It serves as a counterbalance to natural optimism bias in self-reporting, ensuring that the system maintains realistic assessments of its own performance.

## Features

- **Tone Evaluation**: Analyzes loop summaries to detect optimistic language and vague accomplishments
- **Bias Detection**: Identifies specific types of biases including optimism bias, vague summaries, and confidence mismatches
- **Alert Generation**: Creates detailed alerts with bias tags, suggestions, and confidence scores
- **Memory Integration**: Injects alerts and bias tags into memory for future reference
- **Feedback Analysis**: Incorporates operator feedback to adjust bias detection sensitivity

## Implementation Details

### Core Components

1. **Tone Evaluation**
   - `evaluate_summary_tone()`: Analyzes text for optimistic and vague language
   - Uses predefined phrase lists and feedback-adjusted scoring

2. **Bias Detection**
   - `detect_optimism_bias()`: Identifies excessive optimism in summaries
   - `detect_vague_summary()`: Flags summaries that lack specific accomplishments
   - `detect_confidence_mismatch()`: Compares plan confidence with summary tone

3. **Alert Generation**
   - `generate_pessimist_alert()`: Creates structured alerts with bias tags and suggestions
   - Includes severity ratings and confidence scores

4. **Memory Integration**
   - `inject_memory_alert()`: Adds alerts to memory and updates summary metadata
   - `process_loop_summary()`: Main entry point that orchestrates the evaluation process

### Integration Points

- **Loop Controller**: Invokes the Pessimist Agent after loop completion
- **Agent Registry**: Registers the Pessimist Agent in the system
- **Memory Tags**: Defines standard bias tags used by the Pessimist Agent

## Usage

### Basic Usage

```python
from agents.pessimist_agent import process_loop_summary

# Process a loop summary
updated_memory = process_loop_summary(
    loop_id="123",
    summary="Successfully implemented all features perfectly without any issues.",
    feedback=[{"text": "Some features are still buggy.", "rating": 2}],
    memory=current_memory,
    plan_confidence_score=0.5
)

# Check for alerts
if "pessimist_alerts" in updated_memory:
    alerts = updated_memory["pessimist_alerts"]
    for alert in alerts:
        print(f"Alert: {alert['alert_type']}")
        print(f"Bias tags: {', '.join(alert['bias_tags'])}")
        print(f"Suggestion: {alert['suggestion']}")
```

### Loop Controller Integration

```python
from orchestrator.modules.loop_controller import evaluate_loop_with_pessimist

# Evaluate a loop with the Pessimist Agent
result = evaluate_loop_with_pessimist(
    project_id="project_123",
    loop_id=42,
    memory=current_memory,
    config={"enabled": True, "evaluation_threshold": 0.6}
)

# Check the result
if result["status"] == "alert":
    print(f"Bias detected: {result['message']}")
    for alert in result["alerts"]:
        print(f"Alert type: {alert['alert_type']}")
```

## Configuration Options

The Pessimist Agent can be configured through the loop controller:

```python
config = {
    "enabled": True,              # Enable/disable Pessimist Agent evaluation
    "evaluation_threshold": 0.6,  # Only evaluate loops with confidence above this
    "auto_inject_alerts": True    # Automatically inject alerts into memory
}
```

## Bias Tags

The Pessimist Agent uses the following bias tags:

- **optimism_bias**: Tendency to overestimate positive outcomes
- **vague_summary**: Using imprecise language to obscure lack of concrete progress
- **overconfidence**: Excessive certainty in abilities or outcomes
- **feedback_dismissal**: Ignoring or minimizing negative feedback
- **timeline_compression**: Unrealistic compression of time needed for tasks
- **scope_creep**: Expanding scope without acknowledging increased complexity
- **achievement_inflation**: Exaggerating the significance of accomplishments
- **complexity_underestimation**: Underestimating the complexity of tasks
- **risk_blindness**: Failing to acknowledge or address potential risks

## Testing

The Pessimist Agent includes comprehensive unit tests that verify:

- Tone evaluation with different types of summaries
- Bias detection for various scenarios
- Alert generation and memory injection
- Integration with memory tags

Run the tests with:

```bash
python -m unittest tests.agents.test_pessimist_agent
```
