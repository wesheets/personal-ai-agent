"""
NOVA Agent Module

This module provides the consolidated implementation for the NOVA agent, which is responsible for
UI component building in React/HTML. It handles the generation of UI components and
interfaces with the project state system to track progress.

The NOVA agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
"""

import logging
import traceback
import json
import time
from typing import Dict, List, Any, Optional

# Import Agent SDK
from agent_sdk.agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.nova")

# Import memory functions if available
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    logger.warning("⚠️ memory_writer import failed")
    
    # Mock implementation for testing
    def write_memory(memory_data):
        logger.info(f"Mock memory write: {memory_data}")
        return {"status": "success", "message": "Mock memory write successful"}

# Import project_state for tracking project status
try:
    from app.modules.project_state import update_project_state, read_project_state, increment_loop_count
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    logger.warning("⚠️ project_state import failed")
    
    # Mock implementations for testing
    def read_project_state(project_id):
        logger.info(f"Mock read_project_state for {project_id}")
        return {"loop_count": 0, "agents_involved": ["hal"], "files_created": []}
    
    def update_project_state(project_id, state):
        logger.info(f"Mock update_project_state for {project_id}: {state}")
        return {"status": "success"}
    
    def increment_loop_count(project_id, agent):
        logger.info(f"Mock increment_loop_count for {project_id}, agent: {agent}")
        return {"status": "success"}

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    logger.warning("⚠️ system_log import failed")
    
    # Mock implementation for testing
    def log_event(agent, message, project_id, data=None):
        logger.info(f"Mock log_event: {agent}, {message}, {project_id}, {data}")

class NovaAgent(Agent):
    """
    NOVA Agent for UI component building (React/HTML)
    
    This agent is responsible for:
    1. Creating UI components based on project requirements
    2. Generating React/HTML code
    3. Updating project state with created UI files
    4. A/B testing UI designs
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the NOVA agent with SDK compliance."""
        # Define agent properties
        name = "Nova"
        role = "UI Generator"
        tools_list = tools or ["design_ui", "ab_test", "generate_component", "build_ui"]
        permissions = ["read_project_state", "write_memory", "create_files"]
        description = "UI component builder that generates React/HTML code based on project requirements, creates visual designs, and performs A/B testing."
        tone_profile = {
            "creative": "high",
            "positive": "high",
            "experimental": "medium",
            "technical": "high",
            "visual": "high"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/nova/input_schema.json"
        output_schema_path = "app/schemas/nova/output_schema.json"
        
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
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        return validate_schema(data, self.input_schema_path)
    
    async def execute(self, task: str, project_id: str, tools: List[str] = None, ui_requirements: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            task: The task to execute
            project_id: The project identifier
            tools: List of tools to use (optional)
            ui_requirements: Specific UI requirements (optional)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            logger.info(f"NovaAgent.execute called with task: {task}, project_id: {project_id}")
            
            # Prepare input data for validation
            input_data = {
                "task": task,
                "project_id": project_id,
                "tools": tools or self.tools
            }
            
            if ui_requirements:
                input_data["ui_requirements"] = ui_requirements
            
            # Add any additional kwargs to input data
            input_data.update(kwargs)
            
            # Validate input
            if not self.validate_input(input_data):
                logger.warning(f"Input validation failed for task: {task}")
            
            # Log execution start
            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", f"Starting execution with task: {task}", project_id)
            
            # Read current project state
            project_state = {}
            if PROJECT_STATE_AVAILABLE:
                project_state = read_project_state(project_id)
                logger.info(f"Project state read for {project_id}")
                
                if "hal" not in project_state.get("agents_involved", []):
                    logger.warning("HAL has not created initial files yet, cannot proceed")
                    if SYSTEM_LOG_AVAILABLE:
                        log_event("NOVA", "Blocked: HAL has not yet run", project_id, {"blocking_condition": "hal_not_run"})
                    
                    # Return blocked status
                    result = {
                        "status": "blocked",
                        "message": "Cannot proceed — HAL has not yet initialized the project.",
                        "project_id": project_id,
                        "files_created": [],
                        "next_recommended_step": "Run HAL to initialize the project",
                        "memory_tag": f"nova_ui_{project_id}",
                        "timestamp": time.time()
                    }
                    
                    # Validate output
                    if not self.validate_schema(result):
                        logger.warning(f"Output validation failed for blocked result")
                    
                    return result

            # Generate UI components based on the task
            ui_components = self._generate_ui_components(task, project_id, ui_requirements)
            
            # Simulate UI file generation
            design_action = f"Created core UI components for {project_id}"
            ui_files_created = [
                "src/components/Dashboard.jsx",
                "src/components/LoginForm.jsx"
            ]

            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", f"Design action: {design_action}", project_id)

            if MEMORY_WRITER_AVAILABLE:
                memory_data = {
                    "agent": "nova",
                    "project_id": project_id,
                    "action": design_action,
                    "tool_used": "memory_writer",
                    "design_notes": "NOVA designed the core UI structure for the app.",
                    "ui_components": ui_components
                }
                write_memory(memory_data)
                logger.info("Memory logged for NOVA UI generation")

            if PROJECT_STATE_AVAILABLE:
                # 1. Increment loop count
                increment_result = increment_loop_count(project_id, "nova")
                if increment_result.get("status") == "success":
                    logger.info("Loop count incremented and agent set to nova")
                else:
                    logger.warning(f"Loop count increment failed: {increment_result}")

                # 2. Read current memory
                state = read_project_state(project_id)
                logger.info(f"Current project state (before update): {state}")

                # 3. Merge UI files and update keys
                state["files_created"] = state.get("files_created", []) + ui_files_created
                state["completed_steps"] = state.get("completed_steps", []) + ["nova"]
                state["last_completed_agent"] = "nova"
                state["next_recommended_step"] = "Run CRITIC to review NOVA's UI output"

                # 4. Write memory
                update_result = update_project_state(project_id, state)

                if update_result.get("status") != "success":
                    logger.warning(f"Failed to persist NOVA update: {update_result}")
                else:
                    logger.info("NOVA memory successfully persisted")
                    logger.info(f"Files created: {ui_files_created}")
                    logger.info(f"Next step: {state['next_recommended_step']}")

            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", "Execution complete", project_id, {
                    "files_created": ui_files_created
                })

            # Create successful result
            result = {
                "status": "success",
                "message": f"NOVA completed task for {project_id}",
                "project_id": project_id,
                "files_created": ui_files_created,
                "ui_components": ui_components,
                "next_recommended_step": "Run CRITIC to review NOVA's UI output",
                "memory_tag": f"nova_ui_{project_id}",
                "timestamp": time.time()
            }
            
            # Validate output
            if not self.validate_schema(result):
                logger.warning(f"Output validation failed for success result")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in NovaAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("NOVA", f"Error: {str(e)}", project_id)
            
            # Return error response
            result = {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "files_created": [],
                "next_recommended_step": "Retry NOVA agent execution",
                "memory_tag": f"nova_ui_{project_id}",
                "timestamp": time.time()
            }
            
            # Validate output
            if not self.validate_schema(result):
                logger.warning(f"Output validation failed for error result")
            
            return result
    
    def _generate_ui_components(self, task: str, project_id: str, ui_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate UI components based on the task and requirements.
        
        Args:
            task: The task description
            project_id: The project identifier
            ui_requirements: Specific UI requirements (optional)
            
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

async def run_nova_agent(task: str, project_id: str, tools: Optional[List[str]] = None, ui_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run the NOVA agent with the given task.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        ui_requirements: Specific UI requirements (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Execute the agent
    return await nova_agent.execute(
        task=task,
        project_id=project_id,
        tools=tools,
        ui_requirements=ui_requirements
    )

# memory_tag: healed_phase3.3
