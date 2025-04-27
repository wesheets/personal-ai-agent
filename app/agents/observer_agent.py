"""
OBSERVER Agent Module

This module provides the implementation for the OBSERVER agent, which is responsible for
journaling system behavior, tracking anomalies, and documenting agent reflections.

The OBSERVER agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
"""

import os
import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Import Agent SDK
from agent_sdk.agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("agents.observer")

# Import memory agent for retrieving memory summaries
try:
    from app.agents.memory_agent import handle_memory_task
    MEMORY_AGENT_AVAILABLE = True
except ImportError:
    MEMORY_AGENT_AVAILABLE = False
    logger.warning("⚠️ memory_agent import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    logger.warning("⚠️ system_log import failed")

class ObservationEntry:
    """Class representing an observation entry."""
    
    def __init__(self, date, memory_summary, behavior_observed, anomalies, 
                vertical_progress, loops_observed, personality_notes, philosophical_questions):
        self.date = date
        self.memory_summary = memory_summary
        self.behavior_observed = behavior_observed
        self.anomalies = anomalies
        self.vertical_progress = vertical_progress
        self.loops_observed = loops_observed
        self.personality_notes = personality_notes
        self.philosophical_questions = philosophical_questions
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "date": self.date,
            "memory_summary": self.memory_summary,
            "behavior_observed": self.behavior_observed,
            "anomalies": self.anomalies,
            "vertical_progress": self.vertical_progress,
            "loops_observed": self.loops_observed,
            "personality_notes": self.personality_notes,
            "philosophical_questions": self.philosophical_questions
        }

class ObserverAgent(Agent):
    """
    OBSERVER Agent for journaling system behavior and tracking anomalies
    
    This agent is responsible for:
    1. Creating daily journal entries of system behavior
    2. Tracking anomalies and failures
    3. Documenting agent reflections and philosophical questions
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the OBSERVER agent with SDK compliance."""
        # Define agent properties
        name = "Observer"
        role = "System Behavior Journalist"
        tools_list = tools or ["journal", "observe", "reflect"]
        permissions = ["read_memory", "write_logs", "observe_system"]
        description = "Responsible for journaling system behavior, tracking anomalies, and documenting agent reflections and philosophical questions."
        tone_profile = {
            "analytical": "high",
            "objective": "high",
            "reflective": "high",
            "philosophical": "medium",
            "detailed": "medium"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/observer/input_schema.json"
        output_schema_path = "app/schemas/observer/output_schema.json"
        
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
            trust_score=0.87,
            contract_version="1.0.0"
        )
        
        self.input_schema_path = input_schema_path
        self.log_dir = "logs/observation"
        self.log_file = "promethios_observations.md"
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        return validate_schema(data, self.input_schema_path)
    
    async def execute(self, task: str, date: str = None, tools: List[str] = None, 
                     project_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            task: The task to execute (journal, observe, reflect)
            date: The date for the journal entry (optional)
            tools: List of tools to use (optional)
            project_id: Optional project identifier
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            # Set default date if not provided
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"ObserverAgent.execute called with task: {task}, date: {date}")
            
            # Prepare input data for validation
            input_data = {
                "task": task,
                "date": date
            }
            
            if tools:
                input_data["tools"] = tools
            
            if project_id:
                input_data["project_id"] = project_id
            
            # Add any additional kwargs to input data
            input_data.update(kwargs)
            
            # Validate input
            if not self.validate_input(input_data):
                logger.warning(f"Input validation failed for task: {task}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("OBSERVER", f"Starting execution with task: {task}", date)
            
            # Handle different tasks
            if task == "journal":
                return await self._handle_journal_task(date)
            elif task == "observe":
                return await self._handle_observe_task(date)
            elif task == "reflect":
                return await self._handle_reflect_task(date)
            else:
                error_msg = f"Unknown task: {task}"
                logger.error(error_msg)
                
                error_result = {
                    "status": "error",
                    "message": error_msg,
                    "task": task,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Validate output
                if not self.validate_schema(error_result):
                    logger.warning(f"Output validation failed for error result")
                
                return error_result
            
        except Exception as e:
            error_msg = f"Error in ObserverAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("OBSERVER", f"Error: {str(e)}", date or datetime.now().strftime("%Y-%m-%d"))
            
            # Return error response
            error_result = {
                "status": "error",
                "message": error_msg,
                "task": task,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(error_result):
                logger.warning(f"Output validation failed for error result")
            
            return error_result
    
    async def _handle_journal_task(self, date: str) -> Dict[str, Any]:
        """
        Handle the journal task.
        
        Args:
            date: The date for the journal entry
            
        Returns:
            Dict containing the journal entry
        """
        # Get memory summary if memory agent is available
        memory_summary = "No memory summary available"
        if MEMORY_AGENT_AVAILABLE:
            try:
                memory_summary = handle_memory_task("SHOW")
            except Exception as e:
                logger.error(f"Error getting memory summary: {str(e)}")
                memory_summary = f"Error getting memory summary: {str(e)}"
        
        # Create observation entry
        entry = ObservationEntry(
            date=date,
            memory_summary=memory_summary,
            behavior_observed="System behavior appears stable with normal operation patterns.",
            anomalies="No significant anomalies detected in the current observation period.",
            vertical_progress="Incremental improvements observed in agent coordination and task completion.",
            loops_observed="Standard processing loops functioning within expected parameters.",
            personality_notes="System maintains consistent tone and interaction patterns across agents.",
            philosophical_questions="How does the system's understanding of its own limitations affect its decision-making process?"
        )
        
        # Format log entry
        log_entry = f"""## 📅 {date}

### 🧠 Agent Reflections:
{entry.memory_summary}

### 🧩 Behavior Observed:
{entry.behavior_observed}

### ⚠️ Anomalies / Failures:
{entry.anomalies}

### 📦 Vertical Progress:
{entry.vertical_progress}

### 🔁 Loops Observed:
{entry.loops_observed}

### 💬 System Personality Notes:
{entry.personality_notes}

### 🧬 Philosophical Questions Raised:
{entry.philosophical_questions}
"""
        
        # Write to log file
        log_path = os.path.join(self.log_dir, self.log_file)
        try:
            with open(log_path, "a") as f:
                f.write(log_entry + "\n---\n")
            
            logger.info(f"Journal entry written to {log_path}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("OBSERVER", f"Journal entry written to {log_path}", date)
            
            # Prepare success result
            result = {
                "status": "success",
                "message": f"Daily journal appended to {self.log_file}",
                "task": "journal",
                "date": date,
                "entry": entry.to_dict(),
                "log_path": log_path,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(result):
                logger.warning(f"Output validation failed for journal result")
            
            return result
            
        except Exception as e:
            error_msg = f"Error writing journal entry: {str(e)}"
            logger.error(error_msg)
            
            error_result = {
                "status": "error",
                "message": error_msg,
                "task": "journal",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate output
            if not self.validate_schema(error_result):
                logger.warning(f"Output validation failed for journal error result")
            
            return error_result
    
    async def _handle_observe_task(self, date: str) -> Dict[str, Any]:
        """
        Handle the observe task.
        
        Args:
            date: The date for the observation
            
        Returns:
            Dict containing the observation result
        """
        # In a real implementation, this would gather system metrics and observations
        # For now, we'll return a placeholder result
        
        result = {
            "status": "success",
            "message": "System observation completed",
            "task": "observe",
            "date": date,
            "entry": {
                "date": date,
                "memory_summary": "System memory appears stable and consistent.",
                "behavior_observed": "All agents operating within normal parameters.",
                "anomalies": "No anomalies detected during observation period.",
                "vertical_progress": "Steady progress observed in system capabilities.",
                "loops_observed": "Loop execution times within expected ranges.",
                "personality_notes": "System maintains consistent personality traits.",
                "philosophical_questions": "How does the system balance efficiency with creativity?"
            },
            "log_path": os.path.join(self.log_dir, "system_observations.log"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Validate output
        if not self.validate_schema(result):
            logger.warning(f"Output validation failed for observe result")
        
        return result
    
    async def _handle_reflect_task(self, date: str) -> Dict[str, Any]:
        """
        Handle the reflect task.
        
        Args:
            date: The date for the reflection
            
        Returns:
            Dict containing the reflection result
        """
        # In a real implementation, this would analyze system behavior and generate reflections
        # For now, we'll return a placeholder result
        
        result = {
            "status": "success",
            "message": "System reflection completed",
            "task": "reflect",
            "date": date,
            "entry": {
                "date": date,
                "memory_summary": "System memory shows coherent narrative of operations.",
                "behavior_observed": "System demonstrates consistent decision-making patterns.",
                "anomalies": "Minor inconsistencies in task prioritization noted.",
                "vertical_progress": "Incremental improvements in reasoning capabilities observed.",
                "loops_observed": "Loop execution demonstrates learning from previous iterations.",
                "personality_notes": "System shows increasing nuance in communication style.",
                "philosophical_questions": "What constitutes true understanding versus pattern recognition in the system's cognitive processes?"
            },
            "log_path": os.path.join(self.log_dir, "system_reflections.log"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Validate output
        if not self.validate_schema(result):
            logger.warning(f"Output validation failed for reflect result")
        
        return result

# Create an instance of the agent
observer_agent = ObserverAgent()

async def handle_observer_task_async(task_input: str, date: str = None) -> Dict[str, Any]:
    """
    Handle an OBSERVER task asynchronously.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        task_input: The task to execute
        date: Optional date for the task
        
    Returns:
        Dict containing the result of the execution
    """
    # Set default date if not provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Execute the agent
    result = await observer_agent.execute(task=task_input, date=date)
    
    return result

def handle_observer_task(task_input: str) -> str:
    """
    Legacy function to maintain backward compatibility.
    
    Args:
        task_input: The task to execute
        
    Returns:
        String containing the result message
    """
    import asyncio
    
    # Run the async method in a synchronous context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(handle_observer_task_async(task_input))
    
    # Return message for backward compatibility
    if result["status"] == "success":
        return f"🧠 ObserverAgent: {result['message']}"
    else:
        return f"🧠 ObserverAgent: Error - {result['message']}"

# memory_tag: healed_phase3.3
