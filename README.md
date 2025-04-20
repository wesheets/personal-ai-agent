# System Integrity Test Suite

This project implements a comprehensive test suite for ensuring the Promethios cognitive OS is healthy, aligned, and schema-compliant.

## Features

- Validates project memory against schema
- Grades reflection quality and ensures minimum confidence threshold
- Checks loop snapshot consistency
- Confirms orchestrator decisions exist and are traceable
- Verifies CTO system health is above minimum threshold
- Confirms drift logs are empty or non-critical
- Validates agents are triggered in correct dependency order
- Monitors memory growth rate

## Project Structure

```
tests/
├── test_system_integrity.py  # Main integrity test suite
└── test_meta_integrity.py    # Meta-tests to verify test suite functionality

.github/
└── workflows/
    └── system-health-check.yml  # GitHub Action for automated testing
```

## Test Functions

The test suite includes the following validation functions:

- `test_project_memory_schema()`: Validates memory against schema
- `test_reflection_confidence()`: Ensures reflection quality is above threshold
- `test_snapshot_presence()`: Verifies loop snapshots exist
- `test_orchestrator_decisions()`: Confirms decisions exist and are traceable
- `test_system_health_score()`: Checks CTO health score is above threshold
- `test_drift_logs_status()`: Confirms no critical drift logs
- `test_agent_dependency_order()`: Validates correct agent execution order
- `test_loop_snapshot_consistency()`: Checks snapshots are sequential
- `test_memory_growth_rate()`: Monitors for excessive memory growth

## GitHub Action

The included GitHub Action runs the test suite:
- On every push to the main branch
- Once per day via scheduled cron job

## Usage

Run the test suite locally:

```bash
pytest tests/test_system_integrity.py -v
```

Run meta-tests to verify test suite functionality:

```bash
pytest tests/test_meta_integrity.py -v
```

## Integration

To integrate with your existing Promethios system:

1. Copy the test files to your project's test directory
2. Copy the GitHub Action workflow to your .github/workflows directory
3. Ensure your project has the necessary dependencies (pytest)
4. Run the tests to verify system integrity
