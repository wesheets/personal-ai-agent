import os
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class RetryData(BaseModel):
    """Model for retry data"""
    original_response: str
    original_confidence: str
    retry_response: str
    retry_confidence: str
    retry_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ConfidenceRetryManager:
    """
    Manager for confidence-based retry logic
    
    This class handles the retry logic based on agent confidence levels.
    If an agent's confidence is below a threshold, it will trigger a retry
    with revised instructions.
    """
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize the ConfidenceRetryManager
        
        Args:
            confidence_threshold: Threshold below which a retry is triggered (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
    
    async def check_confidence(
        self,
        confidence_level: str,
        agent_type: str,
        model: str,
        input_text: str,
        output_text: str,
        reflection_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if confidence level is below threshold and trigger retry if needed
        
        Args:
            confidence_level: Confidence level string from agent reflection
            agent_type: Type of agent
            model: Model used for generation
            input_text: Original input text
            output_text: Original output text
            reflection_data: Original reflection data
            
        Returns:
            Dictionary with retry information if retry was triggered, otherwise empty dict
        """
        # Parse confidence level from string
        confidence_value = self._parse_confidence(confidence_level)
        
        # If confidence is below threshold, trigger retry
        if confidence_value < self.confidence_threshold:
            return await self._trigger_retry(
                agent_type=agent_type,
                model=model,
                input_text=input_text,
                output_text=output_text,
                confidence_level=confidence_level,
                reflection_data=reflection_data
            )
        
        # Otherwise, return empty dict
        return {}
    
    def _parse_confidence(self, confidence_level: str) -> float:
        """
        Parse confidence level from string
        
        Args:
            confidence_level: Confidence level string from agent reflection
            
        Returns:
            Confidence value as float between 0.0 and 1.0
        """
        # Try to extract numeric values
        import re
        
        # Look for percentages (e.g., "90%", "75 percent")
        percentage_match = re.search(r'(\d+)(?:\s*%|\s*percent)', confidence_level.lower())
        if percentage_match:
            return float(percentage_match.group(1)) / 100.0
        
        # Look for X/10 format (e.g., "7/10", "8 out of 10")
        out_of_ten_match = re.search(r'(\d+)(?:\s*\/|\s*out\s*of)\s*10', confidence_level.lower())
        if out_of_ten_match:
            return float(out_of_ten_match.group(1)) / 10.0
        
        # Look for X/5 format (e.g., "4/5")
        out_of_five_match = re.search(r'(\d+)(?:\s*\/|\s*out\s*of)\s*5', confidence_level.lower())
        if out_of_five_match:
            return float(out_of_five_match.group(1)) / 5.0
        
        # Look for descriptive terms
        if re.search(r'high(?:\s*confidence)?|very\s*confident|certain', confidence_level.lower()):
            return 0.9
        elif re.search(r'medium(?:\s*high)?(?:\s*confidence)?|fairly\s*confident', confidence_level.lower()):
            return 0.75
        elif re.search(r'medium(?:\s*confidence)?|moderately\s*confident', confidence_level.lower()):
            return 0.6
        elif re.search(r'medium(?:\s*low)?(?:\s*confidence)?|somewhat\s*confident', confidence_level.lower()):
            return 0.4
        elif re.search(r'low(?:\s*confidence)?|not\s*(?:very\s*)?confident|uncertain', confidence_level.lower()):
            return 0.2
        
        # Default to medium confidence if we can't parse
        return 0.5
    
    async def _trigger_retry(
        self,
        agent_type: str,
        model: str,
        input_text: str,
        output_text: str,
        confidence_level: str,
        reflection_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a retry with revised instructions
        
        Args:
            agent_type: Type of agent
            model: Model used for generation
            input_text: Original input text
            output_text: Original output text
            confidence_level: Original confidence level
            reflection_data: Original reflection data
            
        Returns:
            Dictionary with retry information
        """
        from app.providers import process_with_model
        from app.core.prompt_manager import PromptManager
        
        # Get the prompt manager
        prompt_manager = PromptManager()
        
        # Load the agent prompt chain
        prompt_chain = prompt_manager.get_prompt_chain(agent_type)
        
        # Create a retry prompt
        retry_prompt = f"""
You previously provided this response to the user's request:

USER REQUEST:
{input_text}

YOUR RESPONSE:
{output_text}

However, you indicated a low confidence level: "{confidence_level}"

You also identified these potential failure points:
{reflection_data.get('failure_points', 'None specified')}

Please revise your response to increase confidence and reduce failure risk. 
Focus on addressing the specific areas of uncertainty and potential failures.
Provide a more robust, well-reasoned response that you can be more confident about.
"""
        
        # Process the retry prompt
        retry_result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=retry_prompt,
            context={"is_retry": True, "original_input": input_text}
        )
        
        # Get the retry output
        retry_output = retry_result.get("content", "")
        
        # Generate a new self-evaluation for the retry
        from app.core.self_evaluation import SelfEvaluationPrompt
        
        retry_evaluation = await SelfEvaluationPrompt.generate_self_evaluation(
            model=model,
            agent_type=agent_type,
            input_text=input_text,
            output_text=retry_output,
            context={"is_retry": True, "original_input": input_text}
        )
        
        retry_confidence = retry_evaluation.get("confidence_level", "")
        
        # Create retry data
        retry_data = RetryData(
            original_response=output_text,
            original_confidence=confidence_level,
            retry_response=retry_output,
            retry_confidence=retry_confidence
        )
        
        # Return retry information
        return {
            "retry_triggered": True,
            "original_confidence": confidence_level,
            "retry_confidence": retry_confidence,
            "retry_response": retry_output,
            "retry_timestamp": retry_data.retry_timestamp
        }

# Singleton instance
_confidence_retry_manager = None

def get_confidence_retry_manager() -> ConfidenceRetryManager:
    """
    Get the singleton ConfidenceRetryManager instance
    """
    global _confidence_retry_manager
    if _confidence_retry_manager is None:
        _confidence_retry_manager = ConfidenceRetryManager()
    return _confidence_retry_manager
