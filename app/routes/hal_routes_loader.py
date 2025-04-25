"""
HAL routes registration module for main.py
This module registers HAL routes with the FastAPI application.
"""
from fastapi import FastAPI
# Import HAL routes using absolute imports to avoid runtime context dependency
from routes.hal_routes import router as hal_router

def register_hal_routes(app: FastAPI, loaded_routes: list):
    """
    Register HAL routes with the FastAPI application.
    
    Args:
        app: FastAPI application
        loaded_routes: List of already loaded routes
    """
    if "hal_routes" not in loaded_routes:
        app.include_router(hal_router)
        loaded_routes.append("hal_routes")
        print("✅ HAL routes loaded")
    return loaded_routes
