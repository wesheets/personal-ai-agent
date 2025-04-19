"""
NOVA Test Strategy Module
This module provides a test implementation of NOVA agent logic.
It demonstrates dynamic loading of logic modules at runtime.
"""

import logging
import json
import os
from typing import Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger("app.modules.logic.test.nova_test_strategy")

def run(project_id: str, task: str) -> Dict[str, Any]:
    """
    Run the NOVA test strategy with the specified project ID and task.
    
    Args:
        project_id: The project identifier
        task: The task to perform
            
    Returns:
        Dict containing the execution results
    """
    try:
        logger.info(f"Running NOVA test strategy for project {project_id} with task: {task}")
        print(f"🚀 Running NOVA test strategy for project {project_id} with task: {task}")
        
        # Import project_state here to avoid circular imports
        from app.modules.project_state import update_project_state, read_project_state
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Update project state with test strategy execution
        update_project_state(project_id, {
            "latest_agent_action": f"NOVA test strategy executed: {task}",
            "agents_involved": ["nova"],
            "next_recommended_step": "critic",  # Set next step to CRITIC
            "test_strategy_executed": True,
            "test_strategy_timestamp": datetime.utcnow().isoformat()
        })
        
        # Create a test output file
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"nova_test_strategy_{project_id}.txt")
        with open(output_file, 'w') as f:
            f.write(f"NOVA test strategy output for project: {project_id}\n")
            f.write(f"Task: {task}\n")
            f.write(f"Timestamp: {datetime.utcnow().isoformat()}\n")
            f.write("This is a test of the dynamic logic loading system.\n")
            f.write("If you're seeing this, the test was successful!\n")
        
        logger.info(f"NOVA test strategy execution successful")
        print(f"✅ NOVA test strategy execution successful")
        
        return {
            "status": "success",
            "message": f"NOVA test strategy executed successfully",
            "project_id": project_id,
            "task": task,
            "output_file": output_file,
            "strategy": "nova_test_strategy"
        }
        
    except Exception as e:
        error_msg = f"Error running NOVA test strategy: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "task": task
        }
