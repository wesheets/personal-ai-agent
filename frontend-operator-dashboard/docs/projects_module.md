# Projects Module Documentation

## Overview

The Projects module provides endpoints for creating and querying project containers as part of the System Lockdown Phase. This module allows creating project containers for orchestrated goals, retrieving project metadata for trace filtering, and scoping memory and task activity by project_id.

## Endpoints

### POST /app/projects

Creates a new project container for orchestrated goals.

#### Input Schema

```json
{
  "project_id": "string",
  "goal": "string",
  "user_id": "string",
  "tags": ["optional", "array"],
  "context": "optional string (summary or notes)"
}
```

#### Output Schema

```json
{
  "status": "success",
  "project_id": "...",
  "created_at": "...",
  "log_id": "...",
  "stored": true
}
```

#### Example Usage

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/app/projects"

# Create a new project
payload = {
    "project_id": "proj-123",
    "goal": "Build a vertical journaling SaaS",
    "user_id": "user-001",
    "tags": ["journaling", "vertical", "foundrflow"],
    "context": "Summary of planning session"
}

response = requests.post(BASE_URL, json=payload)
print(json.dumps(response.json(), indent=2))
```

### GET /app/projects

Query projects by various parameters.

#### Query Parameters

- `project_id`: Filter by project ID (optional)
- `user_id`: Filter by user ID (optional)
- `tags`: Filter by tags, comma-separated (optional)

#### Output Schema

```json
[
  {
    "project_id": "proj-123",
    "goal": "Build a vertical journaling SaaS",
    "user_id": "user-001",
    "tags": ["journaling", "vertical", "foundrflow"],
    "created_at": "...",
    "context": "Summary of planning session"
  }
]
```

#### Example Usage

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/app/projects"

# Query by project_id
response = requests.get(f"{BASE_URL}?project_id=proj-123")
print(json.dumps(response.json(), indent=2))

# Query by user_id
response = requests.get(f"{BASE_URL}?user_id=user-001")
print(json.dumps(response.json(), indent=2))

# Query by tags
response = requests.get(f"{BASE_URL}?tags=journaling,vertical")
print(json.dumps(response.json(), indent=2))
```

## Memory Behavior

Projects are stored in memory with the following metadata:

- `memory_type`: "project_meta"
- `agent_id`: ID of the user who owns the project
- `content`: Human-readable summary of the project
- `tags`: ["project", "meta", "sdk_compliant"] + any user-provided tags
- `project_id`: Project identifier for context
- `status`: "active"

## Logging

The module provides comprehensive logging capabilities:

- Success/failure logging to console
- Human-readable summaries for observers
- Structured logging for future UI audit tools

## Testing

A test script is provided at `/tests/test_projects_module.py` to validate:

- Project creation
- GET filtering by project_id, user_id, and tags
- Memory writing
- Error handling

To run the test script:

```bash
cd /home/ubuntu/personal-ai-agent
python tests/test_projects_module.py
```

## Integration

The Projects module is integrated into the main application in `main.py`:

```python
from app.api.projects import router as projects_router  # Import the projects router
app.include_router(projects_router, prefix="/app")  # Mount the projects router
```

This makes the endpoints accessible at:

- POST /app/projects
- GET /app/projects

## SDK Compliance

This module complies with Promethios_Module_Contract_v1.0.0 by:

- Validating required input fields
- Returning structured responses with all required fields
- Writing memory with proper metadata and trace fields
- Providing comprehensive logging for failures or validation errors
