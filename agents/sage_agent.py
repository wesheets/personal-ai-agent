"""
SAGE Meta-Summary Agent Module

This module provides the SAGE (System-wide Agent for Generating Explanations) agent
that reads memory logs and project state to generate narrative summaries of system activities.

The SAGE agent serves as a reflection engine that can summarize Promethios' recent actions,
memory logs, and project activity, enabling human-readable reports, system audits, and agent handoffs.
"""

import logging
import json
import os
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("agents.sage_agent")

# Check if memory_writer is available
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    try:
        from memory.memory_writer import write_memory
        MEMORY_WRITER_AVAILABLE = True
    except ImportError:
        MEMORY_WRITER_AVAILABLE = False
        logger.warning("Memory writer module not available, SAGE agent will not be able to write summaries to memory")

# Check if project_state is available
try:
    from app.modules.project_state import read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    try:
        from memory.project_state import read_project_state
        PROJECT_STATE_AVAILABLE = True
    except ImportError:
        PROJECT_STATE_AVAILABLE = False
        logger.warning("Project state module not available, SAGE agent will use limited project information")

# Check if memory_thread is available
try:
    from app.modules.memory_thread import THREAD_DB
    MEMORY_THREAD_AVAILABLE = True
except ImportError:
    try:
        from memory.memory_thread import THREAD_DB
        MEMORY_THREAD_AVAILABLE = True
    except ImportError:
        MEMORY_THREAD_AVAILABLE = False
        logger.warning("Memory thread module not available, SAGE agent will use limited memory information")

def run_sage_agent(project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the SAGE (System-wide Agent for Generating Explanations) agent to generate
    a narrative summary of system activities for a specific project.
    
    Args:
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the response and metadata
    """
    if tools is None:
        tools = []
    
    logger.info(f"🤖 SAGE agent execution started for project: {project_id}")
    print(f"🤖 SAGE agent execution started for project: {project_id}")
    
    try:
        # Initialize actions_taken list to track actions
        actions_taken = []
        files_created = []
        
        # Read project state
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            try:
                project_state = read_project_state(project_id)
                logger.info(f"Project state read for {project_id}")
                actions_taken.append(f"Read project state for {project_id}")
            except Exception as e:
                logger.error(f"Error reading project state: {str(e)}")
                actions_taken.append(f"Failed to read project state: {str(e)}")
        
        # Read memory logs
        memory_entries = []
        if MEMORY_THREAD_AVAILABLE:
            try:
                # Collect all memory entries for this project
                for thread_key in THREAD_DB:
                    if thread_key.startswith(f"{project_id}::") or thread_key.startswith(f"{project_id}:"):
                        memory_entries.extend(THREAD_DB[thread_key])
                
                # Sort by timestamp (newest first)
                memory_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                
                logger.info(f"Read {len(memory_entries)} memory entries for {project_id}")
                actions_taken.append(f"Read {len(memory_entries)} memory entries for {project_id}")
            except Exception as e:
                logger.error(f"Error reading memory entries: {str(e)}")
                actions_taken.append(f"Failed to read memory entries: {str(e)}")
        
        # Generate summary
        summary = generate_system_summary(project_id, project_state, memory_entries)
        logger.info(f"Generated summary for {project_id}")
        actions_taken.append(f"Generated summary for {project_id}")
        
        # Write summary to memory if memory_writer is available
        if MEMORY_WRITER_AVAILABLE and "memory_writer" in tools:
            try:
                memory_data = {
                    "category": "system_summary",
                    "content": summary,
                    "project_id": project_id,
                    "agent": "sage",
                    "role": "assistant",
                    "step_type": "thinking"
                }
                
                memory_result = write_memory(memory_data)
                logger.info(f"Summary written to memory: {memory_result.get('memory_id', 'unknown')}")
                actions_taken.append(f"Wrote summary to memory: {memory_result.get('memory_id', 'unknown')}")
            except Exception as e:
                logger.error(f"Error writing summary to memory: {str(e)}")
                actions_taken.append(f"Failed to write summary to memory: {str(e)}")
        
        # Return result with summary and actions_taken list
        return {
            "status": "success",
            "message": f"SAGE successfully generated summary for project {project_id}",
            "summary": summary,
            "files_created": files_created,
            "actions_taken": actions_taken,
            "project_id": project_id,
            "tools": tools
        }
    except Exception as e:
        error_msg = f"Error in run_sage_agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing SAGE agent: {str(e)}",
            "summary": f"Error generating summary: {str(e)}",
            "files_created": [],
            "actions_taken": [],
            "project_id": project_id,
            "tools": tools,
            "error": str(e)
        }

def generate_system_summary(project_id: str, project_state: Dict[str, Any], memory_entries: List[Dict[str, Any]]) -> str:
    """
    Generate a narrative summary of system activities based on project state and memory entries.
    
    Args:
        project_id: The project identifier
        project_state: Dictionary containing project state information
        memory_entries: List of memory entries
        
    Returns:
        A narrative summary of system activities
    """
    try:
        # Extract relevant information from project state
        status = project_state.get("status", "unknown")
        files_created = project_state.get("files_created", [])
        agents_involved = project_state.get("agents_involved", [])
        latest_agent_action = project_state.get("latest_agent_action", {})
        next_recommended_step = project_state.get("next_recommended_step", "")
        
        # Group memory entries by agent
        agent_actions = {}
        for entry in memory_entries:
            agent = entry.get("agent", "unknown")
            if agent not in agent_actions:
                agent_actions[agent] = []
            
            action = entry.get("action", entry.get("content", "unknown action"))
            if isinstance(action, str) and len(action) > 0:
                agent_actions[agent].append(action)
        
        # Generate timestamp
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Start building the summary
        summary_parts = []
        
        # Add date and project status
        summary_parts.append(f"On {current_date}, ")
        
        # Add agent actions
        agent_summaries = []
        for agent, actions in agent_actions.items():
            if agent.lower() == "unknown" or not actions:
                continue
                
            # Get the most recent actions (up to 3)
            recent_actions = actions[:3]
            
            # Summarize what this agent did
            if len(recent_actions) == 1:
                agent_summaries.append(f"{agent.upper()} {recent_actions[0]}")
            elif len(recent_actions) == 2:
                agent_summaries.append(f"{agent.upper()} {recent_actions[0]} and {recent_actions[1]}")
            else:
                # Combine multiple actions
                action_summary = ", ".join(recent_actions[:-1]) + f", and {recent_actions[-1]}"
                agent_summaries.append(f"{agent.upper()} {action_summary}")
        
        # If no agent summaries, use project state information
        if not agent_summaries and agents_involved:
            for agent in agents_involved:
                agent_summaries.append(f"{agent.upper()} was involved in the project")
        
        # Add agent summaries to the main summary
        if len(agent_summaries) == 1:
            summary_parts.append(agent_summaries[0])
        elif len(agent_summaries) == 2:
            summary_parts.append(f"{agent_summaries[0]}. {agent_summaries[1]}")
        elif len(agent_summaries) > 2:
            for i, summary in enumerate(agent_summaries[:-1]):
                summary_parts.append(f"{summary}. ")
            summary_parts.append(agent_summaries[-1])
        else:
            summary_parts.append(f"No agent activity was recorded for project {project_id}")
        
        # Add information about files created if available
        if files_created:
            if len(files_created) == 1:
                summary_parts.append(f". The file {files_created[0]} was created")
            elif len(files_created) == 2:
                summary_parts.append(f". The files {files_created[0]} and {files_created[1]} were created")
            elif len(files_created) > 2:
                file_list = ", ".join(files_created[:-1]) + f", and {files_created[-1]}"
                summary_parts.append(f". The files {file_list} were created")
        
        # Add next recommended step if available
        if next_recommended_step:
            summary_parts.append(f". Next recommended step: {next_recommended_step}")
        
        # Combine all parts into a single summary
        summary = "".join(summary_parts)
        
        # Ensure the summary ends with a period
        if not summary.endswith("."):
            summary += "."
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating system summary: {str(e)}")
        return f"Error generating system summary: {str(e)}"

def get_latest_summary(project_id: str) -> str:
    """
    Retrieve the latest system summary for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The latest system summary or a message if no summary is found
    """
    try:
        # Check if memory_thread is available
        if not MEMORY_THREAD_AVAILABLE:
            return "Memory thread module not available, cannot retrieve latest summary"
        
        # Find all system_summary entries for this project
        summaries = []
        for thread_key in THREAD_DB:
            if thread_key.startswith(f"{project_id}::") or thread_key.startswith(f"{project_id}:"):
                for entry in THREAD_DB[thread_key]:
                    if entry.get("category") == "system_summary":
                        summaries.append(entry)
        
        # Sort by timestamp (newest first)
        summaries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Return the latest summary or a message if no summary is found
        if summaries:
            return summaries[0].get("content", "Summary content not found")
        else:
            return f"No system summary found for project {project_id}"
    
    except Exception as e:
        logger.error(f"Error retrieving latest summary: {str(e)}")
        return f"Error retrieving latest summary: {str(e)}"
