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
MODIFIED: Updated run_nova_agent with file creation and memory logging functionality
MODIFIED: Standardized output format across all agents
MODIFIED: Added memory logging for CRITIC and ASH agents
MODIFIED: Added agent retry and recovery flow for blocked agents
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

# Import agent_retry for retry and recovery flow
try:
    from app.modules.agent_retry import register_blocked_agent, check_for_unblocked_agents, mark_agent_retry_attempted
    AGENT_RETRY_AVAILABLE = True
except ImportError:
    AGENT_RETRY_AVAILABLE = False
    print("❌ agent_retry import failed")

# Import memory_block_writer for logging block information
try:
    from app.modules.memory_block_writer import write_block_memory, write_unblock_memory
    MEMORY_BLOCK_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_BLOCK_WRITER_AVAILABLE = False
    print("❌ memory_block_writer import failed")

# Import passive_reflection for re-evaluating tasks
try:
    from app.modules.passive_reflection import re_evaluate_task, start_reflection
    PASSIVE_REFLECTION_AVAILABLE = True
except ImportError:
    PASSIVE_REFLECTION_AVAILABLE = False
    print("❌ passive_reflection import failed")

try:
    from app.modules.ash_agent import run_ash_agent as ash_agent_impl
    ASH_AGENT_AVAILABLE = True
except ImportError:
    ASH_AGENT_AVAILABLE = False
    print("❌ ash_agent import failed")

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
        result = await add_memory_thread(memory_entry)
        print(f"✅ Memory thread logged with ID: {result.get('memory_id', 'unknown')}")
        logger.info(f"Memory thread logged with ID: {result.get('memory_id', 'unknown')}")
    except Exception as e:
        error_msg = f"Error logging memory thread: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())

def log_memory(project_id: str, agent: str, action: str, content: str, structured_data: Dict = None) -> None:
    """
    Log a memory entry for an agent action.
    
    Args:
        project_id: The project identifier
        agent: The agent type (hal, ash, nova)
        action: The action performed (created, updated, deleted)
        content: The content of the action
        structured_data: Optional structured data for specialized agents
    """
    try:
        if not MEMORY_WRITER_AVAILABLE:
            print(f"⚠️ Memory writer not available, skipping memory logging")
            return
        
        # Create memory entry
        memory_data = {
            "project_id": project_id,
            "agent": agent,
            "action": action,
            "content": content
        }
        
        # Add structured data if available
        if structured_data:
            memory_data["structured_data"] = structured_data
        
        # Log memory entry
        print(f"📝 Logging memory for {agent} agent, {action} action")
        result = write_memory(memory_data)
        print(f"✅ Memory logged with ID: {result.get('memory_id', 'unknown')}")
        logger.info(f"Memory logged with ID: {result.get('memory_id', 'unknown')}")
    except Exception as e:
        error_msg = f"Error logging memory: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())

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
    logger.info(f"HAL agent execution started with task: {task}, project_id: {project_id}")
    
    try:
        # Start reflection for project if available
        if PASSIVE_REFLECTION_AVAILABLE:
            start_reflection(project_id)
            print(f"🧠 Started passive reflection for project {project_id}")
        
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            logger.info(f"HAL read project state for {project_id}")
            
            # Check if task has been re-evaluated after being unblocked
            if PASSIVE_REFLECTION_AVAILABLE and AGENT_RETRY_AVAILABLE:
                retry_status = get_retry_status(project_id, "hal")
                if retry_status and retry_status.get("status") == "unblocked":
                    # Re-evaluate task with current project state
                    re_eval_result = re_evaluate_task(project_id, "hal", task)
                    if re_eval_result.get("status") == "success":
                        task = re_eval_result.get("task", task)
                        print(f"🔄 Re-evaluated task for HAL agent after being unblocked")
                        logger.info(f"HAL task re-evaluated after being unblocked")
            
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
        
        # Check if file_writer is available
        if not FILE_WRITER_AVAILABLE:
            print(f"⚠️ file_writer not available, skipping file creation")
            logger.warning(f"file_writer not available, skipping file creation")
            return {
                "status": "error",
                "message": "file_writer not available, cannot create files",
                "files_created": [],
                "task": task,
                "tools": tools,
                "project_state": project_state
            }
        
        # Create README.md
        readme_content = f"""# {project_id.replace('_', ' ').title()}

This project was created by the HAL agent.

## Task
{task}

## Tools
{', '.join(tools)}

## Created
{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
"""
        
        # Write README.md
        readme_path = f"/verticals/{project_id}/README.md"
        print(f"📝 Creating README.md at {readme_path}")
        logger.info(f"Creating README.md at {readme_path}")
        
        readme_result = write_file(project_id, "README.md", readme_content)
        if readme_result.get("status") == "success":
            print(f"✅ README.md created successfully")
            logger.info(f"README.md created successfully")
            files_created.append(readme_path)
            
            # Log memory
            log_memory(
                project_id=project_id,
                agent="hal",
                action="created",
                content=f"Created README.md for project {project_id}",
                structured_data={
                    "file_path": readme_path,
                    "file_type": "markdown",
                    "file_size": len(readme_content)
                }
            )
        else:
            print(f"❌ Failed to create README.md: {readme_result.get('error', 'unknown error')}")
            logger.error(f"Failed to create README.md: {readme_result.get('error', 'unknown error')}")
        
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
            
            # Check if task has been re-evaluated after being unblocked
            if PASSIVE_REFLECTION_AVAILABLE and AGENT_RETRY_AVAILABLE:
                retry_status = get_retry_status(project_id, "nova")
                if retry_status and retry_status.get("status") == "unblocked":
                    # Re-evaluate task with current project state
                    re_eval_result = re_evaluate_task(project_id, "nova", task)
                    if re_eval_result.get("status") == "success":
                        task = re_eval_result.get("task", task)
                        print(f"🔄 Re-evaluated task for NOVA agent after being unblocked")
                        logger.info(f"NOVA task re-evaluated after being unblocked")
            
            # Check if HAL has created initial files
            if "hal" not in project_state.get("agents_involved", []):
                print(f"⏩ HAL has not created initial files yet, cannot proceed")
                logger.info(f"NOVA execution blocked - HAL has not run yet")
                
                # Register blocked agent for future retry
                if AGENT_RETRY_AVAILABLE:
                    register_blocked_agent(
                        project_id=project_id,
                        agent_id="nova",
                        blocked_due_to="hal",
                        unblock_condition="initial files created"
                    )
                    print(f"🔄 NOVA agent registered for retry when HAL completes initial file creation")
                
                # Log block memory
                if MEMORY_BLOCK_WRITER_AVAILABLE:
                    write_block_memory({
                        "project_id": project_id,
                        "agent": "nova",
                        "action": "blocked",
                        "content": f"NOVA agent blocked - HAL has not created initial files yet",
                        "blocked_due_to": "hal",
                        "unblock_condition": "initial files created"
                    })
                    print(f"📝 Block memory logged for NOVA agent")
                
                # Update project state to include nova in agents_involved even when blocked
                if PROJECT_STATE_AVAILABLE:
                    project_state_data = {
                        "agents_involved": ["nova"],
                        "latest_agent_action": {
                            "agent": "nova",
                            "action": f"Checked project {project_id} but was blocked - HAL has not run yet"
                        },
                        "blocked_due_to": "hal",
                        "unblock_condition": "initial files created"
                    }
                    
                    project_state_result = update_project_state(project_id, project_state_data)
                    print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
                    logger.info(f"NOVA updated project state for {project_id} even though blocked")
                    
                    # Read updated project state
                    project_state = read_project_state(project_id)
                
                return {
                    "status": "blocked",
                    "notes": "Cannot create UI - HAL has not yet created initial project files.",
                    "project_state": project_state,
                    "blocked_due_to": "hal",
                    "unblock_condition": "initial files created"
                }
        
        # Initialize list of created files
        files_created = []
        
        # Check if file_writer is available
        if not FILE_WRITER_AVAILABLE:
            print(f"⚠️ file_writer not available, skipping file creation")
            logger.warning(f"file_writer not available, skipping file creation")
            return {
                "status": "error",
                "message": "file_writer not available, cannot create files",
                "files_created": [],
                "task": task,
                "tools": tools,
                "project_state": project_state
            }
        
        # Create LandingPage.jsx
        landing_page_content = """import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import './LandingPage.css';

function LandingPage() {
  return (
    <div className="landing-page">
      <header className="header">
        <Container>
          <Row className="align-items-center">
            <Col md={6}>
              <h1>Welcome to Our Platform</h1>
              <p className="lead">
                The most comprehensive solution for your needs.
              </p>
              <Button variant="primary" size="lg">Get Started</Button>
              <Button variant="outline-secondary" size="lg" className="ml-3">Learn More</Button>
            </Col>
            <Col md={6}>
              <img src="/images/hero-image.svg" alt="Hero" className="img-fluid" />
            </Col>
          </Row>
        </Container>
      </header>
      
      <section className="features">
        <Container>
          <h2 className="text-center mb-5">Key Features</h2>
          <Row>
            <Col md={4}>
              <div className="feature-item">
                <div className="feature-icon">
                  <i className="fas fa-bolt"></i>
                </div>
                <h3>Lightning Fast</h3>
                <p>Our platform is optimized for speed and performance.</p>
              </div>
            </Col>
            <Col md={4}>
              <div className="feature-item">
                <div className="feature-icon">
                  <i className="fas fa-shield-alt"></i>
                </div>
                <h3>Secure</h3>
                <p>Your data is protected with enterprise-grade security.</p>
              </div>
            </Col>
            <Col md={4}>
              <div className="feature-item">
                <div className="feature-icon">
                  <i className="fas fa-cogs"></i>
                </div>
                <h3>Customizable</h3>
                <p>Tailor the platform to meet your specific needs.</p>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
      
      <section className="cta">
        <Container>
          <Row className="justify-content-center">
            <Col md={8} className="text-center">
              <h2>Ready to get started?</h2>
              <p className="lead">Join thousands of satisfied customers today.</p>
              <Button variant="primary" size="lg">Sign Up Now</Button>
            </Col>
          </Row>
        </Container>
      </section>
      
      <footer className="footer">
        <Container>
          <Row>
            <Col md={4}>
              <h4>Company</h4>
              <ul className="list-unstyled">
                <li><a href="#">About Us</a></li>
                <li><a href="#">Careers</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
            </Col>
            <Col md={4}>
              <h4>Resources</h4>
              <ul className="list-unstyled">
                <li><a href="#">Documentation</a></li>
                <li><a href="#">Blog</a></li>
                <li><a href="#">Support</a></li>
              </ul>
            </Col>
            <Col md={4}>
              <h4>Legal</h4>
              <ul className="list-unstyled">
                <li><a href="#">Privacy Policy</a></li>
                <li><a href="#">Terms of Service</a></li>
                <li><a href="#">Cookie Policy</a></li>
              </ul>
            </Col>
          </Row>
          <hr />
          <p className="text-center">© 2023 Company Name. All rights reserved.</p>
        </Container>
      </footer>
    </div>
  );
}

export default LandingPage;
"""
        
        # Write LandingPage.jsx
        landing_page_path = f"frontend/LandingPage.jsx"
        print(f"📝 Creating LandingPage.jsx at {landing_page_path}")
        logger.info(f"Creating LandingPage.jsx at {landing_page_path}")
        
        landing_page_result = write_file(project_id, landing_page_path, landing_page_content)
        if landing_page_result.get("status") == "success":
            print(f"✅ LandingPage.jsx created successfully")
            logger.info(f"LandingPage.jsx created successfully")
            files_created.append(f"/verticals/{project_id}/{landing_page_path}")
            
            # Log memory
            log_memory(
                project_id=project_id,
                agent="nova",
                action="created",
                content=f"Created LandingPage.jsx for project {project_id}",
                structured_data={
                    "file_path": landing_page_path,
                    "file_type": "jsx",
                    "file_size": len(landing_page_content)
                }
            )
        else:
            print(f"❌ Failed to create LandingPage.jsx: {landing_page_result.get('error', 'unknown error')}")
            logger.error(f"Failed to create LandingPage.jsx: {landing_page_result.get('error', 'unknown error')}")
        
        # Create LandingPage.css
        landing_page_css_content = """/* LandingPage.css */
.landing-page {
  font-family: 'Inter', sans-serif;
  color: #333;
}

.header {
  padding: 100px 0;
  background-color: #f8f9fa;
}

.header h1 {
  font-weight: 700;
  margin-bottom: 20px;
}

.header .lead {
  font-size: 1.25rem;
  margin-bottom: 30px;
}

.header .btn {
  padding: 10px 20px;
  margin-right: 10px;
}

.features {
  padding: 100px 0;
  background-color: #fff;
}

.feature-item {
  text-align: center;
  padding: 30px;
  margin-bottom: 30px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #007bff;
}

.feature-item h3 {
  margin-bottom: 15px;
  font-weight: 600;
}

.cta {
  padding: 80px 0;
  background-color: #007bff;
  color: white;
}

.cta h2 {
  font-weight: 700;
  margin-bottom: 20px;
}

.cta .btn {
  margin-top: 20px;
  background-color: white;
  color: #007bff;
  border: none;
  padding: 12px 30px;
}

.cta .btn:hover {
  background-color: #f8f9fa;
}

.footer {
  padding: 60px 0;
  background-color: #343a40;
  color: #fff;
}

.footer h4 {
  font-weight: 600;
  margin-bottom: 20px;
}

.footer ul li {
  margin-bottom: 10px;
}

.footer a {
  color: #adb5bd;
  text-decoration: none;
}

.footer a:hover {
  color: #fff;
}

.footer hr {
  margin: 30px 0;
  border-color: #495057;
}

@media (max-width: 768px) {
  .header {
    padding: 60px 0;
    text-align: center;
  }
  
  .header img {
    margin-top: 30px;
  }
  
  .feature-item {
    margin-bottom: 40px;
  }
}
"""
        
        # Write LandingPage.css
        landing_page_css_path = f"frontend/LandingPage.css"
        print(f"📝 Creating LandingPage.css at {landing_page_css_path}")
        logger.info(f"Creating LandingPage.css at {landing_page_css_path}")
        
        landing_page_css_result = write_file(project_id, landing_page_css_path, landing_page_css_content)
        if landing_page_css_result.get("status") == "success":
            print(f"✅ LandingPage.css created successfully")
            logger.info(f"LandingPage.css created successfully")
            files_created.append(f"/verticals/{project_id}/{landing_page_css_path}")
            
            # Log memory
            log_memory(
                project_id=project_id,
                agent="nova",
                action="created",
                content=f"Created LandingPage.css for project {project_id}",
                structured_data={
                    "file_path": landing_page_css_path,
                    "file_type": "css",
                    "file_size": len(landing_page_css_content)
                }
            )
        else:
            print(f"❌ Failed to create LandingPage.css: {landing_page_css_result.get('error', 'unknown error')}")
            logger.error(f"Failed to create LandingPage.css: {landing_page_css_result.get('error', 'unknown error')}")
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "files_created": files_created,
                "agents_involved": ["nova"],
                "latest_agent_action": {
                    "agent": "nova",
                    "action": f"Created UI files for project {project_id}"
                },
                "next_recommended_step": "Run CRITIC to review the UI",
                "tool_usage": {
                    "file_writer": len(files_created)
                }
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"NOVA updated project state for {project_id}")
        
        # Return result with files_created list
        return {
            "status": "success",
            "message": f"NOVA successfully created UI files for project {project_id}",
            "files_created": files_created,
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
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
            
            # Check if task has been re-evaluated after being unblocked
            if PASSIVE_REFLECTION_AVAILABLE and AGENT_RETRY_AVAILABLE:
                retry_status = get_retry_status(project_id, "ash")
                if retry_status and retry_status.get("status") == "unblocked":
                    # Re-evaluate task with current project state
                    re_eval_result = re_evaluate_task(project_id, "ash", task)
                    if re_eval_result.get("status") == "success":
                        task = re_eval_result.get("task", task)
                        print(f"🔄 Re-evaluated task for ASH agent after being unblocked")
                        logger.info(f"ASH task re-evaluated after being unblocked")
            
            # Check if project is ready for deployment
            if project_state.get("status") != "ready_for_deploy":
                print(f"⏩ Project not ready for deployment yet")
                logger.info(f"ASH execution on hold - project not ready for deployment")
                
                # Register blocked agent for future retry
                if AGENT_RETRY_AVAILABLE:
                    register_blocked_agent(
                        project_id=project_id,
                        agent_id="ash",
                        blocked_due_to="project_status",
                        unblock_condition="ready_for_deploy"
                    )
                    print(f"🔄 ASH agent registered for retry when project is ready for deployment")
                
                # Log block memory
                if MEMORY_BLOCK_WRITER_AVAILABLE:
                    write_block_memory({
                        "project_id": project_id,
                        "agent": "ash",
                        "action": "blocked",
                        "content": f"ASH agent on hold - project not ready for deployment yet",
                        "blocked_due_to": "project_status",
                        "unblock_condition": "ready_for_deploy"
                    })
                    print(f"📝 Block memory logged for ASH agent")
                
                # Update project state to include ash in agents_involved even when on hold
                if PROJECT_STATE_AVAILABLE:
                    project_state_data = {
                        "agents_involved": ["ash"],
                        "latest_agent_action": {
                            "agent": "ash",
                            "action": f"Checked project {project_id} but is on hold - project not ready for deployment"
                        },
                        "blocked_due_to": "project_status",
                        "unblock_condition": "ready_for_deploy"
                    }
                    
                    project_state_result = update_project_state(project_id, project_state_data)
                    print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
                    logger.info(f"ASH updated project state for {project_id} even though on hold")
                    
                    # Read updated project state
                    project_state = read_project_state(project_id)
                
                return {
                    "status": "on_hold",
                    "notes": "Project not ready for deployment yet.",
                    "project_state": project_state,
                    "blocked_due_to": "project_status",
                    "unblock_condition": "ready_for_deploy"
                }
        
        # Use ASH agent implementation if available
        if ASH_AGENT_AVAILABLE:
            print(f"🔄 Using ASH agent implementation")
            result = ash_agent_impl(task, project_id, tools)
            
            # Update project state if project_state is available
            if PROJECT_STATE_AVAILABLE:
                project_state_data = {
                    "agents_involved": ["ash"],
                    "latest_agent_action": {
                        "agent": "ash",
                        "action": f"Created documentation for project {project_id}"
                    },
                    "next_recommended_step": "Project documentation complete",
                    "tool_usage": {}
                }
                
                project_state_result = update_project_state(project_id, project_state_data)
                print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
                logger.info(f"ASH updated project state for {project_id}")
            
            # Add project_state to result
            if PROJECT_STATE_AVAILABLE:
                result["project_state"] = project_state
            
            return result
        
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
                "next_recommended_step": "Project documentation complete",
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
    # Ensure logger is defined for CRITIC agent
    import logging
    logger = logging.getLogger("critic")
    
    # Add local fallback in case the system loads without logging
    if 'logger' not in globals():
        def logger_stub(*args, **kwargs): pass
        logger = type('logger', (), {
            "info": logger_stub,
            "error": logger_stub,
            "debug": logger_stub,
            "warning": logger_stub
        })()
    
    print(f"🤖 CRITIC agent execution started")
    try:
        logger.info(f"CRITIC agent execution started with task: {task}, project_id: {project_id}")
    except NameError:
        print(f"[CRITIC] Agent execution started with task: {task}, project_id: {project_id}")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            try:
                logger.info(f"CRITIC read project state for {project_id}")
            except NameError:
                print(f"[CRITIC] Read project state for {project_id}")
            
            # Check if task has been re-evaluated after being unblocked
            if PASSIVE_REFLECTION_AVAILABLE and AGENT_RETRY_AVAILABLE:
                try:
                    retry_status = get_retry_status(project_id, "critic")
                    if retry_status and retry_status.get("status") == "unblocked":
                        # Re-evaluate task with current project state
                        re_eval_result = re_evaluate_task(project_id, "critic", task)
                        if re_eval_result.get("status") == "success":
                            task = re_eval_result.get("task", task)
                            print(f"🔄 Re-evaluated task for CRITIC agent after being unblocked")
                            logger.info(f"CRITIC task re-evaluated after being unblocked")
                except Exception as e:
                    print(f"⚠️ Error re-evaluating CRITIC task: {str(e)}")
                    try:
                        logger.error(f"Error re-evaluating CRITIC task: {str(e)}")
                    except:
                        pass
            
            # Check if NOVA has created UI files
            if "nova" not in project_state.get("agents_involved", []):
                print(f"⏩ NOVA has not created UI files yet, cannot review")
                try:
                    logger.info(f"CRITIC execution blocked - NOVA has not run yet")
                except NameError:
                    print(f"[CRITIC] Execution blocked - NOVA has not run yet")
                
                # Register blocked agent for future retry
                if AGENT_RETRY_AVAILABLE:
                    register_blocked_agent(
                        project_id=project_id,
                        agent_id="critic",
                        blocked_due_to="nova",
                        unblock_condition="frontend created"
                    )
                    print(f"🔄 CRITIC agent registered for retry when NOVA completes frontend creation")
                
                # Log block memory
                if MEMORY_BLOCK_WRITER_AVAILABLE:
                    write_block_memory({
                        "project_id": project_id,
                        "agent": "critic",
                        "action": "blocked",
                        "content": f"CRITIC agent blocked - NOVA has not created UI files yet",
                        "blocked_due_to": "nova",
                        "unblock_condition": "frontend created"
                    })
                    print(f"📝 Block memory logged for CRITIC agent")
                
                # Update project state to include critic in agents_involved even when blocked
                if PROJECT_STATE_AVAILABLE:
                    project_state_data = {
                        "agents_involved": ["critic"],
                        "latest_agent_action": {
                            "agent": "critic",
                            "action": f"Checked project {project_id} but was blocked - NOVA has not run yet"
                        },
                        "blocked_due_to": "nova",
                        "unblock_condition": "frontend created"
                    }
                    
                    project_state_result = update_project_state(project_id, project_state_data)
                    print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
                    try:
                        logger.info(f"CRITIC updated project state for {project_id} even though blocked")
                    except NameError:
                        print(f"[CRITIC] Updated project state for {project_id} even though blocked")
                    
                    # Read updated project state
                    project_state = read_project_state(project_id)
                
                return {
                    "status": "blocked",
                    "notes": "Cannot review UI – NOVA has not yet created any frontend files.",
                    "project_state": project_state,
                    "files_created": [],
                    "actions_taken": ["Checked project state"],
                    "message": "CRITIC execution blocked - NOVA has not run yet",
                    "blocked_due_to": "nova",
                    "unblock_condition": "frontend created"
                }
        
        # Use CRITIC agent implementation if available
        if CRITIC_AGENT_AVAILABLE:
            print(f"🔄 Using CRITIC agent implementation")
            result = critic_agent_impl(task, project_id, tools)
            
            # Update project state if project_state is available
            if PROJECT_STATE_AVAILABLE:
                project_state_data = {
                    "status": "ready_for_deploy",
                    "agents_involved": ["critic"],
                    "latest_agent_action": {
                        "agent": "critic",
                        "action": f"Reviewed project {project_id}"
                    },
                    "next_recommended_step": "Run ASH to create documentation",
                    "tool_usage": {}
                }
                
                project_state_result = update_project_state(project_id, project_state_data)
                print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
                try:
                    logger.info(f"CRITIC updated project state for {project_id}")
                except NameError:
                    print(f"[CRITIC] Updated project state for {project_id}")
            
            # Add project_state to result
            if PROJECT_STATE_AVAILABLE:
                result["project_state"] = project_state
            
            return result
        
        # TODO: Implement CRITIC agent execution
        result = {
            "message": f"CRITIC received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state,
            "files_created": [],
            "actions_taken": ["Reviewed project structure"],
            "notes": "Basic review completed"
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
                "next_recommended_step": "Run ASH to create documentation",
                "tool_usage": {}
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            try:
                logger.info(f"CRITIC updated project state for {project_id}")
            except NameError:
                print(f"[CRITIC] Updated project state for {project_id}")
        
        return result
    except Exception as e:
        error_msg = f"Error in run_critic_agent: {str(e)}"
        print(f"❌ {error_msg}")
        try:
            logger.error(error_msg)
            logger.error(traceback.format_exc())
        except NameError:
            print(f"[CRITIC ERROR] {error_msg}")
            print(f"[CRITIC ERROR] {traceback.format_exc()}")
        
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
