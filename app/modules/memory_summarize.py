"""
Memory Summarize Module

This module provides functionality to generate summaries of memory threads.

MODIFIED: Updated schema to make agent_id optional or provide a default value  
MODIFIED: Added enhanced logging for debugging memory summarize issues  
MODIFIED: Updated to use Pydantic model for request validation  
MODIFIED: Fixed thread key format to use double colons  
MODIFIED: Imported SummarizationRequest from schemas to ensure agent_id is truly optional  
"""

import json
import logging
import traceback
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException
from app.schemas.memory import SummarizationRequest
from app.modules.memory_thread import THREAD_DB

# Configure logging
logger = logging.getLogger("modules.memory_summarize")

# Create router for memory summarize endpoint
router = APIRouter()

@router.post("/summarize")
async def summarize_memory_thread(request: SummarizationRequest) -> Dict[str, str]:
    """Generate a summary of a memory thread."""
    logger.info(f"🧠 Summarize route hit: {request.project_id} / {request.chain_id}")
    
    try:
        project_id = request.project_id
        chain_id = request.chain_id
        agent_id = request.agent_id  # Optional, defaults to "orchestrator"

        thread_key = f"{project_id}::{chain_id}"
        if thread_key not in THREAD_DB or not THREAD_DB[thread_key]:
            error_msg = f"No memory thread found for project_id: {project_id}, chain_id: {chain_id}"
            logger.error(f"🧠 Memory Summarize: Error - {error_msg}")
            logger.debug(f"🧠 Memory Summarize: Available thread keys: {list(THREAD_DB.keys())}")
            raise HTTPException(status_code=404, detail=error_msg)

        thread = THREAD_DB[thread_key]
        logger.info(f"🧠 Memory Summarize: Found thread with {len(thread)} entries")

        summary = generate_thread_summary(thread)
        logger.info(f"🧠 Memory Summarize: Summary generated successfully")

        return {
            "summary": summary,
            "agent_id": agent_id
        }

    except HTTPException:
        raise

    except Exception as e:
        error_msg = f"Unexpected error in summarize_memory_thread: {str(e)}"
        logger.error(f"🧠 Memory Summarize: {error_msg}")
        logger.error(f"🧠 Memory Summarize: Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


def generate_thread_summary(thread: List[Dict[str, Any]]) -> str:
    """Generate a human-readable summary of a memory thread."""
    logger.debug(f"🧠 Memory Summarize: Generating thread summary with {len(thread)} entries")

    try:
        agents_activities = {
            "hal": {"tasks": [], "summaries": [], "reflections": [], "uis": [], "plans": [], "docs": []},
            "ash": {"tasks": [], "summaries": [], "reflections": [], "uis": [], "plans": [], "docs": []},
            "nova": {"tasks": [], "summaries": [], "reflections": [], "uis": [], "plans": [], "docs": []},
            "critic": {"tasks": [], "summaries": [], "reflections": [], "uis": [], "plans": [], "docs": []}
        }

        for entry in thread:
            agent = entry["agent"].lower()
            step_type = entry["step_type"]
            content = entry["content"]

            if agent not in agents_activities:
                continue

            key = step_type.lower() if isinstance(step_type, str) else step_type.value.lower()
            if key in agents_activities[agent]:
                agents_activities[agent][key].append(content)

        summary_parts = []
        project_description = "This project involved implementing a function"

        def summarize_agent(agent_name, activity_map):
            parts = []
            for key, descriptions in activity_map.items():
                if descriptions:
                    action = {
                        "tasks": "performed tasks",
                        "summaries": "provided summaries",
                        "reflections": "reflected on the process",
                        "uis": "designed UI components",
                        "plans": "developed plans",
                        "docs": "created documentation"
                    }.get(key, None)
                    if action:
                        parts.append(action)
            return f"{agent_name.upper()} {', '.join(parts)}" if parts else None

        for agent, activities in agents_activities.items():
            summary = summarize_agent(agent, activities)
            if summary:
                summary_parts.append(summary)
            else:
                summary_parts.append(f"{agent.upper()} did not contribute")

        final_summary = f"{project_description}. {', '.join(summary_parts)}."
        return final_summary

    except Exception as e:
        logger.error(f"🧠 Memory Summarize: Error in generate_thread_summary: {str(e)}")
        return "Unable to generate summary due to an error."
