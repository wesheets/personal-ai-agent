from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.api.auth.security import get_current_user
from app.models.user import User

router = APIRouter()

# Memory models
class MemoryBase(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryResponse(MemoryBase):
    id: str
    agent_id: str
    user_id: str
    timestamp: str
    
    class Config:
        orm_mode = True

class MemoriesResponse(BaseModel):
    memories: List[MemoryResponse]

# Get memories for a specific agent, scoped to current user
@router.get("/agent-{agent_id}", response_model=MemoriesResponse)
async def get_agent_memories(
    agent_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    # In a real implementation, this would query the database
    # For now, return mock data
    
    # Check if agent is a system agent (HAL or ASH)
    is_system_agent = agent_id in ["hal9000", "ash-xenomorph"]
    
    # Mock memories
    memories = []
    
    # Add user-specific memories
    user_memories = [
        {
            "id": f"memory-user-{i}",
            "agent_id": agent_id,
            "user_id": current_user.id,
            "content": f"User-specific memory {i} for agent {agent_id}",
            "timestamp": "2025-04-07T02:00:00Z",
            "metadata": {"type": "user", "tags": ["personal"]}
        }
        for i in range(1, 6)
    ]
    memories.extend(user_memories)
    
    # Add public memories for system agents
    if is_system_agent:
        public_memories = [
            {
                "id": f"memory-public-{i}",
                "agent_id": agent_id,
                "user_id": "system",
                "content": f"Public memory {i} for system agent {agent_id}",
                "timestamp": "2025-04-07T01:00:00Z",
                "metadata": {"type": "public", "tags": ["system"]}
            }
            for i in range(1, 4)
        ]
        memories.extend(public_memories)
    
    # Convert to response model
    memory_responses = [MemoryResponse(**memory) for memory in memories]
    
    # Sort by timestamp (newest first)
    memory_responses.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Apply limit
    memory_responses = memory_responses[:limit]
    
    return {"memories": memory_responses}

# Create a new memory
@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory: MemoryCreate,
    agent_id: str,
    current_user: User = Depends(get_current_user)
):
    # In a real implementation, this would save to the database
    # For now, return mock data
    new_memory = {
        "id": f"memory-{agent_id}-{current_user.id}",
        "agent_id": agent_id,
        "user_id": current_user.id,
        "content": memory.content,
        "timestamp": "2025-04-07T03:00:00Z",
        "metadata": memory.metadata or {}
    }
    
    return MemoryResponse(**new_memory)

# Delete a memory
@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user)
):
    # In a real implementation, this would delete from the database
    # For now, just check if the memory belongs to the user
    
    # Mock check - in a real implementation, this would query the database
    if not memory_id.startswith("memory-user-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this memory"
        )
    
    # Return success
    return None
