"""
Plan Generate Module

This module implements the functionality for plan generation operations.
"""

import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("plan_generate")

def generate_plan(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a plan based on the provided goal and parameters.
    
    Args:
        request_data: Request data containing goal, plan_type, format, etc.
        
    Returns:
        Dictionary containing the generated plan
    """
    try:
        goal = request_data.get("goal", "")
        plan_type = request_data.get("plan_type", "task")
        format = request_data.get("format", "steps")
        context = request_data.get("context")
        constraints = request_data.get("constraints", [])
        max_steps = request_data.get("max_steps")
        agent_id = request_data.get("agent_id")
        loop_id = request_data.get("loop_id")
        
        # Validate goal
        if not goal.strip():
            return {
                "message": "Goal must not be empty",
                "goal": goal,
                "plan_type": plan_type,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Generate plan (in a real implementation, this would use an LLM or other planning system)
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        # Generate steps based on plan type and goal
        steps = _generate_steps(goal, plan_type, context, constraints, max_steps)
        
        # Calculate total steps and estimated completion time
        total_steps = len(steps)
        estimated_completion_time = _calculate_estimated_time(steps)
        
        # Generate content in the requested format
        content = _format_plan(steps, format, goal, plan_type)
        
        # Log the plan generation to memory
        _log_plan_generation(plan_id, goal, plan_type, total_steps)
        
        # Return the result
        result = {
            "plan_id": plan_id,
            "goal": goal,
            "plan_type": plan_type,
            "format": format,
            "total_steps": total_steps,
            "estimated_completion_time": estimated_completion_time,
            "agent_id": agent_id,
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        
        # Add steps or content based on format
        if format == "steps":
            result["steps"] = steps
        else:
            result["content"] = content
        
        return result
    
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        return {
            "message": f"Failed to generate plan: {str(e)}",
            "goal": request_data.get("goal"),
            "plan_type": request_data.get("plan_type"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def _generate_steps(
    goal: str,
    plan_type: str,
    context: Optional[str],
    constraints: List[str],
    max_steps: Optional[int]
) -> List[Dict[str, Any]]:
    """
    Generate steps for the plan based on the goal and parameters.
    
    Args:
        goal: Goal or objective for the plan
        plan_type: Type of plan to generate
        context: Additional context for plan generation
        constraints: List of constraints to consider
        max_steps: Maximum number of steps in the plan
        
    Returns:
        List of plan steps
    """
    # In a real implementation, this would use an LLM or other planning system
    # For this implementation, we'll use predefined templates based on plan type
    
    # Define step templates for different plan types
    templates = {
        "task": [
            {"description": "Analyze requirements and create specifications", "estimated_time": "2 hours"},
            {"description": "Design solution architecture", "estimated_time": "3 hours"},
            {"description": "Implement core functionality", "estimated_time": "8 hours"},
            {"description": "Write unit tests", "estimated_time": "4 hours"},
            {"description": "Perform integration testing", "estimated_time": "3 hours"},
            {"description": "Document the implementation", "estimated_time": "2 hours"},
            {"description": "Deploy to production", "estimated_time": "1 hour"}
        ],
        "project": [
            {"description": "Define project scope and objectives", "estimated_time": "1 day"},
            {"description": "Create project plan and timeline", "estimated_time": "2 days"},
            {"description": "Assemble project team", "estimated_time": "3 days"},
            {"description": "Develop project requirements", "estimated_time": "5 days"},
            {"description": "Design project architecture", "estimated_time": "7 days"},
            {"description": "Implement project components", "estimated_time": "14 days"},
            {"description": "Test and validate project", "estimated_time": "7 days"},
            {"description": "Deploy project to production", "estimated_time": "2 days"},
            {"description": "Conduct post-implementation review", "estimated_time": "3 days"}
        ],
        "sprint": [
            {"description": "Sprint planning meeting", "estimated_time": "2 hours"},
            {"description": "Daily standup meetings", "estimated_time": "15 minutes per day"},
            {"description": "Task implementation", "estimated_time": "8 days"},
            {"description": "Code reviews", "estimated_time": "1 day"},
            {"description": "Sprint demo preparation", "estimated_time": "2 hours"},
            {"description": "Sprint review meeting", "estimated_time": "1 hour"},
            {"description": "Sprint retrospective", "estimated_time": "1 hour"}
        ],
        "research": [
            {"description": "Define research question", "estimated_time": "1 day"},
            {"description": "Literature review", "estimated_time": "5 days"},
            {"description": "Develop research methodology", "estimated_time": "3 days"},
            {"description": "Collect data", "estimated_time": "7 days"},
            {"description": "Analyze data", "estimated_time": "5 days"},
            {"description": "Draw conclusions", "estimated_time": "3 days"},
            {"description": "Write research report", "estimated_time": "7 days"},
            {"description": "Present findings", "estimated_time": "1 day"}
        ],
        "analysis": [
            {"description": "Define analysis objectives", "estimated_time": "1 day"},
            {"description": "Collect relevant data", "estimated_time": "3 days"},
            {"description": "Clean and preprocess data", "estimated_time": "2 days"},
            {"description": "Perform exploratory data analysis", "estimated_time": "3 days"},
            {"description": "Apply analytical methods", "estimated_time": "4 days"},
            {"description": "Interpret results", "estimated_time": "2 days"},
            {"description": "Create visualizations", "estimated_time": "2 days"},
            {"description": "Write analysis report", "estimated_time": "3 days"},
            {"description": "Present findings", "estimated_time": "1 day"}
        ],
        "custom": [
            {"description": "Define custom plan objectives", "estimated_time": "1 day"},
            {"description": "Develop custom approach", "estimated_time": "2 days"},
            {"description": "Implement custom solution", "estimated_time": "5 days"},
            {"description": "Test custom solution", "estimated_time": "2 days"},
            {"description": "Deploy custom solution", "estimated_time": "1 day"}
        ]
    }
    
    # Get template for the requested plan type
    template = templates.get(plan_type, templates["custom"])
    
    # Adjust number of steps based on max_steps
    if max_steps is not None and max_steps > 0:
        template = template[:min(max_steps, len(template))]
    
    # Create steps with step numbers and dependencies
    steps = []
    for i, step_template in enumerate(template):
        step = {
            "step_number": i + 1,
            "description": step_template["description"],
            "estimated_time": step_template["estimated_time"],
            "dependencies": [i] if i > 0 else []
        }
        steps.append(step)
    
    return steps

def _calculate_estimated_time(steps: List[Dict[str, Any]]) -> str:
    """
    Calculate the estimated completion time for the entire plan.
    
    Args:
        steps: List of plan steps
        
    Returns:
        Estimated completion time as a string
    """
    # In a real implementation, this would consider dependencies and parallel execution
    # For this implementation, we'll sum up the estimated times
    
    # Extract time values and units
    times = []
    for step in steps:
        estimated_time = step.get("estimated_time", "")
        if estimated_time:
            times.append(estimated_time)
    
    # Count occurrences of each time unit
    minutes = 0
    hours = 0
    days = 0
    
    for time in times:
        if "minute" in time:
            minutes += int(time.split()[0])
        elif "hour" in time:
            hours += int(time.split()[0])
        elif "day" in time:
            days += int(time.split()[0])
    
    # Convert minutes to hours
    hours += minutes // 60
    minutes = minutes % 60
    
    # Convert hours to days
    days += hours // 8  # Assuming 8-hour workdays
    hours = hours % 8
    
    # Build the result string
    result = []
    if days > 0:
        result.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        result.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        result.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    
    return " ".join(result) if result else "Unknown"

def _format_plan(
    steps: List[Dict[str, Any]],
    format: str,
    goal: str,
    plan_type: str
) -> str:
    """
    Format the plan in the requested format.
    
    Args:
        steps: List of plan steps
        format: Output format for the plan
        goal: Goal or objective for the plan
        plan_type: Type of plan
        
    Returns:
        Formatted plan as a string
    """
    if format == "markdown":
        return _format_as_markdown(steps, goal, plan_type)
    elif format == "json":
        return json.dumps(steps, indent=2)
    elif format == "tree":
        return _format_as_tree(steps)
    elif format == "gantt":
        return _format_as_gantt(steps, goal)
    else:
        # Default to steps format (handled separately)
        return ""

def _format_as_markdown(steps: List[Dict[str, Any]], goal: str, plan_type: str) -> str:
    """
    Format the plan as Markdown.
    
    Args:
        steps: List of plan steps
        goal: Goal or objective for the plan
        plan_type: Type of plan
        
    Returns:
        Plan formatted as Markdown
    """
    lines = [
        f"# Plan: {goal}",
        f"**Type:** {plan_type.capitalize()}",
        "",
        "## Steps",
        ""
    ]
    
    for step in steps:
        step_number = step.get("step_number")
        description = step.get("description")
        estimated_time = step.get("estimated_time", "")
        dependencies = step.get("dependencies", [])
        
        line = f"{step_number}. {description}"
        if estimated_time:
            line += f" *(Est. {estimated_time})*"
        
        lines.append(line)
        
        if dependencies:
            deps = ", ".join([str(d) for d in dependencies])
            lines.append(f"   - Dependencies: Steps {deps}")
        
        lines.append("")
    
    return "\n".join(lines)

def _format_as_tree(steps: List[Dict[str, Any]]) -> str:
    """
    Format the plan as a tree structure.
    
    Args:
        steps: List of plan steps
        
    Returns:
        Plan formatted as a tree
    """
    lines = []
    
    for step in steps:
        step_number = step.get("step_number")
        description = step.get("description")
        estimated_time = step.get("estimated_time", "")
        dependencies = step.get("dependencies", [])
        
        indent = "  " * (len(dependencies))
        line = f"{indent}└─ Step {step_number}: {description}"
        if estimated_time:
            line += f" ({estimated_time})"
        
        lines.append(line)
    
    return "\n".join(lines)

def _format_as_gantt(steps: List[Dict[str, Any]], goal: str) -> str:
    """
    Format the plan as a simple Gantt chart representation.
    
    Args:
        steps: List of plan steps
        goal: Goal or objective for the plan
        
    Returns:
        Plan formatted as a Gantt chart
    """
    lines = [
        f"Gantt Chart: {goal}",
        "================================",
        ""
    ]
    
    # Calculate the maximum step description length for alignment
    max_desc_length = max([len(step.get("description", "")) for step in steps])
    
    # Create a simple Gantt chart
    for step in steps:
        step_number = step.get("step_number")
        description = step.get("description", "")
        estimated_time = step.get("estimated_time", "")
        
        # Pad description for alignment
        padded_desc = description.ljust(max_desc_length)
        
        # Create a bar based on estimated time
        bar_length = 1
        if "hour" in estimated_time:
            bar_length = int(estimated_time.split()[0])
        elif "day" in estimated_time:
            bar_length = int(estimated_time.split()[0]) * 8  # 8 hours per day
        
        bar = "=" * min(bar_length, 50)  # Cap at 50 characters
        
        line = f"Step {step_number}: {padded_desc} | {bar} ({estimated_time})"
        lines.append(line)
    
    return "\n".join(lines)

def _log_plan_generation(plan_id: str, goal: str, plan_type: str, total_steps: int) -> None:
    """
    Log plan generation to memory.
    
    Args:
        plan_id: Plan ID
        goal: Goal or objective for the plan
        plan_type: Type of plan
        total_steps: Total number of steps in the plan
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "plan_generate",
            "plan_id": plan_id,
            "goal": goal,
            "plan_type": plan_type,
            "total_steps": total_steps,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Plan generation logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: plan_generate_{plan_id}")
    
    except Exception as e:
        logger.error(f"Error logging plan generation: {str(e)}")
