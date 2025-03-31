import os
from typing import Dict, Any, Optional, List
from fastapi import Depends
from app.providers import get_model_router, process_with_model, initialize_model_providers
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

class PromptManager:
    """
    Manages prompt chains for different agent types
    """
    def __init__(self, prompts_dir: Optional[str] = None):
        self.prompts_dir = prompts_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        self._prompt_cache = {}
        
        # Initialize model providers
        initialize_model_providers()
    
    def get_prompt_chain(self, agent_type: str) -> Dict[str, Any]:
        """
        Get the prompt chain for a specific agent type
        
        Args:
            agent_type: The type of agent (builder, ops, research, memory)
            
        Returns:
            The prompt chain configuration
        """
        # Check if the prompt chain is already cached
        if agent_type in self._prompt_cache:
            return self._prompt_cache[agent_type]
        
        # Load the prompt chain from file
        prompt_file = os.path.join(self.prompts_dir, f"{agent_type}.json")
        
        try:
            with open(prompt_file, 'r') as f:
                prompt_chain = json.load(f)
                self._prompt_cache[agent_type] = prompt_chain
                return prompt_chain
        except FileNotFoundError:
            # If the file doesn't exist, return a default prompt chain
            default_prompt = self._get_default_prompt(agent_type)
            self._prompt_cache[agent_type] = default_prompt
            return default_prompt
    
    def _get_default_prompt(self, agent_type: str) -> Dict[str, Any]:
        """
        Get a default prompt chain for an agent type
        
        Args:
            agent_type: The type of agent
            
        Returns:
            A default prompt chain
        """
        # Create a basic default prompt chain
        return {
            "name": f"{agent_type.capitalize()} Agent",
            "description": f"Default {agent_type} agent prompt chain",
            "model": "gpt-4",
            "system_prompt": f"You are a helpful {agent_type} agent.",
            "tools": []
        }
    
    def get_available_agents(self) -> List[str]:
        """
        Get a list of available agent types
        
        Returns:
            List of agent types
        """
        # For testing purposes, always return these basic agent types
        return ["builder", "ops", "research", "memory"]
        
        # In production, this would scan the prompts directory
        # try:
        #     agents = []
        #     for filename in os.listdir(self.prompts_dir):
        #         if filename.endswith(".json"):
        #             agents.append(filename.replace(".json", ""))
        #     return agents
        # except Exception as e:
        #     print(f"Error getting available agents: {e}")
        #     # Return default agents if there's an error
        #     return ["builder", "ops", "research", "memory"]
    
    async def process_with_agent(
        self,
        agent_type: str,
        input_text: str,
        model_override: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process input with a specific agent
        
        Args:
            agent_type: The type of agent to use
            input_text: The input text to process
            model_override: Optional model to use instead of the one in the prompt chain
            metadata: Optional metadata to include in the response
            
        Returns:
            The agent's response
        """
        # Get the prompt chain
        prompt_chain = self.get_prompt_chain(agent_type)
        
        # Use model override if provided
        model = model_override or prompt_chain.get("model", "gpt-4")
        
        # Get the model router
        model_router = get_model_router()
        
        # For testing purposes, return a mock response
        if os.environ.get("OPENAI_API_KEY") is None or os.environ.get("SUPABASE_URL") is None:
            print(f"Using mock response for {agent_type} agent")
            return {
                "agent_type": agent_type,
                "input": input_text,
                "output": f"Mock response from {agent_type} agent: I've processed your request.",
                "model": model,
                "processing_time": 0.1,
                "metadata": metadata or {}
            }
        
        # Process with the model
        start_time = time.time()
        response = await process_with_model(
            model=model,
            system_prompt=prompt_chain.get("system_prompt", ""),
            user_prompt=input_text,
            tools=prompt_chain.get("tools", [])
        )
        processing_time = time.time() - start_time
        
        # Return the response
        return {
            "agent_type": agent_type,
            "input": input_text,
            "output": response,
            "model": model,
            "processing_time": processing_time,
            "metadata": metadata or {}
        }

# Singleton instance
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """
    Get the singleton PromptManager instance
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
