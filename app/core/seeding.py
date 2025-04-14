import uuid
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("api")

class SeedingManager:
    """
    Manager for seeding default data when the database is empty
    """
    
    @staticmethod
    async def seed_default_agents(prompt_manager):
        """
        Seed default agents if none exist
        """
        logger.info("Checking if agents need to be seeded")
        try:
            # Check if any agents exist
            available_agents = prompt_manager.get_available_agents()
            
            if not available_agents:
                logger.info("No agents found, seeding default agents")
                
                # Define default agents
                default_agents = [
                    {
                        "name": "builder",
                        "description": "A builder agent for code generation and technical tasks",
                        "model": "gpt-4",
                        "system_prompt": "You are a senior backend engineer with expertise in Python and web development."
                    },
                    {
                        "name": "research",
                        "description": "A research agent for gathering and analyzing information",
                        "model": "gpt-4",
                        "system_prompt": "You are a research assistant with expertise in finding and synthesizing information."
                    },
                    {
                        "name": "ops",
                        "description": "An operations agent for system management tasks",
                        "model": "gpt-4",
                        "system_prompt": "You are a DevOps engineer with expertise in system administration and deployment."
                    }
                ]
                
                # Seed each agent
                for agent in default_agents:
                    try:
                        # In a real implementation, this would save to a database or file
                        # For now, we're just simulating the seeding
                        logger.info(f"Seeded default agent: {agent['name']}")
                    except Exception as e:
                        logger.error(f"Error seeding agent {agent['name']}: {str(e)}")
                
                return True
            else:
                logger.info(f"Found {len(available_agents)} existing agents, no seeding needed")
                return False
        except Exception as e:
            logger.error(f"Error checking or seeding agents: {str(e)}")
            return False
    
    @staticmethod
    async def seed_default_goals(task_state_manager):
        """
        Seed default goals if none exist
        """
        logger.info("Checking if goals need to be seeded")
        try:
            # Check if any goals exist
            if not task_state_manager.goals:
                logger.info("No goals found, seeding default goals")
                
                # Create a default goal
                goal_id = str(uuid.uuid4())
                now = datetime.now().isoformat()
                
                # Define default goal
                default_goal = {
                    "goal_id": goal_id,
                    "title": "System Initialization",
                    "description": "Initialize the Personal AI Agent system and prepare for user tasks",
                    "status": "in_progress",
                    "created_at": now,
                    "completed_at": None
                }
                
                # Define default tasks for the goal
                default_tasks = [
                    {
                        "task_id": str(uuid.uuid4()),
                        "goal_id": goal_id,
                        "title": "Setup environment",
                        "description": "Prepare the system environment for operation",
                        "status": "completed",
                        "assigned_agent": "ops",
                        "created_at": now,
                        "started_at": now,
                        "completed_at": now,
                        "dependencies": [],
                        "retry_count": 0
                    },
                    {
                        "task_id": str(uuid.uuid4()),
                        "goal_id": goal_id,
                        "title": "Initialize agents",
                        "description": "Load and configure all agent personalities",
                        "status": "in_progress",
                        "assigned_agent": "builder",
                        "created_at": now,
                        "started_at": now,
                        "completed_at": None,
                        "dependencies": [],
                        "retry_count": 0
                    },
                    {
                        "task_id": str(uuid.uuid4()),
                        "goal_id": goal_id,
                        "title": "Prepare knowledge base",
                        "description": "Initialize the vector memory system",
                        "status": "pending",
                        "assigned_agent": "research",
                        "created_at": now,
                        "started_at": None,
                        "completed_at": None,
                        "dependencies": [],
                        "retry_count": 0
                    }
                ]
                
                # In a real implementation, this would save to a database or file
                # For now, we're just simulating the seeding by adding to the manager
                task_state_manager.goals[goal_id] = type('Goal', (), default_goal)
                
                for task in default_tasks:
                    task_id = task["task_id"]
                    task_state_manager.tasks[task_id] = type('Task', (), task)
                
                logger.info(f"Seeded default goal with {len(default_tasks)} tasks")
                return True
            else:
                logger.info(f"Found {len(task_state_manager.goals)} existing goals, no seeding needed")
                return False
        except Exception as e:
            logger.error(f"Error checking or seeding goals: {str(e)}")
            return False

# Singleton instance
_seeding_manager = SeedingManager()

def get_seeding_manager():
    """
    Get the seeding manager singleton
    """
    return _seeding_manager
