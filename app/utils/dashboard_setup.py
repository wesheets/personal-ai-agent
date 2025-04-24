"""
Static File Serving Module for Dashboard

This module sets up static file serving for the dashboard frontend files.
"""

import os
import shutil
from pathlib import Path

def setup_dashboard_static_files():
    """
    Copy dashboard frontend files to the static directory for serving.
    
    This function ensures that the dashboard frontend files are available
    in the static directory for the FastAPI application to serve.
    """
    # Define source and destination directories
    src_dir = Path("app/frontend/dashboard")
    dst_dir = Path("app/static/dashboard")
    
    # Create destination directory if it doesn't exist
    os.makedirs(dst_dir, exist_ok=True)
    
    # Copy all files from frontend/dashboard to static/dashboard
    for file_path in src_dir.glob("*"):
        if file_path.is_file():
            shutil.copy2(file_path, dst_dir / file_path.name)
            print(f"Copied {file_path.name} to static directory")
    
    return {
        "status": "success",
        "message": "Dashboard static files set up successfully",
        "files_copied": [f.name for f in src_dir.glob("*") if f.is_file()]
    }
