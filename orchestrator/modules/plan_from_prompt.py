"""
Plan From Prompt Module

This module provides functionality to convert natural language prompts into structured loop plans.
"""

import json
import os
import sys
from datetime import datetime
import re

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.plan_validator import validate_and_log
from orchestrator.modules.agent_performance_tracker import get_all_agent_reports

# Available agent types
AVAILABLE_AGENTS = ["hal", "nova", "critic", "ash", "operator", "cto", "orchestrator"]

# Trust score threshold for agent exclusion
TRUST_SCORE_THRESHOLD = 0.4

def generate_plan_from_prompt(prompt: str, loop_id: int, memory: dict = None, override_agents: list = None) -> dict:
    """
    Generates a structured loop plan from a natural language prompt.
    
    Args:
        prompt (str): The natural language prompt from the operator
        loop_id (int): The unique identifier for this loop
        memory (dict, optional): The memory dictionary containing agent performance data
        override_agents (list, optional): List of agent IDs to include regardless of trust score
        
    Returns:
        dict: A structured loop plan object
    """
    if not prompt or len(prompt.strip()) < 10:
        raise ValueError("Prompt is too short or empty. Please provide a more detailed prompt.")
    
    # Extract goals from the prompt
    goals = extract_goals(prompt)
    if not goals:
        goals = ["Process and execute operator request"]
    
    # Determine appropriate agents based on the prompt content and trust scores
    agents, agent_selection_trace = determine_agents(prompt, memory, override_agents)
    
    # Predict files that will be created or modified
    planned_files = predict_files(prompt)
    
    # Determine if any specific tools are required
    tools_required = predict_tools(prompt)
    
    # Create the loop plan object
    loop_plan = {
        "loop_id": loop_id,
        "agents": agents,
        "goals": goals,
        "planned_files": planned_files,
        "confirmed": False,
        "confirmed_by": None,
        "confirmed_at": None,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_selection_trace": agent_selection_trace
    }
    
    # Add optional fields if they have values
    if tools_required:
        loop_plan["tool_requirements"] = tools_required
    
    return loop_plan

def extract_goals(prompt: str) -> list:
    """
    Extracts goals from the prompt.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: Extracted goals
    """
    # Look for explicit goal statements
    goal_patterns = [
        r"(?:goal|objective|aim|purpose|task)(?:s)?\s*(?:is|are|:)?\s*(?:to)?\s*(.*?)(?:\.|$)",
        r"(?:I want|I need|I'd like|Please|Can you)\s+(.*?)(?:\.|$)",
        r"(?:Create|Build|Develop|Implement|Make)\s+(.*?)(?:\.|$)"
    ]
    
    goals = []
    for pattern in goal_patterns:
        matches = re.finditer(pattern, prompt, re.IGNORECASE)
        for match in matches:
            goal = match.group(1).strip()
            if goal and len(goal) > 5 and goal not in goals:
                goals.append(goal)
    
    # If no explicit goals found, break the prompt into potential tasks
    if not goals and len(prompt) > 10:
        sentences = re.split(r'[.!?]', prompt)
        for sentence in sentences:
            if len(sentence.strip()) > 10:
                goals.append(sentence.strip())
                if len(goals) >= 3:  # Limit to 3 goals if extracting from sentences
                    break
    
    # If goals are too vague or ambiguous, add a generic goal
    if goals and all(len(goal.split()) < 4 for goal in goals):
        goals.append("Process and execute operator request")
    
    return goals

def determine_agents(prompt: str, memory: dict = None, override_agents: list = None) -> tuple:
    """
    Determines which agents should be involved based on the prompt content and trust scores.
    
    Args:
        prompt (str): The natural language prompt
        memory (dict, optional): The memory dictionary containing agent performance data
        override_agents (list, optional): List of agent IDs to include regardless of trust score
        
    Returns:
        tuple: (list of agent names, list of selection trace dictionaries)
    """
    # Default agent sequence for most tasks
    default_agents = ["hal", "nova", "critic"]
    
    # Initialize agent selection trace
    agent_selection_trace = []
    
    # Initialize excluded agents list
    excluded_agents = []
    
    # Ensure override_agents is a list
    if override_agents is None:
        override_agents = []
    
    # Get agent trust scores if memory is provided
    agent_trust_scores = {}
    if memory and "agent_performance" in memory:
        try:
            agent_reports = get_all_agent_reports(memory)
            for agent_id, report in agent_reports.items():
                agent_trust_scores[agent_id] = report["trust_score"]
        except Exception as e:
            # If there's an error getting trust scores, log it and continue with default agents
            print(f"Error getting agent trust scores: {str(e)}")
    
    # Check if specific agents are mentioned or implied
    prompt_lower = prompt.lower()
    
    # Determine task type and initial agent selection
    task_type = "general"
    initial_agents = []
    
    # Check for specific development tasks
    if any(term in prompt_lower for term in ["code", "develop", "implement", "programming", "software", "application"]):
        task_type = "development"
        initial_agents = ["hal", "nova", "critic"]
    
    # Check for design or UI tasks
    elif any(term in prompt_lower for term in ["design", "ui", "interface", "layout", "visual", "css", "style"]):
        task_type = "design"
        initial_agents = ["nova", "hal", "critic"]
    
    # Check for analysis or research tasks
    elif any(term in prompt_lower for term in ["analyze", "research", "investigate", "study", "report", "data"]):
        task_type = "analysis"
        initial_agents = ["hal", "critic", "nova"]
    
    # Check for system or architecture tasks
    elif any(term in prompt_lower for term in ["system", "architecture", "infrastructure", "performance", "optimize"]):
        task_type = "system"
        initial_agents = ["hal", "critic", "cto"]
    
    # If specific agents are mentioned, include them
    mentioned_agents = []
    for agent in AVAILABLE_AGENTS:
        if agent in prompt_lower:
            mentioned_agents.append(agent)
    
    if mentioned_agents:
        # Ensure we have at least the three core agents
        for agent in default_agents:
            if agent not in mentioned_agents:
                mentioned_agents.append(agent)
        initial_agents = mentioned_agents[:5]  # Limit to 5 agents
    
    # If no specific task type was identified, use default agents
    if not initial_agents:
        initial_agents = default_agents
    
    # Apply trust scores to filter and sort agents
    final_agents = []
    
    # First, process override agents - these are included regardless of trust score
    for agent in override_agents:
        if agent in AVAILABLE_AGENTS and agent not in final_agents:
            final_agents.append(agent)
            
            # Determine reason for inclusion
            trust_score = agent_trust_scores.get(agent)
            if trust_score is not None and trust_score < TRUST_SCORE_THRESHOLD:
                reason = "Included due to operator override"
            else:
                reason = "Included due to operator override"
                
            agent_selection_trace.append({
                "agent": agent,
                "trust_score": trust_score,
                "reason": reason
            })
    
    # Process each agent based on trust score
    for agent in initial_agents:
        # Skip if agent already included via override
        if agent in final_agents:
            continue
            
        # Skip system agents that are always included
        if agent in ["operator", "orchestrator"]:
            final_agents.append(agent)
            agent_selection_trace.append({
                "agent": agent,
                "trust_score": None,
                "reason": "System agent always included"
            })
            continue
        
        # Check if agent has trust score data
        if agent in agent_trust_scores:
            trust_score = agent_trust_scores[agent]
            
            # Check if agent should be excluded based on trust score
            if trust_score < TRUST_SCORE_THRESHOLD:
                excluded_agents.append(agent)
                agent_selection_trace.append({
                    "agent": agent,
                    "trust_score": trust_score,
                    "excluded": True,
                    "reason": f"Trust score below threshold ({trust_score:.2f} < {TRUST_SCORE_THRESHOLD})"
                })
            else:
                final_agents.append(agent)
                
                # Determine reason for inclusion
                reason = "Sufficient trust score"
                if trust_score > 0.8:
                    reason = "High trust score"
                elif trust_score > 0.6:
                    reason = "Good trust score"
                
                agent_selection_trace.append({
                    "agent": agent,
                    "trust_score": trust_score,
                    "reason": reason
                })
        else:
            # No trust data available for this agent
            final_agents.append(agent)
            agent_selection_trace.append({
                "agent": agent,
                "trust_score": None,
                "reason": "No trust data available, using default inclusion"
            })
    
    # Ensure we have at least the critic agent for validation
    if "critic" not in final_agents:
        final_agents.append("critic")
        agent_selection_trace.append({
            "agent": "critic",
            "trust_score": agent_trust_scores.get("critic"),
            "reason": "Critical agent added for validation purposes"
        })
    
    # Ensure we have at least one primary agent (hal or nova)
    if "hal" not in final_agents and "nova" not in final_agents:
        # Add the agent with the highest trust score, or hal by default
        if "hal" in agent_trust_scores and "nova" in agent_trust_scores:
            if agent_trust_scores["hal"] >= agent_trust_scores["nova"]:
                final_agents.append("hal")
                agent_selection_trace.append({
                    "agent": "hal",
                    "trust_score": agent_trust_scores["hal"],
                    "reason": "Added as primary agent (higher trust than nova)"
                })
            else:
                final_agents.append("nova")
                agent_selection_trace.append({
                    "agent": "nova",
                    "trust_score": agent_trust_scores["nova"],
                    "reason": "Added as primary agent (higher trust than hal)"
                })
        else:
            final_agents.append("hal")
            agent_selection_trace.append({
                "agent": "hal",
                "trust_score": agent_trust_scores.get("hal"),
                "reason": "Added as default primary agent"
            })
    
    return final_agents, agent_selection_trace

def predict_files(prompt: str) -> list:
    """
    Predicts which files will be created or modified based on the prompt.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: List of predicted file paths
    """
    prompt_lower = prompt.lower()
    planned_files = []
    
    # Look for explicit file mentions
    file_patterns = [
        r'(?:file|document|code)\s+(?:called|named)?\s*["\']?([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)["\']?',
        r'([a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+)',
        r'([a-zA-Z0-9_\-]+\.(js|py|jsx|ts|tsx|html|css|json|md|txt))'
    ]
    
    for pattern in file_patterns:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            file = match.group(1).strip()
            if file and file not in planned_files:
                planned_files.append(file)
    
    # Predict files based on task type
    if not planned_files:
        # UI/Frontend tasks
        if any(term in prompt_lower for term in ["ui", "interface", "component", "react", "frontend"]):
            planned_files.extend(["src/components/Component.jsx", "src/styles/component.css"])
        
        # Backend tasks
        elif any(term in prompt_lower for term in ["api", "backend", "server", "database"]):
            planned_files.extend(["src/api/endpoint.js", "src/models/model.js"])
        
        # Documentation tasks
        elif any(term in prompt_lower for term in ["document", "readme", "documentation"]):
            planned_files.extend(["docs/README.md", "docs/usage.md"])
        
        # Data analysis tasks
        elif any(term in prompt_lower for term in ["data", "analysis", "report"]):
            planned_files.extend(["data/analysis.py", "reports/findings.md"])
        
        # Default case
        else:
            planned_files.extend(["src/main.js", "README.md"])
    
    return planned_files

def predict_tools(prompt: str) -> list:
    """
    Predicts which tools might be required based on the prompt.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: List of predicted required tools
    """
    prompt_lower = prompt.lower()
    tools_required = []
    
    # Map keywords to tools
    tool_keywords = {
        "form": "form_builder",
        "chart": "chart_generator",
        "graph": "chart_generator",
        "visualization": "chart_generator",
        "database": "database_connector",
        "sql": "database_connector",
        "api": "api_client",
        "http": "api_client",
        "fetch": "api_client",
        "authentication": "auth_service",
        "login": "auth_service",
        "file upload": "file_uploader",
        "upload": "file_uploader",
        "markdown": "markdown_parser",
        "pdf": "pdf_generator",
        "report": "pdf_generator",
        "email": "email_service",
        "notification": "notification_service",
        "alert": "notification_service",
        "map": "map_service",
        "location": "map_service",
        "geocode": "map_service",
        "payment": "payment_processor",
        "checkout": "payment_processor",
        "search": "search_engine",
        "filter": "search_engine",
        "analytics": "analytics_tracker",
        "tracking": "analytics_tracker",
        "image": "image_processor",
        "photo": "image_processor",
        "video": "video_processor",
        "audio": "audio_processor",
        "sound": "audio_processor",
        "chat": "chat_service",
        "message": "chat_service",
        "calendar": "calendar_service",
        "schedule": "calendar_service",
        "appointment": "calendar_service"
    }
    
    for keyword, tool in tool_keywords.items():
        if keyword in prompt_lower and tool not in tools_required:
            tools_required.append(tool)
    
    return tools_required

def plan_from_prompt_driver(project_id: str, prompt: str, memory: dict = None, override_agents: list = None):
    """
    Orchestrator-facing entrypoint for generating loop plans from prompts.
    
    Args:
        project_id (str): The project identifier
        prompt (str): The natural language prompt
        memory (dict, optional): The memory dictionary containing agent performance data
        override_agents (list, optional): List of agent IDs to include regardless of trust score
        
    Returns:
        dict or None: The validated loop plan or None if validation fails
    """
    try:
        # Generate a loop ID (in a real system, this would be from a sequence or database)
        loop_id = int(datetime.now().timestamp()) % 1000
        
        # Check if prompt is ambiguous
        is_ambiguous = len(prompt.strip().split()) < 5 or prompt.strip().lower() in [
            "do the thing with the stuff", "make it work better"
        ]
        
        # Generate the plan from the prompt
        loop_plan = generate_plan_from_prompt(prompt, loop_id, memory, override_agents)
        
        # Validate the plan
        is_valid, errors, trace = validate_and_log(loop_plan)
        
        # Log the trace to memory
        log_to_memory(project_id, {
            "orchestrator_traces": [trace]
        })
        
        # Log warning if prompt is ambiguous
        if is_ambiguous:
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            log_to_memory(project_id, {
                "orchestrator_warnings": [{
                    "type": "ambiguous_prompt",
                    "timestamp": timestamp,
                    "message": "Prompt is ambiguous or vague. Generated plan may not match expectations."
                }]
            })
        
        if not is_valid:
            # Log validation errors to memory and chat
            error_message = "; ".join(errors)
            log_to_memory(project_id, {
                "orchestrator_warnings": [{
                    "type": "plan_validation_failed",
                    "timestamp": trace["timestamp"],
                    "errors": errors
                }]
            })
            
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"Failed to create loop plan: {error_message}",
                "timestamp": trace["timestamp"]
            })
            
            return None
        
        # Log the successful plan to memory
        log_to_memory(project_id, {
            "loop_plans": [loop_plan]
        })
        
        # Log agent selection trace to memory
        if "agent_selection_trace" in loop_plan:
            log_to_memory(project_id, {
                "loop_trace": {
                    str(loop_id): {
                        "agent_selection_trace": loop_plan["agent_selection_trace"]
                    }
                }
            })
        
        # Extract excluded agents from trace
        excluded_agents = [entry["agent"] for entry in loop_plan.get("agent_selection_trace", []) 
                          if entry.get("excluded", False)]
        
        # Log to chat with warning if ambiguous
        message = f"Created loop plan with {len(loop_plan['goals'])} goals and {len(loop_plan['agents'])} agents."
        
        # Add information about agent selection based on trust
        if excluded_agents:
            message += f" Excluded {len(excluded_agents)} agent(s) due to low trust scores: {', '.join(excluded_agents)}."
            
        if override_agents:
            message += f" Operator override applied for: {', '.join(override_agents)}."
            
        if is_ambiguous:
            message += " Note: Prompt was ambiguous, plan may need refinement."
            
        # Log to chat with the message and loop plan
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": trace["timestamp"],
            "loop_plan": loop_plan,
            "agent_selection_info": {
                "included_agents": loop_plan["agents"],
                "excluded_agents": excluded_agents,
                "override_agents": override_agents if override_agents else []
            }
        })
        
        # Log to sandbox
        log_to_sandbox(project_id, loop_plan)
        
        return loop_plan
        
    except ValueError as e:
        # Handle errors in plan generation
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        log_to_memory(project_id, {
            "orchestrator_warnings": [{
                "type": "plan_generation_failed",
                "timestamp": timestamp,
                "error": str(e)
            }]
        })
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"Failed to generate loop plan: {str(e)}. Please provide a more detailed prompt.",
            "timestamp": timestamp
        })
        
        return None
    except Exception as e:
        # Handle unexpected errors
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        log_to_memory(project_id, {
            "orchestrator_errors": [{
                "type": "unexpected_error",
                "timestamp": timestamp,
                "error": str(e)
            }]
        })
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"An unexpected error occurred: {str(e)}. Please try again.",
            "timestamp": timestamp
        })
        
        return None

def log_to_memory(project_id: str, data: dict):
    """
    Logs data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

def log_to_sandbox(project_id: str, loop_plan: dict):
    """
    Logs a loop plan to the orchestrator sandbox.
    
    Args:
        project_id (str): The project ID
        loop_plan (dict): The loop plan to log
    """
    # In a real implementation, this would update the orchestrator sandbox
    print(f"Logging to sandbox for project {project_id}:")
    print(json.dumps(loop_plan, indent=2))

if __name__ == "__main__":
    # Example usage
    prompt = "Create a new React component for displaying user profiles with avatar, name, and bio."
    project_id = "lifetree_001"
    
    # Example memory with agent performance data
    example_memory = {
        "agent_performance": {
            "hal": {
                "trust_score": 0.85,
                "loops_participated": 10,
                "schema_validations": {"passed": 9, "failed": 1},
                "reflection_validations": {"passed": 8, "failed": 2},
                "critic_rejections": 1,
                "operator_rejections": 0,
                "history": [],
                "last_updated": datetime.utcnow().isoformat() + "Z"
            },
            "nova": {
                "trust_score": 0.92,
                "loops_participated": 8,
                "schema_validations": {"passed": 8, "failed": 0},
                "reflection_validations": {"passed": 7, "failed": 1},
                "critic_rejections": 0,
                "operator_rejections": 0,
                "history": [],
                "last_updated": datetime.utcnow().isoformat() + "Z"
            },
            "ash": {
                "trust_score": 0.38,
                "loops_participated": 5,
                "schema_validations": {"passed": 2, "failed": 3},
                "reflection_validations": {"passed": 1, "failed": 4},
                "critic_rejections": 2,
                "operator_rejections": 1,
                "history": [],
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
        }
    }
    
    # Example override
    override_agents = ["ash"]
    
    plan = plan_from_prompt_driver(project_id, prompt, example_memory, override_agents)
    
    if plan:
        print("\nSuccessfully created loop plan:")
        print(json.dumps(plan, indent=2))
    else:
        print("\nFailed to create loop plan due to errors.")
