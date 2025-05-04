from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    is_system: bool = False
    user_id: str
    status: str = "idle"
    last_active: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    async def find_by_id(cls, agent_id: str):
        # Mock implementation - in a real app, this would query the database
        if agent_id == "hal9000":
            return Agent(
                id="hal9000",
                name="HAL",
                description="General purpose assistant for everyday tasks and questions.",
                is_system=True,
                user_id="system",
                status="idle",
                last_active="2 hours ago"
            )
        elif agent_id == "ash-xenomorph":
            return Agent(
                id="ash-xenomorph",
                name="ASH",
                description="Advanced security handler for sensitive operations and security monitoring.",
                is_system=True,
                user_id="system",
                status="active",
                last_active="5 minutes ago"
            )
        
        # In a real implementation, this would query the database
        return None
    
    @classmethod
    async def find_by_user_id(cls, user_id: str) -> List["Agent"]:
        # Mock implementation - in a real app, this would query the database
        # Return empty list for now - in a real app, this would return user's agents
        return []
    
    @classmethod
    async def find_system_agents(cls) -> List["Agent"]:
        # Mock implementation - in a real app, this would query the database
        return [
            Agent(
                id="hal9000",
                name="HAL",
                description="General purpose assistant for everyday tasks and questions.",
                is_system=True,
                user_id="system",
                status="idle",
                last_active="2 hours ago"
            ),
            Agent(
                id="ash-xenomorph",
                name="ASH",
                description="Advanced security handler for sensitive operations and security monitoring.",
                is_system=True,
                user_id="system",
                status="active",
                last_active="5 minutes ago"
            )
        ]
    
    async def save(self):
        # Mock implementation - in a real app, this would save to the database
        self.updated_at = datetime.now().isoformat()
        return self
    
    async def delete(self):
        # Mock implementation - in a real app, this would delete from the database
        pass
