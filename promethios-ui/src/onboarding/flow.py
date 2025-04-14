"""
Agent Onboarding Flow Design

This module defines the onboarding flow for new agents in the Promethios system.
It implements a structured process to teach agents their role, tools, behavior
expectations, and reflection protocol using standard tool calls and memory operations.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional

# Define the onboarding flow steps and their requirements
ONBOARDING_STEPS = [
    {
        "id": "self_check",
        "description": "Agent performs self-check to identify available tools and status",
        "tool": "agent.self.check",
        "memory_prompt": "Who am I, and what tools am I responsible for?",
        "reflection_template": "My role is {agent_role}. I am responsible for building systems using assigned toolkits."
    },
    {
        "id": "core_values",
        "description": "Agent reads and internalizes core values",
        "tool": "read.doc",
        "tool_args": {"path": "/docs/core_values.md"},
        "memory_prompt": "What values must I uphold while operating?",
        "reflection_template": "I must uphold the Promethios Core Values: Transparency, Accountability, Operator Alignment, Fail Forward, Goal Awareness, and Continual Learning."
    },
    {
        "id": "tool_familiarization",
        "description": "Agent performs a dry-run of a primary tool",
        "tool_hal": "code.write",
        "tool_ash": "copy.tagline",
        "memory_type": "action",
        "reflection_template": "I completed a task using my toolkit. I understand how tool execution and memory logging work."
    },
    {
        "id": "final_checkpoint",
        "description": "Agent completes onboarding and reports to Orchestrator",
        "checkpoint_id": "agent_onboarding_complete",
        "memory_type": "checkpoint",
        "escalation_path": "If agent fails to complete reflection or errors, escalate to operator."
    }
]

# Define the memory and tagging structure
ONBOARDING_TAGS = ["onboarding", "values", "tool_familiarization"]

def generate_goal_id(agent_id: str) -> str:
    """Generate the onboarding goal ID for a specific agent."""
    return f"agent_onboarding_{agent_id}"

def get_agent_specific_tool(agent_id: str, step: Dict[str, Any]) -> str:
    """Get the appropriate tool for a specific agent based on the step configuration."""
    if agent_id.lower() == "hal":
        return step.get("tool_hal", step.get("tool", ""))
    elif agent_id.lower() == "ash":
        return step.get("tool_ash", step.get("tool", ""))
    else:
        # Default to the generic tool if agent-specific one isn't defined
        return step.get("tool", "")

def create_memory_entry(
    agent_id: str,
    step_id: str,
    memory_type: str,
    content: str,
    goal_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a memory entry for the onboarding process.
    
    Args:
        agent_id: ID of the agent being onboarded
        step_id: ID of the onboarding step
        memory_type: Type of memory (system, reflection, action, checkpoint)
        content: Content of the memory
        goal_id: Optional goal ID (defaults to agent_onboarding_{agent_id})
        tags: Optional list of tags (defaults to ONBOARDING_TAGS)
        tool_name: Optional tool name for tool-related memories
        
    Returns:
        A dictionary representing the memory entry
    """
    if goal_id is None:
        goal_id = generate_goal_id(agent_id)
        
    if tags is None:
        tags = ONBOARDING_TAGS.copy()
        
    # Add step-specific tag
    tags.append(f"step:{step_id}")
    
    # Add tool-specific tag if applicable
    if tool_name:
        tags.append(f"tool:{tool_name}")
        
    memory = {
        "id": f"{memory_type}_{step_id}_{int(datetime.datetime.now().timestamp())}",
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_id": agent_id,
        "goal_id": goal_id,
        "type": memory_type,
        "content": content,
        "tags": tags
    }
    
    return memory

def create_reflection_memory(
    agent_id: str,
    step_id: str,
    content: str,
    goal_id: Optional[str] = None,
    tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a reflection memory for the onboarding process.
    
    Args:
        agent_id: ID of the agent being onboarded
        step_id: ID of the onboarding step
        content: Content of the reflection
        goal_id: Optional goal ID (defaults to agent_onboarding_{agent_id})
        tool_name: Optional tool name for tool-related reflections
        
    Returns:
        A dictionary representing the reflection memory
    """
    tags = ONBOARDING_TAGS.copy()
    tags.append("reflection")
    
    return create_memory_entry(
        agent_id=agent_id,
        step_id=step_id,
        memory_type="reflection",
        content=content,
        goal_id=goal_id,
        tags=tags,
        tool_name=tool_name
    )

def create_checkpoint_memory(
    agent_id: str,
    checkpoint_id: str,
    status: str,
    details: Dict[str, Any],
    goal_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a checkpoint memory for the onboarding process.
    
    Args:
        agent_id: ID of the agent being onboarded
        checkpoint_id: ID of the checkpoint
        status: Status of the checkpoint (complete, error, etc.)
        details: Additional details about the checkpoint
        goal_id: Optional goal ID (defaults to agent_onboarding_{agent_id})
        
    Returns:
        A dictionary representing the checkpoint memory
    """
    if goal_id is None:
        goal_id = generate_goal_id(agent_id)
        
    checkpoint = {
        "id": f"checkpoint_{checkpoint_id}_{int(datetime.datetime.now().timestamp())}",
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_id": agent_id,
        "goal_id": goal_id,
        "type": "checkpoint",
        "checkpoint_id": checkpoint_id,
        "status": status,
        "details": details,
        "tags": ONBOARDING_TAGS + ["checkpoint", f"checkpoint:{checkpoint_id}"]
    }
    
    return checkpoint

def get_onboarding_step(step_id: str) -> Optional[Dict[str, Any]]:
    """Get the onboarding step configuration by ID."""
    for step in ONBOARDING_STEPS:
        if step["id"] == step_id:
            return step
    return None

# Define the main onboarding flow controller
class OnboardingFlow:
    """
    Controller for the agent onboarding flow.
    
    This class manages the execution of the onboarding steps, memory creation,
    and checkpoint reporting for new agents.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize the onboarding flow for a specific agent.
        
        Args:
            agent_id: ID of the agent to onboard
        """
        self.agent_id = agent_id
        self.goal_id = generate_goal_id(agent_id)
        self.current_step_index = 0
        self.memories = []
        self.completed_steps = []
        self.errors = []
        
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get the current step in the onboarding flow."""
        if self.current_step_index < len(ONBOARDING_STEPS):
            return ONBOARDING_STEPS[self.current_step_index]
        return None
        
    def advance_to_next_step(self) -> bool:
        """
        Advance to the next step in the onboarding flow.
        
        Returns:
            True if there is a next step, False if onboarding is complete
        """
        if self.current_step_index < len(ONBOARDING_STEPS) - 1:
            self.current_step_index += 1
            return True
        return False
        
    def record_memory(self, memory: Dict[str, Any]) -> str:
        """
        Record a memory in the onboarding flow.
        
        Args:
            memory: The memory to record
            
        Returns:
            The ID of the recorded memory
        """
        self.memories.append(memory)
        return memory["id"]
        
    def record_error(self, step_id: str, error_message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an error in the onboarding flow.
        
        Args:
            step_id: ID of the step where the error occurred
            error_message: Description of the error
            details: Additional details about the error
        """
        if details is None:
            details = {}
            
        error = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_id": step_id,
            "error_message": error_message,
            "details": details
        }
        
        self.errors.append(error)
        
    def mark_step_complete(self, step_id: str) -> None:
        """
        Mark a step as complete in the onboarding flow.
        
        Args:
            step_id: ID of the completed step
        """
        self.completed_steps.append({
            "step_id": step_id,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def is_onboarding_complete(self) -> bool:
        """
        Check if the onboarding flow is complete.
        
        Returns:
            True if all steps are completed, False otherwise
        """
        return len(self.completed_steps) == len(ONBOARDING_STEPS)
        
    def get_onboarding_status(self) -> Dict[str, Any]:
        """
        Get the current status of the onboarding flow.
        
        Returns:
            A dictionary containing the onboarding status
        """
        current_step = self.get_current_step()
        
        return {
            "agent_id": self.agent_id,
            "goal_id": self.goal_id,
            "current_step": current_step["id"] if current_step else None,
            "completed_steps": [step["step_id"] for step in self.completed_steps],
            "progress": f"{len(self.completed_steps)}/{len(ONBOARDING_STEPS)}",
            "is_complete": self.is_onboarding_complete(),
            "has_errors": len(self.errors) > 0,
            "memory_count": len(self.memories)
        }
        
    def generate_onboarding_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of the onboarding process.
        
        Returns:
            A dictionary containing the onboarding report
        """
        return {
            "agent_id": self.agent_id,
            "goal_id": self.goal_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "complete" if self.is_onboarding_complete() else "incomplete",
            "steps": {
                "total": len(ONBOARDING_STEPS),
                "completed": len(self.completed_steps),
                "completed_steps": self.completed_steps
            },
            "memories": {
                "total": len(self.memories),
                "by_type": self._count_memories_by_type()
            },
            "errors": {
                "total": len(self.errors),
                "details": self.errors if self.errors else None
            }
        }
        
    def _count_memories_by_type(self) -> Dict[str, int]:
        """Count memories by type."""
        counts = {}
        for memory in self.memories:
            memory_type = memory.get("type", "unknown")
            counts[memory_type] = counts.get(memory_type, 0) + 1
        return counts
        
    def save_onboarding_log(self, log_dir: str = "/home/ubuntu/workspace/personal-ai-agent/logs") -> str:
        """
        Save the onboarding log to a file.
        
        Args:
            log_dir: Directory to save the log file
            
        Returns:
            Path to the saved log file
        """
        # Ensure the log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate the log filename
        log_filename = f"onboarding_{self.agent_id.lower()}_log.json"
        log_path = os.path.join(log_dir, log_filename)
        
        # Generate the log content
        log_content = {
            "report": self.generate_onboarding_report(),
            "memories": self.memories,
            "errors": self.errors
        }
        
        # Write the log to file
        with open(log_path, "w") as f:
            json.dump(log_content, f, indent=2)
            
        return log_path
            
    def get_agent_specific_tool(self, agent_id: str, step: Dict[str, Any]) -> str:
        """
        Get the appropriate tool for a specific agent based on the step configuration.
        
        Args:
            agent_id: ID of the agent
            step: Step configuration dictionary
            
        Returns:
            The appropriate tool name for the agent
        """
        if agent_id.lower() == "hal":
            return step.get("tool_hal", step.get("tool", ""))
        elif agent_id.lower() == "ash":
            return step.get("tool_ash", step.get("tool", ""))
        else:
            # Default to the generic tool if agent-specific one isn't defined
            return step.get("tool", "")
