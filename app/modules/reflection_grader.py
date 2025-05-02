"""
Reflection Grader Module

This module provides functionality for evaluating agent reflections and scoring their quality
based on completeness, schema compliance, confidence value, goal alignment, verbosity vs clarity,
and tag accuracy. It enables Promethios to have metacognition hygiene — the ability to know
when its own thoughts are weak.
"""

from datetime import datetime
from typing import Dict, Any, List
import logging

from app.schema_registry import SCHEMA_REGISTRY
from app.utils.schema_utils import validate_schema
from app.modules.project_state import read_project_state, update_project_state

# Configure logging
logger = logging.getLogger("app.modules.reflection_grader")

def grade_reflection(project_id: str) -> Dict[str, Any]:
    """
    Grades the last reflection for a project and stores the score in project state.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the grading result
    """
    try:
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Get the last reflection
        reflection = project_state.get("last_reflection", {})
        if not reflection:
            logger.warning(f"No last_reflection found for project {project_id}")
            return {
                "status": "error",
                "message": f"No last_reflection found for project {project_id}",
                "project_id": project_id
            }
        
        # Get the reflection schema
        schema = SCHEMA_REGISTRY["reflection"]
        
        # Initialize score and issues
        score = 1.0
        issues = []
        
        # Check schema compliance
        validation_errors = validate_schema(reflection, schema)
        if validation_errors:
            issues.append(f"Schema mismatch: {validation_errors}")
            score -= 0.3
        
        # Check confidence
        if reflection.get("confidence", 1.0) < 0.6:
            issues.append("Low confidence")
            score -= 0.2
        
        # Check tag quality
        tags = reflection.get("tags", [])
        if not tags or not any(tag.startswith("loop:") for tag in tags):
            issues.append("Missing loop reference tag")
            score -= 0.1
        
        # Check goal alignment
        if "goal" in reflection and "summary" in reflection:
            goal = reflection.get("goal", "").lower()
            summary = reflection.get("summary", "").lower()
            
            # Simple check if summary mentions goal
            if goal and not any(term in summary for term in goal.split()):
                issues.append("Summary doesn't align with goal")
                score -= 0.15
        
        # Check verbosity vs clarity
        if "summary" in reflection:
            summary = reflection.get("summary", "")
            
            # Check if summary is too short
            if len(summary) < 50:
                issues.append("Summary too brief")
                score -= 0.1
            
            # Check if summary is excessively long
            elif len(summary) > 1000:
                issues.append("Summary excessively verbose")
                score -= 0.05
        
        # Create result object
        result = {
            "score": max(0, round(score, 2)),
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat(),
            "loop": project_state.get("loop_count", 0),
            "reflection_id": reflection.get("id", f"reflection_{datetime.utcnow().isoformat()}")
        }
        
        # Update project state with reflection score
        update_data = {}
        
        # Add to reflection_scores array
        reflection_scores = project_state.get("reflection_scores", [])
        reflection_scores.append(result)
        update_data["reflection_scores"] = reflection_scores
        
        # Add to weak_reflections if score is low
        if result["score"] < 0.6:
            weak_reflections = project_state.get("weak_reflections", [])
            weak_reflections.append(reflection)
            update_data["weak_reflections"] = weak_reflections
        
        # Update project state
        update_project_state(project_id, update_data)
        
        logger.info(f"Graded reflection for project {project_id} with score {result['score']}")
        return result
    
    except Exception as e:
        error_msg = f"Error grading reflection for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def get_reflection_scores(project_id: str) -> Dict[str, Any]:
    """
    Gets all reflection scores for a project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the reflection scores
    """
    try:
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Get reflection scores
        reflection_scores = project_state.get("reflection_scores", [])
        
        return {
            "project_id": project_id,
            "reflection_scores": reflection_scores,
            "count": len(reflection_scores),
            "average_score": sum(score.get("score", 0) for score in reflection_scores) / max(1, len(reflection_scores))
        }
    
    except Exception as e:
        error_msg = f"Error getting reflection scores for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def get_weak_reflections(project_id: str) -> Dict[str, Any]:
    """
    Gets all weak reflections for a project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the weak reflections
    """
    try:
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Get weak reflections
        weak_reflections = project_state.get("weak_reflections", [])
        
        return {
            "project_id": project_id,
            "weak_reflections": weak_reflections,
            "count": len(weak_reflections)
        }
    
    except Exception as e:
        error_msg = f"Error getting weak reflections for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }
