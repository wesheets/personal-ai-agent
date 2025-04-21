# Historian Agent Documentation

## Overview

The Historian Agent is a passive cognitive drift detection system that monitors the alignment between loop summaries and the system's declared beliefs. It helps ensure that the system maintains consistency with its core principles over time by detecting when certain beliefs are being forgotten or ignored.

## Features

- **Belief Alignment Scoring**: Evaluates how well loop summaries align with system beliefs
- **Forgotten Beliefs Detection**: Identifies beliefs that haven't been referenced in recent loops
- **Memory Drift Alerts**: Generates alerts when significant drift is detected
- **CTO Warnings**: Escalates severe drift issues to CTO warnings
- **Non-blocking Operation**: Works passively without interrupting normal loop execution

## Components

### 1. Historian Agent (`agents/historian_agent.py`)

The core agent implementation with the following key functions:

- `generate_belief_alignment_score()`: Compares loop summaries against beliefs to calculate alignment
- `detect_forgotten_beliefs()`: Identifies beliefs not referenced in recent loops
- `generate_historian_alert()`: Creates and injects alerts into memory
- `analyze_loop_summary()`: Main function that orchestrates the analysis process

### 2. Belief Reference Utility (`memory/belief_reference.py`)

Utility functions for working with beliefs:

- `load_beliefs_from_file()`: Loads system beliefs from JSON file
- `extract_belief_keywords()`: Extracts significant keywords from beliefs
- `scan_text_for_belief()`: Scans text for references to specific beliefs
- `get_recent_loops()`: Retrieves recent loop summaries from memory
- `get_belief_references_over_time()`: Tracks belief references across multiple loops

### 3. Historian Alert Schema (`schemas/historian_alert.schema.json`)

JSON schema defining the structure of historian alerts:

- `loop_id`: Identifier of the loop that triggered the alert
- `alert_type`: Type of alert (belief_drift_detected or belief_alignment_check)
- `missing_beliefs`: List of beliefs not referenced in recent loops
- `loop_belief_alignment_score`: Alignment score between 0.0 and 1.0
- `suggestion`: Recommended action based on alignment score
- `timestamp`: When the alert was generated

### 4. Loop Controller Integration (`orchestrator/modules/loop_controller.py`)

Integration with the loop controller:

- `analyze_loop_with_historian_agent()`: Analyzes loop summaries with the historian agent
- `handle_loop_completion()`: Handles loop completion with historian agent analysis

## Usage

### Basic Usage

The Historian Agent is automatically invoked after a loop completes:

```python
# Loop controller will call this after a loop completes
result = handle_loop_completion(
    loop_id="loop-123",
    loop_summary="The agent provided accurate information while respecting user privacy.",
    memory=current_memory
)

# Updated memory with historian alerts
updated_memory = result["memory"]
```

### Configuration Options

The Historian Agent can be configured with the following options:

```python
config = {
    "historian_agent": {
        "enabled": True,  # Enable/disable the historian agent
        "beliefs_file": "orchestrator_beliefs.json",  # Path to beliefs file
        "recent_loops_count": 10  # Number of recent loops to analyze
    }
}

result = handle_loop_completion(
    loop_id="loop-123",
    loop_summary="The agent provided accurate information.",
    memory=current_memory,
    config=config
)
```

### Accessing Historian Alerts

Historian alerts are stored in memory and can be accessed as follows:

```python
if "historian_alerts" in memory:
    alerts = memory["historian_alerts"]
    for alert in alerts:
        print(f"Alert type: {alert['alert_type']}")
        print(f"Alignment score: {alert['loop_belief_alignment_score']}")
        print(f"Missing beliefs: {alert['missing_beliefs']}")
        print(f"Suggestion: {alert['suggestion']}")
```

## Alignment Score Calculation

The alignment score is calculated based on several factors:

1. **Exact Matches**: When a belief appears verbatim in the summary (score: 1.0)
2. **Partial Exact Matches**: When at least half of a belief appears as a continuous string (score: 0.85)
3. **Term Matches**: Based on the proportion of significant terms from the belief found in the summary
   - For high match ratios (>50%), scores are boosted using a progressive scale
   - For lower match ratios, a weight of 1.8 is applied to the ratio

The final alignment score is the average of individual belief scores.

## Alert Types

1. **Belief Drift Detected**: Generated when one or more beliefs are not referenced in recent loops
2. **Belief Alignment Check**: Generated when all beliefs are referenced but alignment score is below threshold

## CTO Warnings

When alignment score falls below 0.3 and there are missing beliefs, a CTO warning is generated with:

- Warning type: "belief_drift"
- Message indicating the number of missing beliefs
- Loop ID and timestamp

## Testing

Comprehensive unit tests are available in `tests/agents/test_historian_agent.py` covering:

- Belief alignment scoring for high, medium, and low alignment cases
- Detection of forgotten beliefs
- Generation of historian alerts and CTO warnings
- Utility functions for belief reference tracking

## Future Improvements

Potential enhancements for future versions:

1. **Semantic Matching**: Use embeddings for more accurate semantic matching
2. **Trend Analysis**: Track belief alignment trends over time
3. **Adaptive Thresholds**: Adjust thresholds based on historical data
4. **Belief Importance Weighting**: Weight beliefs by importance for more nuanced scoring
5. **Integration with Sage**: Automatic triggering of Sage for realignment when drift exceeds thresholds
