"""
Enhanced debug logging for route registration to help diagnose deployment issues.

This script adds detailed logging during FastAPI startup to show exactly which routes
are being registered, with their full paths and methods.
"""

import logging
from fastapi import FastAPI, APIRouter

# Configure logging
logger = logging.getLogger("route_registration")
logger.setLevel(logging.DEBUG)

def log_registered_routes(app: FastAPI):
    """
    Log all registered routes in a FastAPI application with their full paths and methods.
    
    This function should be called after all routes have been registered but before the app starts.
    """
    logger.info("🔍 ROUTE REGISTRATION DIAGNOSTIC 🔍")
    logger.info("=" * 50)
    logger.info("Registered Routes:")
    
    # Get all routes from the FastAPI app
    routes = app.routes
    
    # Sort routes by path for easier reading
    sorted_routes = sorted(routes, key=lambda r: getattr(r, "path", ""))
    
    # Log each route with its path and methods
    for i, route in enumerate(sorted_routes):
        path = getattr(route, "path", "Unknown path")
        methods = getattr(route, "methods", ["Unknown method"])
        name = getattr(route, "name", "Unnamed route")
        
        # Format methods as a comma-separated string
        methods_str = ", ".join(methods) if methods else "No methods"
        
        # Log the route details
        logger.info(f"Route {i+1}: {path} [{methods_str}] - {name}")
        
        # Print to console as well for immediate visibility
        print(f"📍 ROUTE {i+1}: {path} [{methods_str}] - {name}")
    
    # Log memory-specific routes separately for easier debugging
    memory_routes = [r for r in sorted_routes if "/memory/" in getattr(r, "path", "")]
    
    if memory_routes:
        logger.info("-" * 50)
        logger.info("Memory-specific Routes:")
        for i, route in enumerate(memory_routes):
            path = getattr(route, "path", "Unknown path")
            methods = getattr(route, "methods", ["Unknown method"])
            name = getattr(route, "name", "Unnamed route")
            
            # Format methods as a comma-separated string
            methods_str = ", ".join(methods) if methods else "No methods"
            
            # Log the route details
            logger.info(f"Memory Route {i+1}: {path} [{methods_str}] - {name}")
            
            # Print to console as well for immediate visibility
            print(f"🧠 MEMORY ROUTE {i+1}: {path} [{methods_str}] - {name}")
    else:
        logger.warning("⚠️ NO MEMORY ROUTES FOUND! This indicates a registration problem.")
        print("⚠️ NO MEMORY ROUTES FOUND! This indicates a registration problem.")
    
    logger.info("=" * 50)
    logger.info(f"Total routes: {len(routes)}")
    logger.info(f"Memory routes: {len(memory_routes)}")
