"""
HAL routes loader module for main.py
This module registers HAL routes with the FastAPI application using flexible import paths.
"""
from fastapi import FastAPI, APIRouter
import logging
import importlib.util
import sys
import os

# Configure logging
logger = logging.getLogger("app.routes.hal_routes_loader")

def register_hal_routes(app: FastAPI, loaded_routes: list):
    """
    Register HAL routes with the FastAPI application using flexible import paths.
    Falls back to a minimal implementation if the actual module cannot be loaded.
    
    Args:
        app: FastAPI application
        loaded_routes: List of already loaded routes
        
    Returns:
        list: Updated list of loaded routes
    """
    if "hal_routes" not in loaded_routes:
        # Try multiple import paths
        router = None
        
        # List of possible import paths to try
        import_paths = [
            "app.routes.hal_routes",
            "routes.hal_routes",
            ".hal_routes"
        ]
        
        # Try each import path
        for import_path in import_paths:
            try:
                module = importlib.import_module(import_path)
                if hasattr(module, 'router'):
                    router = module.router
                    logger.info(f"✅ Successfully imported HAL routes from {import_path}")
                    break
            except ImportError:
                logger.warning(f"⚠️ Could not import HAL routes from {import_path}")
                continue
        
        # If no import succeeded, check if we can load the module from file
        if router is None:
            # List of possible file paths to check
            file_paths = [
                os.path.join("app", "routes", "hal_routes.py"),
                os.path.join("/app", "routes", "hal_routes.py"),
                os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "routes", "hal_routes.py")
            ]
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    try:
                        spec = importlib.util.spec_from_file_location("hal_routes", file_path)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules["hal_routes"] = module
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'router'):
                            router = module.router
                            logger.info(f"✅ Successfully loaded HAL routes from file: {file_path}")
                            break
                    except Exception as e:
                        logger.warning(f"⚠️ Error loading HAL routes from file {file_path}: {str(e)}")
                        continue
        
        # If still no success, create a minimal router
        if router is None:
            # Try to use the fallback mechanism
            try:
                from app.fallbacks.fix_hal_routes import register_hal_routes as fallback_register_hal_routes
                router = fallback_register_hal_routes()
                logger.info("✅ Using fallback HAL routes")
            except Exception as e:
                # If even the fallback fails, create a minimal router
                logger.warning(f"⚠️ Fallback HAL routes failed: {str(e)}")
                router = create_minimal_hal_router()
                logger.info("✅ Created minimal HAL router")
        
        # Include the router
        app.include_router(router)
        loaded_routes.append("hal_routes")
        logger.info("✅ HAL routes registered with application")
    
    return loaded_routes

def create_minimal_hal_router():
    """
    Creates a minimal HAL router with basic endpoints.
    This is used as a last resort if all other methods fail.
    
    Returns:
        APIRouter: A minimal HAL router
    """
    router = APIRouter(tags=["hal"])
    
    @router.get("/api/hal/health")
    async def hal_health_check():
        """
        Basic health check endpoint for HAL.
        """
        return {
            "status": "degraded",
            "message": "Running minimal HAL router",
            "timestamp": str(import_datetime().datetime.now())
        }
    
    @router.get("/api/hal/status")
    async def hal_status():
        """
        Status endpoint for HAL.
        """
        return {
            "status": "degraded",
            "mode": "minimal",
            "message": "HAL routes are running in minimal mode due to loading errors",
            "timestamp": str(import_datetime().datetime.now())
        }
    
    return router

def import_datetime():
    """
    Imports datetime module dynamically to avoid circular imports.
    
    Returns:
        module: The datetime module
    """
    import datetime
    return datetime
