"""
Validator Agent Runner Script

This script executes the System Integration Validator to perform comprehensive checks
across the current system and generate a validation report.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Main function to run the validator agent.
    """
    logger.info("Starting System Integration Validator Agent...")
    
    try:
        # Add the project root to the Python path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Import the system validator
        from app.validators.system_validator import run_validation_tests
        
        # Run validation tests
        logger.info("Running validation tests...")
        validation_report = await run_validation_tests()
        
        # Log validation results
        if validation_report["overall_success"]:
            logger.info("All validation tests passed successfully!")
        else:
            logger.warning(f"Some validation tests failed. {validation_report['tests_failed']} out of {validation_report['tests_run']} tests failed.")
            
            if "recommendations" in validation_report:
                logger.info("Recommendations:")
                for i, recommendation in enumerate(validation_report["recommendations"], 1):
                    logger.info(f"  {i}. {recommendation}")
        
        logger.info(f"Validation report saved to {os.path.join(project_root, 'app', 'logs', 'system_validation_report.json')}")
        
        return validation_report
        
    except Exception as e:
        logger.error(f"Error running validator agent: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
