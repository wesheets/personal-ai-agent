# API Sweep Comparison Report
**Date:** 2025-04-28 12:29:43
**Target URL:** https://personal-ai-agent-ji4s.onrender.com
**Total Endpoints Tested:** 71

## Overall Impact
- **Improved Endpoints:** 0 (0.0%)
- **Degraded Endpoints:** 0 (0.0%)
- **Unchanged Endpoints:** 71 (100.0%)

## Status Code Comparison
| Status Code | Initial Count | Second Count | Change |
|------------|---------------|--------------|--------|
| 200 | 3 | 3 | 0 |
| 404 | 55 | 55 | 0 |
| 422 | 9 | 9 | 0 |
| 500 | 4 | 4 | 0 |

## Remaining Issues
### 404 Not Found Errors
| Method | Endpoint |
|--------|----------|
| POST | /api/agent/analyze-prompt |
| POST | /api/agent/ceo-review |
| POST | /api/agent/cto-review |
| POST | /api/agent/delegate |
| POST | /api/agent/generate-code |
| GET | /api/agent/list |
| POST | /api/agent/loop |
| GET | /api/agent/ping |
| POST | /api/agent/run |
| POST | /api/ash/analyze |
| POST | /api/ash/execute |
| POST | /api/debug/analyze-loop |
| POST | /api/debugger/trace |
| GET | /api/drift/history/{loop_id} |
| GET | /api/drift/log |
| POST | /api/drift/monitor |
| POST | /api/drift/report |
| GET | /api/execute/placeholder |
| POST | /api/historian/log |
| POST | /api/loop/complete |
| GET | /api/loop/debug |
| POST | /api/loop/persona-reflect |
| POST | /api/loop/plan |
| POST | /api/loop/reset |
| POST | /api/loop/respond |
| POST | /api/loop/start |
| GET | /api/loop/trace |
| POST | /api/loop/trace |
| GET | /api/memory/ping |
| GET | /api/memory/read |
| GET | /api/memory/thread |
| POST | /api/memory/write |
| GET | /api/project/placeholder |
| GET | /api/reflection/result/{reflection_id} |
| POST | /api/reflection/trigger |
| POST | /api/reflection/trigger-scan |
| DELETE | /api/reflection/{project_id} |
| GET | /api/reflection/{project_id} |
| POST | /api/reflection/{project_id} |
| GET | /api/reflection/{project_id}/history |
| GET | /api/reflection/{reflection_id} |
| GET | /api/train/placeholder |
| GET | /critic_review/placeholder |
| GET | /debug_analyzer/placeholder |
| GET | /forge/placeholder |
| GET | /forge_build/placeholder |
| GET | /health_monitor/placeholder |
| GET | /loop_validation/placeholder |
| GET | /memory_api/placeholder |
| GET | /orchestrator_contract/placeholder |
| GET | /output_policy/placeholder |
| GET | /pessimist_evaluation/placeholder |
| GET | /plan_generate/placeholder |
| GET | /sage_beliefs/placeholder |
| GET | /upload/placeholder |

### 422 Unprocessable Entity Errors
| Method | Endpoint | Error Details |
|--------|----------|--------------|
| POST | /api/drift/auto-heal | ... |
| POST | /api/loop/validate | ... |
| POST | /api/plan/chain | ... |
| POST | /api/plan/create | ... |
| POST | /api/plan/execute | ... |
| PUT | /api/plan/update | ... |
| POST | /api/reflection/chain | ... |
| POST | /api/snapshot/restore | ... |
| POST | /api/snapshot/save | ... |

### 500 Server Error
| Method | Endpoint | Error Details |
|--------|----------|--------------|
| GET | /api/plan/status/{execution_id} | ... |
| GET | /api/reflection/analyze/{reflection_id} | ... |
| POST | /api/reflection/trigger-scan-deep | ... |
| DELETE | /api/snapshot/{loop_id} | ... |

## Recommendations for Next Steps
### For 404 Not Found Errors:
1. Verify router files exist for all endpoints
2. Check that router files are properly mounted in main.py
3. Ensure router paths match endpoint registry paths

### For 422 Unprocessable Entity Errors:
1. Review schema definitions for required fields
2. Update schema validation in router handlers
3. Consider implementing default values for optional fields

### For 500 Server Errors:
1. Check for runtime errors in endpoint handlers
2. Verify path parameter extraction and validation
3. Implement proper error handling for edge cases
