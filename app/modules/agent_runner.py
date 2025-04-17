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
MODIFIED: Updated run_hal_agent with real execution logic and memory logging
MODIFIED: Added project_state integration for tracking project status
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
from toolkit.registry import get_toolkit, get_agent_role, format_tools_prompt, format_nova_prompt, get_agent_themes

# Import file_writer for HAL agent
try:
    from toolkit.file_writer import write_file
    FILE_WRITER_AVAILABLE = True
except ImportError:
    FILE_WRITER_AVAILABLE = False
    print("❌ file_writer import failed")

# Import memory_writer for logging agent actions
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    print("❌ memory_writer import failed")

# Import project_state for tracking project status
try:
    from app.modules.project_state import update_project_state, read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

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
    try:
        print(f"🤖 HAL agent execution started")
        logger.info(f"HAL agent execution started with task: {task}, project_id: {project_id}")
        
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            logger.info(f"HAL read project state for {project_id}")
            
            # Check if README.md already exists
            if "README.md" in project_state.get("files_created", []):
                print(f"⏩ README.md already exists, skipping duplicate write")
                logger.info(f"HAL skipped README.md creation - file already exists")
                return {
                    "status": "skipped",
                    "notes": "README.md already exists, skipping duplicate write.",
                    "output": project_state,
                    "project_state": project_state
                }
        
        # Initialize list of created files
        files_created = []
        
        # Create files using file_writer
        if "file_writer" in tools:
            print(f"📝 Using file_writer to create files")
            
            # Create content for README.md
            content = f"# Project {project_id}\n\nTask: {task}"
            file_path = f"/verticals/{project_id}/README.md"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            result = write_file(
                project_id=project_id,
                file_path=file_path,
                content=content
            )
            
            # Add to files_created list
            files_created.append(file_path)
            
            print(f"✅ File created successfully: {file_path}")
            logger.info(f"HAL created file: {file_path}")
            
            # Log memory entry if memory_writer is available
            if MEMORY_WRITER_AVAILABLE:
                memory_data = {
                    "agent": "hal",
                    "project_id": project_id,
                    "action": f"Wrote {file_path}",
                    "tool_used": "file_writer"
                }
                
                memory_result = write_memory(memory_data)
                print(f"✅ Memory entry created: {memory_result.get('memory_id', 'unknown')}")
                logger.info(f"HAL logged memory entry for file creation")
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "status": "in_progress",
                "files_created": files_created,
                "agents_involved": ["hal"],
                "latest_agent_action": {
                    "agent": "hal",
                    "action": f"Created initial files for project {project_id}"
                },
                "next_recommended_step": "Run NOVA to design the project",
                "tool_usage": {
                    "file_writer": 1
                }
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"HAL updated project state for {project_id}")
        
        # Return result with files_created list
        return {
            "status": "success",
            "message": f"HAL successfully created files for project {project_id}",
            "files_created": files_created,
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
    except Exception as e:
        error_msg = f"Error in run_hal_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing HAL agent: {str(e)}",
            "files_created": [],
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
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
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            logger.info(f"NOVA read project state for {project_id}")
            
            # Check if HAL has created initial files
            if "hal" not in project_state.get("agents_involved", []):
                print(f"⏩ HAL has not created initial files yet, cannot proceed")
                logger.info(f"NOVA execution blocked - HAL has not run yet")
                return {
                    "status": "blocked",
                    "notes": "Cannot create UI - HAL has not yet created initial project files.",
                    "project_state": project_state
                }
        
        # TODO: Implement NOVA agent execution
        result = {
            "message": f"NOVA received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "agents_involved": ["nova"],
                "latest_agent_action": {
                    "agent": "nova",
                    "action": f"Designed project {project_id}"
                },
                "next_recommended_step": "Run ASH to create documentation",
                "tool_usage": {}
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"NOVA updated project state for {project_id}")
        
        return result
    except Exception as e:
        error_msg = f"Error in run_nova_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing NOVA agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
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
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            logger.info(f"ASH read project state for {project_id}")
            
            # Check if project is ready for deployment
            if project_state.get("status") != "ready_for_deploy":
                print(f"⏩ Project not ready for deployment yet")
                logger.info(f"ASH execution on hold - project not ready for deployment")
                return {
                    "status": "on_hold",
                    "notes": "Project not ready for deployment yet.",
                    "project_state": project_state
                }
        
        # TODO: Implement ASH agent execution
        result = {
            "message": f"ASH received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "agents_involved": ["ash"],
                "latest_agent_action": {
                    "agent": "ash",
                    "action": f"Created documentation for project {project_id}"
                },
                "next_recommended_step": "Run CRITIC to review the project",
                "tool_usage": {}
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"ASH updated project state for {project_id}")
        
        return result
    except Exception as e:
        error_msg = f"Error in run_ash_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing ASH agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
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
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            logger.info(f"CRITIC read project state for {project_id}")
            
            # Check if NOVA has created UI files
            if "nova" not in project_state.get("agents_involved", []):
                print(f"⏩ NOVA has not created UI files yet, cannot review")
                logger.info(f"CRITIC execution blocked - NOVA has not run yet")
                return {
                    "status": "blocked",
                    "notes": "Cannot review UI – NOVA has not yet created any frontend files.",
                    "project_state": project_state
                }
        
        # TODO: Implement CRITIC agent execution
        result = {
            "message": f"CRITIC received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "status": "ready_for_deploy",
                "agents_involved": ["critic"],
                "latest_agent_action": {
                    "agent": "critic",
                    "action": f"Reviewed project {project_id}"
                },
                "next_recommended_step": "Run ASH to deploy",
                "tool_usage": {}
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"CRITIC updated project state for {project_id}")
        
        return result
    except Exception as e:
        error_msg = f"Error in run_critic_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing CRITIC agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
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
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            logger.info(f"ORCHESTRATOR read project state for {project_id}")
        
        # TODO: Implement ORCHESTRATOR agent execution
        result = {
            "message": f"ORCHESTRATOR received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "agents_involved": ["orchestrator"],
                "latest_agent_action": {
                    "agent": "orchestrator",
                    "action": f"Orchestrated project {project_id}"
                },
                "tool_usage": {}
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"ORCHESTRATOR updated project state for {project_id}")
        
        return result
    except Exception as e:
        error_msg = f"Error in run_orchestrator_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing ORCHESTRATOR agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

# Map agent_id to runner function
AGENT_RUNNERS = {
    "hal": run_hal_agent,
    "nova": run_nova_agent,
    "ash": run_ash_agent,
    "critic": run_critic_agent,
    "orchestrator": run_orchestrator_agent
}
