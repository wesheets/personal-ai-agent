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

# Import schema
from app.schemas.sitegen_schema import SiteGenTaskRequest, SiteGenTaskResult, SiteLayout, SiteGenErrorResult

# Import agent_sdk
try:
    from agent_sdk.agent_sdk import AgentSDK
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False
    print("❌ agent_sdk import failed")

# Import OpenAI provider
try:
    from app.providers.openai_provider import OpenAIProvider
    OPENAI_PROVIDER_AVAILABLE = True
except ImportError:
    OPENAI_PROVIDER_AVAILABLE = False
    print("❌ openai_provider import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    print("❌ system_log import failed")

# Configure logging
logger = logging.getLogger("agents.sitegen")

class SiteGenAgent:
    """
    SITEGEN Agent for planning commercial sites and creating optimal layouts
    
    This agent is responsible for:
    1. Analyzing zoning requirements for commercial sites
    2. Creating optimal layouts based on requirements
    3. Evaluating market-fit for construction projects
    """
    
    def __init__(self):
        """Initialize the SITEGEN agent."""
        self.name = "SITEGEN"
        self.description = "Site planning and layout generation agent"
        self.tools = ["analyze_zoning", "create_layout", "evaluate_market_fit"]
        
        # Initialize Agent SDK if available
        if AGENT_SDK_AVAILABLE:
            self.sdk = AgentSDK(agent_name="sitegen")
        
        # Initialize OpenAI provider
        self.openai_provider = None
        if OPENAI_PROVIDER_AVAILABLE:
            try:
                self.openai_provider = OpenAIProvider()
                logger.info("✅ OpenAI provider initialized successfully for SiteGen agent")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI provider for SiteGen agent: {str(e)}")
    
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
    
    async def run_agent_async(self, request: SiteGenTaskRequest) -> SiteGenTaskResult:
        """
        Run the SITEGEN agent with the given request asynchronously.
        
        Args:
            request: The SiteGenTaskRequest containing task and parameters
            
        Returns:
            SiteGenTaskResult containing the response and metadata
        """
        try:
            logger.info(f"Running SITEGEN agent with task: {request.task}")
            print(f"🚀 SITEGEN agent execution started")
            print(f"📋 Task: {request.task}")
            print(f"🆔 Project ID: {request.project_id}")
            print(f"🧰 Tools: {request.tools}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("SITEGEN", f"Starting execution with task: {request.task}", request.project_id)
            
            # Check if OpenAI provider is available
            if not self.openai_provider:
                error_msg = "OpenAI provider not initialized"
                logger.error(error_msg)
                return SiteGenErrorResult(
                    status="error",
                    message=error_msg,
                    task=request.task,
                    project_id=request.project_id
                )
            
            # Process the task through OpenAI
            response = await self._process_with_openai(request.task, request.site_parameters)
            
            # Extract content from response
            content = response.get('content', '')
            
            # Create a basic result
            result = {
                "status": "success",
                "message": "Site plan created successfully",
                "task": request.task,
                "project_id": request.project_id,
                "analysis": "Analysis based on the provided parameters.",
                "recommendations": ["Consider local zoning laws", "Optimize for customer flow", "Ensure adequate parking"]
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
                log_event("SITEGEN", f"Completed execution with task: {request.task}", request.project_id)
            
            # Return success response
            return SiteGenTaskResult(**result)
            
        except Exception as e:
            error_msg = f"Error running SITEGEN agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("SITEGEN", f"Error: {str(e)}", request.project_id)
            
            # Return error response
            return SiteGenErrorResult(
                status="error",
                message=error_msg,
                task=request.task,
                project_id=request.project_id
            )
    
    def run_agent(self, request: SiteGenTaskRequest) -> SiteGenTaskResult:
        """
        Run the SITEGEN agent with the given request.
        
        Args:
            request: The SiteGenTaskRequest containing task and parameters
            
        Returns:
            SiteGenTaskResult containing the response and metadata
        """
        # Run the async method in a synchronous context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.run_agent_async(request))

# Create an instance of the agent
sitegen_agent = SiteGenAgent()

async def handle_sitegen_task_async(task_input: str, project_id: Optional[str] = None) -> str:
    """
    Handle a SITEGEN task asynchronously.
    
    Args:
        task_input: The task description or query
        project_id: Optional project identifier
        
    Returns:
        String containing the result message
    """
    # Create a request object
    request = SiteGenTaskRequest(
        task=task_input,
        project_id=project_id,
        tools=["analyze_zoning", "create_layout", "evaluate_market_fit"]
    )
    
    # Run the agent
    result = await sitegen_agent.run_agent_async(request)
    
    # Return message for backward compatibility
    if result.status == "success":
        return f"🏗️ {result.message}"
    else:
        return f"🏗️ SiteGen Agent Error: {result.message}. Falling back to static response for: '{task_input}'."

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
    return result

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
