from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Form
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
import shutil
from app.api.auth.security import get_current_user
from app.models.user import User

router = APIRouter()

# File upload response model
class FileUploadResponse(BaseModel):
    filename: str
    content_type: str
    size: int
    url: str
    path: str

# Configure upload directory
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Upload a file
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    task_id: Optional[str] = Form(None),
    memory_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Create user-specific directory
    user_dir = os.path.join(UPLOAD_DIR, current_user.id)
    os.makedirs(user_dir, exist_ok=True)
    
    # Define file path
    file_path = os.path.join(user_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Generate public URL
    file_url = f"/api/files/{current_user.id}/{unique_filename}"
    
    # Return file info
    return FileUploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        size=file_size,
        url=file_url,
        path=file_path
    )

# Get file by ID
@router.get("/{user_id}/{file_id}")
async def get_file(
    user_id: str,
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    # Check if user is authorized to access this file
    if user_id != current_user.id:
        # Check if file is attached to a public resource
        # This would require additional logic in a real implementation
        is_public = False
        
        if not is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file"
            )
    
    # Get file path
    file_path = os.path.join(UPLOAD_DIR, user_id, file_id)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Return file
    return FileResponse(file_path)

# Delete file
@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    # Get file path
    file_path = os.path.join(UPLOAD_DIR, current_user.id, file_id)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete file
    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
    
    return {"message": "File deleted successfully"}
