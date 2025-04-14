"""
Agent Self-Presentation Module

This module provides functionality for agents to describe themselves in a structured,
narrative format similar to how the Orchestrator presents information.

Endpoint: /agent/present
"""

import json
import os
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Define the router
router = APIRouter()

# Define the models
class ToneProfile(BaseModel):
    style: str
    emotion: str
    vibe: str
    persona: str

class AgentPresentResponse(BaseModel):
    agent_id: str
    description: str
    skills: List[str]
    tone_profile: ToneProfile
    ideal_tasks: List[str]
    present_markdown: str
    narration_text: str

# Path to the agent manifest file
AGENT_MANIFEST_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 "config", "agent_manifest.json")

def load_agent_manifest() -> Dict[str, Any]:
    """
    Load the agent manifest from the JSON file.
    
    Returns:
        Dict[str, Any]: The agent manifest as a dictionary
    """
    try:
        with open(AGENT_MANIFEST_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load agent manifest: {str(e)}")

def get_agent_info(agent_id: str) -> Dict[str, Any]:
    """
    Get information about a specific agent from the manifest.
    
    Args:
        agent_id (str): The ID of the agent
        
    Returns:
        Dict[str, Any]: Information about the agent
        
    Raises:
        HTTPException: If the agent is not found
    """
    manifest = load_agent_manifest()
    
    # Check if agent_id has -agent suffix, if not add it
    full_agent_id = agent_id if agent_id.endswith("-agent") else f"{agent_id}-agent"
    
    if full_agent_id not in manifest:
        raise HTTPException(status_code=404, 
                           detail=f"Agent '{agent_id}' not found in manifest")
    
    return manifest[full_agent_id]

def generate_ideal_tasks(agent_info: Dict[str, Any]) -> List[str]:
    """
    Generate ideal tasks for an agent based on their skills.
    
    Args:
        agent_info (Dict[str, Any]): Information about the agent
        
    Returns:
        List[str]: A list of ideal tasks for the agent
    """
    skills = agent_info.get("skills", [])
    ideal_tasks = []
    
    skill_to_task_map = {
        "reflect": [
            "Reflect on user interactions and patterns",
            "Provide thoughtful analysis of past decisions",
            "Generate insights from historical data"
        ],
        "summarize": [
            "Generate concise summaries of memory traces",
            "Condense complex information into key points",
            "Create executive summaries of project activities"
        ],
        "monitor": [
            "Monitor system performance and health",
            "Track user engagement patterns",
            "Observe and report on agent interactions"
        ],
        "analyze": [
            "Analyze data for meaningful patterns",
            "Evaluate system efficiency and performance",
            "Assess user needs and preferences"
        ],
        "delegate": [
            "Assign tasks to appropriate agents",
            "Coordinate multi-agent workflows",
            "Manage resource allocation across the system"
        ],
        "execute": [
            "Carry out complex operational tasks",
            "Implement user-requested actions",
            "Execute multi-step processes reliably"
        ],
        "protocol": [
            "Enforce system safety protocols",
            "Maintain compliance with operational guidelines",
            "Implement standardized procedures"
        ],
        "maintain": [
            "Perform routine system maintenance",
            "Update and patch system components",
            "Ensure long-term system stability"
        ],
        "deploy": [
            "Deploy new features and capabilities",
            "Roll out system updates",
            "Implement new agent configurations"
        ],
        "troubleshoot": [
            "Diagnose and fix system issues",
            "Resolve operational conflicts",
            "Address performance bottlenecks"
        ],
        "store": [
            "Securely store important information",
            "Archive historical data",
            "Maintain structured data repositories"
        ],
        "retrieve": [
            "Quickly access relevant information",
            "Find and return requested data",
            "Search through archives efficiently"
        ],
        "organize": [
            "Structure information for optimal access",
            "Categorize and tag data appropriately",
            "Create logical hierarchies of information"
        ],
        "log": [
            "Record system events and activities",
            "Maintain detailed operation logs",
            "Document important interactions"
        ],
        "plan": [
            "Develop strategic action plans",
            "Create schedules and timelines",
            "Design implementation roadmaps"
        ],
        "coach": [
            "Provide guidance and mentorship",
            "Offer constructive feedback",
            "Support skill development and growth"
        ],
        "design": [
            "Create visual and functional designs",
            "Develop user interface layouts",
            "Plan system architecture"
        ],
        "generate": [
            "Produce creative content and assets",
            "Create code and technical solutions",
            "Develop new ideas and concepts"
        ],
        "detect": [
            "Identify patterns and anomalies",
            "Recognize user needs and preferences",
            "Spot potential issues before they escalate"
        ],
        "visualize": [
            "Create visual representations of data",
            "Generate charts, graphs, and diagrams",
            "Produce illustrative examples"
        ],
        "train": [
            "Develop and train machine learning models",
            "Improve system capabilities through learning",
            "Enhance agent performance over time"
        ],
        "predict": [
            "Forecast future trends and patterns",
            "Anticipate user needs",
            "Project likely outcomes of actions"
        ],
        "optimize": [
            "Improve system efficiency and performance",
            "Refine processes for better results",
            "Enhance resource utilization"
        ],
        "orchestrate": [
            "Coordinate complex multi-agent operations",
            "Manage system-wide workflows",
            "Direct collaborative agent activities"
        ],
        "route": [
            "Direct tasks to appropriate handlers",
            "Manage information flow through the system",
            "Ensure requests reach the right destination"
        ]
    }
    
    # Generate tasks based on skills
    for skill in skills:
        if skill in skill_to_task_map:
            # Add 1-2 tasks per skill to avoid too many
            tasks_for_skill = skill_to_task_map[skill][:2]
            ideal_tasks.extend(tasks_for_skill)
    
    # If no tasks were generated, provide a generic fallback
    if not ideal_tasks:
        ideal_tasks = [
            f"Perform tasks related to {', '.join(skills)}",
            "Support system operations",
            "Assist with user requests"
        ]
    
    # Limit to 5 tasks maximum to keep it concise
    return ideal_tasks[:5]

def generate_markdown(agent_id: str, agent_info: Dict[str, Any], ideal_tasks: List[str]) -> str:
    """
    Generate a markdown presentation for the agent.
    
    Args:
        agent_id (str): The ID of the agent
        agent_info (Dict[str, Any]): Information about the agent
        ideal_tasks (List[str]): Ideal tasks for the agent
        
    Returns:
        str: Markdown presentation
    """
    # Extract agent information
    description = agent_info.get("description", "No description available")
    skills = agent_info.get("skills", [])
    tone_profile = agent_info.get("tone_profile", {})
    persona = tone_profile.get("persona", "No persona defined")
    
    # Format the agent ID for display (remove -agent suffix if present)
    display_id = agent_id.replace("-agent", "").upper()
    
    # Build the markdown
    markdown = f"# {display_id}: Self-Presentation\n\n"
    
    markdown += f"## Description\n{description}\n\n"
    
    markdown += "## Skills\n"
    for skill in skills:
        markdown += f"- {skill}\n"
    markdown += "\n"
    
    markdown += "## Ideal Tasks\n"
    for task in ideal_tasks:
        markdown += f"- {task}\n"
    markdown += "\n"
    
    markdown += "## Persona\n"
    markdown += f"{persona}\n\n"
    
    markdown += "## Tone Profile\n"
    if tone_profile:
        markdown += f"- Style: {tone_profile.get('style', 'Not specified')}\n"
        markdown += f"- Emotion: {tone_profile.get('emotion', 'Not specified')}\n"
        markdown += f"- Vibe: {tone_profile.get('vibe', 'Not specified')}\n"
    else:
        markdown += "No tone profile defined.\n"
    
    return markdown

def generate_narration(agent_id: str, agent_info: Dict[str, Any]) -> str:
    """
    Generate a narration text for the agent.
    
    Args:
        agent_id (str): The ID of the agent
        agent_info (Dict[str, Any]): Information about the agent
        
    Returns:
        str: Narration text
    """
    # Extract agent information
    description = agent_info.get("description", "")
    skills = agent_info.get("skills", [])
    tone_profile = agent_info.get("tone_profile", {})
    
    # Format the agent ID for display (remove -agent suffix if present)
    display_id = agent_id.replace("-agent", "").upper()
    
    # Generate narration based on tone profile
    style = tone_profile.get("style", "neutral")
    emotion = tone_profile.get("emotion", "neutral")
    vibe = tone_profile.get("vibe", "assistant")
    
    # Base narration template
    narration = f"I am {display_id}. "
    
    # Add skills description
    if skills:
        skill_text = ", ".join([f"{skill}" for skill in skills[:-1]])
        if len(skills) > 1:
            skill_text += f", and {skills[-1]}"
        else:
            skill_text = skills[0]
        
        narration += f"I specialize in {skill_text}. "
    
    # Add description
    if description:
        narration += f"{description} "
    
    # Add tone-specific closing
    if style == "formal":
        narration += "I maintain professional standards in all interactions."
    elif style == "conversational":
        narration += "I'm here to help in a friendly, approachable way."
    elif style == "precise":
        narration += "I focus on accuracy and clarity in all my operations."
    elif style == "concise":
        narration += "I provide clear, efficient assistance."
    elif style == "creative":
        narration += "I bring innovative thinking to every challenge."
    elif style == "analytical":
        narration += "I approach problems with data-driven insights."
    else:
        narration += "I'm ready to assist with your needs."
    
    return narration

@router.post("/agent/present", response_model=AgentPresentResponse)
async def present_agent(request: Dict[str, str]):
    """
    Generate a self-presentation for an agent.
    
    Args:
        request (Dict[str, str]): Request containing agent_id
        
    Returns:
        AgentPresentResponse: Structured agent presentation
        
    Raises:
        HTTPException: If the agent is not found or other errors occur
    """
    agent_id = request.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=422, detail="agent_id is required")
    
    # Get agent information
    agent_info = get_agent_info(agent_id)
    
    # Extract basic information
    description = agent_info.get("description", "No description available")
    skills = agent_info.get("skills", [])
    
    # Get or create tone profile
    tone_profile_data = agent_info.get("tone_profile", {})
    tone_profile = ToneProfile(
        style=tone_profile_data.get("style", "neutral"),
        emotion=tone_profile_data.get("emotion", "neutral"),
        vibe=tone_profile_data.get("vibe", "assistant"),
        persona=tone_profile_data.get("persona", "Helpful assistant")
    )
    
    # Generate ideal tasks
    ideal_tasks = generate_ideal_tasks(agent_info)
    
    # Generate markdown presentation
    present_markdown = generate_markdown(agent_id, agent_info, ideal_tasks)
    
    # Generate narration text
    narration_text = generate_narration(agent_id, agent_info)
    
    # Create and return the response
    return AgentPresentResponse(
        agent_id=agent_id,
        description=description,
        skills=skills,
        tone_profile=tone_profile,
        ideal_tasks=ideal_tasks,
        present_markdown=present_markdown,
        narration_text=narration_text
    )
