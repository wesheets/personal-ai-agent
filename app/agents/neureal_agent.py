"""
NEUREAL Agent Module

This module provides the implementation for the NEUREAL agent, which is specialized in
mapping emotional vectors, sensory layers, and immersive world nodes.

The NEUREAL agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
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
logger = logging.getLogger("agents.neureal")

# Import OpenAI provider
try:
    from app.providers.openai_provider import OpenAIProvider
    OPENAI_PROVIDER_AVAILABLE = True
except ImportError:
    OPENAI_PROVIDER_AVAILABLE = False
    logger.warning("⚠️ OpenAI provider import failed")
    OpenAIProvider = None

class NeurealAgent(Agent):
    """
    NEUREAL Agent for mapping emotional vectors, sensory layers, and immersive world nodes.
    
    This agent is responsible for creating rich, immersive experiences that blend
    emotional and sensory elements.
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the NEUREAL agent with SDK compliance."""
        # Define agent properties
        name = "Neureal"
        role = "Immersive Experience Designer"
        tools_list = tools or ["map_emotions", "create_sensory_layers", "design_immersive_nodes"]
        permissions = ["generate_content", "analyze_emotions", "create_immersive_experiences"]
        description = "Specialized in mapping emotional vectors, sensory layers, and immersive world nodes to create rich, immersive experiences that blend emotional and sensory elements."
        tone_profile = {
            "visionary": "high",
            "technical": "high",
            "creative": "high",
            "immersive": "high",
            "emotional": "medium"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/neureal/input_schema.json"
        output_schema_path = "app/schemas/neureal/output_schema.json"
        
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
            trust_score=0.82,
            contract_version="1.0.0"
        )
        
        self.input_schema_path = input_schema_path
        
        # Initialize OpenAI provider
        self.openai_provider = None
        if OPENAI_PROVIDER_AVAILABLE:
            try:
                self.openai_provider = OpenAIProvider()
                logger.info("✅ OpenAI provider initialized successfully for NEUREAL agent")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI provider for NEUREAL agent: {str(e)}")
    
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
                     temperature: float = 0.7, max_tokens: int = 1000, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            task_input: The task description or query
            project_id: The project identifier (optional)
            temperature: Temperature setting for response generation (optional)
            max_tokens: Maximum number of tokens in the response (optional)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            logger.info(f"NeurealAgent.execute called with task_input: {task_input}")
            
            # Prepare input data for validation
            input_data = {
                "task_input": task_input,
                "project_id": project_id,
                "temperature": temperature,
                "max_tokens": max_tokens
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
                    "message": f"🌐 NEUREAL Agent Error: {error_msg}. Falling back to static response for: '{task_input}'.",
                    "task_input": task_input,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Validate output
                if not self.validate_schema(error_result):
                    logger.warning(f"Output validation failed for error result")
                
                return error_result
            
            # Create a prompt chain with NEUREAL's specific tone and domain
            prompt_chain = {
                "system": "You are NEUREAL, an advanced AI system specialized in mapping emotional vectors, sensory layers, and immersive world nodes. You speak with a visionary, technical tone and focus on creating rich, immersive experiences that blend emotional and sensory elements.",
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
            
            # Analyze emotional vectors (simplified implementation)
            emotional_vectors = self._extract_emotional_vectors(content)
            
            # Analyze sensory layers (simplified implementation)
            sensory_layers = self._extract_sensory_layers(content)
            
            # Calculate immersion score (simplified implementation)
            immersion_score = self._calculate_immersion_score(emotional_vectors, sensory_layers)
            
            # Prepare success result
            result = {
                "status": "success",
                "message": f"🌐 {content[:50]}...",
                "task_input": task_input,
                "content": content,
                "emotional_vectors": emotional_vectors,
                "sensory_layers": sensory_layers,
                "immersion_score": immersion_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(result):
                logger.warning(f"Output validation failed for success result")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in NeurealAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Return error response
            error_result = {
                "status": "error",
                "message": f"🌐 NEUREAL Agent Error: {str(e)}. Falling back to static response for: '{task_input}'.",
                "task_input": task_input,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(error_result):
                logger.warning(f"Output validation failed for error result")
            
            return error_result
    
    def _extract_emotional_vectors(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract emotional vectors from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of emotional vectors with intensity
        """
        # Simplified implementation - in a real system, this would use NLP
        emotional_vectors = []
        
        # Check for common emotions in the content
        emotions = {
            "joy": ["happy", "joy", "delight", "pleasure", "excitement"],
            "sadness": ["sad", "sorrow", "grief", "melancholy", "despair"],
            "fear": ["fear", "anxiety", "terror", "dread", "horror"],
            "anger": ["anger", "rage", "fury", "irritation", "annoyance"],
            "surprise": ["surprise", "astonishment", "amazement", "shock"],
            "disgust": ["disgust", "revulsion", "aversion", "distaste"],
            "trust": ["trust", "confidence", "faith", "assurance"],
            "anticipation": ["anticipation", "expectation", "hope", "excitement"]
        }
        
        content_lower = content.lower()
        
        for emotion, keywords in emotions.items():
            intensity = 0.0
            for keyword in keywords:
                if keyword in content_lower:
                    # Increase intensity based on frequency
                    intensity += 0.2 * content_lower.count(keyword)
            
            # Cap intensity at 1.0
            intensity = min(intensity, 1.0)
            
            if intensity > 0.0:
                emotional_vectors.append({
                    "emotion": emotion,
                    "intensity": round(intensity, 2)
                })
        
        # If no emotions detected, add a neutral one
        if not emotional_vectors:
            emotional_vectors.append({
                "emotion": "neutral",
                "intensity": 0.5
            })
        
        return emotional_vectors
    
    def _extract_sensory_layers(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract sensory layers from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of sensory layers with elements
        """
        # Simplified implementation - in a real system, this would use NLP
        sensory_layers = []
        
        # Check for sensory words in the content
        senses = {
            "visual": ["see", "look", "view", "watch", "observe", "color", "bright", "dark", "light", "image"],
            "auditory": ["hear", "sound", "listen", "noise", "music", "loud", "quiet", "silence", "rhythm"],
            "tactile": ["touch", "feel", "texture", "smooth", "rough", "soft", "hard", "warm", "cold"],
            "olfactory": ["smell", "scent", "aroma", "fragrance", "odor", "perfume"],
            "gustatory": ["taste", "flavor", "sweet", "sour", "bitter", "salty", "savory"]
        }
        
        content_lower = content.lower()
        
        for sense, keywords in senses.items():
            elements = []
            for keyword in keywords:
                if keyword in content_lower:
                    # Find words around the keyword
                    index = content_lower.find(keyword)
                    start = max(0, index - 20)
                    end = min(len(content_lower), index + 20)
                    context = content_lower[start:end]
                    
                    # Add the context as an element
                    elements.append(f"{keyword} ({context.strip()})")
            
            if elements:
                sensory_layers.append({
                    "sense": sense,
                    "elements": elements[:5]  # Limit to 5 elements per sense
                })
        
        # If no sensory layers detected, add a default one
        if not sensory_layers:
            sensory_layers.append({
                "sense": "conceptual",
                "elements": ["abstract concepts", "ideas", "thoughts"]
            })
        
        return sensory_layers
    
    def _calculate_immersion_score(self, emotional_vectors: List[Dict[str, Any]], 
                                  sensory_layers: List[Dict[str, Any]]) -> float:
        """
        Calculate immersion score based on emotional vectors and sensory layers.
        
        Args:
            emotional_vectors: List of emotional vectors
            sensory_layers: List of sensory layers
            
        Returns:
            Immersion score (0.0-1.0)
        """
        # Simplified implementation
        
        # Base score
        score = 0.5
        
        # Add points for emotional diversity and intensity
        if emotional_vectors:
            # Diversity bonus
            score += min(0.1 * len(emotional_vectors), 0.2)
            
            # Intensity bonus
            total_intensity = sum(v["intensity"] for v in emotional_vectors)
            avg_intensity = total_intensity / len(emotional_vectors)
            score += avg_intensity * 0.1
        
        # Add points for sensory diversity
        if sensory_layers:
            # Diversity bonus
            score += min(0.05 * len(sensory_layers), 0.2)
            
            # Elements bonus
            total_elements = sum(len(layer["elements"]) for layer in sensory_layers)
            score += min(0.01 * total_elements, 0.1)
        
        # Ensure score is within bounds
        score = max(0.0, min(score, 1.0))
        
        return round(score, 2)

# Create an instance of the agent
neureal_agent = NeurealAgent()

async def handle_neureal_task(task_input: str) -> Dict[str, Any]:
    """
    Handle a NEUREAL task asynchronously.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        task_input: The task description or query
        
    Returns:
        Dict containing the result of the execution
    """
    # Execute the agent
    result = await neureal_agent.execute(task_input=task_input)
    
    # For backward compatibility, return the message directly
    if result["status"] == "success":
        return f"🌐 {result['content']}"
    else:
        return result["message"]

# Synchronous wrapper for backward compatibility
def handle_neureal_task_sync(task_input: str) -> str:
    """
    Handle a NEUREAL task synchronously.
    
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
    
    result = loop.run_until_complete(handle_neureal_task(task_input))
    
    # Ensure string return type for backward compatibility
    if isinstance(result, dict):
        return result.get("message", str(result))
    return str(result)

# memory_tag: healed_phase3.3
