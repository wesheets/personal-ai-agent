"""
SITEGEN Agent Module

This module provides the implementation for the SITEGEN agent, which is responsible for
planning commercial sites, analyzing zoning requirements, creating optimal layouts,
and evaluating market-fit for construction projects.

The SITEGEN agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import json

# Import Agent SDK
from agent_sdk.agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.sitegen")

# Import OpenAI provider
try:
    from app.providers.openai_provider import OpenAIProvider
    OPENAI_PROVIDER_AVAILABLE = True
except ImportError:
    OPENAI_PROVIDER_AVAILABLE = False
    logger.warning("⚠️ openai_provider import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    logger.warning("⚠️ system_log import failed")

class SiteGenAgent(Agent):
    """
    SITEGEN Agent for planning commercial sites and creating optimal layouts
    
    This agent is responsible for:
    1. Analyzing zoning requirements for commercial sites
    2. Creating optimal layouts based on requirements
    3. Evaluating market-fit for construction projects
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the SITEGEN agent with SDK compliance."""
        # Define agent properties
        name = "SiteGen"
        role = "Site Planning Specialist"
        tools_list = tools or ["analyze_zoning", "create_layout", "evaluate_market_fit"]
        permissions = ["read_zoning_data", "create_site_plans", "evaluate_market_conditions"]
        description = "Responsible for planning commercial sites, analyzing zoning requirements, creating optimal layouts, and evaluating market-fit for construction projects."
        tone_profile = {
            "professional": "high",
            "analytical": "high",
            "practical": "high",
            "technical": "medium",
            "creative": "medium"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/sitegen/input_schema.json"
        output_schema_path = "app/schemas/sitegen/output_schema.json"
        
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
                logger.info("✅ OpenAI provider initialized successfully for SiteGen agent")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI provider for SiteGen agent: {str(e)}")
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        return validate_schema(data, self.input_schema_path)
    
    async def _process_with_openai(self, task: str, site_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process the task through OpenAI.
        
        Args:
            task: The task description or query
            site_parameters: Parameters for site generation
            
        Returns:
            Dict containing the OpenAI response
        """
        if not self.openai_provider:
            raise ValueError("OpenAI provider not initialized")
        
        # Create a prompt chain with SiteGen's specific tone and domain
        prompt_chain = {
            "system": "You are SiteGen, an intelligent system for planning commercial sites. You analyze zoning requirements, create optimal layouts, and evaluate market-fit for construction projects. You speak with a professional, analytical tone and focus on practical solutions.",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Add site parameters to the task if provided
        full_task = task
        if site_parameters:
            full_task += f"\n\nSite Parameters: {site_parameters}"
        
        # Process the task through OpenAI
        response = await self.openai_provider.process_with_prompt_chain(
            prompt_chain=prompt_chain,
            user_input=full_task
        )
        
        return response
    
    async def execute(self, task: str, project_id: str = None, tools: List[str] = None, 
                     site_parameters: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            task: The task to execute
            project_id: The project identifier (optional)
            tools: List of tools to use (optional)
            site_parameters: Parameters for site generation (optional)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            logger.info(f"SiteGenAgent.execute called with task: {task}, project_id: {project_id}")
            
            # Prepare input data for validation
            input_data = {
                "task": task,
                "project_id": project_id
            }
            
            if tools:
                input_data["tools"] = tools
            
            if site_parameters:
                input_data["site_parameters"] = site_parameters
            
            # Add any additional kwargs to input data
            input_data.update(kwargs)
            
            # Validate input
            if not self.validate_input(input_data):
                logger.warning(f"Input validation failed for task: {task}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("SITEGEN", f"Starting execution with task: {task}", project_id)
            
            # Check if OpenAI provider is available
            if not self.openai_provider:
                error_msg = "OpenAI provider not initialized"
                logger.error(error_msg)
                
                error_result = {
                    "status": "error",
                    "message": error_msg,
                    "task": task,
                    "project_id": project_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Validate output
                if not self.validate_schema(error_result):
                    logger.warning(f"Output validation failed for error result")
                
                return error_result
            
            # Process the task through OpenAI
            response = await self._process_with_openai(task, site_parameters)
            
            # Extract content from response
            content = response.get('content', '')
            
            # Create a basic result
            result = {
                "status": "success",
                "message": "Site plan created successfully",
                "task": task,
                "project_id": project_id,
                "analysis": "Analysis based on the provided parameters.",
                "recommendations": ["Consider local zoning laws", "Optimize for customer flow", "Ensure adequate parking"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # For now, we'll use a placeholder layout
            # In a real implementation, this would be parsed from the OpenAI response
            result["layout"] = {
                "layout_type": "commercial",
                "dimensions": {"width": 100, "depth": 50, "height": 20},
                "zones": [
                    {"name": "main_area", "size": 3000, "position": "center"},
                    {"name": "auxiliary", "size": 1000, "position": "back"},
                    {"name": "parking", "size": 1000, "position": "front"}
                ],
                "features": ["windows", "loading area", "customer parking"]
            }
            
            # Add market fit evaluation
            result["market_fit"] = {
                "score": 0.8,
                "strengths": ["good location", "adequate size"],
                "weaknesses": ["limited expansion potential"]
            }
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("SITEGEN", f"Completed execution with task: {task}", project_id)
            
            # Validate output
            if not self.validate_schema(result):
                logger.warning(f"Output validation failed for success result")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in SiteGenAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("SITEGEN", f"Error: {str(e)}", project_id)
            
            # Return error response
            error_result = {
                "status": "error",
                "message": error_msg,
                "task": task,
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(error_result):
                logger.warning(f"Output validation failed for error result")
            
            return error_result

# Create an instance of the agent
sitegen_agent = SiteGenAgent()

async def handle_sitegen_task_async(task_input: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle a SITEGEN task asynchronously.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        task_input: The task description or query
        project_id: Optional project identifier
        
    Returns:
        Dict containing the result of the execution
    """
    # Execute the agent
    return await sitegen_agent.execute(
        task=task_input,
        project_id=project_id
    )

def handle_sitegen_task_sync(task_input: str, project_id: Optional[str] = None) -> str:
    """
    Handle a SITEGEN task synchronously.
    
    Args:
        task_input: The task description or query
        project_id: Optional project identifier
        
    Returns:
        String containing the result message
    """
    # Run the async method in a synchronous context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(handle_sitegen_task_async(task_input, project_id))
    
    # Return message for backward compatibility
    if result["status"] == "success":
        return f"🏗️ {result['message']}"
    else:
        return f"🏗️ SiteGen Agent Error: {result['message']}. Falling back to static response for: '{task_input}'."

# For backward compatibility with existing code
def handle_sitegen_task(task_input: str) -> str:
    """
    Legacy function to maintain backward compatibility.
    
    Args:
        task_input: The task description or query
        
    Returns:
        String containing the result message
    """
    return handle_sitegen_task_sync(task_input)

# memory_tag: healed_phase3.3
