"""
CRITIC Agent Module

This module provides the consolidated implementation for the CRITIC agent,
which validates loop outputs, applies rejections, and logs reasoning.
"""

import logging
import traceback
import json
import time
import os
from typing import Dict, Any, List, Optional

# Import Agent SDK
from agent_sdk.agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.critic")

# Import OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️ OpenAI client import failed")

# Import memory functions if available
try:
    from app.api.modules.memory import write_memory
    memory_available = True
except ImportError:
    memory_available = False
    logger.warning("⚠️ Memory module not available, using mock implementation")
    
    # Mock implementation for testing
    async def write_memory(agent_id, memory_type, tag, value):
        logger.info(f"Mock memory write: {agent_id}, {memory_type}, {tag}, {len(str(value))} chars")
        return {"status": "success", "message": "Mock memory write successful"}

class CriticAgent(Agent):
    """
    CriticAgent evaluates the outputs of other agents, validates loop outputs,
    applies rejections, and logs reasoning.
    """
    def __init__(self, tools: List[str] = None):
        # Define agent properties
        name = "Critic"
        role = "Quality Evaluator"
        tools_list = tools or ["review", "reject", "log_reason"]
        permissions = ["read_agent_outputs", "write_memory", "reject_outputs"]
        description = "Evaluates agent outputs for quality and improvement opportunities, validates loop outputs, applies rejections, and logs reasoning."
        tone_profile = {
            "analytical": "high",
            "objective": "high",
            "constructive": "high",
            "detailed": "medium",
            "formal": "medium"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/critic/input_schema.json"
        output_schema_path = "app/schemas/critic/output_schema.json"
        
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
            trust_score=0.9,
            contract_version="1.0.0"
        )
        
        self.agent_id = "critic"
        self.input_schema_path = input_schema_path
        
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"OpenAI API Key loaded: {bool(api_key)}")
        
        # Initialize OpenAI client
        try:
            if not api_key:
                raise ValueError("OpenAI API key is not set in environment variables")
            
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {str(e)}"
            logger.error(error_msg)
            self.client = None
    
    async def review(self, loop_id: str, agent_outputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Review the outputs of agents in a loop.
        
        Args:
            loop_id: Unique identifier for the loop
            agent_outputs: Dictionary mapping agent IDs to their outputs
            
        Returns:
            Dict containing review results and reasoning
        """
        try:
            logger.info(f"CriticAgent.review called for loop: {loop_id}")
            
            if not self.client:
                error_msg = "OpenAI client initialization failed. Unable to process request."
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "loop_id": loop_id,
                    "timestamp": time.time()
                }
            
            # Prepare system message
            system_message = """You are a Critic Agent that evaluates the outputs of specialized agents.
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
  },
  "rejection": false,
  "rejection_reason": null
}

If the output has critical flaws that require rejection, set "rejection" to true and provide a detailed "rejection_reason".
"""
            
            # Prepare user message with agent outputs
            user_message = f"Loop ID: {loop_id}\n\n"
            
            for agent_id, output in agent_outputs.items():
                user_message += f"--- {agent_id.upper()} OUTPUT ---\n{output}\n\n"
            
            # Call OpenAI API
            logger.info("Calling OpenAI API for critique...")
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
            logger.info(f"OpenAI API call successful, received {len(content)} characters")
            
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
                
                # Add metadata to result
                review_result = {
                    **result,
                    "status": "success",
                    "loop_id": loop_id,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "timestamp": time.time()
                }
                
                # Validate against schema
                if not self.validate_schema(review_result):
                    logger.warning(f"Review result failed schema validation for loop: {loop_id}")
                
                # Write to memory if available
                if memory_available:
                    memory_tag = f"critic_review_{loop_id}"
                    memory_data = {
                        "agent_id": self.agent_id,
                        "type": "loop",
                        "tag": memory_tag,
                        "content": json.dumps(review_result)
                    }
                    await write_memory(memory_data)
                
                return review_result
                
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON response: {str(e)}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "loop_id": loop_id,
                    "raw_response": content,
                    "timestamp": time.time()
                }
            except ValueError as e:
                error_msg = f"Invalid response structure: {str(e)}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "loop_id": loop_id,
                    "raw_response": content,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            error_msg = f"Error in CriticAgent.review: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "timestamp": time.time()
            }
    
    async def reject(self, loop_id: str, reason: str) -> Dict[str, Any]:
        """
        Reject a loop with a specific reason.
        
        Args:
            loop_id: Unique identifier for the loop
            reason: Reason for rejection
            
        Returns:
            Dict containing rejection status and details
        """
        try:
            logger.info(f"CriticAgent.reject called for loop: {loop_id}")
            
            rejection_result = {
                "status": "success",
                "loop_id": loop_id,
                "rejection": True,
                "rejection_reason": reason,
                "timestamp": time.time()
            }
            
            # Validate against schema
            if not self.validate_schema(rejection_result):
                logger.warning(f"Rejection result failed schema validation for loop: {loop_id}")
            
            # Write to memory if available
            if memory_available:
                memory_tag = f"critic_rejection_{loop_id}"
                memory_data = {
                    "agent_id": self.agent_id,
                    "type": "loop",
                    "tag": memory_tag,
                    "content": json.dumps(rejection_result)
                }
                await write_memory(memory_data)
            
            return rejection_result
            
        except Exception as e:
            error_msg = f"Error in CriticAgent.reject: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "timestamp": time.time()
            }
    
    async def log_reason(self, loop_id: str, reason_type: str, reason_text: str) -> Dict[str, Any]:
        """
        Log a specific reason or observation about a loop.
        
        Args:
            loop_id: Unique identifier for the loop
            reason_type: Type of reason (e.g., "improvement", "concern", "praise")
            reason_text: Detailed explanation
            
        Returns:
            Dict containing logging status and details
        """
        try:
            logger.info(f"CriticAgent.log_reason called for loop: {loop_id}")
            
            log_result = {
                "status": "success",
                "loop_id": loop_id,
                "reason_type": reason_type,
                "reason_text": reason_text,
                "timestamp": time.time()
            }
            
            # Validate against schema
            if not self.validate_schema(log_result):
                logger.warning(f"Log reason result failed schema validation for loop: {loop_id}")
            
            # Write to memory if available
            if memory_available:
                memory_tag = f"critic_reason_{loop_id}_{reason_type}"
                memory_data = {
                    "agent_id": self.agent_id,
                    "type": "loop",
                    "tag": memory_tag,
                    "content": json.dumps(log_result)
                }
                await write_memory(memory_data)
            
            return log_result
            
        except Exception as e:
            error_msg = f"Error in CriticAgent.log_reason: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "timestamp": time.time()
            }
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        return validate_schema(data, self.input_schema_path)
    
    async def execute(self, task: str, project_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            task: The task to execute
            project_id: The project identifier (optional)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            logger.info(f"CriticAgent.execute called with task: {task}, project_id: {project_id}")
            
            # Prepare input data for validation
            input_data = {
                "task": task,
                "project_id": project_id
            }
            
            # Add any additional kwargs to input data
            input_data.update(kwargs)
            
            # Validate input
            if not self.validate_input(input_data):
                logger.warning(f"Input validation failed for task: {task}")
            
            # Parse task to determine action
            if task.startswith("review:"):
                # Extract loop_id and agent_outputs from task
                parts = task.split(":", 1)[1].strip().split("|")
                if len(parts) < 2:
                    raise ValueError("Invalid review task format. Expected 'review:loop_id|{agent_outputs_json}'")
                
                loop_id = parts[0].strip()
                try:
                    agent_outputs = json.loads(parts[1].strip())
                except json.JSONDecodeError:
                    raise ValueError("Invalid agent_outputs JSON in review task")
                
                # Call review method
                return await self.review(loop_id, agent_outputs)
                
            elif task.startswith("reject:"):
                # Extract loop_id and reason from task
                parts = task.split(":", 1)[1].strip().split("|")
                if len(parts) < 2:
                    raise ValueError("Invalid reject task format. Expected 'reject:loop_id|reason'")
                
                loop_id = parts[0].strip()
                reason = parts[1].strip()
                
                # Call reject method
                return await self.reject(loop_id, reason)
                
            elif task.startswith("log_reason:"):
                # Extract loop_id, reason_type, and reason_text from task
                parts = task.split(":", 1)[1].strip().split("|")
                if len(parts) < 3:
                    raise ValueError("Invalid log_reason task format. Expected 'log_reason:loop_id|reason_type|reason_text'")
                
                loop_id = parts[0].strip()
                reason_type = parts[1].strip()
                reason_text = parts[2].strip()
                
                # Call log_reason method
                return await self.log_reason(loop_id, reason_type, reason_text)
                
            else:
                # Default to mock review for testing
                logger.warning(f"Unknown task format: {task}. Using mock review.")
                
                # Create mock agent outputs
                mock_outputs = {
                    "hal": "Mock HAL output for testing",
                    "ash": "Mock ASH output for testing",
                    "nova": "Mock NOVA output for testing"
                }
                
                # Call review method with mock data
                return await self.review(f"mock-{project_id or 'unknown'}", mock_outputs)
                
        except Exception as e:
            error_msg = f"Error in CriticAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Return error response
            return {
                "status": "error",
                "message": error_msg,
                "task": task,
                "project_id": project_id,
                "timestamp": time.time()
            }

# Main function to run the critic agent
async def run_critic_agent(task: str, project_id: str = None, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the CRITIC agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier (optional)
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Running CRITIC agent with task: {task}, project_id: {project_id}")
        
        # Initialize tools if None
        if tools is None:
            tools = ["review", "reject", "log_reason"]
        
        # Create critic agent instance
        critic = CriticAgent(tools)
        
        # Execute the task
        return await critic.execute(task, project_id)
            
    except Exception as e:
        error_msg = f"Error running CRITIC agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "task": task,
            "tools": tools if tools else [],
            "project_id": project_id,
            "timestamp": time.time()
        }

# Test function for isolated testing
async def test_critic_agent():
    """
    Test the CRITIC agent in isolation.
    
    Returns:
        Dict containing test results
    """
    print("\n=== Testing CRITIC Agent in isolation ===\n")
    
    try:
        # Create test data
        loop_id = "test-loop-123"
        agent_outputs = {
            "hal": "I recommend building a real-time collaboration platform with the following features:\n1. Document editing with version control\n2. Task management with assignments\n3. Chat and video conferencing\n4. API for integrations\n\nThe architecture will use a microservices approach with separate services for each core feature.",
            "ash": "The platform should have a clear onboarding flow that guides new users through creating their first project. Documentation should include video tutorials for each feature and a comprehensive API reference.",
            "nova": "The UI should use a clean, minimal design with a blue and white color scheme. The layout should prioritize the document workspace with collapsible sidebars for chat and task management."
        }
        
        # Run the agent with review task
        task = f"review:{loop_id}|{json.dumps(agent_outputs)}"
        result = await run_critic_agent(task, "test-project")
        
        # Print the result
        print(f"\nReview Result:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Reflection: {result.get('reflection', 'No reflection')[:100]}...")
        if "scores" in result:
            print(f"Scores: {result['scores']}")
        
        # Test rejection
        task = f"reject:{loop_id}|Test rejection reason"
        reject_result = await run_critic_agent(task, "test-project")
        
        print(f"\nReject Result:")
        print(f"Status: {reject_result.get('status', 'unknown')}")
        print(f"Rejection: {reject_result.get('rejection', False)}")
        print(f"Reason: {reject_result.get('rejection_reason', 'No reason')}")
        
        # Test log_reason
        task = f"log_reason:{loop_id}|improvement|The documentation could be more comprehensive"
        log_result = await run_critic_agent(task, "test-project")
        
        print(f"\nLog Reason Result:")
        print(f"Status: {log_result.get('status', 'unknown')}")
        print(f"Reason Type: {log_result.get('reason_type', 'unknown')}")
        print(f"Reason Text: {log_result.get('reason_text', 'No text')}")
        
        return {
            "review_result": result,
            "reject_result": reject_result,
            "log_result": log_result
        }
        
    except Exception as e:
        error_msg = f"Error testing CRITIC agent: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "timestamp": time.time()
        }

# memory_tag: healed_phase3.3
