"""
NOVA Agent Module

This module provides the consolidated implementation for the NOVA agent, which is responsible for
UI component building in React/HTML. It handles the generation of UI components and
interfaces with the project state system to track progress.

The NOVA agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
"""

import logging
import traceback
from typing import Dict, List, Any, Optional
import time

# Import schema
from app.schemas.nova_schema import NovaUIRequest, NovaUIResult, NovaUIResultFallback

# Import agent_sdk
try:
    from agent_sdk.agent_sdk import AgentSDK
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False
    print("❌ agent_sdk import failed")

# Import memory_writer for logging agent actions
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    print("❌ memory_writer import failed")

# Import project_state for tracking project status
try:
    from app.modules.project_state import update_project_state, read_project_state, increment_loop_count
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    print("❌ system_log import failed")

# Configure logging
logger = logging.getLogger("agents.nova")

class NovaAgent:
    """
    NOVA Agent for UI component building (React/HTML)
    
    This agent is responsible for:
    1. Creating UI components based on project requirements
    2. Generating React/HTML code
    3. Updating project state with created UI files
    """
    
    def __init__(self):
        """Initialize the NOVA agent."""
        self.name = "NOVA"
        self.description = "UI component builder (React/HTML)"
        self.tools = ["build_ui", "generate_component"]
        
        # Initialize Agent SDK if available
        if AGENT_SDK_AVAILABLE:
            self.sdk = AgentSDK(agent_name="nova")
    
    def run_agent(self, request: NovaUIRequest) -> NovaUIResult:
        """
        Run the NOVA agent with the given request.
        
        Args:
            request: The NovaUIRequest containing task, project_id, and tools
            
        Returns:
            NovaUIResult containing the response and metadata
        """
        try:
            logger.info(f"Running NOVA agent with task: {request.task}, project_id: {request.project_id}")
            print(f"🚀 NOVA agent execution started")
            print(f"📋 Task: {request.task}")
            print(f"🆔 Project ID: {request.project_id}")
            print(f"🧰 Tools: {request.tools}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", f"Starting execution with task: {request.task}", request.project_id)
            
            # Read current project state - avoid generating a default object, use what's already written by HAL
            project_state = {}
            if PROJECT_STATE_AVAILABLE:
                project_state = read_project_state(request.project_id)
                print(f"📊 Project state read for {request.project_id}")
                print(f"📊 Initial state: loop_count={project_state.get('loop_count')}, last_agent={project_state.get('last_completed_agent')}")
                print(f"📊 Initial completed_steps: {project_state.get('completed_steps', [])}")
                print(f"📊 Initial files_created: {project_state.get('files_created', [])}")
                
                if "hal" not in project_state.get("agents_involved", []):
                    print("⏩ HAL has not created initial files yet, cannot proceed")
                    if SYSTEM_LOG_AVAILABLE:
                        log_event("NOVA", "Blocked: HAL has not yet run", request.project_id, {"blocking_condition": "hal_not_run"})
                    
                    # Return blocked status
                    return NovaUIResult(
                        status="blocked",
                        message="Cannot proceed — HAL has not yet initialized the project.",
                        project_id=request.project_id,
                        files_created=[],
                        next_recommended_step="Run HAL to initialize the project",
                        memory_tag=f"nova_ui_{request.project_id}"
                    )

            # Generate UI components based on the task
            ui_components = self._generate_ui_components(request.task, request.project_id)
            
            # Simulate UI file generation
            design_action = f"Created core UI components for {request.project_id}"
            ui_files_created = [
                "src/components/Dashboard.jsx",
                "src/components/LoginForm.jsx"
            ]

            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", f"Design action: {design_action}", request.project_id)

            if MEMORY_WRITER_AVAILABLE:
                memory_data = {
                    "agent": "nova",
                    "project_id": request.project_id,
                    "action": design_action,
                    "tool_used": "memory_writer",
                    "design_notes": "NOVA designed the core UI structure for the app.",
                    "ui_components": ui_components
                }
                write_memory(memory_data)
                print("✅ Memory logged for NOVA UI generation")

            if PROJECT_STATE_AVAILABLE:
                # 1. Increment loop count
                increment_result = increment_loop_count(request.project_id, "nova")
                if increment_result.get("status") == "success":
                    print("✅ Loop count incremented and agent set to nova")
                else:
                    print(f"❌ Loop count increment failed: {increment_result}")

                # 2. Read current memory
                state = read_project_state(request.project_id)
                print("📥 Current project state (before update):", state)

                # 3. Merge UI files and update keys
                state["files_created"] = state.get("files_created", []) + ui_files_created
                state["completed_steps"] = state.get("completed_steps", []) + ["nova"]
                state["last_completed_agent"] = "nova"
                state["next_recommended_step"] = "Run CRITIC to review NOVA's UI output"

                # 4. Write memory
                update_result = update_project_state(request.project_id, state)

                if update_result.get("status") != "success":
                    print("❌ Failed to persist NOVA update:", update_result)
                else:
                    print("✅ NOVA memory successfully persisted")
                    print("📤 Files created:", ui_files_created)
                    print("➡️ Next step:", state["next_recommended_step"])

                # 5. Double-check final state
                new_state = read_project_state(request.project_id)
                print("🧠 Final memory snapshot:", new_state)

            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", "Execution complete", request.project_id, {
                    "files_created": ui_files_created
                })

            # Create successful result
            return NovaUIResult(
                status="success",
                message=f"NOVA completed task for {request.project_id}",
                project_id=request.project_id,
                files_created=ui_files_created,
                ui_components=ui_components,
                next_recommended_step="Run CRITIC to review NOVA's UI output",
                memory_tag=f"nova_ui_{request.project_id}"
            )
            
        except Exception as e:
            error_msg = f"Error running NOVA agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", f"Error: {str(e)}", request.project_id)
            
            # Return error response
            return NovaUIResult(
                status="error",
                message=error_msg,
                project_id=request.project_id,
                files_created=[],
                next_recommended_step="Retry NOVA agent execution",
                memory_tag=f"nova_ui_{request.project_id}"
            )
    
    def _generate_ui_components(self, task: str, project_id: str) -> Dict[str, Any]:
        """
        Generate UI components based on the task.
        
        Args:
            task: The task description
            project_id: The project identifier
            
        Returns:
            Dict containing the generated UI components
        """
        # In a real implementation, this would analyze the task and generate appropriate UI components
        # For this implementation, we'll return mock components
        
        return {
            "dashboard": {
                "type": "component",
                "name": "Dashboard",
                "file_path": "src/components/Dashboard.jsx",
                "code": """
import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';

const Dashboard = ({ user, stats }) => {
  return (
    <Container className="dashboard-container">
      <Row className="header-row">
        <Col>
          <h1>Welcome, {user.name}</h1>
          <p>Here's your project overview</p>
        </Col>
      </Row>
      <Row className="stats-row">
        <Col md={4}>
          <Card>
            <Card.Body>
              <Card.Title>Projects</Card.Title>
              <Card.Text>{stats.projects}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Body>
              <Card.Title>Tasks</Card.Title>
              <Card.Text>{stats.tasks}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Body>
              <Card.Title>Completed</Card.Title>
              <Card.Text>{stats.completed}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
"""
            },
            "login_form": {
                "type": "component",
                "name": "LoginForm",
                "file_path": "src/components/LoginForm.jsx",
                "code": """
import React, { useState } from 'react';
import { Form, Button, Alert } from 'react-bootstrap';

const LoginForm = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }
    
    setError('');
    onLogin({ email, password });
  };
  
  return (
    <div className="login-form-container">
      <h2>Login to Your Account</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group>
          <Form.Label>Email</Form.Label>
          <Form.Control
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
          />
        </Form.Group>
        <Button variant="primary" type="submit" className="mt-3">
          Login
        </Button>
      </Form>
    </div>
  );
};

export default LoginForm;
"""
            }
        }

# Create an instance of the agent
nova_agent = NovaAgent()

def run_nova_agent(task: str, project_id: str, tools: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run the NOVA agent with the given task.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Create a request object
    request = NovaUIRequest(
        task=task,
        project_id=project_id,
        tools=tools if tools is not None else ["build_ui", "generate_component"]
    )
    
    # Run the agent
    result = nova_agent.run_agent(request)
    
    # Convert to dict for backward compatibility
    return result.dict()
