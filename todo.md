# Promethios Phase 2 — UI & Agent Loop Stabilization Todo List

## Sprint 1: manus-task-ui-recovery

### Fix AgentChat Logic
- [x] Replace static agent_id references with dynamic useParams() in AgentChat.jsx
- [x] Scope conversationHistory to: chat_history_${agentId}
- [x] Ensure agent.name renders from loaded agent object (not hardcoded)

### Add UI Feedback States
- [x] Add loading spinner on agent fetch
- [x] Add error fallback: "⚠️ Agent response failed. Try again or switch agents."
- [x] Use AbortController to prevent infinite hangs during fetch

### Handle 502+ API Failures
- [x] Detect 502, 504, or undefined responses from /api/delegate-stream
- [x] Display UI-friendly fallback: "⚠️ This agent is temporarily unavailable. Please try again or switch agents."
- [x] Implement retry once before showing error
- [x] Confirm payload includes valid agent_id (LifeTree, SiteGen, NEUREAL, etc.)

### Agent Mapping Fix (Critical)
- [x] Add agent name → backend ID mapping logic
- [x] Implement mapping using agentNameMap[displayName] || displayName to resolve all delegate calls

### Route Handling
- [x] Confirm sidebar + /agent/:id loads dynamically
- [x] Ensure unknown agent IDs fail gracefully

## Sprint 2: manus-task-agent-loop-test

### Validate Agent Loop Functionality
- [x] Test Core Promethios OS Agents
- [x] Test Life Tree Agent
- [x] Test Site Plan Agent
- [x] Test NEUREAL Agent
- [x] Verify loop validation criteria

## Sprint 3: manus-task-dashboard-stabilize

### Memory Browser
- [x] Fix infinite spinner issues
- [x] Add pagination
- [x] Add fallback on empty/fail states

### Dashboard View
- [x] Add "Loading system metrics..." fallback
- [x] Throttle or debounce heavy API calls

### Agent Activity Map
- [x] Validate /api/agent/status returns clean JSON
- [x] Display health: uptime, response rate, error %

### Diagnostic: Agent Manifest Route
- [x] Call and expose results from GET /api/system/agents/manifest
- [x] Use this for live verification of available agent IDs

### Optional: GPT Usage Debug Route
- [x] Implement /api/debug/gpt-usage route
- [x] Display token use, agent ID, latency, failures
