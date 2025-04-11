"""
Orchestrator Present Module - Architecture Deck Generator

This module provides the /orchestrator/present endpoint for converting stored project scopes
into visual presentation slides with narration. It transforms the technical project plan
into an explained, narratable presentation format.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import os

# Create router
router = APIRouter()
print("🧠 Route defined: /orchestrator/present -> generate_architecture_deck")

class PresentRequest(BaseModel):
    """Request model for the present endpoint"""
    project_id: str

class Slide(BaseModel):
    """Model for a presentation slide"""
    title: str
    content: str
    narration_text: Optional[str] = None

class PresentResponse(BaseModel):
    """Response model for the present endpoint"""
    project_id: str
    slides: List[Slide]
    markdown_script: str
    status: str = "success"

@router.post("/present")
async def generate_architecture_deck(request: Request):
    """
    Generate an architecture deck from a stored project scope.
    
    This endpoint takes a project_id and generates a structured presentation
    with slides and narration based on the stored project scope.
    
    Request body:
    - project_id: Project ID to generate presentation for
    
    Returns:
    - project_id: Project ID
    - slides: List of presentation slides
    - markdown_script: Markdown script for the presentation
    - status: Success or error status
    """
    try:
        # Parse request body
        body = await request.json()
        present_request = PresentRequest(**body)
        
        # Look up stored project scope
        project_scope = lookup_project_scope(present_request.project_id)
        
        # If no scope found, return 404 error
        if not project_scope:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "reason": f"No project_scope memory found for project_id: {present_request.project_id}"
                }
            )
        
        # Generate slides from project scope
        slides = generate_slides(project_scope)
        
        # Generate markdown script
        markdown_script = generate_markdown_script(project_scope, slides)
        
        # Construct response
        response = {
            "project_id": present_request.project_id,
            "slides": [slide.dict() for slide in slides],
            "markdown_script": markdown_script,
            "status": "success"
        }
        
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "reason": f"Error generating architecture deck: {str(e)}"
            }
        )

def lookup_project_scope(project_id: str) -> Dict[str, Any]:
    """
    Look up stored project scope for a given project_id.
    
    Args:
        project_id: Project ID to look up
        
    Returns:
        Project scope dictionary or None if not found
    """
    # Import here to avoid circular imports
    import os
    import json
    
    # Path to memory store file
    memory_file = os.path.join(os.path.dirname(__file__), "memory_store.json")
    
    # Check if memory file exists
    if not os.path.exists(memory_file):
        print(f"Memory file not found: {memory_file}")
        return None
    
    # Load memories from file
    try:
        with open(memory_file, 'r') as f:
            memories = json.load(f)
    except Exception as e:
        print(f"Error loading memories: {str(e)}")
        return None
    
    # Find project scope memory for the given project_id
    for memory in memories:
        if (memory.get("project_id") == project_id and 
            memory.get("type") == "project_scope"):
            # Parse content as JSON
            try:
                return json.loads(memory.get("content", "{}"))
            except json.JSONDecodeError:
                print(f"Error parsing project scope content: {memory.get('content')}")
                return None
    
    # No project scope found
    print(f"No project scope found for project_id: {project_id}")
    return None

def generate_slides(project_scope: Dict[str, Any]) -> List[Slide]:
    """
    Generate presentation slides from a project scope.
    
    Args:
        project_scope: Project scope dictionary
        
    Returns:
        List of presentation slides
    """
    slides = []
    
    # Slide 1: Goal
    goal_slide = Slide(
        title="Goal",
        content=project_scope.get("goal", "No goal specified"),
        narration_text=f"This project aims to {project_scope.get('goal', 'accomplish a specific objective')}."
    )
    slides.append(goal_slide)
    
    # Slide 2: Modules Required
    if "required_modules" in project_scope:
        modules_content = "\n".join([f"- {module}" for module in project_scope["required_modules"]])
        modules_narration = f"To achieve this goal, we'll need {len(project_scope['required_modules'])} modules: {', '.join(project_scope['required_modules'])}."
        modules_slide = Slide(
            title="Modules Required",
            content=modules_content,
            narration_text=modules_narration
        )
        slides.append(modules_slide)
    
    # Slide 3: Agents Involved
    if "suggested_agents" in project_scope:
        agents_content = ""
        for agent in project_scope["suggested_agents"]:
            agent_name = agent.get("agent_name", "Unknown")
            tools = ", ".join(agent.get("tools", []))
            agents_content += f"- {agent_name.upper()} ({tools})\n"
        
        agents_narration = f"This project will involve {len(project_scope['suggested_agents'])} agents, each with specific responsibilities."
        agents_slide = Slide(
            title="Agents Involved",
            content=agents_content,
            narration_text=agents_narration
        )
        slides.append(agents_slide)
    
    # Slide 4: Known Risks
    if "known_risks" in project_scope:
        risks_content = "\n".join([f"- {risk}" for risk in project_scope["known_risks"]])
        risks_narration = f"We've identified {len(project_scope['known_risks'])} potential risks that need to be addressed."
        risks_slide = Slide(
            title="Known Risks",
            content=risks_content,
            narration_text=risks_narration
        )
        slides.append(risks_slide)
    
    # Slide 5: Execution Tasks
    if "execution_tasks" in project_scope:
        tasks_content = ""
        for i, task in enumerate(project_scope["execution_tasks"], 1):
            tasks_content += f"{i}. {task}\n"
        
        tasks_narration = f"The execution plan consists of {len(project_scope['execution_tasks'])} key tasks to complete the project."
        tasks_slide = Slide(
            title="Execution Tasks",
            content=tasks_content,
            narration_text=tasks_narration
        )
        slides.append(tasks_slide)
    
    # Slide 6: Confidence Assessment (if available)
    if "confidence_scores" in project_scope:
        confidence_content = ""
        for agent, score in project_scope["confidence_scores"].items():
            confidence_content += f"- {agent}: {score * 100:.0f}%\n"
        
        avg_confidence = sum(project_scope["confidence_scores"].values()) / len(project_scope["confidence_scores"])
        confidence_narration = f"Our overall confidence in this plan is {avg_confidence * 100:.0f}%."
        confidence_slide = Slide(
            title="Confidence Assessment",
            content=confidence_content,
            narration_text=confidence_narration
        )
        slides.append(confidence_slide)
    
    # Slide 7: Project Dependencies (if available)
    if "project_dependencies" in project_scope and project_scope["project_dependencies"]:
        dependencies_content = ""
        for module, deps in project_scope["project_dependencies"].items():
            dependencies_content += f"- {module} depends on: {', '.join(deps)}\n"
        
        dependencies_narration = "The project has several internal dependencies that must be managed."
        dependencies_slide = Slide(
            title="Project Dependencies",
            content=dependencies_content,
            narration_text=dependencies_narration
        )
        slides.append(dependencies_slide)
    
    return slides

def generate_markdown_script(project_scope: Dict[str, Any], slides: List[Slide]) -> str:
    """
    Generate a markdown script for the presentation.
    
    Args:
        project_scope: Project scope dictionary
        slides: List of presentation slides
        
    Returns:
        Markdown script for the presentation
    """
    markdown = f"# Promethios System Plan: {project_scope.get('project_id', 'Unnamed Project')}\n\n"
    
    # Add each slide as a section
    for slide in slides:
        markdown += f"## {slide.title}\n"
        markdown += f"{slide.content}\n\n"
    
    # Add summary section
    markdown += "## Summary\n"
    markdown += f"This plan outlines the implementation of {project_scope.get('goal', 'the project')}. "
    
    if "required_modules" in project_scope:
        markdown += f"It requires {len(project_scope['required_modules'])} modules "
        markdown += f"and involves {len(project_scope.get('suggested_agents', []))} agents. "
    
    if "execution_tasks" in project_scope:
        markdown += f"The execution will proceed through {len(project_scope['execution_tasks'])} key tasks. "
    
    if "known_risks" in project_scope:
        markdown += f"We've identified {len(project_scope['known_risks'])} risks to mitigate during implementation."
    
    return markdown
