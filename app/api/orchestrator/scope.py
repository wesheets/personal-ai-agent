"""
Orchestrator Scope Module - Strategic Project Planner

This module provides the /orchestrator/scope endpoint for turning high-level user goals
into structured system plans. It outputs a full project scaffold including modules,
agents, schema, risks, and test payloads ready for execution or simulation.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import os

# Import memory-related functions
from app.modules.memory_writer import write_memory

# Create router
router = APIRouter()
print("🧠 Route defined: /orchestrator/scope -> generate_project_scope")

class ScopeRequest(BaseModel):
    """Request model for the scope endpoint"""
    goal: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    mode: str = "scope"  # Future modes: "simulate", "build"
    store_scope: bool = False

class AgentConfig(BaseModel):
    """Model for agent configuration in the scope response"""
    agent_name: str
    tools: List[str]
    persona: str

class SchemaConfig(BaseModel):
    """Model for schema configuration in the scope response"""
    input: List[str]
    output: List[str]

class TestPayload(BaseModel):
    """Model for test payloads in the scope response"""
    endpoint: str
    description: str
    example: Dict[str, Any]

class ScopeResponse(BaseModel):
    """Response model for the scope endpoint"""
    project_id: str
    goal: str
    required_modules: List[str]
    suggested_agents: List[AgentConfig]
    recommended_schema: SchemaConfig
    execution_tasks: List[str]
    known_risks: List[str]
    confidence_scores: Dict[str, float]
    project_dependencies: Dict[str, List[str]]
    agent_training_reqs: Dict[str, List[str]]
    execution_blueprint_id: str
    simulate_pathways: Optional[Any] = None
    suggested_tests: List[TestPayload]
    markdown_summary: str
    stored: bool = False

@router.post("/")
async def generate_project_scope(request: Request):
    """
    Generate a project scope from a high-level goal.
    
    This endpoint takes a high-level user goal and generates a structured system plan
    with modules, agents, schema, risks, and test payloads.
    
    Request body:
    - goal: High-level user goal
    - user_id: (Optional) User ID
    - project_id: (Optional) Project ID
    - mode: "scope" (Future modes: "simulate", "build")
    - store_scope: Whether to store the scope in memory
    
    Returns:
    - project_id: Project ID
    - goal: Original goal
    - required_modules: List of required modules
    - suggested_agents: List of suggested agents with tools and personas
    - recommended_schema: Input and output schema
    - execution_tasks: List of execution tasks
    - known_risks: List of known risks
    - confidence_scores: Confidence scores for agents
    - project_dependencies: Dependencies between modules
    - agent_training_reqs: Training requirements for agents
    - execution_blueprint_id: Execution blueprint ID
    - simulate_pathways: Simulation pathways (null for scope mode)
    - suggested_tests: List of suggested tests
    - markdown_summary: Markdown summary of the project scope
    - stored: Whether the scope was stored in memory
    """
    try:
        # Parse request body
        body = await request.json()
        scope_request = ScopeRequest(**body)
        
        # Generate project_id if not provided
        project_id = scope_request.project_id or f"proj-{str(uuid.uuid4())[:8]}"
        
        # Generate the project scope
        scope = generate_scope(scope_request.goal, project_id)
        
        # Store the scope in memory if requested
        stored = False
        if scope_request.store_scope:
            memory = write_memory(
                agent_id="system",
                type="project_scope",
                content=json.dumps(scope),
                tags=["project_scope", f"project:{project_id}"],
                project_id=project_id,
                status="active",
                task_type="scope"
            )
            stored = True
        
        # Add stored flag to response
        scope["stored"] = stored
        
        # Return the scope
        return scope
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error generating project scope: {str(e)}"
            }
        )

def generate_scope(goal: str, project_id: str) -> Dict[str, Any]:
    """
    Generate a project scope from a high-level goal.
    
    Args:
        goal: High-level user goal
        project_id: Project ID
        
    Returns:
        Project scope
    """
    # This is a static implementation for now
    # In the future, this could use an agent to generate the scope
    
    # Analyze the goal to determine required modules
    required_modules = analyze_goal_for_modules(goal)
    
    # Determine suggested agents based on the goal and required modules
    suggested_agents = determine_suggested_agents(goal, required_modules)
    
    # Generate recommended schema
    recommended_schema = generate_recommended_schema(goal, required_modules)
    
    # Generate execution tasks
    execution_tasks = generate_execution_tasks(goal, required_modules, suggested_agents)
    
    # Identify known risks
    known_risks = identify_known_risks(goal, required_modules, suggested_agents)
    
    # Calculate confidence scores
    confidence_scores = calculate_confidence_scores(suggested_agents)
    
    # Determine project dependencies
    project_dependencies = determine_project_dependencies(required_modules)
    
    # Determine agent training requirements
    agent_training_reqs = determine_agent_training_reqs(suggested_agents)
    
    # Generate execution blueprint ID
    execution_blueprint_id = f"scope-{str(uuid.uuid4())[:8]}"
    
    # Generate suggested tests
    suggested_tests = generate_suggested_tests(goal, required_modules, suggested_agents)
    
    # Generate markdown summary
    markdown_summary = generate_markdown_summary(
        goal, 
        project_id, 
        required_modules, 
        suggested_agents, 
        execution_tasks, 
        known_risks
    )
    
    # Construct the scope response
    scope = {
        "project_id": project_id,
        "goal": goal,
        "required_modules": required_modules,
        "suggested_agents": [agent.dict() for agent in suggested_agents],
        "recommended_schema": recommended_schema.dict(),
        "execution_tasks": execution_tasks,
        "known_risks": known_risks,
        "confidence_scores": confidence_scores,
        "project_dependencies": project_dependencies,
        "agent_training_reqs": agent_training_reqs,
        "execution_blueprint_id": execution_blueprint_id,
        "simulate_pathways": None,  # Null for scope mode
        "suggested_tests": [test.dict() for test in suggested_tests],
        "markdown_summary": markdown_summary
    }
    
    return scope

def analyze_goal_for_modules(goal: str) -> List[str]:
    """
    Analyze the goal to determine required modules.
    
    Args:
        goal: High-level user goal
        
    Returns:
        List of required modules
    """
    # Base modules that are almost always required
    base_modules = ["write", "read", "reflect"]
    
    # Additional modules based on goal keywords
    additional_modules = []
    
    # Check for keywords in the goal
    goal_lower = goal.lower()
    
    if any(keyword in goal_lower for keyword in ["summarize", "summary", "summarization"]):
        additional_modules.append("summarize")
    
    if any(keyword in goal_lower for keyword in ["task", "status", "progress", "track"]):
        additional_modules.append("task/status")
    
    if any(keyword in goal_lower for keyword in ["train", "learning", "teach"]):
        additional_modules.append("train")
    
    if any(keyword in goal_lower for keyword in ["delegate", "assign", "handoff"]):
        additional_modules.append("delegate")
    
    if any(keyword in goal_lower for keyword in ["loop", "iterate", "cycle"]):
        additional_modules.append("loop")
    
    # Combine base and additional modules
    required_modules = base_modules + additional_modules
    
    return required_modules

def determine_suggested_agents(goal: str, required_modules: List[str]) -> List[AgentConfig]:
    """
    Determine suggested agents based on the goal and required modules.
    
    Args:
        goal: High-level user goal
        required_modules: List of required modules
        
    Returns:
        List of suggested agents
    """
    suggested_agents = []
    
    # HAL is good for analytical and reflective tasks
    hal_tools = ["reflect", "summarize"]
    if "summarize" in required_modules:
        hal_tools.append("summarize")
    
    hal = AgentConfig(
        agent_name="hal",
        tools=hal_tools,
        persona="supportive, analytical"
    )
    suggested_agents.append(hal)
    
    # ASH is good for action-oriented tasks
    ash_tools = ["delegate", "execute"]
    if "delegate" in required_modules:
        ash_tools.append("delegate")
    
    ash = AgentConfig(
        agent_name="ash",
        tools=ash_tools,
        persona="direct, action-oriented"
    )
    suggested_agents.append(ash)
    
    return suggested_agents

def generate_recommended_schema(goal: str, required_modules: List[str]) -> SchemaConfig:
    """
    Generate recommended schema based on the goal and required modules.
    
    Args:
        goal: High-level user goal
        required_modules: List of required modules
        
    Returns:
        Recommended schema
    """
    # Base input fields
    input_fields = ["agent_id", "goal", "project_id"]
    
    # Add memory_trace_id if reflection or summarization is needed
    if any(module in required_modules for module in ["reflect", "summarize"]):
        input_fields.append("memory_trace_id")
    
    # Base output fields
    output_fields = ["status", "result"]
    
    # Add summary if summarization is needed
    if "summarize" in required_modules:
        output_fields.append("summary")
    
    return SchemaConfig(
        input=input_fields,
        output=output_fields
    )

def generate_execution_tasks(goal: str, required_modules: List[str], suggested_agents: List[AgentConfig]) -> List[str]:
    """
    Generate execution tasks based on the goal, required modules, and suggested agents.
    
    Args:
        goal: High-level user goal
        required_modules: List of required modules
        suggested_agents: List of suggested agents
        
    Returns:
        List of execution tasks
    """
    # Base execution tasks
    execution_tasks = [
        "Create project container",
        "Register agents"
    ]
    
    # Add training task if train module is required
    if "train" in required_modules:
        execution_tasks.append("Train memory with project context")
    
    # Add reflection and summarization tasks if those modules are required
    if all(module in required_modules for module in ["reflect", "summarize"]):
        execution_tasks.append("Test summary and reflection loop")
    
    # Add trace integrity validation
    execution_tasks.append("Validate trace integrity")
    
    return execution_tasks

def identify_known_risks(goal: str, required_modules: List[str], suggested_agents: List[AgentConfig]) -> List[str]:
    """
    Identify known risks based on the goal, required modules, and suggested agents.
    
    Args:
        goal: High-level user goal
        required_modules: List of required modules
        suggested_agents: List of suggested agents
        
    Returns:
        List of known risks
    """
    # Base risks
    known_risks = []
    
    # Add loop-related risks if loop module is required
    if "loop" in required_modules:
        known_risks.append("Loop runaway without cycle caps")
    
    # Add agent-related risks
    known_risks.append("Missing agent capability validation")
    
    # Add reflection-related risks if reflect module is required
    if "reflect" in required_modules:
        known_risks.append("Reflection without goal alignment")
    
    # Add output-related risks
    known_risks.append("Output returned without success check")
    
    return known_risks

def calculate_confidence_scores(suggested_agents: List[AgentConfig]) -> Dict[str, float]:
    """
    Calculate confidence scores for suggested agents.
    
    Args:
        suggested_agents: List of suggested agents
        
    Returns:
        Dictionary of agent confidence scores
    """
    # For now, use static confidence scores
    # In the future, this could be based on agent capabilities and goal alignment
    confidence_scores = {}
    
    for agent in suggested_agents:
        # Base confidence score
        base_score = 0.85
        
        # Adjust based on agent name
        if agent.agent_name == "hal":
            base_score += 0.07  # HAL is generally more reliable
        
        # Adjust based on number of tools
        tool_bonus = min(len(agent.tools) * 0.01, 0.05)
        
        # Calculate final score
        final_score = min(base_score + tool_bonus, 0.98)  # Cap at 0.98
        
        confidence_scores[agent.agent_name] = round(final_score, 2)
    
    return confidence_scores

def determine_project_dependencies(required_modules: List[str]) -> Dict[str, List[str]]:
    """
    Determine project dependencies based on required modules.
    
    Args:
        required_modules: List of required modules
        
    Returns:
        Dictionary of module dependencies
    """
    # Define known dependencies
    dependencies = {}
    
    # Summarize depends on write and reflect
    if "summarize" in required_modules:
        dependencies["summarize"] = ["write", "reflect"]
    
    # Delegate depends on read
    if "delegate" in required_modules:
        dependencies["delegate"] = ["read"]
    
    # Loop depends on reflect
    if "loop" in required_modules:
        dependencies["loop"] = ["reflect"]
    
    return dependencies

def determine_agent_training_reqs(suggested_agents: List[AgentConfig]) -> Dict[str, List[str]]:
    """
    Determine agent training requirements based on suggested agents.
    
    Args:
        suggested_agents: List of suggested agents
        
    Returns:
        Dictionary of agent training requirements
    """
    # Define known training requirements
    training_reqs = {}
    
    for agent in suggested_agents:
        if agent.agent_name == "hal":
            training_reqs["hal"] = ["tone_profile", "journaling context"]
        elif agent.agent_name == "ash":
            training_reqs["ash"] = ["task delegation patterns"]
    
    return training_reqs

def generate_suggested_tests(goal: str, required_modules: List[str], suggested_agents: List[AgentConfig]) -> List[TestPayload]:
    """
    Generate suggested tests based on the goal, required modules, and suggested agents.
    
    Args:
        goal: High-level user goal
        required_modules: List of required modules
        suggested_agents: List of suggested agents
        
    Returns:
        List of suggested tests
    """
    suggested_tests = []
    
    # Generate train test if train module is required
    if "train" in required_modules:
        # Find an agent that would benefit from training
        for agent in suggested_agents:
            if agent.agent_name == "hal":
                train_test = TestPayload(
                    endpoint="/train",
                    description="Train HAL on tone and journaling",
                    example={
                        "agent_id": "hal",
                        "goal": "Train HAL to support reflective journaling",
                        "project_id": "proj-journal",
                        "content": "HAL should use a warm, supportive tone."
                    }
                )
                suggested_tests.append(train_test)
                break
    
    # Generate reflect test if reflect module is required
    if "reflect" in required_modules:
        reflect_test = TestPayload(
            endpoint="/reflect",
            description="Test reflection capabilities",
            example={
                "agent_id": "hal",
                "goal": goal,
                "project_id": "proj-test",
                "memory_trace_id": "trace-123"
            }
        )
        suggested_tests.append(reflect_test)
    
    # Generate summarize test if summarize module is required
    if "summarize" in required_modules:
        summarize_test = TestPayload(
            endpoint="/summarize",
            description="Test summarization capabilities",
            example={
                "agent_id": "hal",
                "project_id": "proj-test",
                "memory_type": "reflection"
            }
        )
        suggested_tests.append(summarize_test)
    
    return suggested_tests

def generate_markdown_summary(
    goal: str, 
    project_id: str, 
    required_modules: List[str], 
    suggested_agents: List[AgentConfig], 
    execution_tasks: List[str], 
    known_risks: List[str]
) -> str:
    """
    Generate a markdown summary of the project scope.
    
    Args:
        goal: High-level user goal
        project_id: Project ID
        required_modules: List of required modules
        suggested_agents: List of suggested agents
        execution_tasks: List of execution tasks
        known_risks: List of known risks
        
    Returns:
        Markdown summary
    """
    # Format the agent information
    agent_info = ""
    for agent in suggested_agents:
        agent_info += f"- **{agent.agent_name.upper()}**: {agent.persona}\n"
        agent_info += f"  - Tools: {', '.join(agent.tools)}\n"
    
    # Format the module information
    module_info = "- " + "\n- ".join(required_modules)
    
    # Format the execution tasks
    task_info = "- " + "\n- ".join(execution_tasks)
    
    # Format the known risks
    risk_info = "- " + "\n- ".join(known_risks)
    
    # Generate the markdown summary
    markdown = f"""# Project Scope: {project_id}

## Goal
{goal}

## Required Modules
{module_info}

## Suggested Agents
{agent_info}

## Execution Tasks
{task_info}

## Known Risks
{risk_info}

---
Generated by Orchestrator Scope Module
"""
    
    return markdown
