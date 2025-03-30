# Personal AI Agent System

A modular, extensible AI agent system inspired by Manus, featuring multiple specialized agents, memory systems, and multi-model support.

## Features

- **Modular Agent Architecture**: Specialized agents for building, operations, research, and memory management
- **Multi-Model Support**: Seamless integration with OpenAI GPT-4 and Anthropic Claude models
- **Vector Memory System**: Persistent memory using Supabase with pgvector
- **Dynamic Prompt Chains**: JSON/YAML-based prompt configurations for each agent
- **Agent Reflection & Reasoning**: Self-evaluation, rationale logging, and memory context review
- **Multi-Agent Workflow Orchestration**: Automatic task routing between specialized agents
- **Nudging, Looping, and Task Persistence**: Retry logic, user nudging, and task management
- **Behavior Shaping & Escalation Logic**: Adaptive behavior, escalation protocols, and goal awareness
- **Comprehensive Logging**: Execution logs, rationale logs, and execution chain logs
- **Tool Integration**: Pluggable tool system for external integrations
- **Docker Containerization**: Easy deployment with Docker

## Phase 2.4: Behavior Shaping & Escalation Logic

The latest update (Phase 2.4) adds several powerful features to enhance agent intelligence:

### 1. Escalation Protocol

When an agent encounters difficulties, it can now automatically escalate the issue:

- Triggers escalation when retry count exceeds threshold (2+ retries)
- Detects patterns like "I'm stuck", "need help", or "escalating" in agent reflections
- Logs comprehensive escalation events in `/escalation_logs/`
- Supports forwarding escalations to different agents
- Includes agent name, task description, escalation reason, and reflection data

### 2. Behavior Feedback Loop

Agents can now adapt their behavior based on feedback:

- Records success/failure status for each task
- Supports optional user notes for qualitative feedback
- Stores feedback in `/behavior_logs/` organized by agent
- Injects recent feedback context into future prompts
- Enables agents to learn from past successes and failures

### 3. Goal Awareness Scaffold

Each agent now has a persistent mission that guides its actions:

- Goal summaries defined in agent configuration files
- Goals injected into prompt context before task execution
- Helps agents align with business objectives
- Provides consistent purpose across different tasks

### 4. Performance Summary Endpoint

New endpoints for monitoring agent performance:

- `/agent/{name}/performance` - Returns metrics including total tasks, average confidence, escalation count, and success rates
- `/agent/{name}/feedback` - Allows submitting and retrieving feedback
- `/escalations` - Provides access to escalation events
- Supports optional human rating entries

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- (Optional) Claude API key
- (Optional) Supabase account for vector storage

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/wesheets/personal-ai-agent.git
   cd personal-ai-agent
   ```

2. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   CLAUDE_API_KEY=your_claude_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

3. Build and run with Docker:
   ```
   docker-compose up --build
   ```

4. Or run locally:
   ```
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

### Using the API

#### Basic Agent Request

```json
POST /agent/builder
{
  "input": "Create a FastAPI backend for a todo app",
  "model": "gpt-4",
  "enable_retry_loop": true
}
```

#### Multi-Agent Orchestration

```json
POST /agent/builder
{
  "input": "Create a FastAPI backend for a todo app and deploy it",
  "auto_orchestrate": true
}
```

#### Viewing Agent Performance

```
GET /agent/builder/performance
```

#### Submitting Feedback

```json
POST /agent/builder/feedback
{
  "task_id": "task-uuid-here",
  "was_successful": true,
  "user_notes": "Great job on the API design!"
}
```

#### Viewing Escalations

```
GET /escalations
```

#### Forwarding an Escalation

```json
POST /escalations/{escalation_id}/forward
{
  "target_agent": "ops"
}
```

## Creating Custom Agents

1. Create a new prompt configuration file in `app/prompts/`:
   ```json
   {
     "name": "My Custom Agent",
     "model": "gpt-4",
     "system": "You are a specialized agent that...",
     "goal_summary": "The Custom Agent is responsible for...",
     "accepts_tasks": ["category1", "category2"],
     "handoff_keywords": ["keyword1", "keyword2"],
     "tools": ["tool1", "tool2"],
     "persona": {
       "tone": "professional and concise",
       "voice": "experienced specialist",
       "traits": ["analytical", "thorough", "precise"]
     },
     "role": "Handle specialized tasks in domain X",
     "rules": [
       "Always verify inputs before processing",
       "Provide clear explanations for decisions",
       "Focus on accuracy over speed"
     ]
   }
   ```

2. The agent will be automatically available at `/agent/your_file_name`

## Architecture

```
app/
├── api/
│   ├── agent.py          # Main agent API routes
│   ├── memory.py         # Memory API routes
│   └── performance.py    # Performance and feedback API routes
├── core/
│   ├── behavior_manager.py     # Behavior feedback management
│   ├── confidence_retry.py     # Confidence-based retry logic
│   ├── escalation_manager.py   # Escalation protocol management
│   ├── execution_chain_logger.py # Execution chain logging
│   ├── execution_logger.py     # Execution logging
│   ├── memory_context_reviewer.py # Memory context review
│   ├── memory_manager.py       # Memory management
│   ├── nudge_manager.py        # Nudging logic
│   ├── orchestrator.py         # Multi-agent orchestration
│   ├── prompt_manager.py       # Prompt chain management
│   ├── rationale_logger.py     # Rationale logging
│   ├── self_evaluation.py      # Self-evaluation prompts
│   ├── shared_memory.py        # Shared memory layer
│   ├── task_persistence.py     # Task persistence system
│   ├── task_tagger.py          # Task categorization
│   └── vector_memory.py        # Vector memory system
├── db/
│   ├── database.py       # Database connection
│   └── supabase_manager.py # Supabase integration
├── models/
│   └── workflow.py       # Workflow data models
├── prompts/
│   ├── builder.json      # Builder agent prompt
│   ├── memory.json       # Memory agent prompt
│   ├── ops.json          # Ops agent prompt
│   └── research.json     # Research agent prompt
├── providers/
│   ├── claude_provider.py # Claude API integration
│   ├── model_router.py   # Model routing logic
│   └── openai_provider.py # OpenAI API integration
├── tools/
│   ├── github_commit.py  # GitHub integration tool
│   └── search_google.py  # Google search tool
└── main.py              # FastAPI application
```

## Logs and Persistence

The system maintains several types of logs:

- **Execution Logs**: Records of all agent executions
- **Rationale Logs**: Agent reasoning and self-evaluation
- **Execution Chain Logs**: Multi-agent workflow records
- **Nudge Logs**: Records of when agents needed user input
- **Pending Tasks**: Suggested but unexecuted tasks
- **Escalation Logs**: Records of when agents needed escalation
- **Behavior Logs**: Feedback on agent performance

## Advanced Usage

### Escalation Protocol

When an agent encounters difficulties, it can escalate the issue:

```json
{
  "output": "I've attempted to implement the solution...",
  "metadata": { ... },
  "reflection": { ... },
  "escalation": {
    "escalation_needed": true,
    "escalation_id": "esc-uuid-here",
    "escalation_reason": "Exceeded retry limit",
    "timestamp": "2025-03-29T19:10:00.000Z"
  }
}
```

You can forward escalations to other agents:

```json
POST /escalations/esc-uuid-here/forward
{
  "target_agent": "ops"
}
```

### Behavior Feedback

Submit feedback on agent performance:

```json
POST /agent/builder/feedback
{
  "task_id": "task-uuid-here",
  "was_successful": true,
  "user_notes": "Great job on the API design!"
}
```

View agent performance metrics:

```
GET /agent/builder/performance
```

Response:

```json
{
  "agent_name": "builder",
  "total_tasks": 42,
  "avg_confidence": 0.85,
  "escalation_count": 3,
  "recent_success_rate": 0.9,
  "success_rate": 0.85,
  "total_feedback_count": 42,
  "recent_feedback_count": 10,
  "timestamp": "2025-03-29T19:10:00.000Z"
}
```

### Goal Awareness

Agent goals are defined in their configuration files:

```json
{
  "name": "Builder Agent",
  "goal_summary": "The Builder Agent is optimizing backend systems to enable a scalable multi-agent infrastructure. Your focus is on creating robust, maintainable code that follows best practices and can scale efficiently."
}
```

These goals are automatically injected into the agent's prompt context before task execution, helping them align with business objectives.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.


# Autonomous Goal Decomposer + Planner Agent

## Overview
The Autonomous Goal Decomposer + Planner Agent serves as the "conductor" for orchestrating multi-agent, multi-step workflows. It receives high-level goals, decomposes them into executable subtasks, assigns the subtasks to relevant agents, sequences their execution, and tracks results across memory.

## Components

### 1. Planner Agent Configuration
The `planner.json` file defines the Planner Agent with:
- A strategic, precise personality modeled after a senior project manager
- Tools for research, routing, memory writing, and status tracking
- Rules for goal decomposition, agent assignment, and escalation
- Control schema permissions for memory access and tool usage

### 2. Agent Router Tool
The `agent_router.py` tool:
- Routes subtasks to the correct agents via internal API
- Waits for responses or handles failures
- Implements retry logic and error handling
- Logs all routing events
- Finds the best agent for a given task based on its description and type

### 3. Planner Orchestrator
The `planner_orchestrator.py` module serves as the execution core that:
- Receives high-level goals
- Breaks them into subtasks using various decomposition strategies
- Assigns subtasks to appropriate agents
- Sequences execution based on dependencies using topological sorting
- Stores progress in vector memory
- Escalates issues to the Guardian Agent or human when necessary
- Provides goal status, resumption, and history replay capabilities

### 4. Logging and Memory Integration
The system includes comprehensive logging and memory integration:
- All goal progress is logged to `/app/logs/planner_execution_log.json`
- Each goal and subtask is stored in vector memory with appropriate metadata
- Memory entries include goal ID, task ID, agent, status, result summary, and timestamp
- The system can retrieve goal status and history from memory

### 5. Goal Replay and Continuation
The system supports:
- Resuming partially completed goals on system restart
- Replaying goal history from memory
- Tracking the state of active goals

## Usage

### Processing a Goal
To process a high-level goal:

```python
from app.core.planner_orchestrator import process_goal

goal = {
    "id": "goal-123",  # Optional, will be generated if not provided
    "description": "Build a weather API",
    "type": "development",
    "context": {
        "priority": "high",
        "deadline": "2025-04-15"
    },
    "decomposition_strategy": "sequential_breakdown"  # Optional
}

result = process_goal(goal)
```

### Getting Goal Status
To check the status of a goal:

```python
from app.core.planner_orchestrator import get_goal_status

status = get_goal_status("goal-123")
```

### Resuming a Goal
To resume a partially completed goal:

```python
from app.core.planner_orchestrator import resume_goal

result = resume_goal("goal-123")
```

### Replaying Goal History
To replay the history of a goal:

```python
from app.core.planner_orchestrator import replay_goal_history

history = replay_goal_history("goal-123")
```

## Decomposition Strategies
The system supports multiple decomposition strategies:

1. **sequential_breakdown**: Breaks the goal into sequential steps with dependencies
2. **parallel_tasks**: Creates parallel tasks with minimal dependencies
3. **dependency_mapping**: Maps complex dependencies between subtasks
4. **iterative_refinement**: Starts with a basic solution and refines it
5. **research_first**: Prioritizes research before implementation

## Agent Assignment
Subtasks are assigned to agents based on:

1. Task type matching (e.g., "code" → builder agent)
2. Keyword analysis in the task description
3. Agent capability mapping from the planner configuration

## Testing
A comprehensive test script (`test_planner_system.py`) is provided to validate:
- Agent router functionality
- Goal decomposition
- Subtask sequencing
- Memory integration
- Goal continuation
- End-to-end goal processing

## Future Enhancements
Potential future enhancements include:
- More sophisticated goal decomposition using LLM-based planning
- Dynamic adjustment of decomposition strategies based on goal type
- Parallel execution of independent subtasks
- Learning from past goal executions to improve future planning
- Integration with external project management tools
