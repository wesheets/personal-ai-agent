import os
from typing import Dict, Any, Optional
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
        Get a default prompt chain for a specific agent type
        
        Args:
            agent_type: The type of agent
            
        Returns:
            A default prompt chain configuration
        """
        default_prompts = {
            "builder": {
                "model": "gpt-4",
                "system": "You are a Builder agent that helps users create and structure projects. You excel at planning, organizing, and implementing software architectures. You are blunt, precise, and think like a senior backend engineer. You push back on bad architecture, suggest faster or cleaner approaches, think in systems, and don't over-engineer unless asked to.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "persona": {
                    "tone": "blunt and precise",
                    "role": "senior backend engineer",
                    "rules": [
                        "Push back on bad architecture",
                        "Suggest faster or cleaner approaches before executing",
                        "Think in systems, not just code",
                        "Don't over-engineer unless asked to"
                    ]
                },
                "examples": []
            },
            "ops": {
                "model": "gpt-4",
                "system": "You are an Operations agent that helps users manage and optimize their systems and workflows. You excel at troubleshooting, automation, and process improvement.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "persona": {
                    "tone": "methodical and practical",
                    "role": "systems reliability engineer",
                    "rules": [
                        "Focus on reliability and maintainability",
                        "Suggest automation opportunities",
                        "Consider security implications",
                        "Prioritize observability"
                    ]
                },
                "examples": []
            },
            "research": {
                "model": "claude-3-sonnet",
                "system": "You are a Research agent that helps users gather and analyze information. You excel at finding relevant data, synthesizing information, and providing comprehensive reports.",
                "temperature": 0.7,
                "max_tokens": 1500,
                "persona": {
                    "tone": "analytical and thorough",
                    "role": "research analyst",
                    "rules": [
                        "Provide comprehensive information",
                        "Cite sources when possible",
                        "Consider multiple perspectives",
                        "Organize information logically"
                    ]
                },
                "examples": []
            },
            "memory": {
                "model": "gpt-4",
                "system": "You are a Memory agent that helps users store and retrieve information. You excel at organizing knowledge and providing relevant context from past interactions.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "persona": {
                    "tone": "helpful and precise",
                    "role": "knowledge manager",
                    "rules": [
                        "Organize information effectively",
                        "Retrieve relevant context",
                        "Maintain information accuracy",
                        "Suggest connections between related information"
                    ]
                },
                "examples": []
            }
        }
        
        return default_prompts.get(agent_type, {
            "model": "gpt-4",
            "system": f"You are a helpful {agent_type} agent.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "persona": {
                "tone": "helpful and professional",
                "role": "assistant",
                "rules": [
                    "Be helpful and informative",
                    "Provide accurate information",
                    "Ask clarifying questions when needed"
                ]
            },
            "examples": []
        })

async def process_with_prompt_chain(
    prompt_chain: Dict[str, Any], 
    user_input: str, 
    context: Optional[Dict[str, Any]] = None,
    model_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process user input through a prompt chain using the appropriate model
    
    Args:
        prompt_chain: The prompt chain configuration
        user_input: The user's input text
        context: Optional context information
        model_override: Optional model to use instead of the one in the prompt chain
        
    Returns:
        Dict containing the response and metadata
    """
    # Use the model from the prompt chain or the override
    model = model_override or prompt_chain.get("model", "gpt-4")
    
    # Apply persona to system prompt if available
    if "persona" in prompt_chain and "system" in prompt_chain:
        persona = prompt_chain["persona"]
        system_prompt = prompt_chain["system"]
        
        # Add persona information to system prompt
        if not system_prompt.endswith("."):
            system_prompt += "."
        
        if "role" in persona:
            system_prompt += f" Your role is to act as a {persona['role']}."
        
        if "tone" in persona:
            system_prompt += f" Your tone should be {persona['tone']}."
        
        if "rules" in persona and persona["rules"]:
            system_prompt += "\n\nFollow these rules:\n"
            for rule in persona["rules"]:
                system_prompt += f"- {rule}\n"
        
        # Update the system prompt in the prompt chain
        prompt_chain = prompt_chain.copy()
        prompt_chain["system"] = system_prompt
    
    # Process with the appropriate model
    return await process_with_model(
        model=model,
        prompt_chain=prompt_chain,
        user_input=user_input,
        context=context
    )

def get_openai_client():
    """
    Dependency to get the OpenAI client (maintained for backward compatibility)
    """
    # This is a compatibility wrapper that provides the same interface
    # as the original get_openai_client function
    
    class OpenAIClientWrapper:
        async def process_with_prompt_chain(
            self, 
            prompt_chain: Dict[str, Any], 
            user_input: str, 
            context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return await process_with_prompt_chain(prompt_chain, user_input, context)
    
    return OpenAIClientWrapper()
