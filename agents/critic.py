feature/phase-3.5-hardening
__version__ = "3.5.0"
__agent__ = "CRITIC"
__role__ = "reviewer"

main
"""
CriticAgent Module

This module provides a critic agent that evaluates the outputs of HAL, ASH, and NOVA agents.
The critic provides scores and reflections on technical accuracy, UX clarity, visual design,
and monetization strategy.
"""

import logging
import os
from typing import Dict, Any, List, Optional
import time
import traceback
import json

# Import OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI client import failed")

# Configure logging
logger = logging.getLogger("modules.review.critic_agent")

class CriticAgent:
    """
    CriticAgent evaluates the outputs of HAL, ASH, and NOVA agents.
    """
    def __init__(self):
        self.agent_id = "critic"
        self.name = "Critic"
        self.description = "Evaluates agent outputs for quality and improvement opportunities"
        
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        
        # Initialize OpenAI client
        try:
            if not api_key:
                raise ValueError("OpenAI API key is not set in environment variables")
            
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            self.client = None
    
    def evaluate(self, goal: str, agent_outputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate the outputs of HAL, ASH, and NOVA agents.
        
        Args:
            goal: The goal or task description
            agent_outputs: Dictionary mapping agent IDs to their outputs
            
        Returns:
            Dict containing scores and reflections
        """
        try:
            print(f"🔍 CriticAgent.evaluate called for goal: {goal[:50]}...")
            
            if not self.client:
                error_msg = "OpenAI client initialization failed. Unable to process request."
                print(f"❌ {error_msg}")
                return {
                    "reflection": error_msg,
                    "status": "error"
                }
            
            # Prepare system message
            system_message = """You are a Critic Agent that evaluates the outputs of three specialized agents:
1. HAL (SaaS Architect) - Responsible for technical architecture and feature planning
2. ASH (Documentation & UX Explainer) - Responsible for documentation and user experience
3. NOVA (UI Designer & Copy Generator) - Responsible for visual design and copy

Evaluate their outputs based on the following criteria:
- Technical Accuracy: How well the solution addresses technical requirements (0-10)
- UX Clarity: How clear and user-friendly the solution is (0-10)
- Visual Design: How well the visual aspects are described or implemented (0-10)
- Monetization Strategy: How well the solution addresses business and monetization aspects (0-10)

Provide a thoughtful reflection on the strengths and weaknesses of each agent's output.
Your response must be in valid JSON format with the following structure:
{
  "reflection": "Your overall analysis and suggestions for improvement",
  "scores": {
    "technical_accuracy": 0-10,
    "ux_clarity": 0-10,
    "visual_design": 0-10,
    "monetization_strategy": 0-10
  }
}"""
            
            # Prepare user message with goal and agent outputs
            user_message = f"Goal: {goal}\n\n"
            
            for agent_id, output in agent_outputs.items():
                user_message += f"--- {agent_id.upper()} OUTPUT ---\n{output}\n\n"
            
            # Call OpenAI API
            print("📡 Calling OpenAI API for critique...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            print(f"✅ OpenAI API call successful, received {len(content)} characters")
            
            # Parse JSON response
            try:
                result = json.loads(content)
                
                # Validate result structure
                if "reflection" not in result or "scores" not in result:
                    raise ValueError("Response missing required fields")
                
                required_scores = ["technical_accuracy", "ux_clarity", "visual_design", "monetization_strategy"]
                for score in required_scores:
                    if score not in result["scores"]:
                        raise ValueError(f"Response missing required score: {score}")
                
                # Return result with metadata
                return {
                    **result,
                    "status": "success",
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "timestamp": time.time()
                }
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON response: {str(e)}"
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                return {
                    "reflection": f"Error: {error_msg}",
                    "status": "error",
                    "raw_response": content
                }
            except ValueError as e:
                error_msg = f"Invalid response structure: {str(e)}"
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                return {
                    "reflection": f"Error: {error_msg}",
                    "status": "error",
                    "raw_response": content
                }
                
        except Exception as e:
            error_msg = f"Error in CriticAgent.evaluate: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "reflection": f"Error processing request: {str(e)}",
                "status": "error"
            }

def test_critic_agent():
    """
    Test CriticAgent in isolation to verify it works correctly.
    
    Returns:
        Dict containing the test results
    """
    print("\n=== Testing CriticAgent in isolation ===\n")
    
    try:
        # Create test goal and outputs
        goal = "Create a SaaS product for team collaboration"
        agent_outputs = {
            "hal": "I recommend building a real-time collaboration platform with the following features:\n1. Document editing with version control\n2. Task management with assignments\n3. Chat and video conferencing\n4. API for integrations\n\nThe architecture will use a microservices approach with separate services for each core feature.",
            "ash": "The platform should have a clear onboarding flow that guides new users through creating their first project. Documentation should include video tutorials for each feature and a comprehensive API reference.",
            "nova": "The UI should use a clean, minimal design with a blue and white color scheme. The layout should prioritize the document workspace with collapsible sidebars for chat and task management."
        }
        
        # Create agent
        print("🔧 Creating CriticAgent instance")
        agent = CriticAgent()
        
        # Run the agent
        print(f"🏃 Running CriticAgent with test data")
        result = agent.evaluate(goal, agent_outputs)
        
        # Print the result
        print(f"\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Reflection: {result.get('reflection', 'No reflection')[:100]}...")
        if "scores" in result:
            print(f"Scores: {result['scores']}")
        
        if result.get('status') == 'success':
            print("\n✅ Test passed: CriticAgent returned successful response")
        else:
            print("\n❌ Test failed: CriticAgent did not return successful response")
        
        return result
    
    except Exception as e:
        error_msg = f"Error testing CriticAgent in isolation: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "reflection": error_msg
        }

if __name__ == "__main__":
    # Run the isolation test if this module is executed directly
    test_critic_agent()
