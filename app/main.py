from fastapi import FastAPI, APIRouter
from app.routes import debug_routes

app = FastAPI(title="Promethios API", description="API for Promethios AI Agent System")

# Include routers
app.include_router(debug_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Promethios API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
