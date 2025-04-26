from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional, Dict, Any
import os
import shutil
from datetime import datetime

# Create router without prefix to avoid path duplication
router = APIRouter(tags=["file_upload"])

# Basic test route to verify router is working
@router.get("/api/upload/status")
async def get_upload_status():
    """
    Check if the upload service is operational.
    """
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "message": "File upload service is running"
    }

@router.post("/api/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and save it to the temporary uploads directory.
    """
    # Create uploads directory if it doesn't exist
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return {
        "status": "success",
        "message": "File uploaded successfully",
        "data": {
            "filename": file.filename,
            "saved_as": unique_filename,
            "content_type": file.content_type,
            "size": os.path.getsize(file_path),
            "path": file_path
        }
    }    }