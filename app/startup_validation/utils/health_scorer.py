"""
Health Scorer Module

This module calculates health scores for cognitive surfaces based on validation results.
It implements the surface health scoring system with the following weights:
- Agents Health: 30%
- Modules Health: 30%
- Schemas Health: 20%
- Endpoints Health: 10%
- Components Health: 10%
"""

import logging
from typing import Dict, Any, List, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.health_scorer')

# Surface weights as defined in the requirements
SURFACE_WEIGHTS = {
    "agents": 0.3,    # 30%
    "modules": 0.3,   # 30%
    "schemas": 0.2,   # 20%
    "endpoints": 0.1, # 10%
    "components": 0.1 # 10%
}

def calculate_overall_health_score(
    agents_health: float,
    modules_health: float,
    schemas_health: float,
    endpoints_health: float,
    components_health: float
) -> float:
    """
    Calculate the overall surface health score based on individual surface scores and weights.
    
    Args:
        agents_health: Health score for agents (0-100)
        modules_health: Health score for modules (0-100)
        schemas_health: Health score for schemas (0-100)
        endpoints_health: Health score for endpoints (0-100)
        components_health: Health score for components (0-100)
        
    Returns:
        Overall health score as a percentage (0-100)
    """
    logger.info("Calculating overall health score")
    
    # Apply weights to each surface health score
    weighted_scores = [
        agents_health * SURFACE_WEIGHTS["agents"],
        modules_health * SURFACE_WEIGHTS["modules"],
        schemas_health * SURFACE_WEIGHTS["schemas"],
        endpoints_health * SURFACE_WEIGHTS["endpoints"],
        components_health * SURFACE_WEIGHTS["components"]
    ]
    
    # Calculate overall score
    overall_score = sum(weighted_scores)
    
    logger.info(f"Overall health score: {overall_score:.1f}%")
    logger.debug(f"Individual scores: agents={agents_health:.1f}%, modules={modules_health:.1f}%, "
                f"schemas={schemas_health:.1f}%, endpoints={endpoints_health:.1f}%, "
                f"components={components_health:.1f}%")
    
    return overall_score

def calculate_surface_health(valid_count: int, total_count: int) -> float:
    """
    Calculate health score for a specific surface type.
    
    Args:
        valid_count: Number of valid items
        total_count: Total number of items
        
    Returns:
        Health score as a percentage (0-100)
    """
    if total_count == 0:
        logger.debug("No items to calculate health score, returning 100%")
        return 100.0
    
    health_score = (valid_count / total_count) * 100
    logger.debug(f"Health score: {valid_count}/{total_count} = {health_score:.1f}%")
    
    return health_score

def format_health_percentage(health_score: float) -> str:
    """
    Format a health score as a percentage string.
    
    Args:
        health_score: Health score as a float (0-100)
        
    Returns:
        Formatted percentage string (e.g., "98.5%")
    """
    return f"{health_score:.1f}%"
