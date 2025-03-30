"""
Audio Input Handler for the Personal AI Agent System.

This module provides functionality to handle voice input via uploaded audio files,
transcribe them using the audio_transcriber, and forward the transcribed text
to the appropriate agent entry point.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the audio transcriber
from app.tools.audio_transcriber import run as transcribe_audio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audio_input_handler")

class AudioInputHandler:
    """
    Handler for processing audio input files and converting them to text.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the AudioInputHandler.
        
        Args:
            memory_manager: Optional memory manager for storing transcriptions
        """
        self.memory_manager = memory_manager
        self.supported_formats = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    
    def run(
        self,
        audio_path: str,
        language: str = "en",
        include_timestamps: bool = False,
        detect_topics: bool = True,
        detect_sentiment: bool = True,
        store_memory: bool = True,
        memory_tags: List[str] = ["voice_input", "audio", "transcription"],
        memory_scope: str = "agent",
        forward_to_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an audio file, transcribe it, and forward the transcription.
        
        Args:
            audio_path: Path to the audio file
            language: Language code for transcription (e.g., 'en', 'fr', 'de')
            include_timestamps: Whether to include timestamps in the transcription
            detect_topics: Whether to detect main topics in the transcribed content
            detect_sentiment: Whether to analyze sentiment in the transcribed content
            store_memory: Whether to store the transcription in memory
            memory_tags: Tags to apply to the memory entry
            memory_scope: Scope for the memory entry (agent or global)
            forward_to_agent: Optional agent name to forward the transcription to
            
        Returns:
            Dictionary containing the processing results
        """
        logger.info(f"Processing audio input: {audio_path}")
        
        try:
            # Validate the audio file
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Check file extension
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {file_ext}. Supported formats: {', '.join(self.supported_formats)}")
            
            # Transcribe the audio
            transcription_result = transcribe_audio(
                audio_path=audio_path,
                language=language,
                include_timestamps=include_timestamps,
                detect_topics=detect_topics,
                detect_sentiment=detect_sentiment,
                store_memory=False  # We'll handle memory storage ourselves
            )
            
            if not transcription_result["success"]:
                raise Exception(f"Transcription failed: {transcription_result.get('error', 'Unknown error')}")
            
            # Extract the transcribed text
            transcribed_text = transcription_result["transcription"]["full_text"]
            
            # Store in memory if requested
            memory_id = None
            if store_memory and self.memory_manager:
                try:
                    # Create a memory entry with the transcription
                    memory_entry = {
                        "type": "voice_input",
                        "audio_path": audio_path,
                        "language": language,
                        "transcription": transcribed_text,
                        "metadata": transcription_result["metadata"],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Add topics if available
                    if transcription_result.get("topics"):
                        memory_entry["topics"] = transcription_result["topics"]["topics"]
                    
                    # Add sentiment if available
                    if transcription_result.get("sentiment"):
                        memory_entry["sentiment"] = transcription_result["sentiment"]["overall_sentiment"]
                    
                    memory_id = self.memory_manager.add_memory(
                        content=json.dumps(memory_entry),
                        scope=memory_scope,
                        tags=memory_tags + [f"lang_{language}"]
                    )
                    
                    logger.info(f"Stored voice input in memory with ID: {memory_id}")
                except Exception as e:
                    logger.error(f"Failed to store voice input in memory: {str(e)}")
            
            # Prepare the result
            result = {
                "success": True,
                "audio_path": audio_path,
                "transcribed_text": transcribed_text,
                "language": language,
                "metadata": transcription_result["metadata"],
                "memory_id": memory_id,
                "topics": transcription_result.get("topics"),
                "sentiment": transcription_result.get("sentiment")
            }
            
            # Forward to agent if requested
            if forward_to_agent:
                try:
                    # In a real implementation, this would call the agent router
                    # For now, we'll just log the forwarding
                    logger.info(f"Forwarding transcribed text to agent: {forward_to_agent}")
                    result["forwarded_to_agent"] = forward_to_agent
                    
                    # Create a log entry for the forwarding
                    log_dir = "/home/ubuntu/personal-ai-agent/app/logs/input_logs"
                    os.makedirs(log_dir, exist_ok=True)
                    
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "input_type": "voice",
                        "audio_path": audio_path,
                        "transcribed_text": transcribed_text,
                        "forwarded_to_agent": forward_to_agent,
                        "memory_id": memory_id
                    }
                    
                    log_file = os.path.join(log_dir, f"voice_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    with open(log_file, 'w', encoding='utf-8') as f:
                        json.dump(log_entry, f, indent=2)
                    
                    result["log_file"] = log_file
                except Exception as e:
                    logger.error(f"Failed to forward to agent: {str(e)}")
                    result["forward_error"] = str(e)
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing audio input: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "audio_path": audio_path
            }

# Factory function
def get_audio_input_handler(memory_manager=None):
    """
    Get an AudioInputHandler instance.
    
    Args:
        memory_manager: Optional memory manager for storing transcriptions
        
    Returns:
        AudioInputHandler instance
    """
    return AudioInputHandler(memory_manager=memory_manager)
