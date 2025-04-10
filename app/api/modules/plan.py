"""
API endpoint for the Plan Generator module.

This module provides REST API endpoints for generating structured task plans
based on agent persona, project context, and objectives.
"""

print("📁 Loaded: plan.py (Plan Generator route file)")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import traceback
import uuid
from datetime import datetime

# Import agent registry and memory-related functions
from app.api.modules.agent import agent_registry, ensure_core_agents_exist
from app.modules.memory_writer import write_memory, memory_store

# Import plan models
from app.api.modules.plan_models import (
    PlanGenerateRequest,
    PlanGenerateResponse,
    TaskPlan
)

# Configure logging
logger = logging.getLogger("api.modules.plan")

# Create router
router = APIRouter(prefix="/modules/plan", tags=["Plan Generator"])
print("🧠 Route defined: /api/modules/plan/generate -> generate_task_plan")

@router.post("/generate")
async def generate_task_plan(request: Request):
    """
    Generate a structured task plan based on agent persona, project context, and objectives.
    
    This endpoint uses the agent's persona and the provided objective to generate
    a structured plan with a list of tasks, each with a title, type, and day/sequence.
    The plan is also written to memory for future reference.
    
    Request body:
    - agent_id: ID of the agent to generate the plan for
    - project_id: ID of the project context
    - memory_trace_id: ID for memory tracing
    - persona: Persona or role to use for plan generation
    - objective: Main objective or goal of the plan
    - input_data: Additional parameters for customization (e.g., duration, theme)
    
    Returns:
    - status: "success" if successful
    - log: Description of the plan generation process
    - tasks: List of tasks with title, type, and day/sequence
    - task_id: ID of the generated plan
    - project_id: ID of the project context
    - memory_trace_id: ID for memory tracing
    """
    try:
        # Parse request body
        body = await request.json()
        plan_request = PlanGenerateRequest(**body)
        
        # Ensure core agents exist
        ensure_core_agents_exist()
        
        # Check if agent exists
        if plan_request.agent_id not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "log": f"Agent with ID '{plan_request.agent_id}' not found"
                }
            )
        
        # Generate task_id if not provided
        task_id = plan_request.task_id if plan_request.task_id else f"plan-{uuid.uuid4()}"
        
        # Generate memory_trace_id if not provided
        memory_trace_id = plan_request.memory_trace_id if plan_request.memory_trace_id else f"trace-{uuid.uuid4()}"
        
        # Get agent metadata from registry
        agent_data = agent_registry[plan_request.agent_id]
        
        # Generate tasks based on persona and objective
        tasks = generate_tasks_for_persona(
            persona=plan_request.persona,
            objective=plan_request.objective,
            input_data=plan_request.input_data
        )
        
        # Create plan summary for memory
        plan_summary = f"Plan generated for objective: {plan_request.objective}\n\n"
        plan_summary += f"Persona: {plan_request.persona}\n\n"
        plan_summary += "Tasks:\n"
        for task in tasks:
            plan_summary += f"- Day {task.day}: {task.title} ({task.type})\n"
        
        # Write plan to memory
        memory = write_memory(
            agent_id=plan_request.agent_id,
            type="plan_generated",
            content=plan_summary,
            tags=["plan", plan_request.persona, "generated"],
            project_id=plan_request.project_id,
            status="active",
            task_type="plan",
            task_id=task_id,
            memory_trace_id=memory_trace_id
        )
        
        # Create response
        response = PlanGenerateResponse(
            status="success",
            log=f"Generated task plan using {plan_request.agent_id.upper()}'s {plan_request.persona} profile.",
            tasks=tasks,
            task_id=task_id,
            project_id=plan_request.project_id,
            memory_trace_id=memory_trace_id
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"Error generating task plan: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "log": f"Failed to generate task plan: {str(e)}"
            }
        )

def generate_tasks_for_persona(persona: str, objective: str, input_data: Dict[str, Any]) -> List[TaskPlan]:
    """
    Generate tasks based on the persona, objective, and input data.
    
    This function creates a structured list of tasks appropriate for the given
    persona and objective, taking into account any additional input parameters.
    
    Args:
        persona: The persona or role to use for plan generation
        objective: The main objective or goal of the plan
        input_data: Additional parameters for customization
        
    Returns:
        A list of TaskPlan objects with title, type, and day/sequence
    """
    tasks = []
    
    # Extract common input parameters
    theme = input_data.get("theme", "general")
    duration = input_data.get("duration", "7 days")
    
    # Parse duration to get number of days
    try:
        if isinstance(duration, str) and "day" in duration.lower():
            days = int(duration.lower().split("day")[0].strip())
        elif isinstance(duration, int):
            days = duration
        else:
            days = 7  # Default to 7 days
    except:
        days = 7  # Default to 7 days
    
    # Limit to reasonable range
    days = max(1, min(days, 30))
    
    # Generate tasks based on persona
    if persona.lower() == "creative coach":
        tasks = generate_creative_coach_tasks(objective, theme, days)
    elif persona.lower() == "productivity mentor":
        tasks = generate_productivity_mentor_tasks(objective, theme, days)
    elif persona.lower() == "learning guide":
        tasks = generate_learning_guide_tasks(objective, theme, days)
    elif persona.lower() == "wellness advisor":
        tasks = generate_wellness_advisor_tasks(objective, theme, days)
    else:
        # Default generic tasks
        tasks = generate_generic_tasks(objective, theme, days)
    
    return tasks

def generate_creative_coach_tasks(objective: str, theme: str, days: int) -> List[TaskPlan]:
    """Generate tasks for a creative coach persona"""
    creative_tasks = [
        TaskPlan(day=1, title="Reflect on a past creative success", type="reflection"),
        TaskPlan(day=2, title="Write a short story from your dream journal", type="writing"),
        TaskPlan(day=3, title="Create a visual mood board for inspiration", type="visual"),
        TaskPlan(day=4, title="Practice free writing for 15 minutes", type="writing"),
        TaskPlan(day=5, title="Explore a new creative technique", type="exploration"),
        TaskPlan(day=6, title="Collaborate with someone on a mini project", type="collaboration"),
        TaskPlan(day=7, title="Review the week and set creative intentions", type="planning")
    ]
    
    # If more days are requested, add additional creative tasks
    additional_tasks = [
        TaskPlan(day=8, title="Try a creative exercise outside your comfort zone", type="challenge"),
        TaskPlan(day=9, title="Create something inspired by nature", type="inspiration"),
        TaskPlan(day=10, title="Revisit and revise an old creative project", type="revision"),
        TaskPlan(day=11, title="Study the work of a creator you admire", type="learning"),
        TaskPlan(day=12, title="Practice mindfulness to enhance creativity", type="mindfulness"),
        TaskPlan(day=13, title="Create something with limited resources", type="constraint"),
        TaskPlan(day=14, title="Share your work and gather feedback", type="feedback")
    ]
    
    # Add additional tasks if needed
    while len(creative_tasks) < days:
        next_task = additional_tasks[(len(creative_tasks) - 7) % len(additional_tasks)]
        creative_tasks.append(TaskPlan(
            day=len(creative_tasks) + 1,
            title=next_task.title,
            type=next_task.type
        ))
    
    # Limit to requested number of days
    return creative_tasks[:days]

def generate_productivity_mentor_tasks(objective: str, theme: str, days: int) -> List[TaskPlan]:
    """Generate tasks for a productivity mentor persona"""
    productivity_tasks = [
        TaskPlan(day=1, title="Audit your current workflow and identify bottlenecks", type="analysis"),
        TaskPlan(day=2, title="Set up a task management system", type="organization"),
        TaskPlan(day=3, title="Practice time blocking for focused work", type="technique"),
        TaskPlan(day=4, title="Eliminate three unnecessary tasks from your routine", type="simplification"),
        TaskPlan(day=5, title="Learn and apply the Pomodoro Technique", type="method"),
        TaskPlan(day=6, title="Create templates for recurring tasks", type="automation"),
        TaskPlan(day=7, title="Review progress and adjust your productivity system", type="review")
    ]
    
    # If more days are requested, add additional productivity tasks
    additional_tasks = [
        TaskPlan(day=8, title="Practice saying no to low-priority requests", type="boundaries"),
        TaskPlan(day=9, title="Implement a weekly planning ritual", type="planning"),
        TaskPlan(day=10, title="Optimize your digital workspace", type="environment"),
        TaskPlan(day=11, title="Batch similar tasks together", type="batching"),
        TaskPlan(day=12, title="Delegate or outsource one task", type="delegation"),
        TaskPlan(day=13, title="Create a distraction management plan", type="focus"),
        TaskPlan(day=14, title="Measure and celebrate your productivity wins", type="reflection")
    ]
    
    # Add additional tasks if needed
    while len(productivity_tasks) < days:
        next_task = additional_tasks[(len(productivity_tasks) - 7) % len(additional_tasks)]
        productivity_tasks.append(TaskPlan(
            day=len(productivity_tasks) + 1,
            title=next_task.title,
            type=next_task.type
        ))
    
    # Limit to requested number of days
    return productivity_tasks[:days]

def generate_learning_guide_tasks(objective: str, theme: str, days: int) -> List[TaskPlan]:
    """Generate tasks for a learning guide persona"""
    learning_tasks = [
        TaskPlan(day=1, title="Define your learning goals and outcomes", type="planning"),
        TaskPlan(day=2, title="Research and gather learning resources", type="research"),
        TaskPlan(day=3, title="Create a structured learning schedule", type="organization"),
        TaskPlan(day=4, title="Practice active reading techniques", type="technique"),
        TaskPlan(day=5, title="Apply new knowledge through a practical exercise", type="application"),
        TaskPlan(day=6, title="Teach someone else what you've learned", type="teaching"),
        TaskPlan(day=7, title="Review and consolidate your learning", type="review")
    ]
    
    # If more days are requested, add additional learning tasks
    additional_tasks = [
        TaskPlan(day=8, title="Connect new information to existing knowledge", type="connection"),
        TaskPlan(day=9, title="Test yourself with practice questions", type="assessment"),
        TaskPlan(day=10, title="Explore a related subtopic", type="exploration"),
        TaskPlan(day=11, title="Create visual summaries or mind maps", type="visualization"),
        TaskPlan(day=12, title="Join a discussion group on the topic", type="collaboration"),
        TaskPlan(day=13, title="Apply spaced repetition to reinforce learning", type="retention"),
        TaskPlan(day=14, title="Reflect on your learning process", type="metacognition")
    ]
    
    # Add additional tasks if needed
    while len(learning_tasks) < days:
        next_task = additional_tasks[(len(learning_tasks) - 7) % len(additional_tasks)]
        learning_tasks.append(TaskPlan(
            day=len(learning_tasks) + 1,
            title=next_task.title,
            type=next_task.type
        ))
    
    # Limit to requested number of days
    return learning_tasks[:days]

def generate_wellness_advisor_tasks(objective: str, theme: str, days: int) -> List[TaskPlan]:
    """Generate tasks for a wellness advisor persona"""
    wellness_tasks = [
        TaskPlan(day=1, title="Assess your current wellness baseline", type="assessment"),
        TaskPlan(day=2, title="Create a morning routine for wellbeing", type="routine"),
        TaskPlan(day=3, title="Practice mindful breathing for 10 minutes", type="mindfulness"),
        TaskPlan(day=4, title="Try a new physical activity", type="movement"),
        TaskPlan(day=5, title="Focus on balanced nutrition for the day", type="nutrition"),
        TaskPlan(day=6, title="Practice digital detox for part of the day", type="detox"),
        TaskPlan(day=7, title="Reflect on your wellness journey", type="reflection")
    ]
    
    # If more days are requested, add additional wellness tasks
    additional_tasks = [
        TaskPlan(day=8, title="Practice gratitude journaling", type="gratitude"),
        TaskPlan(day=9, title="Improve your sleep environment", type="sleep"),
        TaskPlan(day=10, title="Connect with a friend or loved one", type="connection"),
        TaskPlan(day=11, title="Spend time in nature", type="nature"),
        TaskPlan(day=12, title="Learn a stress management technique", type="stress"),
        TaskPlan(day=13, title="Create boundaries for work-life balance", type="boundaries"),
        TaskPlan(day=14, title="Plan self-care activities for the coming week", type="planning")
    ]
    
    # Add additional tasks if needed
    while len(wellness_tasks) < days:
        next_task = additional_tasks[(len(wellness_tasks) - 7) % len(additional_tasks)]
        wellness_tasks.append(TaskPlan(
            day=len(wellness_tasks) + 1,
            title=next_task.title,
            type=next_task.type
        ))
    
    # Limit to requested number of days
    return wellness_tasks[:days]

def generate_generic_tasks(objective: str, theme: str, days: int) -> List[TaskPlan]:
    """Generate generic tasks for any persona"""
    generic_tasks = [
        TaskPlan(day=1, title=f"Define goals and objectives for {theme}", type="planning"),
        TaskPlan(day=2, title=f"Research best practices related to {theme}", type="research"),
        TaskPlan(day=3, title=f"Create an action plan for {objective}", type="planning"),
        TaskPlan(day=4, title=f"Implement first steps toward {objective}", type="action"),
        TaskPlan(day=5, title=f"Review progress and adjust approach", type="review"),
        TaskPlan(day=6, title=f"Address challenges encountered with {theme}", type="problem-solving"),
        TaskPlan(day=7, title=f"Reflect on learnings and plan next steps", type="reflection")
    ]
    
    # If more days are requested, add additional generic tasks
    additional_tasks = [
        TaskPlan(day=8, title=f"Explore new aspects of {theme}", type="exploration"),
        TaskPlan(day=9, title=f"Gather feedback on your progress", type="feedback"),
        TaskPlan(day=10, title=f"Refine your approach based on experience", type="refinement"),
        TaskPlan(day=11, title=f"Share your progress with others", type="sharing"),
        TaskPlan(day=12, title=f"Integrate new insights about {theme}", type="integration"),
        TaskPlan(day=13, title=f"Overcome obstacles to {objective}", type="problem-solving"),
        TaskPlan(day=14, title=f"Celebrate progress and set new goals", type="celebration")
    ]
    
    # Add additional tasks if needed
    while len(generic_tasks) < days:
        next_task = additional_tasks[(len(generic_tasks) - 7) % len(additional_tasks)]
        generic_tasks.append(TaskPlan(
            day=len(generic_tasks) + 1,
            title=next_task.title.replace("{theme}", theme).replace("{objective}", objective),
            type=next_task.type
        ))
    
    # Limit to requested number of days
    return generic_tasks[:days]
