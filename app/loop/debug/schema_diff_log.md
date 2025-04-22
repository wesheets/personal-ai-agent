# Schema Diff Log: Loop Trace Schema v1.0.0 to v1.0.2

## Overview

This document tracks changes made to the Loop Trace Schema from version 1.0.0 to version 1.0.2 to support the self-evolving cognitive stability layer. All changes follow the append-first strategy, adding new fields without modifying existing ones to ensure backward compatibility.

## Schema Changes

### Added Top-Level Properties

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `rebuild_events` | Array | Events related to system rebuilds | schema_patch_core |
| `ci_results` | Object | Results of CI tests | schema_patch_core |
| `project_manifest_summary` | Object | Summary of the project manifest | schema_patch_core |
| `belief_versions` | Object | Version information for beliefs | schema_patch_core |

### Enhanced Existing Properties

#### `audit_results` Object

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `correlations` | Array | List of correlations between issues | schema_patch_ui |
| Issues.`impact` | Number | Impact of the issue | schema_patch_ui |
| Issues.`likelihood` | Number | Likelihood of the issue | schema_patch_ui |
| Issues.`risk_level` | String | Risk level of the issue | schema_patch_ui |
| Issues.`priority` | String | Priority for addressing the issue | schema_patch_ui |

#### `summary` Object

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `factual_accuracy` | Number | Factual accuracy score for the summary | schema_patch_ui |
| `logical_consistency` | Number | Logical consistency score for the summary | schema_patch_ui |
| `emotional_congruence` | Number | Emotional congruence score for the summary | schema_patch_ui |
| `temporal_coherence` | Number | Temporal coherence score for the summary | schema_patch_ui |
| `confidence` | Number | Confidence score for the summary | schema_patch_ui |

### New Sub-Objects

#### `rebuild_events` Array Items

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `type` | String | Type of rebuild event | schema_patch_core |
| `timestamp` | String (date-time) | ISO 8601 timestamp of the event | schema_patch_core |
| `stability_score` | Number | Stability score at the time of the event | schema_patch_core |
| `threshold` | Number | Threshold that triggered the event | schema_patch_core |
| `orchestrator_mode` | String | Orchestrator mode at the time of the event | schema_patch_core |
| `message` | String | Description of the event | schema_patch_core |
| `severity` | String | Severity of the event | schema_patch_core |
| `details` | Object | Additional details about the event | schema_patch_core |

#### `ci_results` Object

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `status` | String | Overall status of CI tests | schema_patch_core |
| `ci_score` | Number | Overall CI score | schema_patch_core |
| `timestamp` | String (date-time) | ISO 8601 timestamp of CI test execution | schema_patch_core |
| `total_modules` | Integer | Total number of modules tested | schema_patch_core |
| `passed_modules` | Integer | Number of modules that passed tests | schema_patch_core |
| `failed_modules` | Integer | Number of modules that failed tests | schema_patch_core |
| `module_results` | Array | Results for individual modules | schema_patch_core |

#### `project_manifest_summary` Object

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `total_modules` | Integer | Total number of modules in the project | schema_patch_core |
| `module_counts` | Object | Counts of modules by type | schema_patch_core |
| `belief_versions` | Array | List of belief versions used in the project | schema_patch_core |
| `modules_needing_rebuild` | Array | List of modules that need rebuilding | schema_patch_core |
| `modules_with_failed_ci` | Array | List of modules with failed CI tests | schema_patch_core |
| `last_stability_score` | Number | Last stability score for the project | schema_patch_core |
| `last_updated` | String (date-time) | ISO 8601 timestamp of last update to the project manifest | schema_patch_core |

#### `belief_versions` Object Properties

| Property | Type | Description | Tag |
|----------|------|-------------|-----|
| `current_version` | String | Current semantic version of the belief | schema_patch_core |
| `previous_version` | String | Previous semantic version of the belief | schema_patch_core |
| `version_history` | Array | History of versions for this belief | schema_patch_core |
| `dependencies` | Array | Other beliefs this belief depends on | schema_patch_core |
| `dependents` | Array | Other beliefs that depend on this belief | schema_patch_core |
| `change_impact` | Object | Impact of changes to this belief | schema_patch_core |
| `branch_info` | Object | Information about branches of this belief | schema_patch_core |

## Compatibility Notes

1. All changes follow the append-first strategy, ensuring backward compatibility with existing systems.
2. New fields are optional and will not break existing parsers.
3. Core schema patches (`schema_patch_core`) are essential for the self-evolving cognitive stability layer functionality.
4. UI schema patches (`schema_patch_ui`) enhance visualization and user experience but are not critical for core functionality.

## Migration Guide

Existing systems can adopt these schema changes incrementally:

1. First, add support for the core schema patches (`schema_patch_core`).
2. Then, add support for the UI schema patches (`schema_patch_ui`) as needed.
3. No changes to existing field parsers are required.

## Validation

The updated schema has been validated against sample data to ensure compatibility with both new and existing systems. All tests pass with both v1.0.0 and v1.0.2 schema versions.
