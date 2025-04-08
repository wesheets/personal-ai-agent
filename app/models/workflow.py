from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

class AgentStepMetadata(BaseModel):
    """Metadata for an agent step in a workflow"""
    agent: str
    model: str
    tokens_used: int = 0
    timestamp: str
    provider: str = "unknown"
    priority: bool = False
    tools_used: List[str] = Field(default_factory=list)
    task_category: Optional[str] = None
    suggested_next_step: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    log_id: Optional[str] = None

class AgentStepReflection(BaseModel):
    """Reflection data for an agent step in a workflow"""
    rationale: str
    assumptions: str
    improvement_suggestions: str
    confidence_level: str
    failure_points: str
    memory_analysis: Optional[str] = None
    rationale_log_id: Optional[str] = None

class AgentStep(BaseModel):
    """A single step in a multi-agent workflow"""
    step_number: int
    agent_name: str
    input: str
    output: str
    metadata: AgentStepMetadata
    reflection: Optional[AgentStepReflection] = None

class WorkflowResponse(BaseModel):
    """Response model for multi-agent workflows"""
    steps: List[AgentStep]
    chain_id: str
    status: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_tokens: int = 0
    total_steps: int = 0
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "steps": [
                    {
                        "step_number": 1,
                        "agent_name": "builder",
                        "input": "I need to create a REST API for a blog with users, posts, and comments.",
                        "output": "I'll help you create a REST API for a blog...",
                        "metadata": {
                            "agent": "builder",
                            "model": "gpt-4",
                            "tokens_used": 1250,
                            "timestamp": "2025-03-29T19:00:00.000Z",
                            "provider": "openai",
                            "priority": False,
                            "tools_used": [],
                            "task_category": "code",
                            "suggested_next_step": "Implement the database schema",
                            "tags": ["api", "backend", "fastapi"],
                            "log_id": "execution_log_123"
                        },
                        "reflection": {
                            "rationale": "I provided a comprehensive REST API implementation...",
                            "assumptions": "I assumed the user needs authentication...",
                            "improvement_suggestions": "Could add more details on deployment...",
                            "confidence_level": "High confidence (90%) because this is a standard pattern...",
                            "failure_points": "The security implementation is basic and would need enhancement...",
                            "memory_analysis": "This request is similar to previous API design requests...",
                            "rationale_log_id": "rationale_log_123"
                        }
                    },
                    {
                        "step_number": 2,
                        "agent_name": "ops",
                        "input": "Continue this task based on the previous agent's output...",
                        "output": "Now that we have the API design, let's set up the deployment...",
                        "metadata": {
                            "agent": "ops",
                            "model": "gpt-4",
                            "tokens_used": 980,
                            "timestamp": "2025-03-29T19:01:00.000Z",
                            "provider": "openai",
                            "priority": False,
                            "tools_used": [],
                            "task_category": "deployment",
                            "suggested_next_step": "Test the API endpoints",
                            "tags": ["deployment", "docker", "ci-cd"],
                            "log_id": "execution_log_124"
                        },
                        "reflection": {
                            "rationale": "I focused on containerization and deployment...",
                            "assumptions": "I assumed Docker would be the preferred deployment method...",
                            "improvement_suggestions": "Could add Kubernetes manifests for scaling...",
                            "confidence_level": "Medium-high confidence (80%) in the deployment approach...",
                            "failure_points": "The CI/CD pipeline might need customization for specific environments...",
                            "memory_analysis": "Previous deployments have used similar Docker configurations...",
                            "rationale_log_id": "rationale_log_124"
                        }
                    }
                ],
                "chain_id": "workflow_chain_123",
                "status": "completed",
                "created_at": "2025-03-29T19:00:00.000Z",
                "updated_at": "2025-03-29T19:01:30.000Z",
                "total_tokens": 2230,
                "total_steps": 2
            }
        }
    }
