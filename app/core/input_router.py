"""
Unified Input Router for the Personal AI Agent System.

This module provides functionality to accept various input types (text, audio, documents),
auto-detect their format, and route them to the appropriate agent or tool.
"""

import os
import json
import logging
import mimetypes
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64

# Import handlers
from app.tools.audio_input_handler import get_audio_input_handler
# We'll assume these exist or will be implemented
# from app.tools.pdf_input_handler import get_pdf_input_handler
# from app.tools.image_input_handler import get_image_input_handler
# from app.tools.document_input_handler import get_document_input_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("input_router")

class InputRouter:
    """
    Router for handling and directing various types of input to appropriate handlers.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the InputRouter.
        
        Args:
            memory_manager: Optional memory manager for storing inputs and results
        """
        self.memory_manager = memory_manager
        
        # Initialize handlers
        self.audio_handler = get_audio_input_handler(memory_manager)
        
        # In a real implementation, we would initialize other handlers
        # self.pdf_handler = get_pdf_input_handler(memory_manager)
        # self.image_handler = get_image_handler(memory_manager)
        # self.document_handler = get_document_handler(memory_manager)
        
        # Define supported mime types
        self.audio_mime_types = [
            'audio/wav', 'audio/x-wav', 
            'audio/mpeg', 'audio/mp3',
            'audio/ogg', 'audio/flac',
            'audio/x-m4a', 'audio/m4a'
        ]
        
        self.document_mime_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/markdown', 'text/csv'
        ]
        
        self.image_mime_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'image/tiff', 'image/bmp', 'image/webp'
        ]
    
    def route_input(
        self,
        input_data: Any,
        input_type: Optional[str] = None,
        file_path: Optional[str] = None,
        base64_data: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        target_agent: Optional[str] = None,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None,
        memory_scope: str = "agent"
    ) -> Dict[str, Any]:
        """
        Route input to the appropriate handler based on type.
        
        Args:
            input_data: The input data (text string or file content)
            input_type: Optional explicit input type ('text', 'audio', 'pdf', 'image', 'document')
            file_path: Optional path to an input file
            base64_data: Optional base64-encoded data with format prefix (e.g., "data:audio/wav;base64,...")
            metadata: Optional metadata about the input
            target_agent: Optional specific agent to route the input to
            store_memory: Whether to store the input in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry (agent or global)
            
        Returns:
            Dictionary containing the routing results
        """
        logger.info(f"Routing input with type: {input_type or 'auto-detect'}")
        
        try:
            # Initialize result
            result = {
                "success": False,
                "input_type": input_type,
                "detected_type": None,
                "target_agent": target_agent,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create logs directory if it doesn't exist
            log_dir = "/home/ubuntu/personal-ai-agent/app/logs/input_logs"
            os.makedirs(log_dir, exist_ok=True)
            
            # Process based on input type
            if input_type is None:
                # Auto-detect input type
                input_type = self._detect_input_type(input_data, file_path, base64_data)
                result["detected_type"] = input_type
            
            # Set default memory tags based on input type
            if memory_tags is None:
                memory_tags = ["input", input_type]
            elif "input" not in memory_tags:
                memory_tags.append("input")
            
            # Handle based on input type
            if input_type == "text":
                # Process text input
                processed_result = self._handle_text_input(
                    input_data, metadata, target_agent, store_memory, memory_tags, memory_scope
                )
                result.update(processed_result)
                
            elif input_type == "audio":
                # Process audio input
                processed_result = self._handle_audio_input(
                    input_data, file_path, base64_data, metadata, target_agent, store_memory, memory_tags, memory_scope
                )
                result.update(processed_result)
                
            elif input_type == "pdf":
                # Process PDF input
                processed_result = self._handle_pdf_input(
                    input_data, file_path, base64_data, metadata, target_agent, store_memory, memory_tags, memory_scope
                )
                result.update(processed_result)
                
            elif input_type == "image":
                # Process image input
                processed_result = self._handle_image_input(
                    input_data, file_path, base64_data, metadata, target_agent, store_memory, memory_tags, memory_scope
                )
                result.update(processed_result)
                
            elif input_type == "document":
                # Process document input
                processed_result = self._handle_document_input(
                    input_data, file_path, base64_data, metadata, target_agent, store_memory, memory_tags, memory_scope
                )
                result.update(processed_result)
                
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
            
            # Log the routing
            log_file = os.path.join(log_dir, f"input_router_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                # Create a safe copy of the result for logging
                log_result = result.copy()
                
                # Truncate large content fields
                if "input_text" in log_result and isinstance(log_result["input_text"], str) and len(log_result["input_text"]) > 500:
                    log_result["input_text"] = log_result["input_text"][:500] + "..."
                
                if "processed_text" in log_result and isinstance(log_result["processed_text"], str) and len(log_result["processed_text"]) > 500:
                    log_result["processed_text"] = log_result["processed_text"][:500] + "..."
                
                # Remove binary data
                if "base64_data" in log_result:
                    log_result["base64_data"] = "[BASE64 DATA TRUNCATED]"
                
                json.dump(log_result, f, indent=2)
            
            result["log_file"] = log_file
            return result
            
        except Exception as e:
            error_msg = f"Error routing input: {str(e)}"
            logger.error(error_msg)
            
            # Log the error
            log_file = os.path.join(log_dir, f"input_router_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "error": error_msg,
                    "input_type": input_type,
                    "target_agent": target_agent
                }, f, indent=2)
            
            return {
                "success": False,
                "error": error_msg,
                "input_type": input_type,
                "detected_type": result.get("detected_type"),
                "log_file": log_file
            }
    
    def _detect_input_type(
        self,
        input_data: Any,
        file_path: Optional[str] = None,
        base64_data: Optional[str] = None
    ) -> str:
        """
        Auto-detect the input type based on the provided data.
        
        Args:
            input_data: The input data
            file_path: Optional path to an input file
            base64_data: Optional base64-encoded data
            
        Returns:
            Detected input type as a string
        """
        # Check if we have a file path
        if file_path:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                if mime_type in self.audio_mime_types:
                    return "audio"
                elif mime_type in self.document_mime_types:
                    if mime_type == 'application/pdf':
                        return "pdf"
                    else:
                        return "document"
                elif mime_type in self.image_mime_types:
                    return "image"
        
        # Check if we have base64 data
        if base64_data:
            # Extract mime type from base64 prefix
            if base64_data.startswith('data:'):
                mime_part = base64_data.split(',')[0].split(':')[1].split(';')[0]
                if mime_part in self.audio_mime_types:
                    return "audio"
                elif mime_part in self.document_mime_types:
                    if mime_part == 'application/pdf':
                        return "pdf"
                    else:
                        return "document"
                elif mime_part in self.image_mime_types:
                    return "image"
        
        # If we have input_data as a string, assume it's text
        if isinstance(input_data, str):
            return "text"
        
        # Default to text if we can't determine the type
        return "text"
    
    def _handle_text_input(
        self,
        input_text: str,
        metadata: Optional[Dict[str, Any]],
        target_agent: Optional[str],
        store_memory: bool,
        memory_tags: List[str],
        memory_scope: str
    ) -> Dict[str, Any]:
        """
        Handle text input.
        
        Args:
            input_text: The text input
            metadata: Optional metadata about the input
            target_agent: Optional specific agent to route the input to
            store_memory: Whether to store the input in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry
            
        Returns:
            Dictionary containing the processing results
        """
        logger.info("Processing text input")
        
        # Store in memory if requested
        memory_id = None
        if store_memory and self.memory_manager:
            try:
                memory_entry = {
                    "type": "text_input",
                    "text": input_text,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_id = self.memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored text input in memory with ID: {memory_id}")
            except Exception as e:
                logger.error(f"Failed to store text input in memory: {str(e)}")
        
        # Forward to agent if specified
        if target_agent:
            logger.info(f"Forwarding text input to agent: {target_agent}")
            # In a real implementation, this would call the agent router
        
        return {
            "success": True,
            "input_type": "text",
            "input_text": input_text,
            "memory_id": memory_id,
            "forwarded_to_agent": target_agent
        }
    
    def _handle_audio_input(
        self,
        input_data: Any,
        file_path: Optional[str],
        base64_data: Optional[str],
        metadata: Optional[Dict[str, Any]],
        target_agent: Optional[str],
        store_memory: bool,
        memory_tags: List[str],
        memory_scope: str
    ) -> Dict[str, Any]:
        """
        Handle audio input.
        
        Args:
            input_data: The audio input data
            file_path: Optional path to an audio file
            base64_data: Optional base64-encoded audio data
            metadata: Optional metadata about the input
            target_agent: Optional specific agent to route the input to
            store_memory: Whether to store the input in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry
            
        Returns:
            Dictionary containing the processing results
        """
        logger.info("Processing audio input")
        
        # Handle file path
        if file_path and os.path.exists(file_path):
            # Use the audio input handler to process the file
            result = self.audio_handler.run(
                audio_path=file_path,
                store_memory=store_memory,
                memory_tags=memory_tags,
                memory_scope=memory_scope,
                forward_to_agent=target_agent
            )
            
            return {
                "success": result["success"],
                "input_type": "audio",
                "file_path": file_path,
                "transcribed_text": result.get("transcribed_text"),
                "memory_id": result.get("memory_id"),
                "forwarded_to_agent": target_agent
            }
        
        # Handle base64 data
        elif base64_data:
            # In a real implementation, we would decode the base64 data and save to a temp file
            # For now, we'll just return an error
            return {
                "success": False,
                "input_type": "audio",
                "error": "Base64 audio processing not implemented yet"
            }
        
        else:
            return {
                "success": False,
                "input_type": "audio",
                "error": "No valid audio input provided"
            }
    
    def _handle_pdf_input(
        self,
        input_data: Any,
        file_path: Optional[str],
        base64_data: Optional[str],
        metadata: Optional[Dict[str, Any]],
        target_agent: Optional[str],
        store_memory: bool,
        memory_tags: List[str],
        memory_scope: str
    ) -> Dict[str, Any]:
        """
        Handle PDF input.
        
        Args:
            input_data: The PDF input data
            file_path: Optional path to a PDF file
            base64_data: Optional base64-encoded PDF data
            metadata: Optional metadata about the input
            target_agent: Optional specific agent to route the input to
            store_memory: Whether to store the input in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry
            
        Returns:
            Dictionary containing the processing results
        """
        logger.info("Processing PDF input")
        
        # In a real implementation, we would use a PDF handler
        # For now, we'll just return a placeholder result
        return {
            "success": True,
            "input_type": "pdf",
            "file_path": file_path,
            "placeholder": "PDF processing would happen here",
            "forwarded_to_agent": target_agent
        }
    
    def _handle_image_input(
        self,
        input_data: Any,
        file_path: Optional[str],
        base64_data: Optional[str],
        metadata: Optional[Dict[str, Any]],
        target_agent: Optional[str],
        store_memory: bool,
        memory_tags: List[str],
        memory_scope: str
    ) -> Dict[str, Any]:
        """
        Handle image input.
        
        Args:
            input_data: The image input data
            file_path: Optional path to an image file
            base64_data: Optional base64-encoded image data
            metadata: Optional metadata about the input
            target_agent: Optional specific agent to route the input to
            store_memory: Whether to store the input in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry
            
        Returns:
            Dictionary containing the processing results
        """
        logger.info("Processing image input")
        
        # In a real implementation, we would use an image handler
        # For now, we'll just return a placeholder result
        return {
            "success": True,
            "input_type": "image",
            "file_path": file_path,
            "placeholder": "Image processing would happen here",
            "forwarded_to_agent": target_agent
        }
    
    def _handle_document_input(
        self,
        input_data: Any,
        file_path: Optional[str],
        base64_data: Optional[str],
        metadata: Optional[Dict[str, Any]],
        target_agent: Optional[str],
        store_memory: bool,
        memory_tags: List[str],
        memory_scope: str
    ) -> Dict[str, Any]:
        """
        Handle document input.
        
        Args:
            input_data: The document input data
            file_path: Optional path to a document file
            base64_data: Optional base64-encoded document data
            metadata: Optional metadata about the input
            target_agent: Optional specific agent to route the input to
            store_memory: Whether to store the input in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry
            
        Returns:
            Dictionary containing the processing results
        """
        logger.info("Processing document input")
        
        # In a real implementation, we would use a document handler
        # For now, we'll just return a placeholder result
        return {
            "success": True,
            "input_type": "document",
            "file_path": file_path,
            "placeholder": "Document processing would happen here",
            "forwarded_to_agent": target_agent
        }

# Factory function
def get_input_router(memory_manager=None):
    """
    Get an InputRouter instance.
    
    Args:
        memory_manager: Optional memory manager for storing inputs and results
        
    Returns:
        InputRouter instance
    """
    return InputRouter(memory_manager=memory_manager)
