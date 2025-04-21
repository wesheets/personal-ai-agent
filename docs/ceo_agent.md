# CEO Agent

The CEO Agent evaluates loop summaries for alignment with system beliefs, tracks operator satisfaction, and logs strategic insights for system improvement.

## Overview

The CEO Agent serves as a strategic oversight component in the Promethios system, ensuring that the agent's operations remain aligned with core system beliefs and values. It analyzes completed loop summaries, evaluates their alignment with predefined system beliefs, tracks operator satisfaction trends, and generates strategic insights when misalignments or concerning trends are detected.

## Features

- **Belief Alignment Evaluation**: Analyzes loop summaries to determine how well they align with core system beliefs
- **Missing Belief Detection**: Identifies which specific beliefs are not being referenced or followed in loop summaries
- **Operator Satisfaction Tracking**: Monitors trends in operator feedback to detect improvements or declines
- **Strategic Insight Generation**: Creates actionable insights with recommendations when alignment issues are detected
- **CTO Warning Escalation**: Automatically escalates significant satisfaction declines to CTO warnings

## Implementation Details

The CEO Agent is implemented in `agents/ceo_agent.py` and relies on the belief similarity utilities in `memory/belief_similarity.py`. It integrates with the loop controller to analyze loop summaries after completion.

### Core Functions

#### `evaluate_loop_alignment(loop_summary, beliefs)`

Evaluates a loop summary for alignment with system beliefs, returning:
- Alignment score (0.0 to 1.0)
- List of missing beliefs
- Evaluation status (excellent, good, moderate, poor)
- Descriptive message

#### `generate_ceo_insight(loop_id, loop_summary, beliefs, recent_loops, alignment_threshold)`

Generates a CEO insight when alignment is below threshold or beliefs are missing, including:
- Insight type (vision_drift_warning, belief_omission_alert, alignment_improvement_needed)
- Alignment score
- Missing beliefs
- Recommendation for improvement
- Trend context based on recent loops

#### `track_operator_satisfaction_trend(operator_reviews, window_size)`

Tracks operator satisfaction trends based on review scores, providing:
- Review delta between recent and previous periods
- Average scores for recent and previous periods
- Trend status (significant_improvement, improvement, stable, decline, significant_decline)
- Descriptive message

#### `analyze_loop_with_ceo_agent(loop_id, loop_summary, beliefs, memory, config)`

Main entry point that combines all functionality to analyze a loop and update memory with insights and satisfaction trends.

## Integration

The CEO Agent integrates with the system through:

1. **Agent Registry**: Registered as "ceo-agent" in both AGENT_REGISTRY and AGENT_PERSONALITIES
2. **Loop Controller**: Integrated in the handle_loop_completion function to analyze loops after completion
3. **Memory System**: Stores insights in memory under "ceo_insights" and satisfaction trends under "satisfaction_trends"

### Loop Controller Integration

The loop controller calls the CEO Agent after the Historian Agent during loop completion:

```python
def handle_loop_completion(loop_id, loop_summary, memory, config=None):
    # First analyze with historian agent
    historian_result = analyze_loop_with_historian_agent(...)
    memory = historian_result["memory"]
    
    # Then analyze with CEO agent
    ceo_result = process_loop_with_ceo_agent(...)
    
    # Return combined results
    return {
        "status": "completed",
        "memory": ceo_result["memory"],
        "message": f"Historian: {historian_result['message']}; CEO: {ceo_result['message']}"
    }
```

## Configuration Options

The CEO Agent supports the following configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| enabled | Whether the CEO Agent is active | true |
| beliefs_file | Path to the JSON file containing system beliefs | "orchestrator_beliefs.json" |
| alignment_threshold | Threshold below which insights are generated | 0.6 |
| recent_loops_count | Number of recent loops to consider for trend analysis | 10 |
| review_window_size | Number of reviews to include in satisfaction trend calculation | 5 |

## Schema

The CEO Agent uses the `ceo_insight.schema.json` schema to define the structure of insights:

```json
{
  "loop_id": "string",
  "insight_type": "vision_drift_warning | belief_omission_alert | alignment_improvement_needed",
  "alignment_score": 0.0-1.0,
  "missing_beliefs": ["string"],
  "recommendation": "string",
  "timestamp": "ISO 8601 date-time string"
}
```

## Example Usage

```python
from agents.ceo_agent import analyze_loop_with_ceo_agent
from memory.belief_reference import load_beliefs_from_file

# Load system beliefs
beliefs = load_beliefs_from_file("orchestrator_beliefs.json")

# Analyze a loop summary
loop_id = "loop-123"
loop_summary = "The system successfully implemented the feature with high quality code."
memory = {...}  # Existing memory dictionary

# Run CEO Agent analysis
updated_memory = analyze_loop_with_ceo_agent(loop_id, loop_summary, beliefs, memory)

# Check for insights
if "ceo_insights" in updated_memory:
    latest_insight = updated_memory["ceo_insights"][-1]
    print(f"CEO Insight: {latest_insight['insight_type']} - {latest_insight['recommendation']}")
```

## Testing

The CEO Agent has comprehensive unit tests in `tests/agents/test_ceo_agent.py` covering:

- Belief alignment evaluation
- Insight generation
- Satisfaction trend tracking
- Memory integration

## Future Improvements

Potential enhancements for the CEO Agent include:

1. **Adaptive Thresholds**: Dynamically adjust alignment thresholds based on historical performance
2. **Belief Prioritization**: Weight beliefs by importance for more nuanced alignment scoring
3. **Operator Feedback Integration**: Directly incorporate qualitative operator feedback
4. **Recommendation Engine**: Develop more specific, actionable recommendations based on historical success patterns
5. **Cross-Project Analysis**: Compare belief alignment across different projects or domains
