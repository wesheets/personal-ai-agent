# Enhanced AI Agent System

A personal AI agent system with vector memory, multi-model support, and configurable agent personalities.

## Features

- **Vector Memory System**: Store and retrieve memories using Supabase with pgvector
- **Multi-Model Support**: Pluggable architecture supporting both OpenAI and Claude models
- **Unlimited Agent Creation**: Add new agents by simply creating prompt configuration files
- **Agent Specialization**: Builder, Ops, Research, Memory agents with configurable personalities
- **Fallback Mechanisms**: Automatic fallback between models if one fails
- **Priority Flagging**: Flag important memories for faster retrieval

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
- **GET /agent/{agent_name}/history**: Get history of agent interactions

### Memory Endpoints

- **POST /memory/add**: Add a new memory
- **POST /memory/search**: Search for memories
- **GET /memory/get/{memory_id}**: Get a specific memory
- **PATCH /memory/priority/{memory_id}**: Update memory priority
- **DELETE /memory/delete/{memory_id}**: Delete a memory
- **GET /memory/status**: Get memory system status

### System Endpoints

- **GET /system/models**: Get available models

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

No code changes required! The system dynamically registers routes for all prompt files found in the `app/prompts` directory.

## Agent Personalities

Each agent has a configurable personality defined in its prompt file:

- **Builder**: Blunt, precise senior backend engineer who pushes back on bad architecture
- **Ops**: Methodical and practical systems reliability engineer
- **Research**: Analytical and thorough research analyst
- **Memory**: Helpful and precise knowledge manager

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
```

## Postman Collection

A Postman collection is included for testing the API endpoints. Import `postman_collection.json` into Postman to get started.

## License

MIT
