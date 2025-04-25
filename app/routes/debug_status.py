"""
Debug Status Endpoint

This module provides a comprehensive status endpoint that checks all critical components
of the application and returns detailed diagnostics about their status.
"""

import logging
import os
import sys
import importlib.util
import datetime
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("app.routes.debug_status")

# Create router
router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)

@router.get("/status")
async def get_deployment_status():
    """
    Get comprehensive status of all critical components.
    
    This endpoint checks:
    - HAL schema file existence and path resolution
    - HAL agent registration status
    - Memory module availability
    - Orchestrator router status
    - Import paths for all critical modules
    
    Returns:
        Dict containing detailed status information
    """
    status_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": get_environment_info(),
        "components": {
            "hal": check_hal_status(),
            "memory": check_memory_status(),
            "orchestrator": check_orchestrator_status(),
            "dashboard": check_dashboard_status()
        },
        "import_paths": check_import_paths(),
        "file_paths": check_file_paths(),
        "overall_status": "unknown"  # Will be updated based on component statuses
    }
    
    # Determine overall status
    component_statuses = [
        status_report["components"]["hal"]["status"],
        status_report["components"]["memory"]["status"],
        status_report["components"]["orchestrator"]["status"],
        status_report["components"]["dashboard"]["status"]
    ]
    
    if all(status == "operational" for status in component_statuses):
        status_report["overall_status"] = "operational"
    elif any(status == "failed" for status in component_statuses):
        status_report["overall_status"] = "degraded"
    else:
        status_report["overall_status"] = "partial"
    
    # Log the status report
    log_status_report(status_report)
    
    return status_report

def get_environment_info() -> Dict[str, Any]:
    """
    Get information about the current environment.
    
    Returns:
        Dict containing environment information
    """
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "sys_path": sys.path,
        "env_vars": {
            key: value for key, value in os.environ.items()
            if key.startswith(("APP_", "PYTHON", "PATH", "HOME"))
        }
    }

def check_hal_status() -> Dict[str, Any]:
    """
    Check the status of the HAL component.
    
    Returns:
        Dict containing HAL status information
    """
    status_info = {
        "status": "unknown",
        "schema_file": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "agent_registration": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "routes_loaded": False,
        "import_status": "unknown"
    }
    
    # Check HAL schema file
    schema_paths = [
        os.path.join("app", "schemas", "hal_agent.schema.json"),
        os.path.join("app", "schemas", "schemas", "hal_agent.schema.json"),
        os.path.join("/app", "schemas", "hal_agent.schema.json"),
        os.path.join("/app", "schemas", "schemas", "hal_agent.schema.json"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "schemas", "hal_agent.schema.json"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "schemas", "schemas", "hal_agent.schema.json")
    ]
    
    for path in schema_paths:
        status_info["schema_file"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["schema_file"]["found"] = True
            status_info["schema_file"]["path"] = path
            break
    
    # Check HAL agent registration
    registry_paths = [
        os.path.join("app", "config", "agent_registry.json"),
        os.path.join("/app", "config", "agent_registry.json"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "config", "agent_registry.json")
    ]
    
    for path in registry_paths:
        status_info["agent_registration"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["agent_registration"]["found"] = True
            status_info["agent_registration"]["path"] = path
            
            # Check if HAL is in the registry
            try:
                with open(path, "r") as f:
                    registry = json.load(f)
                    if "hal" in registry:
                        status_info["agent_registration"]["hal_registered"] = True
                    else:
                        status_info["agent_registration"]["hal_registered"] = False
            except Exception as e:
                status_info["agent_registration"]["error"] = str(e)
            
            break
    
    # Check HAL routes import
    try:
        # Try multiple import paths
        import_paths = [
            "app.routes.hal_routes",
            "routes.hal_routes",
            ".hal_routes"
        ]
        
        for import_path in import_paths:
            try:
                module = importlib.import_module(import_path)
                if hasattr(module, 'router'):
                    status_info["routes_loaded"] = True
                    status_info["import_status"] = f"Imported from {import_path}"
                    break
            except ImportError:
                continue
        
        if not status_info["routes_loaded"]:
            status_info["import_status"] = "Failed to import HAL routes"
    except Exception as e:
        status_info["import_status"] = f"Error checking HAL routes: {str(e)}"
    
    # Determine overall HAL status
    if status_info["schema_file"]["found"] and status_info["agent_registration"]["found"] and status_info["routes_loaded"]:
        status_info["status"] = "operational"
    elif not status_info["schema_file"]["found"] and not status_info["agent_registration"]["found"] and not status_info["routes_loaded"]:
        status_info["status"] = "failed"
    else:
        status_info["status"] = "degraded"
    
    return status_info

def check_memory_status() -> Dict[str, Any]:
    """
    Check the status of the memory component.
    
    Returns:
        Dict containing memory status information
    """
    status_info = {
        "status": "unknown",
        "memory_writer": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "orchestrator_memory": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "project_memory": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "import_status": "unknown"
    }
    
    # Check memory_writer.py
    memory_writer_paths = [
        os.path.join("app", "modules", "memory_writer.py"),
        os.path.join("/app", "modules", "memory_writer.py"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "modules", "memory_writer.py")
    ]
    
    for path in memory_writer_paths:
        status_info["memory_writer"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["memory_writer"]["found"] = True
            status_info["memory_writer"]["path"] = path
            break
    
    # Check orchestrator_memory.py
    orchestrator_memory_paths = [
        os.path.join("app", "modules", "orchestrator_memory.py"),
        os.path.join("/app", "modules", "orchestrator_memory.py"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "modules", "orchestrator_memory.py")
    ]
    
    for path in orchestrator_memory_paths:
        status_info["orchestrator_memory"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["orchestrator_memory"]["found"] = True
            status_info["orchestrator_memory"]["path"] = path
            break
    
    # Check project_memory.py
    project_memory_paths = [
        os.path.join("app", "memory", "project_memory.py"),
        os.path.join("/app", "memory", "project_memory.py"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "memory", "project_memory.py")
    ]
    
    for path in project_memory_paths:
        status_info["project_memory"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["project_memory"]["found"] = True
            status_info["project_memory"]["path"] = path
            break
    
    # Check memory module import
    try:
        # Try multiple import paths for memory_writer
        import_paths = [
            "app.modules.memory_writer",
            "modules.memory_writer",
            ".memory_writer"
        ]
        
        for import_path in import_paths:
            try:
                module = importlib.import_module(import_path)
                if hasattr(module, 'read_memory') and hasattr(module, 'write_memory'):
                    status_info["import_status"] = f"Imported memory_writer from {import_path}"
                    break
            except ImportError:
                continue
        
        # Try multiple import paths for orchestrator_memory
        import_paths = [
            "app.modules.orchestrator_memory",
            "modules.orchestrator_memory",
            ".orchestrator_memory"
        ]
        
        for import_path in import_paths:
            try:
                module = importlib.import_module(import_path)
                if hasattr(module, 'read_memory') and hasattr(module, 'list_memories'):
                    status_info["import_status"] += f", Imported orchestrator_memory from {import_path}"
                    break
            except ImportError:
                continue
    except Exception as e:
        status_info["import_status"] = f"Error checking memory imports: {str(e)}"
    
    # Determine overall memory status
    if status_info["memory_writer"]["found"] and status_info["orchestrator_memory"]["found"] and status_info["project_memory"]["found"]:
        status_info["status"] = "operational"
    elif not status_info["memory_writer"]["found"] and not status_info["orchestrator_memory"]["found"] and not status_info["project_memory"]["found"]:
        status_info["status"] = "failed"
    else:
        status_info["status"] = "degraded"
    
    return status_info

def check_orchestrator_status() -> Dict[str, Any]:
    """
    Check the status of the orchestrator component.
    
    Returns:
        Dict containing orchestrator status information
    """
    status_info = {
        "status": "unknown",
        "orchestrator_router": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "import_status": "unknown"
    }
    
    # Check orchestrator_router.py
    router_paths = [
        os.path.join("app", "routes", "orchestrator_router.py"),
        os.path.join("/app", "routes", "orchestrator_router.py"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "routes", "orchestrator_router.py")
    ]
    
    for path in router_paths:
        status_info["orchestrator_router"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["orchestrator_router"]["found"] = True
            status_info["orchestrator_router"]["path"] = path
            break
    
    # Check orchestrator router import
    try:
        # Try multiple import paths
        import_paths = [
            "app.routes.orchestrator_router",
            "routes.orchestrator_router",
            ".orchestrator_router"
        ]
        
        for import_path in import_paths:
            try:
                module = importlib.import_module(import_path)
                if hasattr(module, 'router'):
                    status_info["import_status"] = f"Imported from {import_path}"
                    break
            except ImportError:
                continue
        
        if status_info["import_status"] == "unknown":
            status_info["import_status"] = "Failed to import orchestrator router"
    except Exception as e:
        status_info["import_status"] = f"Error checking orchestrator router: {str(e)}"
    
    # Determine overall orchestrator status
    if status_info["orchestrator_router"]["found"] and status_info["import_status"] != "Failed to import orchestrator router":
        status_info["status"] = "operational"
    elif not status_info["orchestrator_router"]["found"]:
        status_info["status"] = "failed"
    else:
        status_info["status"] = "degraded"
    
    return status_info

def check_dashboard_status() -> Dict[str, Any]:
    """
    Check the status of the dashboard component.
    
    Returns:
        Dict containing dashboard status information
    """
    status_info = {
        "status": "unknown",
        "dashboard_routes": {
            "found": False,
            "path": None,
            "paths_checked": []
        },
        "memory_available": False,
        "import_status": "unknown"
    }
    
    # Check dashboard_routes.py
    dashboard_paths = [
        os.path.join("app", "routes", "dashboard_routes.py"),
        os.path.join("/app", "routes", "dashboard_routes.py"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "routes", "dashboard_routes.py")
    ]
    
    for path in dashboard_paths:
        status_info["dashboard_routes"]["paths_checked"].append(path)
        if os.path.exists(path):
            status_info["dashboard_routes"]["found"] = True
            status_info["dashboard_routes"]["path"] = path
            break
    
    # Check dashboard routes import and memory availability
    try:
        # Try to import dashboard_routes
        import_paths = [
            "app.routes.dashboard_routes",
            "routes.dashboard_routes",
            ".dashboard_routes"
        ]
        
        for import_path in import_paths:
            try:
                module = importlib.import_module(import_path)
                if hasattr(module, 'router'):
                    status_info["import_status"] = f"Imported from {import_path}"
                    
                    # Check if memory is available in the module
                    if hasattr(module, 'memory_available'):
                        status_info["memory_available"] = module.memory_available
                    
                    break
            except ImportError:
                continue
        
        if status_info["import_status"] == "unknown":
            status_info["import_status"] = "Failed to import dashboard routes"
    except Exception as e:
        status_info["import_status"] = f"Error checking dashboard routes: {str(e)}"
    
    # Determine overall dashboard status
    if status_info["dashboard_routes"]["found"] and status_info["memory_available"]:
        status_info["status"] = "operational"
    elif not status_info["dashboard_routes"]["found"]:
        status_info["status"] = "failed"
    else:
        status_info["status"] = "degraded"
    
    return status_info

def check_import_paths() -> Dict[str, Any]:
    """
    Check import paths for all critical modules.
    
    Returns:
        Dict containing import path information
    """
    import_info = {}
    
    # List of critical modules to check
    modules_to_check = [
        "app.routes.hal_routes",
        "app.modules.orchestrator_memory",
        "app.modules.memory_writer",
        "app.memory.project_memory",
        "app.routes.orchestrator_router",
        "app.routes.dashboard_routes"
    ]
    
    for module_path in modules_to_check:
        try:
            module = importlib.import_module(module_path)
            import_info[module_path] = {
                "status": "imported",
                "file": getattr(module, "__file__", "unknown"),
                "has_router": hasattr(module, "router")
            }
        except ImportError as e:
            import_info[module_path] = {
                "status": "import_error",
                "error": str(e)
            }
        except Exception as e:
            import_info[module_path] = {
                "status": "error",
                "error": str(e)
            }
    
    return import_info

def check_file_paths() -> Dict[str, Any]:
    """
    Check file paths for all critical files.
    
    Returns:
        Dict containing file path information
    """
    file_info = {}
    
    # List of critical files to check
    files_to_check = [
        os.path.join("app", "schemas", "hal_agent.schema.json"),
        os.path.join("app", "config", "agent_registry.json"),
        os.path.join("app", "config", "agent_contracts.json"),
        os.path.join("app", "modules", "memory_writer.py"),
        os.path.join("app", "modules", "orchestrator_memory.py"),
        os.path.join("app", "memory", "project_memory.py"),
        os.path.join("app", "routes", "hal_routes.py"),
        os.path.join("app", "routes", "orchestrator_router.py"),
        os.path.join("app", "routes", "dashboard_routes.py")
    ]
    
    for file_path in files_to_check:
        # Check with different base paths
        base_paths = ["", "/", "/app/", "/home/ubuntu/personal-ai-agent/"]
        
        for base_path in base_paths:
            full_path = os.path.join(base_path, file_path) if base_path else file_path
            exists = os.path.exists(full_path)
            
            if exists:
                try:
                    stats = os.stat(full_path)
                    file_info[full_path] = {
                        "exists": True,
                        "size": stats.st_size,
                        "permissions": oct(stats.st_mode)[-3:],
                        "last_modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat()
                    }
                except Exception as e:
                    file_info[full_path] = {
                        "exists": True,
                        "error": str(e)
                    }
                break
            else:
                file_info[full_path] = {
                    "exists": False
                }
    
    return file_info

def log_status_report(status_report: Dict[str, Any]) -> None:
    """
    Log the status report to a file.
    
    Args:
        status_report: The status report to log
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join("logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"deployment_status_{timestamp}.json")
        
        # Write status report to file
        with open(log_file, "w") as f:
            json.dump(status_report, f, indent=2)
        
        logger.info(f"Status report logged to {log_file}")
    except Exception as e:
        logger.error(f"Error logging status report: {str(e)}")
