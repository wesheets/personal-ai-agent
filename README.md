# Personal AI Agent System

A modular AI agent system modeled after Manus, built with FastAPI, Docker, and OpenAI integration.

## Overview

This project implements a personal AI agent system with multiple specialized agents:

- **Builder Agent**: Helps with planning, organizing, and implementing software architectures
- **Ops Agent**: Assists with troubleshooting, automation, and process improvement
- **Research Agent**: Gathers and analyzes information, providing comprehensive reports
- **Memory Agent**: Stores and retrieves information from past interactions

The system is designed to be modular, extensible, and easy to deploy using Docker.

## Tech Stack

- **Backend**: FastAPI
- **Containerization**: Docker
- **AI**: OpenAI GPT-4 via API
- **Memory**: Local file-based storage (with Supabase integration option)

## Features

- Modular agent routes with specialized capabilities
- Dynamic prompt chain loading from JSON/YAML files
- Memory system for storing and retrieving past interactions
- Comprehensive API documentation with Swagger UI
- Docker containerization for easy deployment

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- OpenAI API key

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/wesheets/personal-ai-agent.git
   cd personal-ai-agent
   ```

2. Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DB_TYPE=local  # Use "supabase" for Supabase integration
   
   # Only needed if using Supabase
   # SUPABASE_URL=your_supabase_url
   # SUPABASE_KEY=your_supabase_key
   ```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Access the API documentation at http://localhost:8000/docs

### Running with Docker

1. Build and start the Docker container:
   ```bash
   docker-compose up --build
   ```

2. Access the API documentation at http://localhost:8000/docs

## API Usage

The system provides several endpoints for interacting with different agent types:

### Builder Agent

```bash
# Process a request with the Builder agent
curl -X POST http://localhost:8000/agent/builder/ \
  -H "Content-Type: application/json" \
  -d '{
    "input": "I want to create a React application with TypeScript",
    "context": {
      "project_name": "my-react-app"
    }
  }'

# Get history of Builder agent interactions
curl -X GET http://localhost:8000/agent/builder/history?limit=5
```

### Ops Agent

```bash
# Process a request with the Ops agent
curl -X POST http://localhost:8000/agent/ops/ \
  -H "Content-Type: application/json" \
  -d '{
    "input": "How can I optimize my Docker containers?",
    "context": {
      "application_type": "node.js"
    }
  }'

# Get history of Ops agent interactions
curl -X GET http://localhost:8000/agent/ops/history?limit=5
```

### Research Agent

```bash
# Process a request with the Research agent
curl -X POST http://localhost:8000/agent/research/ \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compare different machine learning frameworks",
    "context": {
      "focus_areas": ["ease of use", "deployment"]
    }
  }'

# Get history of Research agent interactions
curl -X GET http://localhost:8000/agent/research/history?limit=5
```

### Memory Agent

```bash
# Store a memory
curl -X POST http://localhost:8000/agent/memory/store \
  -H "Content-Type: application/json" \
  -d '{
    "input": "How do I implement a vector database?",
    "output": "You can use technologies like Pinecone or Weaviate...",
    "metadata": {
      "topic": "vector_databases"
    }
  }'

# Query memories
curl -X POST http://localhost:8000/agent/memory/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vector database",
    "limit": 5
  }'

# Get memory statistics
curl -X GET http://localhost:8000/agent/memory/stats
```

## Customizing Prompt Chains

Prompt chains are stored as JSON files in the `app/prompts` directory. Each agent type has its own prompt chain file:

- `builder.json`: Prompt chain for the Builder agent
- `ops.json`: Prompt chain for the Ops agent
- `research.json`: Prompt chain for the Research agent
- `memory.json`: Prompt chain for the Memory agent

You can customize these files to change the behavior of the agents. Each prompt chain file has the following structure:

```json
{
  "model": "gpt-4",
  "system": "System prompt that defines the agent's role and capabilities",
  "temperature": 0.7,
  "max_tokens": 1500,
  "examples": [
    {
      "user": "Example user input",
      "assistant": "Example assistant response"
    }
  ]
}
```

## Testing with Postman

A Postman collection is included in the repository for testing the API endpoints. To use it:

1. Import the `postman_collection.json` file into Postman
2. Set the `base_url` variable to your API endpoint (default: `http://localhost:8000`)
3. Use the collection to test the various endpoints

## Project Structure

```
personal-ai-agent/
├── app/
│   ├── api/
│   │   └── agent/
│   │       ├── builder.py
│   │       ├── ops.py
│   │       ├── research.py
│   │       └── memory.py
│   ├── core/
│   │   ├── openai_client.py
│   │   ├── prompt_manager.py
│   │   └── memory_manager.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   ├── utils/
│   ├── prompts/
│   │   ├── builder.json
│   │   ├── ops.json
│   │   ├── research.json
│   │   └── memory.json
│   └── main.py
├── logs/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── postman_collection.json
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
