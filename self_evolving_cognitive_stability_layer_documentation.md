# Self-Evolving Cognitive Stability Layer for Promethios

## Overview

The Self-Evolving Cognitive Stability Layer is a comprehensive system designed to maintain the cognitive stability of Promethios by automatically detecting degradation or drift, coordinating rebuilds, and ensuring system integrity over time. This document provides detailed information about the architecture, components, and integration of this layer.

## Architecture

The Self-Evolving Cognitive Stability Layer consists of three main components:

1. **Rebuilder Agent**: Detects degradation or drift and coordinates rebuilds
2. **Project Manifest System**: Tracks and versions all project modules
3. **Loop CI Test Runner**: Verifies build integrity through automated testing

These components work together to form a cohesive system that continuously monitors, tests, and maintains the cognitive stability of Promethios.

## Components

### 1. Rebuilder Agent

The Rebuilder Agent is responsible for detecting system degradation or drift and coordinating rebuilds when necessary.

#### Key Features

- **System Stability Monitoring**:
  - Scans project manifests for outdated modules and version gaps
  - Detects belief mismatches across different components
  - Identifies failing agents and CI test failures
  - Calculates a comprehensive stability score

- **Adaptive Rebuild Determination**:
  - Uses orchestrator mode-specific thresholds (FAST, BALANCED, THOROUGH, RESEARCH)
  - Generates detailed rebuild events with severity levels
  - Creates prioritized recommendations for system improvement

- **Integration with Existing Systems**:
  - Implemented using the Agent SDK pattern for seamless integration
  - Updates project manifests with stability information
  - Logs rebuild events to appropriate locations

#### Usage

```python
from app.plugins.agents.rebuilder.rebuilder import run_agent

# Create context for Rebuilder Agent
context = {
    "project_id": "promethios-core",
    "orchestrator_mode": "BALANCED",
    "loop_id": "stability-check-20250422033800"
}

# Run Rebuilder Agent
result = run_agent(context)

# Check if rebuild is needed
if result.get("needs_rebuild", False):
    # Handle rebuild recommendation
    print(f"Rebuild recommended with score: {result.get('stability_score', 0.0)}")
    print(f"Rebuild events: {result.get('rebuild_events', [])}")
    print(f"Recommendations: {result.get('recommendations', [])}")
```

### 2. Project Manifest System

The Project Manifest System tracks and versions all project modules, providing a central repository of information for the Rebuilder Agent.

#### Key Features

- **Comprehensive Module Tracking**:
  - Stores detailed metadata for each module (creation info, updates, versions)
  - Records CI test results with status, scores, and failure reasons
  - Tracks belief versions across all modules
  - Flags modules that need rebuilding with reasons

- **Powerful Query Capabilities**:
  - Retrieves modules by belief version
  - Filters modules by CI status
  - Identifies modules needing rebuild
  - Generates project-wide summaries

- **Robust Data Management**:
  - Handles missing manifests gracefully
  - Provides atomic update operations
  - Maintains audit trails with timestamps
  - Ensures data consistency

#### Usage

```python
from app.modules.project_manifest import (
    load_manifest,
    save_manifest,
    get_module,
    update_ci_result,
    mark_for_rebuild,
    get_manifest_summary
)

# Load project manifest
manifest = load_manifest("promethios-core")

# Get information about a specific module
module_info = get_module("promethios-core", "loop")

# Update CI result for a module
ci_result = {
    "status": "passed",
    "ci_score": 0.95,
    "timestamp": "2025-04-22T03:30:00Z",
    "total_tests": 50,
    "passed_tests": 48,
    "failed_tests": 2
}
update_ci_result("promethios-core", "loop", ci_result)

# Mark a module for rebuild
mark_for_rebuild(
    "promethios-core",
    "reconciler_agent",
    True,
    "Contradiction detection failing on complex cases"
)

# Get project manifest summary
summary = get_manifest_summary("promethios-core")
```

### 3. Loop CI Test Runner

The Loop CI Test Runner verifies build integrity by running automated tests on modules and updating the project manifest with the results.

#### Key Features

- **Comprehensive Test Execution**:
  - Dynamically discovers and runs tests for each module
  - Supports parallel test execution for improved performance
  - Handles test failures and errors gracefully
  - Provides detailed test results with execution times

- **CI Result Management**:
  - Generates standardized CI results with scores and status
  - Maintains a history of test runs for trend analysis
  - Provides APIs for retrieving latest results and historical data
  - Stores detailed test reports for debugging

- **Project Manifest Integration**:
  - Updates project manifest with test results automatically
  - Marks modules for rebuild when tests fail
  - Provides detailed failure reasons for failed tests
  - Calculates overall project CI scores

#### Usage

```python
from app.modules.loop_ci_test_runner import (
    run_tests,
    get_latest_result,
    get_result_history
)

# Run CI tests for a project
result = run_tests("promethios-core")

# Run CI tests for specific modules
modules = ["loop", "reconciler_agent"]
result = run_tests("promethios-core", modules)

# Get the latest CI result
latest_result = get_latest_result("promethios-core")

# Get CI result history
history = get_result_history("promethios-core", limit=5)
```

## System Integration

The Self-Evolving Cognitive Stability Layer integrates with the existing Promethios architecture through the Loop Hardening Integration module, which provides hooks into the loop execution system.

### Integration Points

- **Post-Loop Stability Hook**: Runs after loop completion to check stability
- **Scheduled CI Hook**: Runs CI tests on a scheduled basis
- **Rebuild Trigger Hook**: Triggers rebuilds when stability issues are detected

### Background Tasks

The integration module also provides background tasks for continuous monitoring:

- **Stability Check Loop**: Periodically checks system stability
- **CI Test Loop**: Periodically runs CI tests on all modules

### Configuration

The integration can be configured through the `stability_integration.json` file, which allows customization of:

- Stability check interval
- CI test interval
- Orchestrator mode
- Auto-rebuild settings
- Notification settings
- CI test module selection

### Usage

```python
from app.modules.loop_hardening_integration import (
    StabilityIntegration,
    post_loop_stability_hook,
    scheduled_ci_hook,
    rebuild_trigger_hook,
    start_stability_monitoring,
    stop_stability_monitoring,
    update_monitoring_config
)

# Create stability integration
integration = StabilityIntegration("promethios-core")

# Start background monitoring
integration.start_background_tasks()

# Run stability check
result = integration.run_stability_check()

# Run CI tests
result = integration.run_ci_tests()

# Update configuration
config_updates = {
    "stability_check_interval": 1800,  # 30 minutes
    "ci_test_interval": 43200,  # 12 hours
    "orchestrator_mode": "THOROUGH",
    "auto_rebuild": True
}
integration.update_config(config_updates)

# Stop background monitoring
integration.stop_background_tasks()
```

## Schema Updates

The Self-Evolving Cognitive Stability Layer introduces several schema updates to support its functionality. These updates follow an append-first strategy to ensure backward compatibility.

### New Top-Level Properties

- `rebuild_events`: Events related to system rebuilds
- `ci_results`: Results of CI tests
- `project_manifest_summary`: Summary of the project manifest
- `belief_versions`: Version information for beliefs

### Enhanced Existing Properties

- `audit_results`: Added correlations, impact, likelihood, risk level, and priority
- `summary`: Added factual accuracy, logical consistency, emotional congruence, temporal coherence, and confidence

For detailed information about schema changes, see the [Schema Diff Log](app/loop/debug/schema_diff_log.md).

## Sample Files

The following sample files demonstrate the Self-Evolving Cognitive Stability Layer in action:

- **Project Manifest**: [promethios-core.json](data/project_manifest/promethios-core.json)
- **CI Result**: [promethios-core_20250422033700.json](data/ci_results/promethios-core_20250422033700.json)
- **Loop Trace**: [stability-check-20250422033800.json](data/loop_traces/stability-check-20250422033800.json)

## Performance Considerations

The Self-Evolving Cognitive Stability Layer is designed to be efficient and scalable:

- **Parallel Test Execution**: The Loop CI Test Runner uses parallel execution to improve performance
- **Incremental Updates**: The Project Manifest System supports incremental updates to minimize I/O
- **Configurable Intervals**: Stability checks and CI tests can be scheduled at appropriate intervals
- **Resource Management**: Background tasks are designed to minimize resource usage

## Security Considerations

The Self-Evolving Cognitive Stability Layer includes several security features:

- **Permission Validation**: All operations are validated against the agent permission system
- **Audit Logging**: All operations are logged for audit purposes
- **Error Handling**: Robust error handling prevents security issues from cascading
- **Data Validation**: All inputs and outputs are validated to prevent injection attacks

## Future Enhancements

Potential future enhancements for the Self-Evolving Cognitive Stability Layer include:

- **Machine Learning-Based Anomaly Detection**: Using ML to improve detection of subtle anomalies
- **Predictive Maintenance**: Predicting stability issues before they occur
- **Self-Healing Capabilities**: Automatically fixing certain types of issues
- **Distributed Testing**: Supporting distributed test execution across multiple nodes
- **Enhanced Visualization**: Providing better visualization of stability metrics and trends

## Conclusion

The Self-Evolving Cognitive Stability Layer provides Promethios with the ability to maintain its cognitive stability over time by automatically detecting degradation or drift, coordinating rebuilds, and ensuring system integrity. By integrating the Rebuilder Agent, Project Manifest System, and Loop CI Test Runner, this layer forms a comprehensive system for cognitive stability maintenance.
