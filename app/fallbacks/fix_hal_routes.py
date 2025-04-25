"""
HAL Routes Fallback Module

This module provides a fallback mechanism for HAL routes when the original module fails to load.
It ensures that a valid APIRouter is returned even when the HAL contract/schema is partially defined.
"""
from fastapi import APIRouter, HTTPException
import json
import os
import logging
import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.fallbacks.fix_hal_routes")

# Ensure logs directory exists
os.makedirs("/home/ubuntu/personal-ai-agent/logs", exist_ok=True)

def register_hal_routes() -> APIRouter:
    """
    Creates and returns a fallback HAL router with basic endpoints.
    This function is called when the original HAL routes module fails to load.
    
    Returns:
        APIRouter: A FastAPI router with fallback HAL endpoints
    """
    # Log the fallback activation
    log_fallback_activation()
    
    # Create a new router
    router = APIRouter(tags=["hal"])
    
    # Add basic health check endpoint
    @router.get("/api/hal/health")
    async def hal_health_check():
        """
        Basic health check endpoint for HAL.
        """
        return {
            "status": "degraded",
            "message": "Running in fallback mode",
            "timestamp": str(datetime.datetime.now())
        }
    
    # Add status endpoint
    @router.get("/api/hal/status")
    async def hal_status():
        """
        Status endpoint for HAL.
        """
        return {
            "status": "degraded",
            "mode": "fallback",
            "message": "HAL routes are running in fallback mode due to loading errors",
            "timestamp": str(datetime.datetime.now())
        }
    
    # Verify HAL schema exists and is valid
    schema_valid = verify_hal_schema()
    
    # Verify HAL agent is registered
    agent_registered = verify_hal_agent_registration()
    
    # Add schema validation status endpoint
    @router.get("/api/hal/schema/status")
    async def hal_schema_status():
        """
        Schema validation status endpoint for HAL.
        """
        return {
            "schema_valid": schema_valid,
            "agent_registered": agent_registered,
            "timestamp": str(datetime.datetime.now())
        }
    
    return router

def verify_hal_schema() -> bool:
    """
    Verifies that hal_agent.schema.json exists and is valid JSON.
    
    Returns:
        bool: True if schema exists and is valid, False otherwise
    """
    schema_path = "/home/ubuntu/personal-ai-agent/app/schemas/hal_agent.schema.json"
    try:
        if not os.path.exists(schema_path):
            logger.error(f"HAL schema file not found at {schema_path}")
            log_error("schema_missing", f"HAL schema file not found at {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            json.load(f)  # Attempt to parse JSON
        
        logger.info("HAL schema validation successful")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"HAL schema validation failed: {str(e)}")
        log_error("schema_invalid", f"HAL schema validation failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during HAL schema validation: {str(e)}")
        log_error("schema_error", f"Error during HAL schema validation: {str(e)}")
        return False

def verify_hal_agent_registration() -> bool:
    """
    Verifies that HAL agent is listed in agent_registry and agent_contracts.json.
    
    Returns:
        bool: True if HAL agent is properly registered, False otherwise
    """
    registry_path = "/home/ubuntu/personal-ai-agent/app/config/agent_registry.json"
    contracts_path = "/home/ubuntu/personal-ai-agent/app/config/agent_contracts.json"
    
    try:
        # Check agent_registry.json
        registry_valid = False
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                registry = json.load(f)
                if any(agent.get('id') == 'hal' for agent in registry):
                    registry_valid = True
        
        # Check agent_contracts.json
        contracts_valid = False
        if os.path.exists(contracts_path):
            with open(contracts_path, 'r') as f:
                contracts = json.load(f)
                if 'hal' in contracts:
                    contracts_valid = True
        
        result = registry_valid and contracts_valid
        if result:
            logger.info("HAL agent registration validation successful")
        else:
            logger.error("HAL agent registration validation failed")
            if not registry_valid:
                log_error("registry_missing", "HAL agent not found in agent_registry.json")
            if not contracts_valid:
                log_error("contract_missing", "HAL agent not found in agent_contracts.json")
        
        return result
    except Exception as e:
        logger.error(f"Error during HAL agent registration validation: {str(e)}")
        log_error("registration_error", f"Error during HAL agent registration validation: {str(e)}")
        return False

def log_fallback_activation():
    """
    Logs the activation of the HAL routes fallback mechanism.
    """
    log_file = "/home/ubuntu/personal-ai-agent/logs/hal_route_failures.json"
    
    try:
        # Create log entry
        log_entry = {
            "timestamp": str(datetime.datetime.now()),
            "event": "fallback_activated",
            "message": "HAL routes fallback mechanism activated due to loading errors"
        }
        
        # Check if log file exists
        if os.path.exists(log_file):
            # Read existing logs
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except json.JSONDecodeError:
                # If file exists but is not valid JSON, start with empty list
                logs = []
        else:
            logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        logger.info("HAL routes fallback activation logged successfully")
    except Exception as e:
        logger.error(f"Error logging HAL routes fallback activation: {str(e)}")

def log_error(error_type: str, message: str):
    """
    Logs an error to the HAL route failures log file.
    
    Args:
        error_type: Type of error
        message: Error message
    """
    log_file = "/home/ubuntu/personal-ai-agent/logs/hal_route_failures.json"
    
    try:
        # Create log entry
        log_entry = {
            "timestamp": str(datetime.datetime.now()),
            "event": "error",
            "error_type": error_type,
            "message": message
        }
        
        # Check if log file exists
        if os.path.exists(log_file):
            # Read existing logs
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except json.JSONDecodeError:
                # If file exists but is not valid JSON, start with empty list
                logs = []
        else:
            logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        logger.info(f"HAL routes error logged successfully: {error_type}")
    except Exception as e:
        logger.error(f"Error logging HAL routes error: {str(e)}")
