# API Sweep V7 Recommendations

## Overview

This document provides recommendations for addressing the issues identified during the Phase 5.3 Connected API Verification Sweep (V7). These recommendations aim to improve the API health percentage from the current 72.73% to 100%.

## Priority Recommendations

### 1. Implement Memory Thread Endpoint

**Issue:** The `/api/memory/thread` endpoint returns 404 Not Found instead of 200 OK.

**Recommendation:**
- Implement the missing endpoint in `memory_routes.py`
- The endpoint should retrieve thread-based memory entries for a specific project
- Follow the pattern of the existing `/api/memory/read` endpoint

**Implementation Example:**
```python
@router.get("/memory/thread")
async def get_memory_thread(project_id: str):
    """
    Retrieve memory thread for a specific project.
    
    Args:
        project_id: The ID of the project to retrieve memory for
        
    Returns:
        JSON response with memory thread data
    """
    try:
        # Retrieve memory entries for the project
        memory_entries = await get_memory_entries_for_project(project_id)
        
        # Organize entries into thread format
        thread = organize_entries_as_thread(memory_entries)
        
        return {
            "status": "success",
            "message": f"Retrieved memory thread for project {project_id}",
            "thread": thread
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve memory thread: {str(e)}"
        }
```

### 2. Implement Project State Endpoint

**Issue:** The `/api/project/state` endpoint returns 404 Not Found instead of 200 OK.

**Recommendation:**
- Create a new `project_routes.py` file if it doesn't exist
- Implement the endpoint to retrieve the current state of a project as JSON
- Register the router in `main.py`

**Implementation Example:**
```python
from fastapi import APIRouter
from app.core.project_state import get_project_state

router = APIRouter()

@router.get("/project/state")
async def get_state(project_id: str):
    """
    Retrieve the current state of a project as JSON.
    
    Args:
        project_id: The ID of the project to retrieve state for
        
    Returns:
        JSON response with project state data
    """
    try:
        # Get project state
        state = await get_project_state(project_id)
        
        return {
            "status": "success",
            "message": f"Retrieved state for project {project_id}",
            "state": state
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve project state: {str(e)}"
        }
```

**Main.py Update:**
```python
# Import project routes
try:
    from routes.project_routes import router as project_router
    print("✅ Successfully imported project_router")
except ModuleNotFoundError as e:
    print(f"⚠️ Router Load Failed: project_routes — {e}")
    project_router = APIRouter()

# Add to app.include_router section
app.include_router(project_router, prefix="/api")
```

### 3. Fix Orchestrator Consult Endpoint

**Issue:** The `/api/orchestrator/consult` endpoint returns 422 Unprocessable Entity instead of 200 OK.

**Recommendation:**
- Review the request validation in `orchestrator_routes.py`
- Update the endpoint to handle the provided payload correctly
- Add better error handling and payload validation

**Implementation Example:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# Define request model with proper validation
class OrchestratorConsultRequest(BaseModel):
    task: str = Field(..., description="Task description for orchestrator consultation")
    project_id: str = Field(..., description="Project ID for orchestrator consultation")
    context: Optional[str] = Field(None, description="Additional context for the consultation")

# Define response model
class OrchestratorConsultResponse(BaseModel):
    status: str
    message: str
    agent_id: str
    reasoning: str

router = APIRouter()

@router.post("/orchestrator/consult", response_model=OrchestratorConsultResponse)
async def orchestrator_consult(request: OrchestratorConsultRequest):
    """
    Consult the orchestrator to determine the best agent for a task.
    
    Args:
        request: The consultation request containing task and project_id
        
    Returns:
        JSON response with recommended agent and reasoning
    """
    try:
        # Determine the best agent for the task
        agent_id, reasoning = await determine_best_agent(request.task, request.project_id, request.context)
        
        return {
            "status": "success",
            "message": "Orchestrator consultation completed",
            "agent_id": agent_id,
            "reasoning": reasoning
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator consultation failed: {str(e)}"
        )
```

## Additional Recommendations

### 1. Implement Comprehensive Error Handling

- Add consistent error handling across all endpoints
- Use try-except blocks to catch and properly report errors
- Return appropriate HTTP status codes and error messages

### 2. Add Request Validation

- Use Pydantic models for request validation
- Document required fields and their types
- Provide clear error messages for invalid requests

### 3. Improve API Documentation

- Update API documentation to reflect current endpoints
- Include example requests and responses
- Document error codes and their meanings

### 4. Implement API Versioning

- Consider adding API versioning (e.g., `/api/v1/`)
- This will allow for future changes without breaking existing clients

## Implementation Plan

1. **Short-term fixes (Priority 1):**
   - Implement the three missing/broken endpoints
   - Add basic error handling and validation

2. **Medium-term improvements (Priority 2):**
   - Enhance error handling across all endpoints
   - Improve request validation
   - Update API documentation

3. **Long-term enhancements (Priority 3):**
   - Implement API versioning
   - Add comprehensive logging
   - Develop automated API tests

By implementing these recommendations, the API health percentage should improve from 72.73% to 100%, ensuring all expected endpoints are functioning correctly.
