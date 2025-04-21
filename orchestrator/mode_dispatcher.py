"""
Orchestrator Mode Dispatcher

This module is responsible for dispatching the appropriate mode for the Orchestrator
based on configuration and context. It connects different modes (like Thought Partner,
Architect, Sage, etc.) to the appropriate behavior.
"""

import logging
from typing import Dict, Any, Optional, List

# Import modes
from orchestrator.modes.thought_partner import (
    analyze_prompt,
    generate_reflection_questions,
    store_prompt_analysis,
    get_last_prompt_analysis
)

# Configure logging
logger = logging.getLogger(__name__)

# Mode constants
MODE_THOUGHT_PARTNER = "thought_partner"
MODE_ARCHITECT = "architect"
MODE_SAGE = "sage"
MODE_DEFAULT = MODE_ARCHITECT

class ModeDispatcher:
    """
    Dispatches the appropriate mode for the Orchestrator based on configuration and context.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the mode dispatcher with configuration.
        
        Args:
            config (Dict[str, Any], optional): Configuration for the mode dispatcher. Defaults to None.
        """
        self.config = config or {}
        self.active_mode = self.config.get("default_mode", MODE_DEFAULT)
        self.sage_mode_enabled = self.config.get("sage_mode_enabled", True)
        
    def set_mode(self, mode: str) -> None:
        """
        Set the active mode.
        
        Args:
            mode (str): The mode to set as active
        """
        if mode in [MODE_THOUGHT_PARTNER, MODE_ARCHITECT, MODE_SAGE]:
            self.active_mode = mode
            logger.info(f"Orchestrator mode set to: {mode}")
        else:
            logger.warning(f"Unknown mode: {mode}, defaulting to {MODE_DEFAULT}")
            self.active_mode = MODE_DEFAULT
    
    def toggle_sage_mode(self, enabled: bool) -> None:
        """
        Toggle Sage Mode on or off.
        
        Args:
            enabled (bool): Whether to enable Sage Mode
        """
        self.sage_mode_enabled = enabled
        logger.info(f"Sage Mode {'enabled' if enabled else 'disabled'}")
        
        # If enabling Sage Mode, also set the active mode to Thought Partner
        if enabled:
            self.set_mode(MODE_THOUGHT_PARTNER)
    
    def should_analyze_prompt(self, prompt: str, confidence_threshold: float = 0.7) -> bool:
        """
        Determine if the prompt should be analyzed based on the active mode.
        
        Args:
            prompt (str): The prompt to potentially analyze
            confidence_threshold (float, optional): Threshold for confidence score. Defaults to 0.7.
            
        Returns:
            bool: True if the prompt should be analyzed, False otherwise
        """
        # Always analyze in Thought Partner mode
        if self.active_mode == MODE_THOUGHT_PARTNER:
            return True
        
        # In Sage mode, analyze if enabled
        if self.active_mode == MODE_SAGE and self.sage_mode_enabled:
            return True
        
        # In other modes, only analyze if the prompt seems ambiguous or complex
        if len(prompt.split()) > 50:  # Simple heuristic for complex prompts
            return True
            
        return False
    
    def process_prompt(self, prompt: str, project_id: str, loop_id: int, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a prompt based on the active mode.
        
        Args:
            prompt (str): The prompt to process
            project_id (str): The project identifier
            loop_id (int): The loop identifier
            memory (Dict[str, Any]): The memory object
            
        Returns:
            Dict[str, Any]: Processing results including analysis and reflection questions if applicable
        """
        result = {
            "mode": self.active_mode,
            "sage_mode_enabled": self.sage_mode_enabled,
            "prompt_analyzed": False,
            "analysis": None,
            "reflection_questions": None
        }
        
        # Check if we should analyze the prompt
        if self.should_analyze_prompt(prompt):
            # Analyze the prompt
            analysis = analyze_prompt(prompt)
            result["prompt_analyzed"] = True
            result["analysis"] = analysis
            
            # Store the analysis in memory
            memory = store_prompt_analysis(project_id, loop_id, analysis, memory)
            
            # Generate reflection questions if confidence is low or ambiguity is detected
            if analysis["confidence_score"] < 0.7 or analysis["ambiguous_phrases"]:
                reflection_questions = generate_reflection_questions(analysis)
                result["reflection_questions"] = reflection_questions
        
        return result
    
    def get_previous_analysis(self, project_id: str, memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get the previous prompt analysis for a project.
        
        Args:
            project_id (str): The project identifier
            memory (Dict[str, Any]): The memory object
            
        Returns:
            Optional[Dict[str, Any]]: The previous analysis or None if not found
        """
        return get_last_prompt_analysis(project_id, memory)
