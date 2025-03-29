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
- **Comprehensive Logging**: Execution logs, rationale logs, and execution chain logs
- **Tool Integration**: Pluggable tool system for external integrations
- **Docker Containerization**: Easy deployment with Docker

## Phase 2.3: Nudging, Looping, and Task Persistence

The latest update (Phase 2.3) adds several powerful features to enhance agent intelligence:

### 1. Confidence-Based Retry Loop

When an agent's self-evaluation indicates low confidence, the system automatically triggers a retry with revised instructions. This helps improve response quality without user intervention.

- Configurable confidence threshold
- Automatic retry with context from the original attempt
- Comparison of original and retry confidence levels
- Option to enable/disable via `enable_retry_loop` parameter

### 2. Nudging Logic

The system now detects when agents are uncertain or blocked and generates appropriate nudge messages to request user input.

- Pattern detection for uncertainty indicators
- Contextual nudge message generation
- Comprehensive logging in `/nudge_logs/`
- Integration with orchestration to pause workflows when user input is needed

### 3. Suggested Task Persistence

When `auto_orchestrate` is disabled but an agent suggests a next step, the system now stores this as a pending task that can be executed later.

- Persistent storage in `/pending_tasks/`
- Task metadata including origin agent, suggested agent, priority, etc.
- New endpoints for listing and executing pending tasks
- Integration with the existing orchestration system

### 4. API Parameter Controls

New API parameters provide fine-grained control over the system's behavior:

- `enable_retry_loop: true/false` - Controls whether confidence-based retry is active
- `auto_orchestrate: true/false` - Controls whether suggested next steps are automatically executed

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

#### Viewing Pending Tasks

```
GET /tasks/pending
```

#### Executing a Pending Task

```json
POST /tasks/execute
{
  "task_id": "task-uuid-here"
}
```

#### Viewing Nudge Logs

```
GET /nudges
```

## Creating Custom Agents

1. Create a new prompt configuration file in `app/prompts/`:
   ```json
   {
     "name": "My Custom Agent",
     "model": "gpt-4",
     "system": "You are a specialized agent that...",
     "accepts_tasks": ["category1", "category2"],
     "handoff_keywords": ["keyword1", "keyword2"],
     "tools": ["tool1", "tool2"]
   }
   ```

2. The agent will be automatically available at `/agent/your_file_name`

## Architecture

```
app/
├── api/
│   ├── agent.py          # Main agent API routes
│   └── memory.py         # Memory API routes
├── core/
│   ├── confidence_retry.py     # Confidence-based retry logic
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

## Advanced Usage

### Confidence-Based Retry

The system automatically retries when agent confidence is low:

```json
POST /agent/builder
{
  "input": "Create a complex architecture for a distributed system",
  "enable_retry_loop": true
}
```

Response will include both original and retry data if triggered:

```json
{
  "output": "Improved response after retry...",
  "metadata": { ... },
  "reflection": { ... },
  "retry_data": {
    "original_confidence": "Medium confidence (6/10)",
    "retry_confidence": "High confidence (8/10)",
    "retry_response": "Improved response...",
    "retry_timestamp": "2025-03-29T19:10:00.000Z"
  }
}
```

### Handling Nudges

When an agent is uncertain or blocked, it will generate a nudge:

```json
{
  "output": "I've analyzed the requirements...",
  "metadata": { ... },
  "reflection": { ... },
  "nudge": {
    "nudge_needed": true,
    "nudge_message": "I need additional information about the database schema. Could you provide more details?",
    "nudge_reason": "needs_information",
    "nudge_id": "nudge-uuid-here"
  }
}
```

### Task Persistence

View and execute pending tasks:

```
GET /tasks/pending?origin_agent=builder&status=pending
```

```json
POST /tasks/execute
{
  "task_id": "task-uuid-here"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
