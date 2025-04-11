"""
Agent Task Verification Module

This module provides functionality for agents to self-qualify for tasks based on their skills.
It allows agents to evaluate whether they should take on a given task based on their skillset,
role, and current state.

Endpoint: /agent/verify_task
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Set
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Define the router
router = APIRouter()

# Define the models
class TaskRequirement(BaseModel):
    """Model for a task requirement"""
    skill: str
    importance: str = "required"  # required, preferred, optional

class VerifyTaskRequest(BaseModel):
    """Request model for the verify_task endpoint"""
    agent_id: str
    task_description: str
    required_skills: Optional[List[str]] = None

class VerifyTaskResponse(BaseModel):
    """Response model for the verify_task endpoint"""
    agent_id: str
    task_description: str
    qualified: bool
    confidence_score: float
    missing_skills: List[str] = []
    matching_skills: List[str] = []
    justification: str
    suggested_agents: Optional[List[str]] = None

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

def extract_required_skills(task_description: str) -> List[str]:
    """
    Extract required skills from a task description.
    
    Args:
        task_description (str): The task description
        
    Returns:
        List[str]: List of required skills
    """
    # Define common skills that might be required for different tasks
    skill_keywords = {
        "analyze": ["analyze", "assessment", "evaluate", "examine"],
        "summarize": ["summarize", "summary", "condense", "brief"],
        "monitor": ["monitor", "track", "observe", "watch"],
        "reflect": ["reflect", "introspect", "consider", "contemplate"],
        "delegate": ["delegate", "assign", "allocate", "distribute"],
        "execute": ["execute", "perform", "implement", "carry out"],
        "protocol": ["protocol", "procedure", "standard", "guideline"],
        "maintain": ["maintain", "upkeep", "sustain", "preserve"],
        "deploy": ["deploy", "launch", "release", "roll out"],
        "troubleshoot": ["troubleshoot", "debug", "fix", "solve"],
        "store": ["store", "save", "record", "archive"],
        "retrieve": ["retrieve", "fetch", "get", "access"],
        "organize": ["organize", "arrange", "structure", "categorize"],
        "log": ["log", "record", "document", "register"],
        "plan": ["plan", "schedule", "strategize", "outline"],
        "coach": ["coach", "mentor", "guide", "advise"],
        "design": ["design", "create", "develop", "craft"],
        "generate": ["generate", "produce", "create", "build"],
        "detect": ["detect", "identify", "recognize", "spot"],
        "visualize": ["visualize", "display", "show", "illustrate"],
        "train": ["train", "teach", "educate", "instruct"],
        "predict": ["predict", "forecast", "anticipate", "project"],
        "optimize": ["optimize", "improve", "enhance", "refine"],
        "orchestrate": ["orchestrate", "coordinate", "manage", "direct"],
        "route": ["route", "direct", "channel", "guide"]
    }
    
    # Extract skills based on keywords in the task description
    required_skills = []
    task_lower = task_description.lower()
    
    for skill, keywords in skill_keywords.items():
        if any(keyword in task_lower for keyword in keywords):
            required_skills.append(skill)
    
    # If no skills were extracted, use a fallback approach
    if not required_skills:
        # Look for verbs at the beginning of sentences or after certain phrases
        action_patterns = [
            r"(?:^|[.!?]\s+)(\w+)\s+",  # Verb at the beginning of a sentence
            r"(?:need to|should|must|will|can)\s+(\w+)\s+"  # Verb after modal
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, task_lower)
            for match in matches:
                # Check if the verb matches any skill
                for skill, keywords in skill_keywords.items():
                    if match in keywords or match == skill:
                        required_skills.append(skill)
    
    return list(set(required_skills))  # Remove duplicates

def verify_agent_skills(agent_id: str, required_skills: List[str]) -> tuple[bool, float, List[str], List[str]]:
    """
    Verify if an agent has the required skills for a task.
    
    Args:
        agent_id (str): The ID of the agent
        required_skills (List[str]): List of required skills
        
    Returns:
        Tuple of (qualified, confidence_score, missing_skills, matching_skills)
    """
    # Get agent information
    agent_info = get_agent_info(agent_id)
    
    # Get agent skills
    agent_skills = agent_info.get("skills", [])
    
    # Check if agent has all required skills
    missing_skills = []
    matching_skills = []
    
    for skill in required_skills:
        if skill in agent_skills:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)
    
    # Calculate qualification and confidence score
    qualified = len(missing_skills) == 0
    
    # Calculate confidence score based on matching and missing skills
    if not required_skills:
        confidence_score = 0.5  # Neutral score if no skills required
    else:
        # Base score on percentage of matching skills
        match_percentage = len(matching_skills) / len(required_skills)
        
        # Adjust confidence based on match percentage
        if match_percentage == 1.0:
            confidence_score = 0.9  # High confidence but not absolute
        elif match_percentage >= 0.75:
            confidence_score = 0.8  # Good match
        elif match_percentage >= 0.5:
            confidence_score = 0.6  # Moderate match
        elif match_percentage > 0:
            confidence_score = 0.4  # Poor match
        else:
            confidence_score = 0.1  # Very poor match
    
    return qualified, confidence_score, missing_skills, matching_skills

def find_alternative_agents(required_skills: List[str], current_agent_id: str) -> List[str]:
    """
    Find alternative agents that have the required skills.
    
    Args:
        required_skills (List[str]): List of required skills
        current_agent_id (str): The ID of the current agent
        
    Returns:
        List[str]: List of alternative agent IDs
    """
    # Load agent manifest
    manifest = load_agent_manifest()
    
    # Find agents with matching skills
    matching_agents = []
    
    for agent_id, agent_data in manifest.items():
        # Skip the current agent
        if agent_id == current_agent_id or agent_id == f"{current_agent_id}-agent":
            continue
        
        # Get agent skills
        agent_skills = agent_data.get("skills", [])
        
        # Check if agent has all required skills
        if all(skill in agent_skills for skill in required_skills):
            # Extract base agent ID without -agent suffix
            base_agent_id = agent_id.replace("-agent", "")
            matching_agents.append(base_agent_id)
    
    return matching_agents

def generate_justification(qualified: bool, matching_skills: List[str], missing_skills: List[str]) -> str:
    """
    Generate a justification for the verification result.
    
    Args:
        qualified (bool): Whether the agent is qualified
        matching_skills (List[str]): List of matching skills
        missing_skills (List[str]): List of missing skills
        
    Returns:
        str: Justification text
    """
    if qualified:
        if matching_skills:
            return f"Agent is fully qualified with all required skills: {', '.join(matching_skills)}."
        else:
            return "Agent is qualified as no specific skills are required for this task."
    else:
        if matching_skills and missing_skills:
            return f"Agent has some required skills ({', '.join(matching_skills)}), but lacks others ({', '.join(missing_skills)})."
        elif missing_skills:
            return f"Agent lacks all required skills for this task: {', '.join(missing_skills)}."
        else:
            return "Agent qualification could not be determined due to insufficient information."

@router.post("/agent/verify_task", response_model=VerifyTaskResponse)
async def verify_task(request: VerifyTaskRequest):
    """
    Verify if an agent is qualified for a task based on their skills.
    
    Args:
        request (VerifyTaskRequest): The verification request
        
    Returns:
        VerifyTaskResponse: The verification response
        
    Raises:
        HTTPException: If the agent is not found or other errors occur
    """
    # Validate the request
    if not request.agent_id:
        raise HTTPException(status_code=422, detail="agent_id is required")
    
    if not request.task_description:
        raise HTTPException(status_code=422, detail="task_description is required")
    
    # Determine required skills
    required_skills = request.required_skills or extract_required_skills(request.task_description)
    
    # Verify agent skills
    qualified, confidence_score, missing_skills, matching_skills = verify_agent_skills(
        request.agent_id, required_skills
    )
    
    # Generate justification
    justification = generate_justification(qualified, matching_skills, missing_skills)
    
    # Find alternative agents if not qualified
    suggested_agents = None
    if not qualified and missing_skills:
        suggested_agents = find_alternative_agents(required_skills, request.agent_id)
    
    # Create and return the response
    return VerifyTaskResponse(
        agent_id=request.agent_id,
        task_description=request.task_description,
        qualified=qualified,
        confidence_score=confidence_score,
        missing_skills=missing_skills,
        matching_skills=matching_skills,
        justification=justification,
        suggested_agents=suggested_agents
    )
