from fastapi import APIRouter

# Create a minimal router with no prefix to avoid any issues
router = APIRouter(tags=["file_upload"])

# Simple test endpoint to verify the router is working
@router.get("/api/upload/status")
async def get_upload_status():
    """
    Check if the upload service is operational.
    """
    return {
        "status": "operational",
        "message": "File upload service is running"
    }
