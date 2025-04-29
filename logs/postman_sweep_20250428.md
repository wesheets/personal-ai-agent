# Initial API Sweep Report
**Date:** 2025-04-28 12:21:40
**Target URL:** https://personal-ai-agent-ji4s.onrender.com
**Total Endpoints Tested:** 71
**Success Rate:** 16.9%

## Status Code Summary
| Status Code | Count | Percentage |
|------------|-------|------------|
| 200 | 3 | 4.2% |
| 404 | 55 | 77.5% |
| 422 | 9 | 12.7% |
| 500 | 4 | 5.6% |

## Payload Validation Summary
| Validation Result | Count | Percentage |
|-------------------|-------|------------|
| Error Status Code | 68 | 95.8% |
| JSON OK | 3 | 4.2% |

## Module Summary
| Module | Total Endpoints | Success (200) | Partial Success (422) | Failure |
|--------|----------------|---------------|----------------------|---------|
| agent | 9 | 0 | 0 | 9 |
| ash | 2 | 0 | 0 | 2 |
| debug | 1 | 0 | 0 | 1 |
| debugger | 1 | 0 | 0 | 1 |
| drift | 5 | 0 | 1 | 4 |
| execute | 1 | 0 | 0 | 1 |
| historian | 1 | 0 | 0 | 1 |
| loop | 10 | 0 | 1 | 9 |
| memory | 4 | 0 | 0 | 4 |
| placeholder | 13 | 0 | 0 | 13 |
| plan | 6 | 1 | 4 | 1 |
| project | 1 | 0 | 0 | 1 |
| reflection | 11 | 0 | 1 | 10 |
| routes | 1 | 1 | 0 | 0 |
| snapshot | 4 | 1 | 2 | 1 |
| train | 1 | 0 | 0 | 1 |

## Successful Endpoints (200 OK)
| Method | Endpoint | Response Time (ms) | Payload Validation |
|--------|----------|-------------------|-------------------|
| GET | /api/plan/{plan_id} | N/A | JSON OK |
| GET | /api/snapshot/list/{loop_id} | N/A | JSON OK |
| GET | /diagnostics/routes | N/A | JSON OK |

## Partial Success Endpoints (422 Unprocessable Entity)
| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | /api/drift/auto-heal | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","drift_id"],"msg":" |
| POST | /api/loop/validate | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","project_id"],"msg" |
| POST | /api/plan/chain | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","reflection_id"],"m |
| POST | /api/plan/create | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","title"],"msg":"Fie |
| POST | /api/plan/execute | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","plan_id"],"msg":"F |
| PUT | /api/plan/update | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","plan_id"],"msg":"F |
| POST | /api/reflection/chain | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","reflection_ids"]," |
| POST | /api/snapshot/restore | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","loop_id"],"msg":"F |
| POST | /api/snapshot/save | Unprocessable Entity. Error Response: {"detail":[{"type":"missing","loc":["body","loop_id"],"msg":"F |

## Failed Endpoints (404 Not Found)
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

## Server Error Endpoints (5xx)
| Method | Endpoint | Status Code | Notes |
|--------|----------|------------|-------|
| GET | /api/plan/status/{execution_id} | 500 | Path parameters ['execution_id'] replaced with 'test_id'. Internal Server Error. Error Response: {"d |
| GET | /api/reflection/analyze/{reflection_id} | 500 | Path parameters ['reflection_id'] replaced with 'test_id'. Internal Server Error. Error Response: {" |
| POST | /api/reflection/trigger-scan-deep | 500 | Internal Server Error. Error Response: {"detail":"Failed to complete deep reflection scan: 'dict' ob |
| DELETE | /api/snapshot/{loop_id} | 500 | Path parameters ['loop_id'] replaced with 'test_id'. Internal Server Error. Error Response: {"detail |

## Other Errors
No other errors occurred during testing.

## Recommendations for Batch Fixes
Based on the sweep results, the following batch fixes should be considered:

1. **Router Implementation Fixes:**
   - Verify router paths match endpoint registry paths
   - Check for missing router implementations
   - Ensure routers are properly mounted in main.py

2. **Schema Validation Fixes:**
   - Update schema definitions to match expected request formats
   - Ensure schema imports are correct in router files
   - Check for missing schema files

3. **Server Error Fixes:**
   - Check for missing dependencies in router implementations
   - Verify module imports and function calls
   - Look for runtime errors in endpoint handlers

4. **General Recommendations:**
   - Synchronize endpoint registry with actual implementations
   - Update schema registry to match endpoint requirements
   - Ensure consistent error handling across all endpoints
   - Consider implementing standardized response formats