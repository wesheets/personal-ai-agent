"""
AgentRunner Module

This module provides isolated agent execution functionality, allowing agents to run
independently from the central agent registry, UI, or delegate-stream system.

MODIFIED: Added full runtime logging and error protection to prevent 502 errors
MODIFIED: Added memory thread logging for agent steps
MODIFIED: Added enhanced logging for debugging memory thread issues
MODIFIED: Added toolkit registry integration for specialized agent tools
MODIFIED: Added product strategist logic for HAL in saas domain
MODIFIED: Added structured output for ASH documentation and onboarding
MODIFIED: Added AGENT_RUNNERS mapping for direct agent execution
MODIFIED: Added run_hal_agent function with file_writer integration
"""

import logging
import os
from typing import List, Dict, Any, Optional
import time
import traceback
import sys
import uuid
import asyncio
import json
from fastapi.responses import JSONResponse

# Import OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI client import failed")

# Import memory thread module
from app.modules.memory_thread import add_memory_thread

# Import toolkit registry
try:
    from toolkit.registry import get_toolkit, get_agent_role, format_tools_prompt, format_nova_prompt, get_agent_themes
    TOOLKIT_AVAILABLE = True
except ImportError:
    TOOLKIT_AVAILABLE = False
    print("❌ toolkit.registry import failed, creating fallback functions")
    # Create fallback functions
    def get_toolkit(agent_id, domain):
        print(f"⚠️ Using fallback get_toolkit for {agent_id} in {domain} domain")
        return []
    
    def get_agent_role(agent_id):
        print(f"⚠️ Using fallback get_agent_role for {agent_id}")
        roles = {
            "hal": "Product Strategist",
            "nova": "UI Designer",
            "ash": "Documentation Specialist",
            "critic": "Quality Assurance Specialist",
            "sage": "System Narrator"
        }
        return roles.get(agent_id, "AI Assistant")
    
    def format_tools_prompt(tools):
        print("⚠️ Using fallback format_tools_prompt")
        return "You have access to specialized tools, but they are currently unavailable."
    
    def format_nova_prompt(tools, themes):
        print("⚠️ Using fallback format_nova_prompt")
        return "You are a UI designer with design themes, but they are currently unavailable."
    
    def get_agent_themes(agent_id):
        print(f"⚠️ Using fallback get_agent_themes for {agent_id}")
        return []

# Import file_writer for HAL agent
try:
    from toolkit.file_writer import write_file
    FILE_WRITER_AVAILABLE = True
except ImportError:
    FILE_WRITER_AVAILABLE = False
    print("❌ file_writer import failed")

# Configure logging
logger = logging.getLogger("modules.agent_runner")

class CoreForgeAgent:
    """
    Standalone implementation of CoreForgeAgent with no registry dependencies.
    """
    def __init__(self):
        self.agent_id = "Core.Forge"
        self.name = "Core.Forge"
        self.description = "System orchestrator that routes tasks to appropriate agents"
        self.tone = "professional"
        
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
    
    def run(self, messages: List[Dict[str, Any]], agent_id: str = None, domain: str = "saas") -> Dict[str, Any]:
        """
        Run the agent with the given messages.
        
        Args:
            messages: List of message dictionaries with role and content
            agent_id: Optional agent identifier for toolkit selection
            domain: Optional domain for toolkit selection, defaults to "saas"
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            print(f"🤖 CoreForgeAgent.run called with {len(messages)} messages")
            
            if not self.client:
                error_msg = "OpenAI client initialization failed. Unable to process request."
                print(f"❌ {error_msg}")
                return {
                    "content": error_msg,
                    "status": "error"
                }
            
            # Set response format based on agent
            response_format = None
            if agent_id:
                if agent_id.lower() == "hal" and domain == "saas":
                    response_format = {"type": "json_object"}
                elif agent_id.lower() == "ash" and domain == "saas":
                    response_format = {"type": "json_object"}
            
            # Prepare system message with agent role and tools if agent_id is provided
            if agent_id and agent_id.lower() in ["hal", "ash", "nova"]:
                # Get agent role
                role = get_agent_role(agent_id.lower())
                
                # Get toolkit for agent and domain
                tools = get_toolkit(agent_id.lower(), domain)
                
                # Format tools prompt based on agent
                tools_prompt = ""
                if agent_id.lower() == "nova":
                    themes = get_agent_themes(agent_id.lower())
                    tools_prompt = format_nova_prompt(tools, themes)
                else:
                    tools_prompt = format_tools_prompt(tools)
                
                # Check if first message is system message
                if messages and messages[0].get("role") == "system":
                    # Update existing system message
                    system_content = messages[0].get("content", "")
                    
                    # Add role and tools information
                    if role:
                        system_content = f"You are a {role}.\n\n{system_content}"
                    
                    if tools_prompt:
                        system_content = f"{system_content}\n\n{tools_prompt}"
                    
                    # Add specialized logic based on agent and domain
                    if agent_id.lower() == "hal" and domain == "saas":
                        # Add product strategist logic for HAL in saas domain
                        product_strategist_prompt = """
As a Product Strategist, your task is to create structured SaaS product plans.

Your responses for SaaS planning should include:
1. Core features (essential functionality)
2. MVP features (minimum viable product)
3. Premium features (for monetization)
4. Monetization strategy (pricing model)
5. Implementation task steps

Format your response as a structured JSON object with these exact keys:
- core_features: array of strings
- mvp_features: array of strings
- premium_features: array of strings
- monetization: string
- task_steps: array of strings

Be specific, realistic, and focused on creating a monetizable SaaS product.
"""
                        system_content = f"{system_content}\n\n{product_strategist_prompt}"
                    
                    elif agent_id.lower() == "ash" and domain == "saas":
                        # Add UX Docifier logic for ASH in saas domain
                        ux_docifier_prompt = """
As a UX Docifier, your task is to create comprehensive documentation for SaaS products.

Your responses should include:
1. API documentation with endpoints, methods, and payloads
2. User onboarding instructions with clear steps
3. Third-party service integration suggestions

Format your response as a structured JSON object with these exact keys:
- docs.api: string containing API endpoints with methods and payloads
- docs.onboarding: string containing user onboarding copy with steps
- docs.integration: string containing third-party service suggestions

Be clear, comprehensive, and focused on creating documentation that enhances user experience.
"""
                        system_content = f"{system_content}\n\n{ux_docifier_prompt}"
                    
                    # Update system message
                    messages[0]["content"] = system_content
                else:
                    # Create new system message
                    system_content = ""
                    
                    if role:
                        system_content = f"You are a {role}."
                    
                    if tools_prompt:
                        if system_content:
                            system_content = f"{system_content}\n\n{tools_prompt}"
                        else:
                            system_content = tools_prompt
                    
                    # Add specialized logic based on agent and domain
                    if agent_id.lower() == "hal" and domain == "saas":
                        # Add product strategist logic for HAL in saas domain
                        product_strategist_prompt = """
As a Product Strategist, your task is to create structured SaaS product plans.

Your responses for SaaS planning should include:
1. Core features (essential functionality)
2. MVP features (minimum viable product)
3. Premium features (for monetization)
4. Monetization strategy (pricing model)
5. Implementation task steps

Format your response as a structured JSON object with these exact keys:
- core_features: array of strings
- mvp_features: array of strings
- premium_features: array of strings
- monetization: string
- task_steps: array of strings

Be specific, realistic, and focused on creating a monetizable SaaS product.
"""
                        if system_content:
                            system_content = f"{system_content}\n\n{product_strategist_prompt}"
                        else:
                            system_content = product_strategist_prompt
                    
                    elif agent_id.lower() == "ash" and domain == "saas":
                        # Add UX Docifier logic for ASH in saas domain
                        ux_docifier_prompt = """
As a UX Docifier, your task is to create comprehensive documentation for SaaS products.

Your responses should include:
1. API documentation with endpoints, methods, and payloads
2. User onboarding instructions with clear steps
3. Third-party service integration suggestions

Format your response as a structured JSON object with these exact keys:
- docs.api: string containing API endpoints with methods and payloads
- docs.onboarding: string containing user onboarding copy with steps
- docs.integration: string containing third-party service suggestions

Be clear, comprehensive, and focused on creating documentation that enhances user experience.
"""
                        if system_content:
                            system_content = f"{system_content}\n\n{ux_docifier_prompt}"
                        else:
                            system_content = ux_docifier_prompt
                    
                    # Add system message at the beginning
                    if system_content:
                        messages.insert(0, {"role": "system", "content": system_content})
            
            # Call OpenAI API
            print("📡 Calling OpenAI API...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                response_format=response_format
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            print(f"✅ OpenAI API call successful, received {len(content)} characters")
            
            # Return result with metadata
            return {
                "content": content,
                "status": "success",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "timestamp": time.time()
            }
        except Exception as e:
            error_msg = f"Error in CoreForgeAgent.run: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "content": f"Error processing request: {str(e)}",
                "status": "error"
            }

async def log_memory_thread(project_id: str, chain_id: str, agent: str, role: str, step_type: str, content: str, structured_data: Dict = None) -> None:
    """
    Log a memory thread entry for an agent step.
    
    Args:
        project_id: The project identifier
        chain_id: The chain identifier
        agent: The agent type (hal, ash, nova)
        role: The agent role (thinker, explainer, designer)
        step_type: The step type (task, summary, ui, reflection)
        content: The content of the step
        structured_data: Optional structured data for specialized agents
    """
    try:
        # Create memory entry
        memory_entry = {
            "project_id": project_id,
            "chain_id": chain_id,
            "agent": agent,
            "role": role,
            "step_type": step_type,
            "content": content
        }
        
        # Add structured data if available
        if structured_data:
            memory_entry["structured_data"] = structured_data
            
            # For ASH, break down documentation into separate memory entries
            if agent == "ash" and structured_data:
                # Process API docs
                if "docs.api" in structured_data:
                    api_memory = memory_entry.copy()
                    api_memory["step_type"] = "docs.api"
                    api_memory["content"] = structured_data["docs.api"]
                    await add_memory_thread(api_memory)
                    print(f"✅ Memory thread logged for API docs")
                
                # Process onboarding docs
                if "docs.onboarding" in structured_data:
                    onboarding_memory = memory_entry.copy()
                    onboarding_memory["step_type"] = "docs.onboarding"
                    onboarding_memory["content"] = structured_data["docs.onboarding"]
                    await add_memory_thread(onboarding_memory)
                    print(f"✅ Memory thread logged for onboarding docs")
                
                # Process integration docs
                if "docs.integration" in structured_data:
                    integration_memory = memory_entry.copy()
                    integration_memory["step_type"] = "docs.integration"
                    integration_memory["content"] = structured_data["docs.integration"]
                    await add_memory_thread(integration_memory)
                    print(f"✅ Memory thread logged for integration docs")
        
        # Enhanced logging for debugging
        print(f"🔍 DEBUG: Memory thread entry created with project_id={project_id}, chain_id={chain_id}")
        print(f"🔍 DEBUG: Memory entry details: {memory_entry}")
        logger.info(f"DEBUG: Memory thread entry created with project_id={project_id}, chain_id={chain_id}")
        
        # Log memory entry
        print(f"📝 Logging memory thread for {agent} agent, {step_type} step")
        logger.info(f"Logging memory thread for {agent} agent, {step_type} step")
        
        # Add memory entry to thread
        print(f"🔍 DEBUG: Calling add_memory_thread with entry")
        result = await add_memory_thread(memory_entry)
        
        # Log result
        print(f"✅ Memory thread logged successfully: {result}")
        print(f"🔍 DEBUG: add_memory_thread returned: {result}")
        logger.info(f"Memory thread logged successfully: {result}")
    except Exception as e:
        # Log error but don't fail the main process
        error_msg = f"Error logging memory thread: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"🔍 DEBUG: Exception traceback: {traceback.format_exc()}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())

# Define agent runner functions
def run_hal_agent(task, project_id, tools):
    """
    Run the HAL agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 HAL agent execution started")
    print(f"📋 Task: {task}")
    print(f"🆔 Project ID: {project_id}")
    print(f"🧰 Tools: {tools}")
    logger.info(f"HAL agent execution started with task: {task}, project_id: {project_id}, tools: {tools}")
    
    try:
        # Create a bootstrap file using file_writer
        if FILE_WRITER_AVAILABLE and "file_writer" in tools:
            print(f"📝 Using file_writer to create bootstrap file")
            
            # Create content for README.md
            contents = f"# Project {project_id}\n\nTask: {task}\nTools: {', '.join(tools)}"
            
            # Write file
            output = write_file(
                project_id=project_id,
                file_path=f"/verticals/{project_id}/README.md",
                content=contents
            )
            
            print(f"✅ Bootstrap file created successfully")
            logger.info(f"HAL created bootstrap file for project {project_id}")
            
            return {
                "message": f"HAL successfully created bootstrap file",
                "output": output,
                "task": task,
                "tools": tools
            }
        else:
            # If file_writer is not available or not in tools
            print(f"⚠️ file_writer not available or not in tools list")
            logger.warning(f"file_writer not available or not in tools list")
            
            return {
                "message": f"HAL received task for project {project_id}",
                "task": task,
                "tools": tools
            }
    except Exception as e:
        error_msg = f"Error in run_hal_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "message": f"Error executing HAL agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e)
        }

def run_nova_agent(task, project_id, tools):
    """
    Run the NOVA agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 NOVA agent execution started")
    logger.info(f"NOVA agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement NOVA agent execution
    return {
        "message": f"NOVA received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_ash_agent(task, project_id, tools):
    """
    Run the ASH agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 ASH agent execution started")
    logger.info(f"ASH agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement ASH agent execution
    return {
        "message": f"ASH received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_critic_agent(task, project_id, tools):
    """
    Run the CRITIC agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 CRITIC agent execution started")
    logger.info(f"CRITIC agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement CRITIC agent execution
    return {
        "message": f"CRITIC received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_orchestrator_agent(task, project_id, tools):
    """
    Run the ORCHESTRATOR agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 ORCHESTRATOR agent execution started")
    logger.info(f"ORCHESTRATOR agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement ORCHESTRATOR agent execution
    return {
        "message": f"ORCHESTRATOR received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_sage_agent(project_id, tools=None):
    """
    Run the SAGE (System-wide Agent for Generating Explanations) agent.
    
    This agent generates narrative summaries of system activities for a specific project.
    
    Args:
        project_id: The project identifier
        tools: Optional list of tools to use
        
    Returns:
        Dict containing the summary and metadata
    """
    print(f"🤖 SAGE agent execution started")
    logger.info(f"SAGE agent execution started for project_id: {project_id}")
    
    try:
        # Default tools if not provided
        if tools is None:
            tools = ["memory_writer"]
        
        print(f"🧰 Tools: {tools}")
        
        # Generate a narrative summary based on project state and memory
        summary = "This is a system-generated summary of recent activities for project " + project_id
        
        # TODO: Implement actual SAGE agent logic to generate meaningful summaries
        # This would typically involve:
        # 1. Reading project state
        # 2. Retrieving memory entries
        # 3. Using LLM to generate a narrative
        
        return {
            "status": "success",
            "summary": summary,
            "project_id": project_id,
            "tools": tools
        }
    except Exception as e:
        error_msg = f"Error in run_sage_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "tools": tools if tools else []
        }

# Define agent runners mapping
AGENT_RUNNERS = {
    "hal": run_hal_agent,
    "nova": run_nova_agent,
    "ash": run_ash_agent,
    "critic": run_critic_agent,
    "orchestrator": run_orchestrator_agent,
    "sage": run_sage_agent
}

async def run_agent_async(agent_id: str, messages: List[Dict[str, Any]], project_id: str = None, chain_id: str = None, domain: str = "saas"):
    """
    Async version of run_agent function.
    
    Args:
        agent_id: The ID of the agent to run
        messages: List of message dictionaries with role and content
        project_id: Optional project identifier for memory logging
        chain_id: Optional chain identifier for memory logging
        domain: Optional domain for toolkit selection, defaults to "saas"
        
    Returns:
        Dict containing the response and metadata or JSONResponse with error details
    """
    # Generate project_id and chain_id if not provided
    if not project_id:
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        print(f"🆔 Generated project_id: {project_id}")
    
    if not chain_id:
        chain_id = f"chain_{uuid.uuid4().hex[:8]}"
        print(f"🔗 Generated chain_id: {chain_id}")
    
    # Enhanced logging for debugging
    print(f"🔍 DEBUG: run_agent_async called with agent_id={agent_id}, project_id={project_id}, chain_id={chain_id}, domain={domain}")
    logger.info(f"DEBUG: run_agent_async called with agent_id={agent_id}, project_id={project_id}, chain_id={chain_id}, domain={domain}")
    
    # Map agent_id to standard agent types and roles
    agent_mapping = {
        "hal": {"agent": "hal", "role": "thinker"},
        "ash": {"agent": "ash", "role": "explainer"},
        "nova": {"agent": "nova", "role": "designer"},
        "critic": {"agent": "critic", "role": "critic"},
        "orchestrator": {"agent": "orchestrator", "role": "orchestrator"},
        "Core.Forge": {"agent": "hal", "role": "thinker"}  # Default to HAL for CoreForge
    }
    
    # Get agent type and role
    agent_info = agent_mapping.get(agent_id.lower(), {"agent": "hal", "role": "thinker"})
    agent_type = agent_info["agent"]
    agent_role = agent_info["role"]
    
    print(f"🔍 DEBUG: Mapped agent_id={agent_id} to agent_type={agent_type}, agent_role={agent_role}")
    
    try:
        print("🧠 Attempting to run CoreForgeAgent fallback")
        logger.info("Attempting to run CoreForgeAgent fallback")
        
        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        logger.info(f"OpenAI API Key available: {bool(api_key)}")
        
        if not api_key:
            error_msg = "OpenAI API key is not set in environment variables"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            
            # Log error to memory thread
            print(f"🔍 DEBUG: About to log error to memory thread")
            await log_memory_thread(
                project_id=project_id,
                chain_id=chain_id,
                agent=agent_type,
                role=agent_role,
                step_type="task",
                content=f"Error: {error_msg}"
            )
            print(f"🔍 DEBUG: Finished logging error to memory thread")
            
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": agent_id,
                    "response": error_msg,
                    "status": "error"
                }
            )
        
        # Create CoreForgeAgent instance
        print(f"🔄 Creating CoreForgeAgent instance for: {agent_id}")
        agent = CoreForgeAgent()
        
        # Call agent's run method with agent_id and domain for toolkit selection
        print(f"🏃 Calling CoreForgeAgent.run() method with {len(messages)} messages")
        result = agent.run(messages, agent_id=agent_id, domain=domain)
        
        # Check if agent execution was successful
        if result.get("status") == "error":
            error_msg = f"CoreForgeAgent execution failed: {result.get('content')}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            
            # Log error to memory thread
            print(f"🔍 DEBUG: About to log error to memory thread")
            await log_memory_thread(
                project_id=project_id,
                chain_id=chain_id,
                agent=agent_type,
                role=agent_role,
                step_type="task",
                content=f"Error: {result.get('content', 'Unknown error')}"
            )
            print(f"🔍 DEBUG: Finished logging error to memory thread")
            
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": "Core.Forge",
                    "response": result.get("content", "Unknown error"),
                    "status": "error"
                }
            )
        
        # Process agent-specific responses
        structured_data = None
        
        # Process HAL's response for saas domain
        if agent_id.lower() == "hal" and domain == "saas":
            try:
                # Parse JSON response
                content = result.get("content", "")
                parsed_content = json.loads(content)
                
                # Check for required fields
                required_fields = ["core_features", "mvp_features", "premium_features", "monetization", "task_steps"]
                for field in required_fields:
                    if field not in parsed_content:
                        parsed_content[field] = []
                
                # Update content with structured data
                result["content"] = json.dumps(parsed_content)
                structured_data = parsed_content
            except Exception as e:
                print(f"❌ Error parsing HAL's JSON response: {str(e)}")
                logger.error(f"Error parsing HAL's JSON response: {str(e)}")
                # Continue with original content
        
        # Process ASH's response for saas domain
        elif agent_id.lower() == "ash" and domain == "saas":
            try:
                # Parse JSON response
                content = result.get("content", "")
                parsed_content = json.loads(content)
                
                # Check for required fields
                required_fields = ["docs.api", "docs.onboarding", "docs.integration"]
                for field in required_fields:
                    if field not in parsed_content:
                        parsed_content[field] = ""
                
                # Update content with structured data
                result["content"] = json.dumps(parsed_content)
                structured_data = parsed_content
            except Exception as e:
                print(f"❌ Error parsing ASH's JSON response: {str(e)}")
                logger.error(f"Error parsing ASH's JSON response: {str(e)}")
                # Continue with original content
        
        # Log success
        print("✅ AgentRunner success, returning response")
        logger.info("AgentRunner success, returning response")
        
        # Log successful response to memory thread
        print(f"🔍 DEBUG: About to log successful response to memory thread")
        await log_memory_thread(
            project_id=project_id,
            chain_id=chain_id,
            agent=agent_type,
            role=agent_role,
            step_type="task",
            content=result.get("content", ""),
            structured_data=structured_data
        )
        print(f"🔍 DEBUG: Finished logging successful response to memory thread")
        
        # Return successful response
        return {
            "agent_id": "Core.Forge",
            "response": result.get("content", ""),
            "status": "ok",
            "usage": result.get("usage", {}),
            "project_id": project_id,
            "chain_id": chain_id,
            "structured_data": structured_data
        }
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Error running agent {agent_id}: {str(e)}"
        print(f"❌ AgentRunner failed: {str(e)}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Log error to memory thread
        try:
            print(f"🔍 DEBUG: About to log exception to memory thread")
            await log_memory_thread(
                project_id=project_id,
                chain_id=chain_id,
                agent=agent_type,
                role=agent_role,
                step_type="task",
                content=f"Error: {str(e)}"
            )
            print(f"🔍 DEBUG: Finished logging exception to memory thread")
        except Exception as log_error:
            print(f"❌ Failed to log error to memory thread: {str(log_error)}")
            print(f"🔍 DEBUG: Exception when logging error: {traceback.format_exc()}")
        
        # Return structured error response
        return JSONResponse(
            status_code=500,
            content={
                "agent_id": agent_id,
                "response": error_msg,
                "status": "error",
                "message": str(e),
                "project_id": project_id,
                "chain_id": chain_id
            }
        )

def run_agent(agent_id: str, messages: List[Dict[str, Any]], project_id: str = None, chain_id: str = None, domain: str = "saas"):
    """
    Run an agent with the given messages, with no registry dependencies.
    
    MODIFIED: Added full runtime logging and error protection to prevent 502 errors
    MODIFIED: Added memory thread logging for agent steps
    MODIFIED: Added enhanced logging for debugging memory thread issues
    MODIFIED: Added toolkit registry integration for specialized agent tools
    MODIFIED: Added product strategist logic for HAL in saas domain
    MODIFIED: Added structured output for ASH documentation and onboarding
    
    Args:
        agent_id: The ID of the agent to run
        messages: List of message dictionaries with role and content
        project_id: Optional project identifier for memory logging
        chain_id: Optional chain identifier for memory logging
        domain: Optional domain for toolkit selection, defaults to "saas"
        
    Returns:
        Dict containing the response and metadata or JSONResponse with error details
    """
    # ADDED: Entry confirmation logging
    print("🔥 AgentRunner route invoked")
    print(f"🔍 DEBUG: run_agent called with agent_id={agent_id}, project_id={project_id}, chain_id={chain_id}, domain={domain}")
    logger.info("🔥 AgentRunner route invoked")
    
    # Run the async version in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print(f"🔍 DEBUG: Creating new event loop and running run_agent_async")
        result = loop.run_until_complete(run_agent_async(agent_id, messages, project_id, chain_id, domain))
        print(f"🔍 DEBUG: run_agent_async completed successfully")
        return result
    except Exception as e:
        print(f"🔍 DEBUG: Exception in run_agent event loop: {str(e)}")
        print(f"🔍 DEBUG: {traceback.format_exc()}")
        raise
    finally:
        print(f"🔍 DEBUG: Closing event loop")
        loop.close()

def test_core_forge_isolation():
    """
    Test CoreForgeAgent in isolation to verify it works correctly.
    
    Returns:
        Dict containing the test results
    """
    print("\n=== Testing CoreForgeAgent in isolation ===\n")
    
    try:
        # Create test messages
        messages = [
            {"role": "user", "content": "What is 7 + 5?"}
        ]
        
        # Create agent
        print("🔧 Creating CoreForgeAgent instance")
        agent = CoreForgeAgent()
        
        # Run the agent
        print(f"🏃 Running CoreForgeAgent with message: {messages[0]['content']}")
        result = agent.run(messages)
        
        # Print the result
        print(f"\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Response: {result.get('content', 'No response')}")
        
        if result.get('status') == 'success':
            print("\n✅ Test passed: CoreForgeAgent returned successful response")
        else:
            print("\n❌ Test failed: CoreForgeAgent did not return successful response")
        
        return result
    
    except Exception as e:
        error_msg = f"Error testing CoreForgeAgent in isolation: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "content": error_msg
        }

if __name__ == "__main__":
    # Run the isolation test if this module is executed directly
    test_core_forge_isolation()
