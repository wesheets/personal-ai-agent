from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import builder, ops, research, memory

app = FastAPI(
    title="Personal AI Agent System",
    description="A modular AI agent system modeled after Manus",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(builder.router, prefix="/agent/builder", tags=["builder"])
app.include_router(ops.router, prefix="/agent/ops", tags=["ops"])
app.include_router(research.router, prefix="/agent/research", tags=["research"])
app.include_router(memory.router, prefix="/agent/memory", tags=["memory"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Personal AI Agent System",
        "docs": "/docs",
        "available_agents": [
            "/agent/builder",
            "/agent/ops",
            "/agent/research",
            "/agent/memory"
        ]
    }
