# AgentRunner Module Documentation

## Overview

The AgentRunner module provides isolated agent execution functionality, allowing agents to run independently from the central agent registry, UI, or delegate-stream system. This modular approach helps isolate problems and makes the system more robust by providing fallback mechanisms when the registry fails.

## Files

- `app/modules/agent_runner.py` - Core implementation of the isolated agent execution functionality
- `app/api/modules/agent.py` - REST API endpoint for executing agents in isolation
- `app/modules/__init__.py` - Module initialization file
- `app/api/modules/__init__.py` - API module initialization file
- `tests/test_agent_runner.py` - Test script for the AgentRunner module

## Features

- **Isolated Agent Execution**: Run agents without relying on the central registry
- **Fallback Mechanisms**: Continue operating even when the registry fails
- **Direct OpenAI Integration**: Fallback to direct OpenAI calls when needed
- **Comprehensive Error Handling**: Proper handling of all error scenarios
- **Detailed Logging**: Thorough logging for debugging and monitoring

## API Endpoint

The module exposes a REST API endpoint at `/api/modules/agent/run` that accepts POST requests with the following schema:

### Request Schema

```json
{
  "agent_id": "Core.Forge",
  "messages": [{ "role": "user", "content": "What is 7 + 5?" }]
}
```

### Response Schema

```json
{
  "agent_id": "Core.Forge",
  "response": "The answer is 12.",
  "status": "ok",
  "execution_time": 0.25,
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Error Response

```json
{
  "agent_id": "NonExistentAgent",
  "response": "Agent NonExistentAgent not found and no fallback available",
  "status": "error",
  "execution_time": 0.05
}
```

## Usage Examples

### Using the Module Directly

```python
from app.modules.agent_runner import run_agent

# Create messages
messages = [
    {"role": "user", "content": "What is 7 + 5?"}
]

# Run the agent
result = run_agent("Core.Forge", messages)

# Process the result
if result.get("status") == "ok":
    print(f"Response: {result.get('response')}")
else:
    print(f"Error: {result.get('response')}")
```

### Using the API Endpoint

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/modules/agent/run"

# Request data
data = {
    "agent_id": "Core.Forge",
    "messages": [
        {"role": "user", "content": "What is 7 + 5?"}
    ]
}

# Send request
response = requests.post(url, json=data)

# Process response
if response.status_code == 200:
    result = response.json()
    print(f"Response: {result.get('response')}")
else:
    print(f"Error: {response.text}")
```

## Fallback Mechanism

The module implements a multi-level fallback strategy:

1. First, it attempts to use the agent from the registry
2. If the agent is not found or the registry is unavailable:
   - For Core.Forge, it uses a built-in fallback implementation
   - For other agents, it returns an error
3. If the agent doesn't have a `run` method, it falls back to direct OpenAI calls

This ensures that the system can continue operating even when parts of it fail.

## Error Handling

The module handles various error scenarios:

- Registry unavailable
- Agent not found
- OpenAI API errors
- Invalid messages
- Unexpected exceptions

All errors are properly logged and appropriate error responses are returned.

## Integration with Main Application

To integrate this module with the main application, you need to:

1. Include the API router in the main FastAPI application:

   ```python
   from app.api.modules.agent import router as agent_module_router
   app.include_router(agent_module_router, prefix="/api")
   ```

2. Ensure the OpenAI API key is set in the environment variables:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Testing

The module includes a test script that verifies:

1. Core.Forge agent execution
2. Error handling for invalid agents

Run the tests with:

```
python tests/test_agent_runner.py
```
