"""
System Summary Memory Module

This module provides functionality for storing and retrieving system summary memory entries.
It serves as the memory backend for the SAGE Meta-Summary Agent.
"""

import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("memory.system_summary")

# In-memory database to store system summaries
SUMMARY_DB: Dict[str, List[Dict[str, Any]]] = {}

def write_system_summary(project_id: str, summary: str) -> Dict[str, Any]:
    """
    Write a system summary to memory.
    
    Args:
        project_id: The project identifier
        summary: The narrative summary text
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Generate a unique summary ID
        summary_id = str(uuid.uuid4())
        
        # Create summary entry
        summary_entry = {
            "summary_id": summary_id,
            "category": "system_summary",
            "content": summary,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Initialize project entry in SUMMARY_DB if it doesn't exist
        if project_id not in SUMMARY_DB:
            SUMMARY_DB[project_id] = []
        
        # Add summary to SUMMARY_DB
        SUMMARY_DB[project_id].append(summary_entry)
        
        # Log the summary creation
        logger.info(f"System summary created for project {project_id}: {summary_id}")
        
        # Write to file for persistence
        try:
            # Ensure the summaries directory exists
            summaries_dir = os.path.join(os.path.dirname(__file__), "summaries")
            os.makedirs(summaries_dir, exist_ok=True)
            
            # Define the path to the summaries file
            summaries_file = os.path.join(summaries_dir, f"{project_id}_summaries.json")
            
            # Read existing summaries
            existing_summaries = []
            if os.path.exists(summaries_file):
                try:
                    with open(summaries_file, 'r') as f:
                        existing_summaries = json.load(f)
                except json.JSONDecodeError:
                    existing_summaries = []
            
            # Add new summary
            existing_summaries.append(summary_entry)
            
            # Write updated summaries
            with open(summaries_file, 'w') as f:
                json.dump(existing_summaries, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing summary to file: {str(e)}")
        
        return {
            "status": "success",
            "summary_id": summary_id,
            "message": f"System summary created: {summary_id}"
        }
    except Exception as e:
        error_msg = f"Error creating system summary: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "message": error_msg,
            "error": str(e)
        }

def get_latest_summary(project_id: str) -> str:
    """
    Retrieve the latest system summary for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The latest system summary or a message if no summary is found
    """
    try:
        # Check if project exists in SUMMARY_DB
        if project_id in SUMMARY_DB and SUMMARY_DB[project_id]:
            # Sort by timestamp (newest first)
            sorted_summaries = sorted(
                SUMMARY_DB[project_id], 
                key=lambda x: x.get("timestamp", ""), 
                reverse=True
            )
            
            # Return the latest summary
            if sorted_summaries:
                return sorted_summaries[0].get("content", "Summary content not found")
        
        # If not in memory, try to read from file
        try:
            summaries_file = os.path.join(
                os.path.dirname(__file__), 
                "summaries", 
                f"{project_id}_summaries.json"
            )
            
            if os.path.exists(summaries_file):
                with open(summaries_file, 'r') as f:
                    summaries = json.load(f)
                
                # Sort by timestamp (newest first)
                sorted_summaries = sorted(
                    summaries, 
                    key=lambda x: x.get("timestamp", ""), 
                    reverse=True
                )
                
                # Return the latest summary
                if sorted_summaries:
                    # Update in-memory database
                    if project_id not in SUMMARY_DB:
                        SUMMARY_DB[project_id] = []
                    SUMMARY_DB[project_id].extend(summaries)
                    
                    return sorted_summaries[0].get("content", "Summary content not found")
        except Exception as e:
            logger.error(f"Error reading summaries from file: {str(e)}")
        
        # If no summary found
        return f"No system summary found for project {project_id}"
    
    except Exception as e:
        error_msg = f"Error retrieving latest summary: {str(e)}"
        logger.error(error_msg)
        return f"Error retrieving latest summary: {str(e)}"

def get_all_summaries(project_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all system summaries for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        List of all system summaries for the project
    """
    try:
        summaries = []
        
        # Check if project exists in SUMMARY_DB
        if project_id in SUMMARY_DB:
            summaries.extend(SUMMARY_DB[project_id])
        
        # Try to read from file
        try:
            summaries_file = os.path.join(
                os.path.dirname(__file__), 
                "summaries", 
                f"{project_id}_summaries.json"
            )
            
            if os.path.exists(summaries_file):
                with open(summaries_file, 'r') as f:
                    file_summaries = json.load(f)
                
                # Add file summaries to in-memory database
                if project_id not in SUMMARY_DB:
                    SUMMARY_DB[project_id] = []
                
                # Add only summaries that aren't already in memory
                existing_ids = {s.get("summary_id") for s in SUMMARY_DB[project_id]}
                for summary in file_summaries:
                    if summary.get("summary_id") not in existing_ids:
                        SUMMARY_DB[project_id].append(summary)
                        summaries.append(summary)
        except Exception as e:
            logger.error(f"Error reading summaries from file: {str(e)}")
        
        # Sort by timestamp (newest first)
        summaries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return summaries
    
    except Exception as e:
        error_msg = f"Error retrieving summaries: {str(e)}"
        logger.error(error_msg)
        return []
