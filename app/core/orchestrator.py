import os
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.confidence_retry import get_confidence_retry_manager
from app.core.nudge_manager import get_nudge_manager
from app.core.task_persistence import get_task_persistence_manager

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
    
    async def orchestrate(
        self,
        initial_agent: str,
        initial_input: str,
        context: Optional[Dict[str, Any]] = None,
        auto_orchestrate: bool = True,
        max_steps: int = 5,
        background_tasks=None,
        db=None,
        supabase_client=None,
        enable_retry_loop: bool = True
    ) -> OrchestratorChain:
        """
        Orchestrate a multi-agent workflow
        
        Args:
            initial_agent: The initial agent to use
            initial_input: The initial input
            context: Additional context for the request
            auto_orchestrate: Whether to automatically orchestrate the workflow
            max_steps: Maximum number of steps in the workflow
            background_tasks: FastAPI background tasks
            db: Database connection
            supabase_client: Supabase client
            enable_retry_loop: Whether to enable confidence-based retry loop
            
        Returns:
            The orchestration chain
        """
        # Create a new chain
        chain = OrchestratorChain()
        
        # Log the chain
        await self.execution_chain_logger.log_chain(chain)
        
        # Process the initial agent
        from app.api.agent import AgentRequest, process_agent_request
        
        current_agent = initial_agent
        current_input = initial_input
        current_context = context or {}
        step_number = 1
        
        while step_number <= max_steps:
            # Create a request for the current agent
            request = AgentRequest(
                input=current_input,
                context=current_context,
                save_to_memory=True,
                auto_orchestrate=False,  # We handle orchestration here
                enable_retry_loop=enable_retry_loop  # Pass through the retry loop setting
            )
            
            # Process the request
            response = await process_agent_request(
                agent_type=current_agent,
                request=request,
                background_tasks=background_tasks,
                db=db,
                supabase_client=supabase_client
            )
            
            # Create a step for this agent
            step = OrchestratorStep(
                step_number=step_number,
                agent_name=current_agent,
                input_text=current_input,
                output_text=response.output,
                metadata=response.metadata,
                reflection=response.reflection,
                retry_data=response.retry_data,
                nudge_data=response.nudge
            )
            
            # Add the step to the chain
            chain.steps.append(step)
            
            # Log the step
            await self.execution_chain_logger.log_step(chain.chain_id, step)
            
            # Update the chain
            chain.updated_at = datetime.now().isoformat()
            await self.execution_chain_logger.update_chain(chain)
            
            # Check if we should continue orchestration
            if not auto_orchestrate:
                # If auto_orchestrate is disabled, we're done after the first step
                chain.status = "completed"
                await self.execution_chain_logger.update_chain(chain)
                return chain
            
            # Check if there's a nudge that requires user input
            if response.nudge and response.nudge.get("nudge_needed", False):
                # If there's a nudge, we need to pause for user input
                chain.status = "needs_input"
                await self.execution_chain_logger.update_chain(chain)
                return chain
            
            # Check if there's a suggested next step
            suggested_next_step = response.metadata.get("suggested_next_step")
            if not suggested_next_step:
                # If there's no suggested next step, we're done
                chain.status = "completed"
                await self.execution_chain_logger.update_chain(chain)
                return chain
            
            # Determine the next agent
            next_agent = await self._determine_next_agent(
                current_agent=current_agent,
                suggested_next_step=suggested_next_step,
                task_category=response.metadata.get("task_category"),
                tags=response.metadata.get("tags", [])
            )
            
            if not next_agent:
                # If we can't determine the next agent, we're done
                chain.status = "completed"
                await self.execution_chain_logger.update_chain(chain)
                return chain
            
            # Update for the next iteration
            current_agent = next_agent
            current_input = suggested_next_step
            current_context = {
                "previous_agent": step.agent_name,
                "previous_output": step.output_text,
                "previous_reflection": step.reflection,
                "chain_id": chain.chain_id,
                "step_number": step_number,
                **(current_context or {})
            }
            step_number += 1
        
        # If we've reached the maximum number of steps, we're done
        chain.status = "max_steps_reached"
        await self.execution_chain_logger.update_chain(chain)
        return chain
    
    async def _determine_next_agent(
        self,
        current_agent: str,
        suggested_next_step: str,
        task_category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Determine the next agent based on the suggested next step and task category
        
        Args:
            current_agent: The current agent
            suggested_next_step: The suggested next step
            task_category: The task category
            tags: The tags
            
        Returns:
            The next agent, or None if no suitable agent is found
        """
        # Get all agent prompt chains
        agent_configs = {}
        for agent_type in self.prompt_manager.get_available_agents():
            agent_configs[agent_type] = self.prompt_manager.get_prompt_chain(agent_type)
        
        # Check for direct handoff keywords in each agent config
        for agent_type, config in agent_configs.items():
            # Skip the current agent
            if agent_type == current_agent:
                continue
            
            # Check if this agent accepts the task category
            accepts_tasks = config.get("accepts_tasks", [])
            if task_category and accepts_tasks and task_category in accepts_tasks:
                # Check if any handoff keywords match
                handoff_keywords = config.get("handoff_keywords", [])
                if handoff_keywords:
                    for keyword in handoff_keywords:
                        if keyword.lower() in suggested_next_step.lower():
                            return agent_type
        
        # If no direct match, try to match based on task category
        if task_category:
            for agent_type, config in agent_configs.items():
                # Skip the current agent
                if agent_type == current_agent:
                    continue
                
                # Check if this agent accepts the task category
                accepts_tasks = config.get("accepts_tasks", [])
                if accepts_tasks and task_category in accepts_tasks:
                    return agent_type
        
        # If no match based on task category, try to match based on tags
        if tags:
            for agent_type, config in agent_configs.items():
                # Skip the current agent
                if agent_type == current_agent:
                    continue
                
                # Check if this agent accepts any of the tags
                accepts_tasks = config.get("accepts_tasks", [])
                if accepts_tasks:
                    for tag in tags:
                        if tag in accepts_tasks:
                            return agent_type
        
        # If no match, return None
        return None

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
