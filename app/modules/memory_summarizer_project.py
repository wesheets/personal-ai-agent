"""
Project-scoped memory summarization module for generating natural language summaries of agent memories.

This module provides functionality to summarize a list of memory entries filtered by project_id
into a coherent natural language summary, either using simple concatenation or
more advanced AI-powered summarization.
"""

from typing import List, Dict, Optional
import logging
from app.modules.memory_summarizer import summarize_memories

# Configure logging
logger = logging.getLogger("memory_summarizer_project")

def summarize_project_memories(memories: List[Dict], project_id: str) -> Dict:
    """
    Generate a natural language summary of memory entries filtered by project_id.
    
    Args:
        memories: List of memory dictionaries to summarize
        project_id: Project ID to include in the response
        
    Returns:
        A dictionary containing the summary text and metadata
    """
    if not memories:
        return {
            "summary": "No relevant memories found for this project.",
            "project_id": project_id,
            "memory_count": 0
        }
    
    # Use the existing summarize_memories function
    summary_text = summarize_memories(memories)
    
    # Return structured response with summary, project_id, and memory_count
    return {
        "summary": summary_text,
        "project_id": project_id,
        "memory_count": len(memories)
    }
