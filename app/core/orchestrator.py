import os
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.confidence_retry import get_confidence_retry_manager
from app.core.nudge_manager import get_nudge_manager
from app.core.task_persistence import get_task_persistence_manager
from app.core.task_state_manager import get_task_state_manager

class OrchestratorStep(BaseModel):
    """Model for a step in an orchestration chain"""
    step_number: int
    agent_name: str
    input_text: str
    output_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    reflection: Optional[Dict[str, Any]] = None
    retry_data: Optional[Dict[str, Any]] = None
    nudge_data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class OrchestratorChain(BaseModel):
    """Model for an orchestration chain"""
    chain_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[OrchestratorStep] = Field(default_factory=list)
    status: str = "in_progress"  # in_progress, completed, failed
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Orchestrator:
    """
    Orchestrator for multi-agent workflows
    
    This class handles routing tasks between agents based on suggested next steps,
    task categories, and agent configurations.
    """
    
    def __init__(self):
        """Initialize the Orchestrator"""
        from app.core.prompt_manager import PromptManager
        from app.core.execution_chain_logger import get_execution_chain_logger
        
        self.prompt_manager = PromptManager()
        self.execution_chain_logger = get_execution_chain_logger()
        self.confidence_retry_manager = get_confidence_retry_manager()
        self.nudge_manager = get_nudge_manager()
        self.task_persistence_manager = get_task_persistence_manager()
        self.task_state_manager = get_task_state_manager()  # Initialize task_state_manager
        self.execution_mode = "manual"  # Default execution mode
    
    async def execute_with_agent(
        self,
        agent_type: str,
        input_text: str,
        chain_id: Optional[str] = None,
        step_number: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        auto_orchestrate: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a task with a specific agent
        
        Args:
            agent_type: The type of agent to use
            input_text: The input text to process
            chain_id: Optional chain ID for multi-step orchestration
            step_number: Step number in the orchestration chain
            metadata: Optional metadata to include in the response
            auto_orchestrate: Whether to automatically orchestrate next steps
            
        Returns:
            The agent's response with orchestration metadata
        """
        # Mock response for testing when credentials are missing
        if os.environ.get("OPENAI_API_KEY") is None or os.environ.get("SUPABASE_URL") is None:
            print(f"Using mock response for orchestrator with {agent_type} agent")
            return {
                "agent_type": agent_type,
                "input": input_text,
                "output": f"Mock response from {agent_type} agent: I've processed your request.",
                "model": "mock-model",
                "processing_time": 0.1,
                "metadata": metadata or {},
                "chain_id": chain_id or str(uuid.uuid4()),
                "step_number": step_number,
                "suggested_next_step": None
            }
            
        # Process with the agent
        from app.core.prompt_manager import get_prompt_manager
        prompt_manager = get_prompt_manager()
        
        response = await prompt_manager.process_with_agent(
            agent_type=agent_type,
            input_text=input_text,
            metadata=metadata
        )
        
        # TODO: Extract suggested next step from response
        suggested_next_step = None
        
        # Create orchestration step
        step = OrchestratorStep(
            step_number=step_number,
            agent_name=agent_type,
            input_text=input_text,
            output_text=response["output"],
            metadata=response["metadata"]
        )
        
        # Create or update orchestration chain
        if chain_id:
            # TODO: Load existing chain and append step
            pass
        else:
            chain = OrchestratorChain(steps=[step])
            chain_id = chain.chain_id
            
            # Log the chain
            await self.execution_chain_logger.log_chain(chain)
        
        # Auto-orchestrate if enabled and there's a suggested next step
        if auto_orchestrate and suggested_next_step:
            # TODO: Implement auto-orchestration
            pass
        
        # Return the response with orchestration metadata
        return {
            **response,
            "chain_id": chain_id,
            "step_number": step_number,
            "suggested_next_step": suggested_next_step
        }

# Singleton instance
_orchestrator = None

def get_orchestrator() -> Orchestrator:
    """
    Get the singleton Orchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
