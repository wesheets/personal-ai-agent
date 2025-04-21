# Loop Summary Rejection Handler

## Overview

The Loop Summary Rejection Handler provides functionality for rejecting and rewriting loop summaries that don't meet quality standards. This document describes the implementation details, usage, and integration with other modules.

## Features

- Reject loop summaries with specific reasons
- Automatically rewrite rejected summaries with improved quality
- Track version history of summaries (original, rejected, rewritten)
- Integrate with the loop feedback logger for comprehensive feedback tracking
- Apply trust score adjustments to agents based on summary rejections

## Implementation Details

### Core Components

1. **Summary Rejection**
   - Marks a summary as rejected with a specific reason
   - Stores rejection metadata (timestamp, reason)
   - Adds CTO warnings for rejected summaries
   - Integrates with loop_feedback_logger for feedback tracking

2. **Summary Rewriting**
   - Regenerates summaries with emphasis on specific aspects (tone, criticality, agent accuracy)
   - Adds note about previous rejection to rewritten summaries
   - Updates version history to track all versions

3. **Version History**
   - Maintains complete history of all summary versions
   - Tracks status of each version (accepted, rejected, rewritten)
   - Provides access to all versions for reference and comparison

## Usage

### Rejecting a Summary

```python
from orchestrator.modules.loop_summary_generator import reject_loop_summary

# Reject a summary
result = reject_loop_summary(
    project_id="project_123",
    loop_id=42,
    reason="Tone mismatch. Summary downplayed critical plan reroute.",
    memory=memory_dict,
    auto_rewrite=True  # Set to False to disable automatic rewriting
)
```

### Retrieving Summary Versions

```python
from orchestrator.modules.loop_summary_generator import get_summary_versions

# Get all versions of a summary
versions = get_summary_versions(
    project_id="project_123",
    loop_id=42,
    memory=memory_dict
)

# Versions are returned in order (newest first)
latest_version = versions[0]
original_version = versions[-1]
```

## Integration with Other Modules

The Loop Summary Rejection Handler integrates with:

1. **Loop Feedback Logger**
   - Records summary rejections as feedback
   - Applies trust score penalties to the orchestrator (-0.2)
   - Adds CTO warnings for rejected summaries

2. **Memory System**
   - Stores version history in memory
   - Updates loop_trace and loop_summaries with rejection metadata
   - Adds chat messages for rejection and rewriting events

## Error Handling

- Gracefully handles nonexistent loops
- Provides detailed error messages for failures
- Continues with rejection process even if integration with other modules fails

## Testing

The module includes comprehensive tests for:
- Rejecting summaries
- Automatic rewriting
- Version history tracking
- Integration with loop_feedback_logger

## Future Improvements

- Enhance integration testing with loop_feedback_logger
- Add support for operator comments on rejections
- Implement more sophisticated rewriting strategies based on rejection reasons
