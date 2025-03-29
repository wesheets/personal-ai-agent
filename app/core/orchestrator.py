import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.prompt_manager import PromptManager
from app.core.execution_logger import get_execution_logger
from app.core.rationale_logger import get_rationale_logger
from app.api.agent import process_agent_request, AgentRequest
from fastapi import BackgroundTasks

class OrchestratorStep(BaseModel):
    """Model for a step in an orchestrated workflow"""
    step_number: int
    agent_name: str
    input_text: str
    output_text: str
    metadata: Dict[str, Any]
    reflection: Optional[Dict[str, Any]] = None
    
class OrchestratorChain(BaseModel):
    """Model for an orchestrated workflow chain"""
    chain_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[OrchestratorStep] = Field(default_factory=list)
    status: str = "in_progress"  # in_progress, completed, failed
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Orchestrator:
    """
    Orchestrator for multi-agent workflows
    
    This module handles routing tasks between agents based on suggested_next_step
    and agent routing configurations.
    """
    
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.execution_logger = get_execution_logger()
        self.rationale_logger = get_rationale_logger()
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "execution_chain_logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    async def orchestrate(
        self,
        initial_agent: str,
        initial_input: str,
        context: Optional[Dict[str, Any]] = None,
        auto_orchestrate: bool = False,
        max_steps: int = 5,
        background_tasks: Optional[BackgroundTasks] = None,
        db=None,
        supabase_client=None
    ) -> OrchestratorChain:
        """
        Orchestrate a multi-agent workflow
        
        Args:
            initial_agent: Name of the first agent to call
            initial_input: Input text for the first agent
            context: Additional context for the agents
            auto_orchestrate: Whether to automatically orchestrate based on suggested_next_step
            max_steps: Maximum number of steps in the workflow
            background_tasks: FastAPI background tasks
            db: Database connection
            supabase_client: Supabase client
            
        Returns:
            OrchestratorChain with all steps in the workflow
        """
        # Initialize the chain
        chain = OrchestratorChain()
        
        # Process the initial request
        current_agent = initial_agent
        current_input = initial_input
        current_context = context or {}
        
        # Keep track of steps
        step_number = 1
        
        try:
            while step_number <= max_steps:
                # Create the agent request
                request = AgentRequest(
                    input=current_input,
                    context=current_context,
                    save_to_memory=True
                )
                
                # Process the request
                response = await process_agent_request(
                    agent_type=current_agent,
                    request=request,
                    background_tasks=background_tasks,
                    db=db,
                    supabase_client=supabase_client
                )
                
                # Create a step from the response
                step = OrchestratorStep(
                    step_number=step_number,
                    agent_name=current_agent,
                    input_text=current_input,
                    output_text=response.output,
                    metadata=response.metadata,
                    reflection=response.reflection
                )
                
                # Add the step to the chain
                chain.steps.append(step)
                
                # Log the step
                await self._log_chain_step(chain, step)
                
                # Check if we should continue orchestrating
                if not auto_orchestrate:
                    # If auto_orchestrate is False, stop after the first step
                    break
                
                # Get the suggested next step
                suggested_next_step = response.metadata.get("suggested_next_step")
                
                if not suggested_next_step:
                    # If there's no suggested next step, stop
                    break
                
                # Determine the next agent
                next_agent = await self._determine_next_agent(
                    current_agent=current_agent,
                    suggested_next_step=suggested_next_step,
                    task_category=response.metadata.get("task_category"),
                    tags=response.metadata.get("tags", [])
                )
                
                if not next_agent or next_agent == current_agent:
                    # If there's no next agent or it's the same agent, stop
                    break
                
                # Update for the next step
                current_agent = next_agent
                current_input = f"""
Continue this task based on the previous agent's output.

Previous agent: {step.agent_name}
Previous output: {step.output_text}

Suggested next step: {suggested_next_step}

Please handle this next step: {suggested_next_step}
"""
                
                # Update the context with the previous step's information
                current_context = {
                    "previous_agent": step.agent_name,
                    "previous_output": step.output_text,
                    "previous_reflection": step.reflection,
                    "suggested_next_step": suggested_next_step,
                    "task_category": response.metadata.get("task_category"),
                    "tags": response.metadata.get("tags", []),
                    "chain_id": chain.chain_id,
                    "step_number": step_number + 1
                }
                
                # Increment the step number
                step_number += 1
            
            # Mark the chain as completed
            chain.status = "completed"
            chain.updated_at = datetime.now().isoformat()
            
            # Log the final chain
            await self._log_chain(chain)
            
            return chain
            
        except Exception as e:
            # Mark the chain as failed
            chain.status = "failed"
            chain.updated_at = datetime.now().isoformat()
            
            # Add error information
            error_step = OrchestratorStep(
                step_number=step_number,
                agent_name=current_agent,
                input_text=current_input,
                output_text=f"Error: {str(e)}",
                metadata={"error": str(e)},
                reflection=None
            )
            
            chain.steps.append(error_step)
            
            # Log the failed chain
            await self._log_chain(chain)
            
            # Re-raise the exception
            raise
    
    async def _determine_next_agent(
        self,
        current_agent: str,
        suggested_next_step: str,
        task_category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Determine the next agent based on the suggested next step
        
        Args:
            current_agent: Current agent name
            suggested_next_step: Suggested next step
            task_category: Category of the task
            tags: Tags for the task
            
        Returns:
            Name of the next agent or None if no suitable agent is found
        """
        # Get all agent configs
        agent_configs = {}
        prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        
        for filename in os.listdir(prompts_dir):
            if filename.endswith(".json"):
                agent_name = os.path.splitext(filename)[0]
                config_path = os.path.join(prompts_dir, filename)
                
                with open(config_path, "r") as f:
                    config = json.load(f)
                    agent_configs[agent_name] = config
        
        # Initialize scores for each agent
        agent_scores = {agent: 0 for agent in agent_configs.keys()}
        
        # Don't consider the current agent
        if current_agent in agent_scores:
            del agent_scores[current_agent]
        
        # Score each agent based on routing config
        for agent_name, config in agent_configs.items():
            if agent_name == current_agent:
                continue
            
            # Check accepts_tasks
            accepts_tasks = config.get("accepts_tasks", [])
            if task_category and task_category in accepts_tasks:
                agent_scores[agent_name] += 2
            
            # Check handoff_keywords
            handoff_keywords = config.get("handoff_keywords", [])
            for keyword in handoff_keywords:
                if keyword.lower() in suggested_next_step.lower():
                    agent_scores[agent_name] += 3
            
            # Check if the agent is mentioned by name
            if agent_name.lower() in suggested_next_step.lower():
                agent_scores[agent_name] += 5
        
        # Get the agent with the highest score
        if not agent_scores:
            return None
        
        max_score = max(agent_scores.values())
        
        # If no agent has a score above 0, return None
        if max_score == 0:
            return None
        
        # Get all agents with the max score
        best_agents = [agent for agent, score in agent_scores.items() if score == max_score]
        
        # Return the first one (could implement more sophisticated selection)
        return best_agents[0] if best_agents else None
    
    async def _log_chain_step(self, chain: OrchestratorChain, step: OrchestratorStep) -> None:
        """
        Log a step in an orchestrated workflow chain
        
        Args:
            chain: The orchestrator chain
            step: The step to log
        """
        # Create the log directory if it doesn't exist
        chain_dir = os.path.join(self.log_dir, chain.chain_id)
        os.makedirs(chain_dir, exist_ok=True)
        
        # Create the step log file
        step_file = os.path.join(chain_dir, f"step_{step.step_number}.json")
        
        # Prepare the step data
        step_data = step.dict()
        
        # Add links to related logs
        if "log_id" in step.metadata:
            step_data["execution_log_link"] = step.metadata["log_id"]
        
        if step.reflection and "rationale_log_id" in step.reflection:
            step_data["rationale_log_link"] = step.reflection["rationale_log_id"]
        
        # Write the step log
        with open(step_file, "w") as f:
            json.dump(step_data, f, indent=2)
    
    async def _log_chain(self, chain: OrchestratorChain) -> None:
        """
        Log an orchestrated workflow chain
        
        Args:
            chain: The orchestrator chain to log
        """
        # Create the log directory if it doesn't exist
        chain_dir = os.path.join(self.log_dir, chain.chain_id)
        os.makedirs(chain_dir, exist_ok=True)
        
        # Create the chain log file
        chain_file = os.path.join(chain_dir, "chain.json")
        
        # Write the chain log
        with open(chain_file, "w") as f:
            json.dump(chain.dict(), f, indent=2)

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
