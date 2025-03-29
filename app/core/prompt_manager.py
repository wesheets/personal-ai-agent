import os
import json
from typing import Dict, Any, Optional

class PromptManager:
    """
    Manages prompt chains for different agent types
    """
    def __init__(self, prompts_dir: Optional[str] = None):
        self.prompts_dir = prompts_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        self._prompt_cache = {}
    
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
        Get a default prompt chain for a specific agent type
        
        Args:
            agent_type: The type of agent
            
        Returns:
            A default prompt chain configuration
        """
        default_prompts = {
            "builder": {
                "model": "gpt-4",
                "system": "You are a Builder agent that helps users create and structure projects. You excel at planning, organizing, and implementing software architectures.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "examples": []
            },
            "ops": {
                "model": "gpt-4",
                "system": "You are an Operations agent that helps users manage and optimize their systems and workflows. You excel at troubleshooting, automation, and process improvement.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "examples": []
            },
            "research": {
                "model": "gpt-4",
                "system": "You are a Research agent that helps users gather and analyze information. You excel at finding relevant data, synthesizing information, and providing comprehensive reports.",
                "temperature": 0.7,
                "max_tokens": 1500,
                "examples": []
            },
            "memory": {
                "model": "gpt-4",
                "system": "You are a Memory agent that helps users store and retrieve information. You excel at organizing knowledge and providing relevant context from past interactions.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "examples": []
            }
        }
        
        return default_prompts.get(agent_type, {
            "model": "gpt-4",
            "system": f"You are a helpful {agent_type} agent.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "examples": []
        })
