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
print("🧠 Route defined: /api/modules/orchestrator/scope -> generate_project_scope")

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

class UnmatchedTask(BaseModel):
    """Model for unmatched tasks in the scope response"""
    tool: str
    reason: str

class ToneProfile(BaseModel):
    """Model for agent tone profile in agent creation suggestions"""
    style: str
    emotion: str
    vibe: str
    persona: str

class AgentCreationSuggestion(BaseModel):
    """Model for agent creation suggestions in the scope response"""
    agent_name: str
    proposed_skills: List[str]
    tone_profile: ToneProfile
    reason: str

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
    skill_validation_passed: bool = True
    unmatched_tasks: Optional[List[UnmatchedTask]] = None
    agent_creation_suggestions: Optional[List[AgentCreationSuggestion]] = None

@router.post("/scope")
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
    - skill_validation_passed: Whether all required tools have matching agent skills
    - unmatched_tasks: List of tools that don't have matching agent skills
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
    suggested_agents, skill_validation_passed, unmatched_tasks, agent_creation_suggestions = determine_suggested_agents(goal, required_modules)
    
    # Generate recommended schema
    recommended_schema = generate_recommended_schema(goal, required_modules)
    
    # Generate execution tasks
    execution_tasks = generate_execution_tasks(goal, required_modules, suggested_agents)
    
    # Identify known risks
    known_risks = identify_known_risks(goal, required_modules, suggested_agents)
    
    # Calculate confidence scores
    confidence_scores = calculate_confidence_scores(suggested_agents, skill_validation_passed)
    
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
        "markdown_summary": markdown_summary,
        "skill_validation_passed": skill_validation_passed
    }
    
    # Add unmatched_tasks if there are any
    if unmatched_tasks:
        scope["unmatched_tasks"] = [task.dict() for task in unmatched_tasks]
    else:
        scope["unmatched_tasks"] = []
    
    # Add agent_creation_suggestions if there are any
    if agent_creation_suggestions:
        scope["agent_creation_suggestions"] = [suggestion.dict() for suggestion in agent_creation_suggestions]
    
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

def get_agent_skills() -> Dict[str, List[str]]:
    """
    Get agent skills from agent_manifest.json.
    
    Returns:
        Dictionary of agent skills
    """
    try:
        # Load agent manifest
        manifest_path = os.path.join(os.path.dirname(__file__), '../../config/agent_manifest.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Extract agent skills
        agent_skills = {}
        for agent_key, agent_data in manifest.items():
            agent_id = agent_key.split('-')[0]  # Extract agent_id from key (e.g., "hal-agent" -> "hal")
            if "skills" in agent_data:
                agent_skills[agent_id] = agent_data["skills"]
        
        return agent_skills
    except Exception as e:
        print(f"Error loading agent skills: {str(e)}")
        return {}

def determine_suggested_agents(goal: str, required_modules: List[str]) -> tuple[List[AgentConfig], bool, List[UnmatchedTask], List[AgentCreationSuggestion]]:
    """
    Determine suggested agents based on the goal and required modules.
    Validates that agents have the required skills for the tools they're assigned.
    When skill gaps are detected, suggests new agents that could fill those gaps.
    
    Args:
        goal: High-level user goal
        required_modules: List of required modules
        
    Returns:
        Tuple of (suggested_agents, skill_validation_passed, unmatched_tasks, agent_creation_suggestions)
    """
    suggested_agents = []
    unmatched_tasks = []
    agent_creation_suggestions = []
    skill_validation_passed = True
    
    # Get agent skills from agent_manifest.json
    agent_skills = get_agent_skills()
    
    # Map of required tools to potential agents
    tool_to_agents = {
        "reflect": ["hal", "lifetree"],
        "summarize": ["hal"],
        "delegate": ["ash"],
        "execute": ["ash"],
        "write": ["memory", "hal"],
        "read": ["memory", "hal"],
        "train": ["neureal"],
        "loop": ["core-forge"],
        "task/status": ["ops"],
        "emotional_analysis": []  # No existing agent has this skill
    }
    
    # Track which required modules have a qualified agent
    module_has_qualified_agent = {module: False for module in required_modules}
    
    # Track unmatched skills for agent creation suggestions
    unmatched_skills = []
    
    # Define required tools for each agent
    hal_tools = ["reflect", "summarize"]
    ash_tools = ["delegate", "execute"]
    
    # Check if HAL has the required skills
    hal_has_skills = True
    for tool in hal_tools:
        if "hal" not in agent_skills or tool not in agent_skills["hal"]:
            hal_has_skills = False
            unmatched_tasks.append(UnmatchedTask(
                tool=tool,
                reason=f"HAL does not have the required skill for {tool}"
            ))
            # Mark this tool as unmatched
            if tool in module_has_qualified_agent:
                module_has_qualified_agent[tool] = False
                unmatched_skills.append(tool)
    
    # Add HAL with appropriate confidence score
    hal = AgentConfig(
        agent_name="hal",
        tools=hal_tools,
        persona="supportive, analytical"
    )
    suggested_agents.append(hal)
    
    # If HAL has skills, mark its tools as having a qualified agent
    if hal_has_skills:
        for tool in hal_tools:
            if tool in module_has_qualified_agent:
                module_has_qualified_agent[tool] = True
    
    # Check if ASH has the required skills
    ash_has_skills = True
    for tool in ash_tools:
        if "ash" not in agent_skills or tool not in agent_skills["ash"]:
            ash_has_skills = False
            unmatched_tasks.append(UnmatchedTask(
                tool=tool,
                reason=f"ASH does not have the required skill for {tool}"
            ))
            # Mark this tool as unmatched
            if tool in module_has_qualified_agent:
                module_has_qualified_agent[tool] = False
                unmatched_skills.append(tool)
    
    # Add ASH with appropriate confidence score
    ash = AgentConfig(
        agent_name="ash",
        tools=ash_tools,
        persona="direct, action-oriented"
    )
    suggested_agents.append(ash)
    
    # If ASH has skills, mark its tools as having a qualified agent
    if ash_has_skills:
        for tool in ash_tools:
            if tool in module_has_qualified_agent:
                module_has_qualified_agent[tool] = True
    
    # Check if any required modules don't have matching agent skills
    for module in required_modules:
        # Skip modules we've already checked
        if module in hal_tools and hal_has_skills:
            continue
        if module in ash_tools and ash_has_skills:
            continue
            
        # Find potential agents for this module
        potential_agents = tool_to_agents.get(module, [])
        has_qualified_agent = False
        
        for agent_id in potential_agents:
            if agent_id in agent_skills and module in agent_skills[agent_id]:
                has_qualified_agent = True
                module_has_qualified_agent[module] = True
                break
        
        if not has_qualified_agent:
            unmatched_tasks.append(UnmatchedTask(
                tool=module,
                reason=f"No agent declared capability for {module}"
            ))
            module_has_qualified_agent[module] = False
            unmatched_skills.append(module)
    
    # Check if all required modules have a qualified agent
    for module, has_agent in module_has_qualified_agent.items():
        if not has_agent:
            skill_validation_passed = False
    
    # Generate agent creation suggestions if there are unmatched skills
    if unmatched_skills:
        agent_creation_suggestions = generate_agent_suggestions(goal, unmatched_skills)
    
    return suggested_agents, skill_validation_passed, unmatched_tasks, agent_creation_suggestions

def generate_agent_suggestions(goal: str, unmatched_skills: List[str]) -> List[AgentCreationSuggestion]:
    """
    Generate agent creation suggestions based on unmatched skills.
    
    Args:
        goal: High-level user goal
        unmatched_skills: List of skills that don't have matching agents
        
    Returns:
        List of agent creation suggestions
    """
    suggestions = []
    
    # Group related skills for more coherent agent suggestions
    skill_groups = group_related_skills(unmatched_skills)
    
    # Generate a suggestion for each skill group
    for skill_group in skill_groups:
        # Generate agent name based on skills
        agent_name = generate_agent_name(skill_group)
        
        # Generate tone profile based on skills and goal
        tone_profile = generate_tone_profile(skill_group, goal)
        
        # Generate reason for agent creation
        reason = generate_agent_reason(skill_group, goal)
        
        # Create agent creation suggestion
        suggestion = AgentCreationSuggestion(
            agent_name=agent_name,
            proposed_skills=skill_group,
            tone_profile=tone_profile,
            reason=reason
        )
        
        suggestions.append(suggestion)
    
    return suggestions

def group_related_skills(skills: List[str]) -> List[List[str]]:
    """
    Group related skills together for more coherent agent suggestions.
    
    Args:
        skills: List of skills
        
    Returns:
        List of skill groups
    """
    # Define skill relationships
    skill_relationships = {
        "reflect": ["summarize", "emotional_analysis"],
        "summarize": ["reflect", "emotional_analysis"],
        "emotional_analysis": ["reflect", "summarize"],
        "delegate": ["execute"],
        "execute": ["delegate"],
        "write": ["read"],
        "read": ["write"],
        "train": [],
        "loop": [],
        "task/status": []
    }
    
    # Initialize groups
    groups = []
    remaining_skills = skills.copy()
    
    # Process skills
    while remaining_skills:
        # Take the first skill
        current_skill = remaining_skills.pop(0)
        current_group = [current_skill]
        
        # Find related skills
        related_skills = skill_relationships.get(current_skill, [])
        
        # Add related skills to the group if they're in the remaining skills
        for skill in related_skills:
            if skill in remaining_skills:
                current_group.append(skill)
                remaining_skills.remove(skill)
        
        # Add the group to the list of groups
        groups.append(current_group)
    
    return groups

def generate_agent_name(skills: List[str]) -> str:
    """
    Generate an agent name based on skills.
    
    Args:
        skills: List of skills
        
    Returns:
        Agent name
    """
    # Define name mappings for common skill combinations
    name_mappings = {
        frozenset(["reflect", "summarize"]): "echo",
        frozenset(["reflect", "emotional_analysis"]): "empathy",
        frozenset(["summarize", "emotional_analysis"]): "sentiment",
        frozenset(["reflect", "summarize", "emotional_analysis"]): "echo",
        frozenset(["delegate", "execute"]): "taskmaster",
        frozenset(["write", "read"]): "scribe",
        frozenset(["train"]): "mentor",
        frozenset(["loop"]): "cycle",
        frozenset(["task/status"]): "tracker"
    }
    
    # Try to find a name for the exact skill set
    skills_set = frozenset(skills)
    if skills_set in name_mappings:
        return name_mappings[skills_set]
    
    # If no exact match, use the first skill to generate a name
    primary_skill = skills[0]
    
    # Define fallback names for individual skills
    skill_names = {
        "reflect": "mirror",
        "summarize": "digest",
        "emotional_analysis": "empathy",
        "delegate": "director",
        "execute": "performer",
        "write": "author",
        "read": "reader",
        "train": "coach",
        "loop": "cycle",
        "task/status": "monitor"
    }
    
    return skill_names.get(primary_skill, f"{primary_skill}_agent")

def generate_tone_profile(skills: List[str], goal: str) -> ToneProfile:
    """
    Generate a tone profile based on skills and goal.
    
    Args:
        skills: List of skills
        goal: High-level user goal
        
    Returns:
        Tone profile
    """
    # Define tone profiles for common skill combinations
    if "emotional_analysis" in skills:
        return ToneProfile(
            style="gentle",
            emotion="empathetic",
            vibe="therapist",
            persona="A compassionate presence for emotional understanding tasks"
        )
    elif "reflect" in skills and "summarize" in skills:
        return ToneProfile(
            style="thoughtful",
            emotion="contemplative",
            vibe="mentor",
            persona="A reflective guide for synthesizing information and insights"
        )
    elif "delegate" in skills or "execute" in skills:
        return ToneProfile(
            style="direct",
            emotion="confident",
            vibe="coordinator",
            persona="An efficient organizer for task management and execution"
        )
    elif "train" in skills:
        return ToneProfile(
            style="instructive",
            emotion="encouraging",
            vibe="teacher",
            persona="A patient educator for knowledge transfer and skill development"
        )
    else:
        # Default tone profile
        return ToneProfile(
            style="balanced",
            emotion="neutral",
            vibe="assistant",
            persona="A helpful specialist focused on specific task domains"
        )

def generate_agent_reason(skills: List[str], goal: str) -> str:
    """
    Generate a reason for agent creation based on skills and goal.
    
    Args:
        skills: List of skills
        goal: High-level user goal
        
    Returns:
        Reason for agent creation
    """
    # Define reasons for common skill combinations
    if "emotional_analysis" in skills:
        return "This agent is needed for tone-aware memory reflection and emotional context processing"
    elif "reflect" in skills and "summarize" in skills:
        return "This agent specializes in deep reflection and concise summarization of complex information"
    elif "delegate" in skills and "execute" in skills:
        return "This agent is required for effective task delegation and execution coordination"
    elif "train" in skills:
        return "This agent provides specialized training and knowledge transfer capabilities"
    elif "loop" in skills:
        return "This agent manages iterative processes and feedback loops"
    else:
        # Generate a reason based on the skills
        skills_text = ", ".join(skills)
        return f"No existing agent supports the required skills: {skills_text}"

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

def calculate_confidence_scores(suggested_agents: List[AgentConfig], skill_validation_passed: bool) -> Dict[str, float]:
    """
    Calculate confidence scores for suggested agents.
    
    Args:
        suggested_agents: List of suggested agents
        skill_validation_passed: Whether skill validation passed
        
    Returns:
        Dictionary of agent confidence scores
    """
    # Get agent skills from agent_manifest.json
    agent_skills = get_agent_skills()
    
    confidence_scores = {}
    
    for agent in suggested_agents:
        # Base confidence score
        base_score = 0.85
        
        # Adjust based on agent name
        if agent.agent_name == "hal":
            base_score += 0.07  # HAL is generally more reliable
        
        # Adjust based on number of tools
        tool_bonus = min(len(agent.tools) * 0.01, 0.05)
        
        # Calculate initial score
        initial_score = base_score + tool_bonus
        
        # Check if agent has all required skills
        has_all_skills = True
        missing_skills = []
        for tool in agent.tools:
            if agent.agent_name not in agent_skills or tool not in agent_skills[agent.agent_name]:
                has_all_skills = False
                missing_skills.append(tool)
        
        # Adjust score based on skill validation
        if not has_all_skills:
            # Set to 0.0 if agent doesn't have required skills
            initial_score = 0.0
            print(f"Agent {agent.agent_name} lacks skills for: {', '.join(missing_skills)}, setting confidence to 0.0")
        elif not skill_validation_passed:
            # Reduce score if overall validation failed but this agent has its skills
            initial_score = max(initial_score * 0.7, 0.5)
            print(f"Overall skill validation failed, reducing {agent.agent_name}'s confidence to {initial_score:.2f}")
        
        # Cap at 0.98
        final_score = min(initial_score, 0.98)
        
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
    
    # Generate reflect test if reflect module is required
    if "reflect" in required_modules:
        reflect_test = TestPayload(
            endpoint="/reflect",
            description="Test reflection capability",
            example={
                "agent_id": "hal",
                "goal": "Reflect on journal entries",
                "project_id": "proj-journal",
                "memory_trace_id": "trace-123"
            }
        )
        suggested_tests.append(reflect_test)
    
    # Generate summarize test if summarize module is required
    if "summarize" in required_modules:
        summarize_test = TestPayload(
            endpoint="/summarize",
            description="Test summarization capability",
            example={
                "agent_id": "hal",
                "goal": "Summarize journal entries",
                "project_id": "proj-journal",
                "memory_trace_id": "trace-123"
            }
        )
        suggested_tests.append(summarize_test)
    
    # Generate delegate test if delegate module is required
    if "delegate" in required_modules:
        delegate_test = TestPayload(
            endpoint="/delegate",
            description="Test delegation capability",
            example={
                "from_agent": "ash",
                "to_agent": "hal",
                "task": "Reflect on journal entries",
                "project_id": "proj-journal"
            }
        )
        suggested_tests.append(delegate_test)
    
    return suggested_tests

def generate_markdown_summary(goal: str, project_id: str, required_modules: List[str], suggested_agents: List[AgentConfig], execution_tasks: List[str], known_risks: List[str]) -> str:
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
    # Generate agent section
    agent_section = ""
    for agent in suggested_agents:
        agent_section += f"- **{agent.agent_name.upper()}**: {agent.persona}\n"
        agent_section += f"  - Tools: {', '.join(agent.tools)}\n"
    
    # Generate markdown
    markdown = f"""# Project Scope: {project_id}

## Goal
{goal}

## Required Modules
{chr(10).join([f"- {module}" for module in required_modules])}

## Suggested Agents
{agent_section}
## Execution Tasks
{chr(10).join([f"- {task}" for task in execution_tasks])}

## Known Risks
{chr(10).join([f"- {risk}" for risk in known_risks])}

---
Generated by Orchestrator Scope Module"""
    
    return markdown
