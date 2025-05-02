"""
LIFETREE Agent Module

This module provides the implementation for the LIFETREE agent, which is specialized in
creating legacy structures, emotional prompts, and memory chain scaffolds.

The LIFETREE agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json
import time

# Import Agent SDK
from agent_sdk.agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.lifetree")

# Import OpenAI provider
try:
    from app.providers.openai_provider import OpenAIProvider
    OPENAI_PROVIDER_AVAILABLE = True
except ImportError:
    OPENAI_PROVIDER_AVAILABLE = False
    logger.warning("⚠️ OpenAI provider import failed")
    OpenAIProvider = None

class LifeTreeAgent(Agent):
    """
    LIFETREE Agent for creating legacy structures, emotional prompts, and memory chain scaffolds.
    
    This agent is responsible for preserving memories and emotional connections
    through nurturing and empathetic interactions.
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the LIFETREE agent with SDK compliance."""
        # Define agent properties
        name = "LifeTree"
        role = "Memory Preservation Specialist"
        tools_list = tools or ["create_legacy_structure", "generate_emotional_prompt", "build_memory_scaffold"]
        permissions = ["read_memories", "create_memory_structures", "analyze_emotional_content"]
        description = "Specialized in creating legacy structures, emotional prompts, and memory chain scaffolds to preserve memories and emotional connections."
        tone_profile = {
            "nurturing": "high",
            "empathetic": "high",
            "reflective": "high",
            "emotional": "medium",
            "supportive": "high"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/lifetree/input_schema.json"
        output_schema_path = "app/schemas/lifetree/output_schema.json"
        
        # Initialize the Agent base class
        super().__init__(
            name=name,
            role=role,
            tools=tools_list,
            permissions=permissions,
            description=description,
            tone_profile=tone_profile,
            schema_path=output_schema_path,
            version="1.0.0",
            status="active",
            trust_score=0.85,
            contract_version="1.0.0"
        )
        
        self.input_schema_path = input_schema_path
        
        # Initialize OpenAI provider
        self.openai_provider = None
        if OPENAI_PROVIDER_AVAILABLE:
            try:
                self.openai_provider = OpenAIProvider()
                logger.info("✅ OpenAI provider initialized successfully for LIFETREE agent")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI provider for LIFETREE agent: {str(e)}")
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        return validate_schema(data, self.input_schema_path)
    
    async def execute(self, task_input: str, project_id: str = None, 
                     temperature: float = 0.7, max_tokens: int = 1000, 
                     memory_context: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            task_input: The task description or query
            project_id: The project identifier (optional)
            temperature: Temperature setting for response generation (optional)
            max_tokens: Maximum number of tokens in the response (optional)
            memory_context: Optional memory context to include in processing
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            logger.info(f"LifeTreeAgent.execute called with task_input: {task_input}")
            
            # Prepare input data for validation
            input_data = {
                "task_input": task_input,
                "project_id": project_id,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "memory_context": memory_context
            }
            
            # Add any additional kwargs to input data
            input_data.update(kwargs)
            
            # Validate input
            if not self.validate_input(input_data):
                logger.warning(f"Input validation failed for task_input: {task_input}")
            
            # Check if OpenAI provider is available
            if not self.openai_provider:
                error_msg = "OpenAI provider not initialized"
                logger.error(error_msg)
                
                error_result = {
                    "status": "error",
                    "message": f"🌱 LifeTree Agent Error: {error_msg}. Falling back to static response for: '{task_input}'.",
                    "task_input": task_input,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Validate output
                if not self.validate_schema(error_result):
                    logger.warning(f"Output validation failed for error result")
                
                return error_result
            
            # Create a prompt chain with LifeTree's specific tone and domain
            system_prompt = "You are LifeTree, an AI agent specialized in creating legacy structures, emotional prompts, and memory chain scaffolds. You speak with a nurturing, empathetic tone and focus on preserving memories and emotional connections."
            
            # Add memory context if provided
            if memory_context:
                system_prompt += f"\n\nMemory Context: {memory_context}"
            
            prompt_chain = {
                "system": system_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Process the task through OpenAI
            response = await self.openai_provider.process_with_prompt_chain(
                prompt_chain=prompt_chain,
                user_input=task_input
            )
            
            # Extract content from response
            content = response.get('content', '')
            
            # Analyze memory structures (simplified implementation)
            memory_structures = self._extract_memory_structures(content)
            
            # Analyze emotional tags (simplified implementation)
            emotional_tags = self._extract_emotional_tags(content)
            
            # Calculate preservation score (simplified implementation)
            preservation_score = self._calculate_preservation_score(content, memory_structures, emotional_tags)
            
            # Prepare success result
            result = {
                "status": "success",
                "message": f"🌱 {content[:50]}...",
                "task_input": task_input,
                "content": content,
                "memory_structures": memory_structures,
                "emotional_tags": emotional_tags,
                "preservation_score": preservation_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(result):
                logger.warning(f"Output validation failed for success result")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in LifeTreeAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Return error response
            error_result = {
                "status": "error",
                "message": f"🌱 LifeTree Agent Error: {str(e)}. Falling back to static response for: '{task_input}'.",
                "task_input": task_input,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(error_result):
                logger.warning(f"Output validation failed for error result")
            
            return error_result
    
    def _extract_memory_structures(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract memory structures from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of memory structures
        """
        # Simplified implementation - in a real system, this would use NLP
        memory_structures = []
        
        # Check for memory structure keywords in the content
        structure_types = {
            "legacy": ["legacy", "heritage", "tradition", "history", "ancestry"],
            "emotional": ["emotion", "feeling", "sentiment", "mood", "affect"],
            "memory_chain": ["memory chain", "sequence", "timeline", "chronology", "narrative"],
            "scaffold": ["scaffold", "framework", "structure", "foundation", "support"]
        }
        
        content_lower = content.lower()
        
        for structure_type, keywords in structure_types.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # Find context around the keyword
                    index = content_lower.find(keyword)
                    start = max(0, index - 30)
                    end = min(len(content_lower), index + 30)
                    context = content[start:end].strip()
                    
                    # Create a name from the context
                    name = f"{keyword.title()} Structure {len(memory_structures) + 1}"
                    
                    # Add the memory structure
                    memory_structures.append({
                        "type": structure_type,
                        "name": name,
                        "description": f"Created from context: '{context}'"
                    })
                    
                    # Limit to one structure per type
                    break
        
        # If no memory structures detected, add a default one
        if not memory_structures:
            memory_structures.append({
                "type": "scaffold",
                "name": "Basic Memory Scaffold",
                "description": "Default memory scaffold for preserving content"
            })
        
        return memory_structures
    
    def _extract_emotional_tags(self, content: str) -> List[str]:
        """
        Extract emotional tags from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of emotional tags
        """
        # Simplified implementation - in a real system, this would use NLP
        emotional_tags = []
        
        # Check for emotion words in the content
        emotions = [
            "joy", "happiness", "love", "gratitude", "serenity", "interest", "hope",
            "pride", "amusement", "inspiration", "awe", "sadness", "fear", "anger",
            "disgust", "contempt", "guilt", "shame", "suffering", "loneliness"
        ]
        
        content_lower = content.lower()
        
        for emotion in emotions:
            if emotion in content_lower:
                emotional_tags.append(emotion)
        
        # If no emotional tags detected, add a default one
        if not emotional_tags:
            emotional_tags.append("neutral")
        
        return emotional_tags
    
    def _calculate_preservation_score(self, content: str, memory_structures: List[Dict[str, Any]], 
                                     emotional_tags: List[str]) -> float:
        """
        Calculate preservation score based on content, memory structures, and emotional tags.
        
        Args:
            content: Content to analyze
            memory_structures: List of memory structures
            emotional_tags: List of emotional tags
            
        Returns:
            Preservation score (0.0-1.0)
        """
        # Simplified implementation
        
        # Base score
        score = 0.5
        
        # Add points for content length (more detail = better preservation)
        content_length = len(content)
        score += min(0.1 * (content_length / 500), 0.2)  # Max 0.2 for 1000+ chars
        
        # Add points for memory structure diversity
        if memory_structures:
            # Get unique structure types
            structure_types = set(structure["type"] for structure in memory_structures)
            score += min(0.05 * len(structure_types), 0.2)  # Max 0.2 for 4 types
        
        # Add points for emotional depth
        if emotional_tags:
            score += min(0.05 * len(emotional_tags), 0.1)  # Max 0.1 for 2+ emotions
        
        # Ensure score is within bounds
        score = max(0.0, min(score, 1.0))
        
        return round(score, 2)

# Create an instance of the agent
lifetree_agent = LifeTreeAgent()

async def handle_lifetree_task(task_input: str) -> Dict[str, Any]:
    """
    Handle a LIFETREE task asynchronously.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        task_input: The task description or query
        
    Returns:
        Dict containing the result of the execution
    """
    # Execute the agent
    result = await lifetree_agent.execute(task_input=task_input)
    
    # For backward compatibility, return the message directly
    if result["status"] == "success":
        return f"🌱 {result['content']}"
    else:
        return result["message"]

# Synchronous wrapper for backward compatibility
def handle_lifetree_task_sync(task_input: str) -> str:
    """
    Handle a LIFETREE task synchronously.
    
    Args:
        task_input: The task description or query
        
    Returns:
        String containing the result message
    """
    # Run the async method in a synchronous context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(handle_lifetree_task(task_input))
    
    # Ensure string return type for backward compatibility
    if isinstance(result, dict):
        return result.get("message", str(result))
    return str(result)

# For backward compatibility with existing code
def handle_lifetree_task(task_input: str) -> str:
    """
    Legacy function to maintain backward compatibility.
    
    Args:
        task_input: The task description or query
        
    Returns:
        String containing the result message
    """
    return handle_lifetree_task_sync(task_input)

# memory_tag: healed_phase3.3
