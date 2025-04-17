from fastapi import FastAPI
from fastapi.responses import JSONResponse
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enhanced AI Agent System (ERROR MODE)",
    description="The application failed to start properly. See logs for details.",
    version="1.0.0"
)

@app.get("/")
async def error_root():
    try:
        # Simulate error handling logic or serve static response
        raise Exception("Simulated startup failure")
    except Exception as e:
        return {
            "status": "error",
            "message": "Application is in error recovery mode due to startup failure",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

@app.get("/health")
async def error_health():
    try:
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Add CORS middleware even in error mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
