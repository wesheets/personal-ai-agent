# Schema Diff Log: Loop Trace Schema

## Overview
This document tracks changes made to the Loop Trace Schema as part of the Loop Hardening Modules implementation.

## Version History
- v1.0.0: Base schema (original implementation)
- v1.0.1: UI enhancements (schema_patch_ui)
- v1.0.2: Core enhancements (schema_patch_core)

## Schema Diff: v1.0.0 → v1.0.2

### New Core Fields (schema_patch_core: 1.0.2)

#### Added to root schema:
- `belief_dependencies`: Object mapping belief IDs to arrays of dependency IDs

#### Added to metrics:
- `schema_patch_core`: String indicating schema patch version
- `sequence_efficiency`: Object with metrics for agent transition efficiency
  - `average_transition_time_ms`: Average time between agent transitions
  - `max_transition_time_ms`: Maximum time between agent transitions
  - `efficiency_score`: Overall efficiency score for transitions
- `resource_efficiency`: Object with resource utilization metrics
  - `memory_time_ratio`: Memory usage (MB) to execution time (s) ratio
  - `operations_per_second`: Memory operations per second
  - `memory_per_operation`: Memory usage (MB) per operation
- `belief_reference_analysis`: Object with belief reference metrics
  - `reference_density`: Belief references per agent
  - `reference_efficiency`: Belief references per second
- `error_analysis`: Object with error analysis information
  - `error_type`: Type of error
  - `error_message`: Error message
  - `timestamp`: Timestamp of the error
  - `recovery_attempted`: Whether recovery was attempted
- `performance_trends`: Object with performance trend analysis
  - `execution_time_trend`: Trend in execution time (improving/stable/degrading)
  - `memory_usage_trend`: Trend in memory usage (improving/stable/degrading)
  - `historical_data_points`: Number of historical data points used
  - `trend_confidence`: Confidence in trend analysis

#### Added to summary.metadata:
- `schema_patch_core`: String indicating schema patch version
- `emotional_congruence`: Emotional congruence score
- `confidence_explanation`: Array of strings explaining confidence factors
- `adaptive_thresholds`: Object containing adaptive thresholds used for scoring
- `levels`: Object containing classification levels for different dimensions

#### Added to snapshots items:
- `schema_patch_core`: String indicating schema patch version
- `size_analysis`: Object with size analysis information
  - `relative_size`: Size relative to average snapshot size
  - `is_outlier`: Whether this snapshot is a size outlier
- `type_distribution`: Object with type distribution analysis
  - `count_by_type`: Object mapping snapshot types to counts
  - `percentage_of_type`: Percentage of snapshots of this type

#### Added to audit_info:
- `schema_patch_core`: String indicating schema patch version
- `risk_assessment`: Object with risk assessment information
  - `risk_level`: Overall risk level (low/medium/high/critical)
  - `impact`: Potential impact of issues (low/medium/high/critical)
  - `likelihood`: Likelihood of issues occurring (low/medium/high/critical)
  - `priority_issues`: Array of priority issues to address
- `correlation_analysis`: Object with correlation analysis information
  - `correlated_issues`: Array of objects with correlated issue information
    - `issue_pair`: Array of two strings representing correlated issues
    - `correlation_strength`: Strength of correlation between issues
    - `systemic`: Whether this is a systemic problem
  - `root_causes`: Array of objects with root cause information
    - `cause`: Root cause description
    - `affected_issues`: Array of issues affected by this root cause
    - `confidence`: Confidence in this root cause

#### Added to belief_versions items:
- `schema_patch_core`: String indicating schema patch version
- `semantic_version`: Object with semantic version information
  - `major`: Major version number
  - `minor`: Minor version number
  - `patch`: Patch version number
- `change_type`: Type of change (creation/major/minor/patch)
- `change_summary`: Summary of changes in this version
- `branch`: Branch name for this version

#### Added to project_locks items:
- `schema_patch_core`: String indicating schema patch version
- `semantic_lock_info`: Object with semantic lock information
  - `is_exclusive`: Whether this is an exclusive lock
  - `allows_shared`: Whether this lock allows shared locks
  - `is_expired`: Whether this lock is expired

#### Added to metadata:
- `schema_patch_core`: String indicating schema patch version
- `schema_patch_ui`: String indicating schema patch version for UI fields
- `error_analysis`: Object with error analysis information
  - `error_type`: Type of error
  - `error_message`: Error message
  - `timestamp`: Timestamp of the error
  - `recovery_attempted`: Whether recovery was attempted

### New UI Fields (schema_patch_ui: 1.0.1)

#### Added to metadata:
- `risk_level`: Risk level based on orchestrator mode (low/medium/high/very_high)

## Compatibility Notes
- All schema changes are backward compatible
- New fields are added as extensions to existing structures
- No existing fields are modified or removed
- All new fields are clearly tagged with schema_patch_core or schema_patch_ui
- Core schema version is now 1.0.2
- UI schema version is now 1.0.1
