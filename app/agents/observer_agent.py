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

# Import schema
from app.schemas.observer_schema import ObserverTaskRequest, ObserverTaskResult, ObservationEntry, ObserverErrorResult

# Import agent_sdk
try:
    from agent_sdk.agent_sdk import AgentSDK
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False
    print("❌ agent_sdk import failed")

# Import memory agent for retrieving memory summaries
try:
    from app.agents.memory_agent import handle_memory_task
    MEMORY_AGENT_AVAILABLE = True
except ImportError:
    MEMORY_AGENT_AVAILABLE = False
    print("❌ memory_agent import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    print("❌ system_log import failed")

# Configure logging
logger = logging.getLogger("agents.observer")

class ObserverAgent:
    """
    OBSERVER Agent for journaling system behavior and tracking anomalies
    
    This agent is responsible for:
    1. Creating daily journal entries of system behavior
    2. Tracking anomalies and failures
    3. Documenting agent reflections and philosophical questions
    """
    
    def __init__(self):
        """Initialize the OBSERVER agent."""
        self.name = "OBSERVER"
        self.description = "System behavior observer and journal keeper"
        self.tools = ["journal", "observe", "reflect"]
        self.log_dir = "logs/observation"
        self.log_file = "promethios_observations.md"
        
        # Initialize Agent SDK if available
        if AGENT_SDK_AVAILABLE:
            self.sdk = AgentSDK(agent_name="observer")
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
    
    def run_agent(self, request: ObserverTaskRequest) -> ObserverTaskResult:
        """
        Run the OBSERVER agent with the given request.
        
        Args:
            request: The ObserverTaskRequest containing task and date
            
        Returns:
            ObserverTaskResult containing the response and metadata
        """
        try:
            logger.info(f"Running OBSERVER agent with task: {request.task}, date: {request.date}")
            print(f"🚀 OBSERVER agent execution started")
            print(f"📋 Task: {request.task}")
            print(f"📅 Date: {request.date}")
            print(f"🧰 Tools: {request.tools}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("OBSERVER", f"Starting execution with task: {request.task}", request.date)
            
            # Handle different tasks
            if request.task == "journal":
                return self._handle_journal_task(request.date)
            else:
                error_msg = f"Unknown task: {request.task}"
                logger.error(error_msg)
                return ObserverErrorResult(
                    status="error",
                    message=error_msg,
                    task=request.task
                )
            
        except Exception as e:
            error_msg = f"Error running OBSERVER agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("OBSERVER", f"Error: {str(e)}", request.date)
            
            # Return error response
            return ObserverErrorResult(
                status="error",
                message=error_msg,
                task=request.task
            )
    
    def _handle_journal_task(self, date: str) -> ObserverTaskResult:
        """
        Handle the journal task.
        
        Args:
            date: The date for the journal entry
            
        Returns:
            ObserverTaskResult containing the journal entry
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
            behavior_observed="[todo]",
            anomalies="[todo]",
            vertical_progress="[todo]",
            loops_observed="[todo]",
            personality_notes="[todo]",
            philosophical_questions="[todo]"
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
            
            # Return success response
            return ObserverTaskResult(
                status="success",
                message=f"Daily journal appended to {self.log_file}",
                task="journal",
                date=date,
                entry=entry,
                log_path=log_path
            )
        except Exception as e:
            error_msg = f"Error writing journal entry: {str(e)}"
            logger.error(error_msg)
            return ObserverErrorResult(
                status="error",
                message=error_msg,
                task="journal"
            )

# Create an instance of the agent
observer_agent = ObserverAgent()

def handle_observer_task(task_input: str) -> str:
    """
    Legacy function to maintain backward compatibility.
    
    Args:
        task_input: The task to execute
        
    Returns:
        String containing the result message
    """
    # Create a request object
    request = ObserverTaskRequest(
        task=task_input,
        date=datetime.now().strftime("%Y-%m-%d"),
        tools=["journal", "observe", "reflect"]
    )
    
    # Run the agent
    result = observer_agent.run_agent(request)
    
    # Return message for backward compatibility
    if result.status == "success":
        return f"🧠 ObserverAgent: {result.message}"
    else:
        return f"🧠 ObserverAgent: Error - {result.message}"
