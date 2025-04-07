from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from app.core.execution_logger import get_execution_logger

# Configure logging
logger = logging.getLogger("api")

# Create router
router = APIRouter()

@router.get("/logs/latest")
async def get_latest_logs(limit: int = 10, agent_name: Optional[str] = None):
    """
    Get the latest activity logs
    
    This endpoint returns the most recent activity logs from the system.
    """
    logger.info(f"Getting latest logs. Limit: {limit}, Agent: {agent_name}")
    print("✅ /logs/latest endpoint hit")
    
    try:
        # Get the execution logger
        execution_logger = get_execution_logger()
        
        # Get the latest logs
        logs = await execution_logger.get_logs(agent_name=agent_name, limit=limit)
        
        # If no logs are found, return mock data
        if not logs:
            logger.info("No logs found, returning mock data")
            mock_logs = [
                {
                    "id": f"mock-log-{i}",
                    "timestamp": datetime.now().isoformat(),
                    "agent_name": "builder" if i % 2 == 0 else "research",
                    "model": "gpt-4",
                    "input_summary": f"Mock input for log {i}",
                    "output_summary": f"Mock output for log {i}",
                    "tools_used": ["web_search", "code_executor"] if i % 3 == 0 else [],
                    "metadata": {"task_category": "code" if i % 2 == 0 else "research"}
                }
                for i in range(limit)
            ]
            return mock_logs
        
        logger.info(f"Returning {len(logs)} logs")
        print(f"✅ Returning {len(logs)} logs")
        return logs
        
    except Exception as e:
        logger.error(f"Error getting latest logs: {str(e)}")
        print(f"❌ Error getting latest logs: {str(e)}")
        # Return mock data in case of error to prevent frontend hang
        return [
            {
                "id": "error-fallback",
                "timestamp": datetime.now().isoformat(),
                "agent_name": "system",
                "model": "fallback",
                "input_summary": "Error occurred while retrieving logs",
                "output_summary": f"Error: {str(e)}",
                "tools_used": [],
                "metadata": {"error": True}
            }
        ]

# Export router
logs_router = router
