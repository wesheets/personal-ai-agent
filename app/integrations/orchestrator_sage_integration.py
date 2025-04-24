"""
Orchestrator Loop Integration for SAGE Cascade Mode

This module updates the orchestrator to include SAGE in the agent sequence,
enabling cascade mode where SAGE is automatically invoked after CRITIC.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("app.integrations.orchestrator_sage_integration")

# Import SAGE cascade integration
try:
    from app.integrations.sage_cascade_integration import process_critic_result, should_invoke_sage
    sage_cascade_available = True
except ImportError:
    sage_cascade_available = False
    logger.warning("⚠️ SAGE cascade integration not available, cascade mode will be disabled")

class OrchestratorSageIntegration:
    """
    Integration class for adding SAGE to the orchestrator agent sequence.
    """
    
    @staticmethod
    def update_agent_sequence(agent_sequence: List[str]) -> List[str]:
        """
        Update the agent sequence to include SAGE after CRITIC.
        
        Args:
            agent_sequence: Original agent sequence
            
        Returns:
            Updated agent sequence with SAGE after CRITIC
        """
        # Check if SAGE is already in the sequence
        if "sage" in agent_sequence:
            # Make sure SAGE comes after CRITIC
            try:
                critic_index = agent_sequence.index("critic")
                sage_index = agent_sequence.index("sage")
                
                # If SAGE is not after CRITIC, reposition it
                if sage_index != critic_index + 1:
                    # Remove SAGE from its current position
                    agent_sequence.pop(sage_index)
                    
                    # Insert SAGE after CRITIC
                    agent_sequence.insert(critic_index + 1, "sage")
            except ValueError:
                # If CRITIC is not in the sequence, just append SAGE
                agent_sequence.append("sage")
        else:
            # If CRITIC is in the sequence, add SAGE after it
            try:
                critic_index = agent_sequence.index("critic")
                agent_sequence.insert(critic_index + 1, "sage")
            except ValueError:
                # If CRITIC is not in the sequence, just append SAGE
                agent_sequence.append("sage")
        
        logger.info(f"Updated agent sequence: {agent_sequence}")
        return agent_sequence
    
    @staticmethod
    async def handle_critic_completion(loop_id: str, critic_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CRITIC completion by triggering SAGE review if appropriate.
        
        Args:
            loop_id: Unique identifier for the loop
            critic_result: Result from CRITIC review
            
        Returns:
            Dict containing the SAGE review result or status information
        """
        if not sage_cascade_available:
            logger.warning("SAGE cascade integration not available, skipping cascade")
            return {
                "status": "skipped",
                "message": "SAGE cascade integration not available",
                "loop_id": loop_id
            }
        
        # Check if SAGE should be invoked
        should_invoke = await should_invoke_sage(loop_id)
        
        if not should_invoke:
            logger.info(f"SAGE invocation skipped for loop {loop_id} based on should_invoke_sage")
            return {
                "status": "skipped",
                "message": "SAGE invocation skipped based on should_invoke_sage",
                "loop_id": loop_id
            }
        
        # Process CRITIC result and trigger SAGE review
        return await process_critic_result(loop_id, critic_result)
