from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.api.auth.security import get_current_user
from app.models.user import User
from app.models.agent import Agent

router = APIRouter()

# Agent models
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    is_system: bool = False

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    pass

class AgentResponse(AgentBase):
    id: str
    user_id: str
    status: str = "idle"
    last_active: Optional[str] = None
    
    class Config:
        orm_mode = True

class AgentsResponse(BaseModel):
    agents: List[AgentResponse]

# Get all agents for current user (including system agents)
@router.get("/agents", response_model=AgentsResponse)
async def get_agents(current_user: User = Depends(get_current_user)):
    # Get user's agents
    user_agents = await Agent.find_by_user_id(current_user.id)
    
    # Get system agents (HAL and ASH)
    system_agents = await Agent.find_system_agents()
    
    # Combine user agents and system agents
    all_agents = user_agents + system_agents
    
    return {"agents": all_agents}

# Get agent by ID
@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await Agent.find_by_id(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if agent belongs to user or is a system agent
    if agent.user_id != current_user.id and not agent.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this agent"
        )
    
    return agent

# Create a new agent
@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, current_user: User = Depends(get_current_user)):
    # Users cannot create system agents
    if agent.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create system agents"
        )
    
    # Create new agent with user_id
    new_agent = Agent(
        name=agent.name,
        description=agent.description,
        avatar=agent.avatar,
        is_system=False,  # Force is_system to be False
        user_id=current_user.id,
        status="idle"
    )
    
    # Save agent to database
    created_agent = await new_agent.save()
    
    return created_agent

# Update an agent
@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentUpdate, current_user: User = Depends(get_current_user)):
    existing_agent = await Agent.find_by_id(agent_id)
    
    if not existing_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if agent belongs to user
    if existing_agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this agent"
        )
    
    # Cannot change system status
    if agent.is_system != existing_agent.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change system status of an agent"
        )
    
    # Update agent
    existing_agent.name = agent.name
    existing_agent.description = agent.description
    existing_agent.avatar = agent.avatar
    
    # Save updated agent
    updated_agent = await existing_agent.save()
    
    return updated_agent

# Delete an agent
@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    existing_agent = await Agent.find_by_id(agent_id)
    
    if not existing_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if agent belongs to user
    if existing_agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this agent"
        )
    
    # Cannot delete system agents
    if existing_agent.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system agents"
        )
    
    # Delete agent
    await existing_agent.delete()
    
    return None
