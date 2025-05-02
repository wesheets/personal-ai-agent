from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Skip logging for health checks to reduce noise
    if request.url.path == "/health":
        return await call_next(request)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_details = {
        "error": str(exc),
        "type": str(type(exc)),
        "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__)
    }
    print(f"HEALTHCHECK ERROR: {error_details}", file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_type": str(type(exc))}
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Add a root route that redirects to health for convenience
@app.get("/")
def root():
    return {"message": "API is running. Use /health for healthcheck."}
