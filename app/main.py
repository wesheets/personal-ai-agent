"""
Main Application

This module defines the FastAPI application and includes all routes.
"""

from fastapi import FastAPI
import uvicorn

# Import routes
from app.routes.agent_config_routes import router as agent_config_router
from app.routes.agent_context_routes import router as agent_context_router
from app.routes.memory_recall_routes import router as memory_recall_router
from app.routes.memory_embed_routes import router as memory_embed_router
from app.routes.plan_generate_routes import router as plan_generate_router
from app.routes.train_routes import router as train_router
from app.routes.export_routes import router as export_router
from app.routes.fix_routes import router as fix_router
from app.routes.delegate_stream_routes import router as delegate_stream_router

# Create FastAPI app
app = FastAPI(
    title="Promethios API",
    description="API for the Promethios Cognitive System",
    version="1.0.0",
)

# Include routers
app.include_router(agent_config_router)
app.include_router(agent_context_router)
app.include_router(memory_recall_router)
app.include_router(memory_embed_router)
app.include_router(plan_generate_router)
app.include_router(train_router)
app.include_router(export_router)
app.include_router(fix_router)
app.include_router(delegate_stream_router)

# Add more routers here as they are implemented

@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Promethios API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
