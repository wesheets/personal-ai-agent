# Phase 5.3 API Verification Sweep (V7) Test Plan

## Overview
This test plan outlines the approach for conducting a comprehensive API verification sweep to determine the current API health percentage and verify new modules added in Phase 5.0-5.2.

## Test Scope
The test will cover all endpoints listed in the endpoint test table, with particular focus on:
1. Confirming functionality of working endpoints
2. Identifying issues with problematic endpoints
3. Verifying new modules added in Phase 5.0-5.2
4. Comparing results with previous API sweep (v4.7)

## Endpoint Test Matrix

| Endpoint | Method | Expected Status | Test Priority | Test Payload Required |
|----------|--------|----------------|---------------|------------------------|
| /api/agent/run | POST | 200 | High | Yes (HAL, NOVA, CRITIC, ASH) |
| /api/agent/loop | POST | 200 | Medium | Yes |
| /api/agent/list | GET | 200 | Medium | No |
| /api/agent/delegate | POST | 200 | Medium | Yes |
| /api/memory/write | POST | 200 | High | Yes |
| /api/memory/read | GET | 200 | High | Yes (query params) |
| /api/memory/thread | GET | 200 | Medium | Yes (query params) |
| /api/memory/summarize | POST | 200 | Medium | Yes |
| /api/debug/memory/log | GET | 200 | Medium | Yes (query params) |
| /api/project/state | GET | 200 | High | Yes (query params) |
| /api/orchestrator/consult | POST | 200 | Medium | Yes |
| /api/train | POST | 404/501 | Low | No (expected to fail) |
| /api/plan | POST | 404/501 | Low | No (expected to fail) |
| /api/snapshot | POST | 404/501 | Low | No (expected to fail) |
| /api/status | GET | 404/501 | Low | No (expected to fail) |
| /api/system/integrity | GET | 404/501 | Medium | No (path mismatch) |
| /api/debug/agents | GET | 404/501 | Medium | No (double prefix) |

## Test Approach

### 1. Test Script Development
- Create a comprehensive Bash script that tests all endpoints
- Include proper error handling and response logging
- Implement test cases for each endpoint with appropriate payloads
- Add timing measurements for performance assessment

### 2. Test Execution Strategy
- First test all endpoints expected to work (marked with ✅)
- Then test problematic endpoints (marked with ❌)
- Log all responses including status codes, response bodies, and execution times
- Store results in structured format for analysis

### 3. Test Payloads
- HAL agent: Test file creation capabilities
- NOVA agent: Test UI component creation
- CRITIC agent: Test feedback functionality
- ASH agent: Test deployment simulation
- Memory operations: Test write, read, thread, and summarize functions
- Project state: Test state retrieval functionality
- Orchestrator: Test consultation capabilities

### 4. Analysis Methodology
- Calculate API health percentage based on successful endpoints vs. total endpoints
- Compare results with previous API sweep (v4.7)
- Identify any newly working endpoints
- Document any lingering broken routes
- Provide recommendations for fixing problematic endpoints

## Expected Deliverables
1. API test script (api_sweep_v7_test.sh)
2. Complete test results with response codes
3. Execution logs from all test cases
4. API health percentage calculation
5. Findings and issues documentation
6. Recommendations for fixes
7. Comprehensive API sweep report

## Success Criteria
- API health percentage of 70-75% or higher
- All endpoints marked with ✅ in the endpoint test table return 200 status codes
- Clear documentation of any issues found
- Actionable recommendations for fixing problematic endpoints
