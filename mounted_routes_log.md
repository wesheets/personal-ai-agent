# Mounted Routes Log

This document provides a comprehensive log of all routes that have been mounted in the Promethios API.

## Core Infrastructure Routes

| Route | Method | Status | Description |
|-------|--------|--------|-------------|
| `/health` | GET | ✅ Added | Health check endpoint |
| `/system/status` | GET | ✅ Added | System status including environment and module load state |
| `/memory/read` | POST | ✅ Added | Retrieve memory by key |
| `/memory/write` | POST | ✅ Added | Direct memory injection |
| `/memory/delete` | POST | ✅ Added | Clear keys from memory |

## Loop Execution Routes

| Route | Method | Status | Description |
|-------|--------|--------|-------------|
| `/loop/trace` | GET | ✅ Added | Get loop memory trace log |
| `/loop/trace` | POST | ✅ Added | Inject synthetic loop trace |
| `/loop/reset` | POST | ✅ Added | Memory reset for clean test runs |
| `/analyze-prompt` | POST | ✅ Added | Thought Partner prompt analysis |
| `/generate-variants` | POST | ✅ Added | Thought Variant Generator |
| `/plan-and-execute` | POST | ✅ Added | HAL, ASH, NOVA execution |
| `/run-critic` | POST | ✅ Added | Loop summary review |
| `/pessimist-check` | POST | ✅ Added | Tone realism scoring |
| `/ceo-review` | POST | ✅ Added | Alignment + Operator satisfaction |
| `/cto-review` | POST | ✅ Added | Trust decay + loop health |
| `/historian-check` | POST | ✅ Added | Forgotten belief analysis |
| `/drift-summary` | POST | ✅ Added | Aggregated loop-level drift |
| `/generate-weekly-drift-report` | POST | ✅ Added | Weekly system meta-summary |

## Persona & Reflection Routes

| Route | Method | Status | Description |
|-------|--------|--------|-------------|
| `/persona/switch` | POST | ✅ Added | Change active mode |
| `/persona/current` | GET | ✅ Added | Return current orchestrator_persona |
| `/loop/persona-reflect` | POST | ✅ Added | Inject mode-aligned reflection trace |
| `/mode/trace` | GET | ✅ Added | Trace of persona usage over loops |

## Summary

- Total routes: 22
- Routes added: 22
- Routes modified: 0
- Routes unchanged: 0

All required routes have been successfully implemented and mounted in the Promethios API.
