# Enhanced AI Agent System

A personal AI agent system with vector memory, multi-model support, configurable agent personalities, tool integration, agent reflection capabilities, and multi-agent workflow orchestration.

## Features

- **Vector Memory System**: Store and retrieve memories using Supabase with pgvector
- **Shared Memory Layer**: Global and agent-specific memory scopes with topic filtering
- **Multi-Model Support**: Pluggable architecture supporting both OpenAI and Claude models
- **Unlimited Agent Creation**: Add new agents by simply creating prompt configuration files
- **Tool Integration**: Extensible tool system with support for custom tools
- **Execution Logging**: Comprehensive audit trail of all agent interactions
- **Agent Specialization**: Builder, Ops, Research, Memory agents with configurable personalities
- **Fallback Mechanisms**: Automatic fallback between models if one fails
- **Priority Flagging**: Flag important memories for faster retrieval
- **Agent Reflection**: Rationale logging, self-evaluation, and memory context review
- **Task Tagging**: Categorization and next step suggestions for future orchestration
- **Multi-Agent Workflow Orchestration**: Agents can pass work between each other based on suggested next steps

## New in Phase 2.2: Multi-Agent Workflow Orchestration

- **Orchestrator Module**: Automatically routes tasks between agents based on suggested next steps
- **Agent Routing Config**: Each agent defines what tasks it accepts and what keywords trigger handoffs
- **Execution Chain Logging**: Comprehensive logging of multi-agent workflows
- **Control Parameters**: Optional auto_orchestrate parameter to enable automatic handoffs
- **Structured Output**: Array of step responses when multiple agents are called in sequence

## Tech Stack

- **Backend**: FastAPI
- **Containerization**: Docker
- **AI Models**: OpenAI GPT-4 and Anthropic Claude 3
- **Vector Database**: Supabase with pgvector

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (optional)
- OpenAI API key
- Claude API key (optional)
- Supabase account and project

### Environment Setup

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

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Supabase Setup

1. Create a new Supabase project
2. Enable the pgvector extension in the SQL editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Run the SQL setup script from `app/db/supabase_setup.sql` in the Supabase SQL editor

### Running Locally

Start the FastAPI server:
```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Docker Deployment

Build and run with Docker Compose:
```
docker-compose up --build
```

## API Endpoints

### Agent Endpoints

- **POST /agent/{agent_name}**: Process a request using the specified agent
  - Now includes reflection data in the response
  - Supports auto_orchestrate parameter for multi-agent workflows
- **GET /agent/{agent_name}/history**: Get history of agent interactions
- **GET /agent/{agent_name}/rationale**: Get rationale logs for an agent

### Orchestration Endpoints

- **POST /agent/orchestrate**: Orchestrate a multi-agent workflow
  - Requires agent_type parameter to specify the initial agent
- **GET /agent/chains**: Get all execution chains
- **GET /agent/chains/{chain_id}**: Get a specific execution chain
- **GET /agent/chains/{chain_id}/steps/{step_number}**: Get a specific step in an execution chain

### Memory Endpoints

- **POST /memory/add**: Add a new memory
- **POST /memory/search**: Search for memories
- **GET /memory/get/{memory_id}**: Get a specific memory
- **PATCH /memory/priority/{memory_id}**: Update memory priority
- **DELETE /memory/delete/{memory_id}**: Delete a memory
- **GET /memory/status**: Get memory system status

### System Endpoints

- **GET /system/models**: Get available models
- **GET /system/tools**: Get available tools

## Multi-Agent Workflow Orchestration

### How It Works

1. A user sends a request to an agent with `auto_orchestrate: true`
2. The agent processes the request and generates a response with a `suggested_next_step`
3. The orchestrator determines which agent should handle the next step based on:
   - Task category matching (via `accepts_tasks` in agent config)
   - Keyword matching (via `handoff_keywords` in agent config)
   - Direct agent mentions in the suggested next step
4. The next agent receives the previous agent's output and the suggested next step
5. This process continues until there are no more suggested next steps or the maximum number of steps is reached
6. The entire workflow is logged in the execution chain logs

### Agent Routing Configuration

Each agent has a routing configuration in its prompt file:

```json
{
  "accepts_tasks": ["code", "architecture", "design"],
  "handoff_keywords": ["build", "implement", "code", "develop"]
}
```

- `accepts_tasks`: Categories of tasks this agent can handle
- `handoff_keywords`: Keywords that trigger a handoff to this agent

### Example Workflow Request

```json
{
  "input": "I need to create a REST API for a blog and deploy it to production",
  "auto_orchestrate": true
}
```

This might trigger a workflow like:
1. Builder agent creates the API design and code
2. Ops agent handles the deployment configuration
3. Memory agent summarizes the entire process

### Execution Chain Logging

Each workflow execution is logged in the `execution_chain_logs` directory:
- One directory per chain, named with the chain ID
- `chain.json` contains the overall chain metadata
- `step_1.json`, `step_2.json`, etc. contain individual step details
- Links to related execution logs and rationale logs

## Agent Reflection & Reasoning

### Rationale Logging

After each agent completes a task, it generates answers to:
- "What was your rationale for this response?"
- "What assumptions did you make?"
- "What could improve this next time?"

These reflections are stored in the `rationale_logs/` directory as JSON files, one per interaction.

### Self-Evaluation

Agents now reflect on their outputs with:
- "How confident are you in this output?"
- "What are possible failure points?"

This self-evaluation is stored alongside the rationale in the same log file.

### Memory Context Review

When retrieving memories, agents now analyze:
- "Here are previous related memories. How do they connect to the current task?"

This helps agents connect dots over time and build on past interactions.

### Task Tagging Metadata

Execution logs now include:
- `task_category` (e.g., code, strategy, research)
- `suggested_next_step` (optional field for future actions)
- `tags` (relevant keywords for the task)

This prepares the system for future orchestration and workflow automation.

## Creating New Agents

You can create new agents without modifying any code:

1. Create a new prompt configuration file in `app/prompts/{agent_name}.json`:

```json
{
  "model": "gpt-4",
  "system": "You are a helpful {agent_name} agent that specializes in...",
  "temperature": 0.7,
  "max_tokens": 1500,
  "persona": {
    "tone": "helpful and precise",
    "role": "specialized assistant",
    "rules": [
      "Rule 1",
      "Rule 2",
      "Rule 3"
    ]
  },
  "tools": [
    "search_google",
    "github_commit"
  ],
  "accepts_tasks": [
    "category1",
    "category2"
  ],
  "handoff_keywords": [
    "keyword1",
    "keyword2"
  ],
  "examples": [
    {
      "user": "Example user input",
      "assistant": "Example assistant response"
    }
  ]
}
```

2. Restart the server, and the new agent will be automatically available at:
   - **POST /agent/{agent_name}**
   - **GET /agent/{agent_name}/history**
   - **GET /agent/{agent_name}/rationale**

No code changes required! The system dynamically registers routes for all prompt files found in the `app/prompts` directory.

## Agent Personalities

Each agent has a configurable personality defined in its prompt file:

- **Builder**: Blunt, precise senior backend engineer who pushes back on bad architecture
- **Ops**: Methodical and practical systems reliability engineer
- **Research**: Analytical and thorough research analyst
- **Memory**: Helpful and precise knowledge manager

## Tool System

The system includes a tool framework that allows agents to use external tools:

1. Tools are defined in the `app/tools/` directory
2. Each agent can specify which tools it can use in its prompt configuration
3. Tools can be overridden in the API request using the `tools_to_use` parameter

Available tools:
- **search_google**: Search Google for information
- **github_commit**: Commit changes to a GitHub repository

To add a new tool:
1. Create a new Python file in `app/tools/`
2. Implement the tool class with an `execute()` method
3. Add a getter function that returns a singleton instance
4. The tool will be automatically loaded and available to agents

## Shared Memory Layer

The system includes a shared memory layer that allows agents to share information:

1. Memories can be scoped as "global" or "agent-specific"
2. Memories can be tagged with topics for semantic filtering
3. Agents can retrieve relevant memories from both their own scope and the global scope

## Execution Logging

The system includes comprehensive logging of all agent interactions:

1. Each agent execution is logged with:
   - Agent name
   - Timestamp
   - Model used
   - Input/output summaries
   - Tools used
   - Task category and suggested next steps
   - Additional metadata

2. Logs are stored as individual JSON files in the `execution_logs/` directory

## Rationale Logging

The system includes comprehensive logging of agent rationale and self-evaluation:

1. Each agent reflection is logged with:
   - Rationale for the response
   - Assumptions made
   - Improvement suggestions
   - Confidence level
   - Potential failure points
   - Task category and suggested next steps

2. Logs are stored as individual JSON files in the `rationale_logs/` directory

## Model Selection

You can specify which model to use in two ways:

1. In the agent's prompt configuration file (`app/prompts/{agent_name}.json`)
2. By passing a `model` parameter in the API request:
   ```json
   {
     "input": "Your query here",
     "model": "claude-3-sonnet"
   }
   ```

## Obtaining API Keys

### OpenAI API Key

1. Go to [OpenAI's platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to the API keys section
4. Create a new secret key
5. Add to your `.env` file as `OPENAI_API_KEY`

### Claude API Key

1. Go to [Anthropic's console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to the API keys section
4. Create a new API key
5. Add to your `.env` file as `CLAUDE_API_KEY`

## Security Considerations

- Never commit your `.env` file to version control
- Consider using a secrets manager for production deployments
- Rotate API keys regularly
- Set appropriate rate limits and budgets on your API keys

## Testing

Run the test suite:
```
python -m tests.test_memory_integration
python -m tests.test_multi_model_support
python -m tests.test_claude_integration
python -m tests.test_reflection_capabilities
python -m tests.test_multi_agent_workflow
```

## Postman Collection

A Postman collection is included for testing the API endpoints. Import `postman_collection.json` into Postman to get started.

## License

MIT
