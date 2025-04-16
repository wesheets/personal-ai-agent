# Orchestrator Multi-Modal Planning & Approval System Architecture

## Overview

The Orchestrator Multi-Modal Planning & Approval System transforms the Orchestrator into a strategic planning and execution hub with operator approval capabilities. It combines LaunchMind-style consultation with tactical execution, agent delegation, checkpoint approval, and memory logging.

## System Components

### 1. Consultation Flow

- **Purpose**: Begin a conversational session with the operator to clarify goals and develop a strategic plan
- **Endpoint**: `/orchestrator/consult`
- **Key Features**:
  - Accept open-ended goals from operator
  - Ask 2-5 dynamic follow-up questions to clarify vision
  - Store consultation session using `session_id`
  - Use `mode: "strategic"` internally
  - Output a proposed plan (phases, tools, agents)

### 2. Operator Approval Loop

- **Purpose**: Allow the operator to approve or modify the proposed plan
- **Endpoint**: `/orchestrator/confirm`
- **Key Features**:
  - Switch to `mode: "tactical"` on confirmation
  - Generate `goal_id`
  - Break plan into subgoals
  - Delegate tasks to agents using `/delegate`
  - Set initial tool calls and system caps

### 3. Credential Intake

- **Purpose**: Gather and securely store credentials needed for execution
- **Endpoint**: `/orchestrator/credentials`
- **Key Features**:
  - Collect hosting provider, GitHub repo/token, domain provider, etc.
  - Store securely in `agent.secrets`
  - Inject into relevant tools

### 4. Execution Checkpoint Layer

- **Purpose**: Allow agents to report task completion and await approval
- **Endpoints**:
  - `/orchestrator/checkpoint` - For agents to report completion
  - `/orchestrator/review-status` - List pending checkpoints
  - `/orchestrator/approve` - Resume or revise execution
- **Key Features**:
  - Support for "hard" and "soft" checkpoints
  - Optional auto-approval for non-critical checkpoints
  - Execution halts at hard checkpoints until approved

### 5. Real-Time Narration (Trust Logs)

- **Purpose**: Log every major step with natural language commentary
- **Key Features**:
  - Write to `orchestrator_action_log.json`
  - Create memories with `type: "system_update"` or `"decision"`
  - Provide transparent progress updates

### 6. Reflection Memory

- **Purpose**: Summarize completed phases and outcomes
- **Key Features**:
  - Auto-write `"reflection"` memories after phase completion
  - Include summary of outcomes and time to completion

## Data Models

### Session

```json
{
  "session_id": "string",
  "timestamp": "datetime",
  "operator_id": "string",
  "mode": "strategic | tactical",
  "goal": "string",
  "questions": [
    {
      "question": "string",
      "answer": "string",
      "timestamp": "datetime"
    }
  ],
  "plan": {
    "phases": [
      {
        "phase_id": "string",
        "title": "string",
        "description": "string",
        "estimated_duration": "string",
        "tools": ["string"],
        "agents": ["string"]
      }
    ]
  }
}
```

### Goal

```json
{
  "goal_id": "string",
  "session_id": "string",
  "title": "string",
  "description": "string",
  "status": "pending | in_progress | completed | failed",
  "subgoals": [
    {
      "subgoal_id": "string",
      "title": "string",
      "description": "string",
      "assigned_agent": "string",
      "status": "pending | in_progress | completed | failed",
      "tools": ["string"]
    }
  ]
}
```

### Checkpoint

```json
{
  "checkpoint_id": "string",
  "checkpoint_name": "string",
  "checkpoint_type": "hard | soft",
  "goal_id": "string",
  "subgoal_id": "string",
  "agent_id": "string",
  "status": "pending | approved | rejected",
  "auto_approve_if_silent": "boolean",
  "output_memory_id": "string",
  "created_at": "datetime",
  "approved_at": "datetime",
  "details": "object"
}
```

### Credentials

```json
{
  "credential_id": "string",
  "goal_id": "string",
  "hosting_provider": "string",
  "github_repo": "string",
  "github_token": "string",
  "domain_provider": "string",
  "stripe_keys": "object",
  "api_credentials": "object",
  "environment": "staging | production"
}
```

### Action Log Entry

```json
{
  "log_id": "string",
  "timestamp": "datetime",
  "goal_id": "string",
  "action_type": "consultation | planning | delegation | checkpoint | approval | execution",
  "description": "string",
  "details": "object"
}
```

### Memory

```json
{
  "memory_id": "string",
  "timestamp": "datetime",
  "goal_id": "string",
  "agent_id": "string",
  "type": "system_update | decision | reflection",
  "content": "string",
  "tags": ["string"]
}
```

## Directory Structure

```
/src/orchestrator/
  ├── __init__.py
  ├── consultation.py      # Consultation flow implementation
  ├── approval.py          # Operator approval loop implementation
  ├── credentials.py       # Credential intake implementation
  ├── checkpoint.py        # Execution checkpoint layer implementation
  ├── logging.py           # Real-time narration and logging implementation
  ├── reflection.py        # Reflection memory implementation
  ├── models.py            # Data models
  ├── utils.py             # Utility functions
  └── endpoints.py         # API endpoint definitions
```

## API Endpoints

### 1. Consultation Endpoint

```
POST /orchestrator/consult
Request:
{
  "operator_id": "string",
  "goal": "string"
}
Response:
{
  "session_id": "string",
  "questions": ["string"],
  "mode": "strategic"
}
```

### 2. Consultation Response Endpoint

```
POST /orchestrator/consult/respond
Request:
{
  "session_id": "string",
  "question_id": "string",
  "answer": "string"
}
Response:
{
  "next_question": "string" | null,
  "plan": object | null
}
```

### 3. Confirmation Endpoint

```
POST /orchestrator/confirm
Request:
{
  "session_id": "string",
  "approved": "boolean",
  "modifications": "object" | null
}
Response:
{
  "goal_id": "string",
  "status": "string",
  "next_steps": ["string"]
}
```

### 4. Credentials Endpoint

```
POST /orchestrator/credentials
Request:
{
  "goal_id": "string",
  "credentials": {
    "hosting_provider": "string",
    "github_repo": "string",
    "github_token": "string",
    "domain_provider": "string",
    "stripe_keys": "object",
    "api_credentials": "object",
    "environment": "staging | production"
  }
}
Response:
{
  "status": "string",
  "message": "string"
}
```

### 5. Checkpoint Endpoint

```
POST /orchestrator/checkpoint
Request:
{
  "agent_id": "string",
  "goal_id": "string",
  "subgoal_id": "string",
  "checkpoint_name": "string",
  "checkpoint_type": "hard | soft",
  "auto_approve_if_silent": "boolean",
  "output_memory_id": "string",
  "details": "object"
}
Response:
{
  "checkpoint_id": "string",
  "status": "pending | approved",
  "message": "string"
}
```

### 6. Review Status Endpoint

```
GET /orchestrator/review-status
Request:
{
  "goal_id": "string"
}
Response:
{
  "pending_checkpoints": [
    {
      "checkpoint_id": "string",
      "checkpoint_name": "string",
      "checkpoint_type": "hard | soft",
      "agent_id": "string",
      "created_at": "datetime",
      "details": "object"
    }
  ]
}
```

### 7. Approve Endpoint

```
POST /orchestrator/approve
Request:
{
  "checkpoint_id": "string",
  "approved": "boolean",
  "feedback": "string",
  "modifications": "object" | null
}
Response:
{
  "status": "string",
  "message": "string",
  "next_steps": ["string"]
}
```

## Integration with Existing Systems

The Orchestrator will integrate with:

1. **Agent System**: To delegate tasks to HAL, ASH, and other agents
2. **Memory System**: To store consultation sessions, plans, and reflections
3. **Tool System**: To execute tools and track their results
4. **Security System**: To securely store and manage credentials

## Security Considerations

1. Credentials will be stored securely and never exposed in logs or memories
2. Access to approval endpoints will require operator authentication
3. Sensitive operations will require explicit operator approval
4. All actions will be logged for audit purposes

## Implementation Plan

1. Create the basic directory structure and models
2. Implement the consultation flow
3. Implement the operator approval loop
4. Implement the credential intake system
5. Implement the execution checkpoint layer
6. Implement real-time narration and logging
7. Implement reflection memory
8. Create API endpoints
9. Test the system end-to-end
10. Document the implementation

This architecture provides a comprehensive framework for implementing the Orchestrator Multi-Modal Planning & Approval System as specified in Phase 7.0.
