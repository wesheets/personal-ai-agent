#!/usr/bin/env python3
"""
Promethios Internal Checklist Engine (P.I.C.E.) Update Script

This script safely triggers a refresh of the system consciousness checklist.
It runs the checklist engine to scan the system structure and generate an updated checklist.

Usage:
    python tools/update_checklist.py

Output:
    The updated checklist is saved to /app/system/system_consciousness_index.json
    A log entry is created with the tag 'checklist_update_<timestamp>'
"""

import os
import sys
import json
import datetime
import logging
from pathlib import Path

# Add the parent directory to the path to allow importing the checklist engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'checklist_updates.log'))
    ]
)
logger = logging.getLogger('checklist_update')

def main():
    """Run the checklist engine and update the system consciousness index."""
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    log_tag = f"checklist_update_{timestamp}"
    
    logger.info(f"Starting checklist update with tag: {log_tag}")
    
    try:
        # Import the checklist engine
        from system.checklist_engine import ChecklistEngine
        
        # Create the logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Run the checklist engine
        logger.info("Running checklist engine...")
        engine = ChecklistEngine()
        success, error, checklist = engine.run()
        
        if success:
            logger.info(f"Checklist updated successfully and saved to {engine.output_file}")
            
            # Log some statistics
            logger.info(f"Checklist statistics:")
            logger.info(f"  - Agents: {len(checklist['agents'])}")
            logger.info(f"  - Routes: {len(checklist['routes'])}")
            logger.info(f"  - Schemas: {len(checklist['schemas'])}")
            logger.info(f"  - Modules: {len(checklist['modules'])}")
            logger.info(f"  - Tools: {len(checklist['tools'])}")
            logger.info(f"  - Execution checklist items: {len(checklist['execution_checklist'])}")
            
            # Print the execution checklist
            logger.info("Execution checklist:")
            for i, item in enumerate(checklist['execution_checklist'], 1):
                logger.info(f"  {i}. {item}")
            
            # Save a backup of the checklist with timestamp
            backup_file = os.path.join(logs_dir, f"checklist_backup_{timestamp}.json")
            with open(backup_file, 'w') as f:
                json.dump(checklist, f, indent=2)
            logger.info(f"Backup saved to {backup_file}")
            
            print(f"\n✅ Checklist Engine Update - System Status Refreshed")
            print(f"✅ Checklist saved to: {engine.output_file}")
            print(f"✅ Log Memory Tag: {log_tag}")
            print(f"✅ Backup saved to: {backup_file}")
            
            return 0
        else:
            logger.error(f"Error updating checklist: {error}")
            print(f"\n❌ Checklist Engine Update Failed")
            print(f"❌ Error: {error}")
            print(f"❌ Log Memory Tag: {log_tag}")
            
            return 1
    except Exception as e:
        logger.exception(f"Unexpected error during checklist update: {e}")
        print(f"\n❌ Checklist Engine Update Failed")
        print(f"❌ Unexpected error: {e}")
        print(f"❌ Log Memory Tag: {log_tag}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
