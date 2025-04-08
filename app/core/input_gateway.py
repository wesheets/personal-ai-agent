"""
Input Gateway API Endpoint for the Personal AI Agent System.

This module provides an API endpoint to accept various input types (text, audio, documents),
and routes them to the appropriate handlers via the input router.
"""

import os
import json
import logging
import tempfile
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import the input router
from app.core.input_router import get_input_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("input_gateway")

# Create a memory manager instance (placeholder)
# In a real implementation, this would be properly initialized
memory_manager = None  # Replace with actual memory manager initialization

# Get an input router instance
input_router = get_input_router(memory_manager)

# Define input models
class TextInput(BaseModel):
    """Model for text input"""
    text: str = Field(..., description="The text input to process")
    target_agent: Optional[str] = Field(None, description="Optional agent to route the input to")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata about the input")
    store_memory: bool = Field(True, description="Whether to store the input in memory")
    memory_tags: Optional[List[str]] = Field(None, description="Tags to apply to the memory entry")
    memory_scope: str = Field("agent", description="Scope for the memory entry")

class Base64Input(BaseModel):
    """Model for base64-encoded input"""
    base64_data: str = Field(..., description="Base64-encoded data with format prefix")
    input_type: Optional[str] = Field(None, description="Optional explicit input type")
    target_agent: Optional[str] = Field(None, description="Optional agent to route the input to")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata about the input")
    store_memory: bool = Field(True, description="Whether to store the input in memory")
    memory_tags: Optional[List[str]] = Field(None, description="Tags to apply to the memory entry")
    memory_scope: str = Field("agent", description="Scope for the memory entry")

# Create FastAPI app
app = FastAPI(title="Input Gateway API", description="API for accepting various input types for the AI agent system")

@app.post("/input_gateway/text")
async def process_text_input(input_data: TextInput):
    """
    Process text input and route it to the appropriate agent.
    
    Args:
        input_data: The text input data
        
    Returns:
        JSON response with processing results
    """
    logger.info("Received text input")
    
    try:
        result = input_router.route_input(
            input_data=input_data.text,
            input_type="text",
            metadata=input_data.metadata,
            target_agent=input_data.target_agent,
            store_memory=input_data.store_memory,
            memory_tags=input_data.memory_tags,
            memory_scope=input_data.memory_scope
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        error_msg = f"Error processing text input: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/input_gateway/file")
async def process_file_input(
    file: UploadFile = File(...),
    input_type: Optional[str] = Form(None),
    target_agent: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    store_memory: bool = Form(True),
    memory_tags: Optional[str] = Form(None),
    memory_scope: str = Form("agent")
):
    """
    Process file input (audio, PDF, image, document) and route it to the appropriate agent.
    
    Args:
        file: The uploaded file
        input_type: Optional explicit input type
        target_agent: Optional agent to route the input to
        metadata: Optional JSON string with metadata about the input
        store_memory: Whether to store the input in memory
        memory_tags: Optional comma-separated list of tags
        memory_scope: Scope for the memory entry
        
    Returns:
        JSON response with processing results
    """
    logger.info(f"Received file input: {file.filename}")
    
    try:
        # Parse metadata if provided
        parsed_metadata = json.loads(metadata) if metadata else None
        
        # Parse memory tags if provided
        parsed_memory_tags = memory_tags.split(",") if memory_tags else None
        
        # Save the uploaded file to a temporary location
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())
        
        # Route the input
        result = input_router.route_input(
            input_data=None,
            input_type=input_type,
            file_path=temp_file_path,
            metadata=parsed_metadata,
            target_agent=target_agent,
            store_memory=store_memory,
            memory_tags=parsed_memory_tags,
            memory_scope=memory_scope
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        error_msg = f"Error processing file input: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/input_gateway/base64")
async def process_base64_input(input_data: Base64Input):
    """
    Process base64-encoded input and route it to the appropriate agent.
    
    Args:
        input_data: The base64-encoded input data
        
    Returns:
        JSON response with processing results
    """
    logger.info("Received base64 input")
    
    try:
        result = input_router.route_input(
            input_data=None,
            input_type=input_data.input_type,
            base64_data=input_data.base64_data,
            metadata=input_data.metadata,
            target_agent=input_data.target_agent,
            store_memory=input_data.store_memory,
            memory_tags=input_data.memory_tags,
            memory_scope=input_data.memory_scope
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        error_msg = f"Error processing base64 input: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/input_gateway")
async def process_any_input(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    base64_data: Optional[str] = Form(None),
    input_type: Optional[str] = Form(None),
    target_agent: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    store_memory: bool = Form(True),
    memory_tags: Optional[str] = Form(None),
    memory_scope: str = Form("agent")
):
    """
    Universal endpoint to process any type of input and route it to the appropriate agent.
    
    Args:
        text: Optional text input
        file: Optional file input
        base64_data: Optional base64-encoded input
        input_type: Optional explicit input type
        target_agent: Optional agent to route the input to
        metadata: Optional JSON string with metadata about the input
        store_memory: Whether to store the input in memory
        memory_tags: Optional comma-separated list of tags
        memory_scope: Scope for the memory entry
        
    Returns:
        JSON response with processing results
    """
    logger.info("Received input through universal endpoint")
    
    try:
        # Parse metadata if provided
        parsed_metadata = json.loads(metadata) if metadata else None
        
        # Parse memory tags if provided
        parsed_memory_tags = memory_tags.split(",") if memory_tags else None
        
        # Determine which input to use
        if file:
            # Save the uploaded file to a temporary location
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, file.filename)
            
            with open(temp_file_path, "wb") as f:
                f.write(await file.read())
            
            # Route the file input
            result = input_router.route_input(
                input_data=None,
                input_type=input_type,
                file_path=temp_file_path,
                metadata=parsed_metadata,
                target_agent=target_agent,
                store_memory=store_memory,
                memory_tags=parsed_memory_tags,
                memory_scope=memory_scope
            )
        
        elif base64_data:
            # Route the base64 input
            result = input_router.route_input(
                input_data=None,
                input_type=input_type,
                base64_data=base64_data,
                metadata=parsed_metadata,
                target_agent=target_agent,
                store_memory=store_memory,
                memory_tags=parsed_memory_tags,
                memory_scope=memory_scope
            )
        
        elif text:
            # Route the text input
            result = input_router.route_input(
                input_data=text,
                input_type="text",
                metadata=parsed_metadata,
                target_agent=target_agent,
                store_memory=store_memory,
                memory_tags=parsed_memory_tags,
                memory_scope=memory_scope
            )
        
        else:
            raise HTTPException(status_code=400, detail="No input provided")
        
        return JSONResponse(content=result)
    
    except Exception as e:
        error_msg = f"Error processing input: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Create necessary directories
def create_log_directories():
    """Create necessary log directories"""
    os.makedirs("/home/ubuntu/personal-ai-agent/app/logs/input_logs", exist_ok=True)

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    create_log_directories()
    logger.info("Input Gateway API started")

# For local testing
if __name__ == "__main__":
    import uvicorn
    create_log_directories()
    # Explicitly set port to 8000 for consistency across environments
    port = 8000
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
