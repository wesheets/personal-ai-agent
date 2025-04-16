# Phase 10.0 Orchestrator Instruction Schema Engine Documentation

## Overview

The Orchestrator Instruction Schema Engine ensures all instructions are schema-bound, trackable, and validated throughout the execution process. This enhancement significantly improves the reliability and traceability of agent operations in the Promethios Operator UI.

## Core Components

### 1. Instruction Data Model

Located in `/backend/instruction_engine.ts`, the Instruction interface defines the schema for all agent instructions:

```typescript
interface Instruction {
  instruction_id: string;
  goal_id: string;
  thread_id?: string;
  agent_id: string;
  task_summary: string;
  tools_required: string[];
  expected_outputs: InstructionExpectedOutput[];
  loop_enforcement: number;
  allow_retry: boolean;
  escalate_on_failure: boolean;
  status: 'pending' | 'in_progress' | 'complete' | 'failed';
  last_updated: Date;
}

interface InstructionExpectedOutput {
  type: 'memory' | 'reflection' | 'checkpoint';
  tag: string;
  required: boolean;
}
```

### 2. Instruction Registry

The InstructionRegistry class manages instruction objects with methods for:

- Creating new instructions
- Updating instruction status
- Validating instruction completion
- Tracking instruction history

### 3. UI Components

#### InstructionPreviewCard

Displays instruction details including:

- Task summary
- Required tools
- Expected outputs with required/optional status
- Current status with visual indicators

#### AgentSandboxCard Enhancements

Added an Active Instruction panel showing:

- Current instruction details
- Progress indicators
- Tool usage validation
- Checkpoint status

#### AgentChat Enhancements

Updated to support:

- Instruction assignment logging
- Thread-based instruction tracking
- Visual indicators for instruction status

### 4. Validation Services

#### checkpointService

Enforces checkpoint creation and approval:

- Validates required checkpoints
- Prevents advancement until checkpoints are approved
- Logs checkpoint status changes

#### reflectionService

Ensures proper reflection creation:

- Validates reflection tags match expected outputs
- Enforces required reflection creation
- Provides reflection templates based on instruction type

#### escalationService

Handles escalation logic:

- Triggers escalation when instructions fail validation
- Monitors loop count against loop_enforcement limit
- Escalates when required outputs are skipped
- Provides detailed escalation reports

## Implementation Details

### Orchestrator Instruction Generation

When the operator sends a goal, the Orchestrator:

1. Generates a structured instruction object
2. Assigns it to the appropriate agent
3. Logs the instruction in the chat with a collapsible details view

### Agent Execution with Validation

Agents now:

1. Accept instructions with schema validation
2. Execute tasks using only specified tools
3. Log memory with validation tags
4. Trigger checkpoints at appropriate stages
5. Report status accurately through the UI

### Checkpoint Enforcement

The system ensures:

1. Agents don't advance until required checkpoints are created
2. Operators are notified of pending checkpoints
3. Checkpoint approval/rejection is logged

### Thread Integration

Instructions are integrated with the threaded conversation architecture:

1. Instructions can be assigned to specific threads
2. Thread-based permissions control which agents can execute instructions
3. Thread resolution can mark instructions as complete

## Testing

The implementation includes a comprehensive testing component:

- InstructionTester.tsx for simulating instruction creation and validation
- TestPage.tsx for viewing test results
- Mock data for demonstration purposes

## Deployment

The implementation has been deployed to GitHub with all TypeScript errors fixed and dependencies installed.
