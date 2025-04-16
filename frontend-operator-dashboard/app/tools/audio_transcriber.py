"""
Audio Transcriber Tool for the Personal AI Agent System.

This module provides functionality to transcribe speech from audio files
and extract key information from the transcribed content.
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("audio_transcriber")

def run(
    audio_path: str,
    language: str = "en",
    speaker_diarization: bool = False,
    max_speakers: int = 2,
    include_timestamps: bool = True,
    include_confidence: bool = False,
    detect_topics: bool = False,
    detect_sentiment: bool = False,
    output_format: str = "text",
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["audio", "transcription", "speech"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Transcribe speech from an audio file and extract information.
    
    Args:
        audio_path: Path to the audio file
        language: Language code for transcription (e.g., 'en', 'fr', 'de', 'es', 'zh')
        speaker_diarization: Whether to identify different speakers
        max_speakers: Maximum number of speakers to identify (if speaker_diarization is True)
        include_timestamps: Whether to include timestamps in the transcription
        include_confidence: Whether to include confidence scores for each transcribed segment
        detect_topics: Whether to detect main topics in the transcribed content
        detect_sentiment: Whether to analyze sentiment in the transcribed content
        output_format: Format for the transcription output (text, json, srt, vtt)
        store_memory: Whether to store the transcription in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the transcription and analysis results
    """
    logger.info(f"Transcribing audio file: {audio_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        # Validate inputs
        if output_format not in ["text", "json", "srt", "vtt"]:
            raise ValueError(f"Invalid output format: {output_format}. Supported formats: text, json, srt, vtt")
        
        # Get audio metadata
        audio_metadata = _get_audio_metadata(audio_path)
        
        # In a real implementation, this would use speech recognition APIs
        # For now, we'll simulate the transcription
        
        # Simulate transcription
        transcription_result = _simulate_transcription(
            audio_path,
            language,
            speaker_diarization,
            max_speakers,
            include_timestamps,
            include_confidence,
            audio_metadata.get("duration", 60)
        )
        
        # Detect topics if requested
        topics_result = None
        if detect_topics:
            topics_result = _detect_topics(transcription_result["full_text"])
        
        # Analyze sentiment if requested
        sentiment_result = None
        if detect_sentiment:
            sentiment_result = _analyze_sentiment(transcription_result["full_text"])
        
        # Format the output
        formatted_output = _format_output(
            transcription_result,
            topics_result,
            sentiment_result,
            output_format
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the transcription
                memory_entry = {
                    "type": "audio_transcription",
                    "audio_path": audio_path,
                    "language": language,
                    "transcription": transcription_result["full_text"][:500] + ("..." if len(transcription_result["full_text"]) > 500 else ""),
                    "duration": audio_metadata.get("duration", 0),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add topics if available
                if topics_result:
                    memory_entry["topics"] = topics_result["topics"]
                
                # Add sentiment if available
                if sentiment_result:
                    memory_entry["sentiment"] = sentiment_result["overall_sentiment"]
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + [f"lang_{language}"]
                )
                
                logger.info(f"Stored audio transcription in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store audio transcription in memory: {str(e)}")
        
        return {
            "success": True,
            "audio_path": audio_path,
            "metadata": audio_metadata,
            "transcription": transcription_result,
            "topics": topics_result,
            "sentiment": sentiment_result,
            "formatted_output": formatted_output
        }
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "audio_path": audio_path
        }

def _get_audio_metadata(audio_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an audio file.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Dictionary with audio metadata
    """
    # In a real implementation, this would use libraries like pydub or ffmpeg
    # For now, we'll extract basic file information
    
    file_stats = os.stat(audio_path)
    file_name = os.path.basename(audio_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Map common extensions to formats
    format_map = {
        ".mp3": "MP3",
        ".wav": "WAV",
        ".flac": "FLAC",
        ".aac": "AAC",
        ".ogg": "OGG",
        ".m4a": "M4A",
        ".wma": "WMA"
    }
    
    audio_format = format_map.get(file_ext, "Unknown")
    
    # Generate a deterministic but seemingly random duration based on the file path
    seed = sum(ord(c) for c in audio_path)
    random.seed(seed)
    duration = random.randint(30, 600)  # Between 30 seconds and 10 minutes
    
    return {
        "file_name": file_name,
        "file_path": audio_path,
        "file_size": file_stats.st_size,
        "format": audio_format,
        "duration": duration,
        "sample_rate": random.choice([8000, 16000, 22050, 44100, 48000]),
        "channels": random.choice([1, 2]),
        "bit_rate": random.choice([64, 128, 192, 256, 320]),
        "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
    }

def _simulate_transcription(
    audio_path: str,
    language: str,
    speaker_diarization: bool,
    max_speakers: int,
    include_timestamps: bool,
    include_confidence: bool,
    duration: int
) -> Dict[str, Any]:
    """
    Simulate speech transcription from an audio file.
    
    Args:
        audio_path: Path to the audio file
        language: Language code for transcription
        speaker_diarization: Whether to identify different speakers
        max_speakers: Maximum number of speakers to identify
        include_timestamps: Whether to include timestamps
        include_confidence: Whether to include confidence scores
        duration: Duration of the audio in seconds
        
    Returns:
        Dictionary with simulated transcription results
    """
    # Generate a deterministic but seemingly random seed based on the audio path
    seed = sum(ord(c) for c in audio_path)
    random.seed(seed)
    
    # Determine the type of audio based on the file name
    file_name = os.path.basename(audio_path).lower()
    
    # Predefined transcription content for different types of audio
    if "interview" in file_name or "conversation" in file_name:
        transcription_type = "interview"
    elif "lecture" in file_name or "presentation" in file_name:
        transcription_type = "lecture"
    elif "meeting" in file_name:
        transcription_type = "meeting"
    elif "podcast" in file_name:
        transcription_type = "podcast"
    elif "speech" in file_name:
        transcription_type = "speech"
    else:
        # Default to a generic transcription
        transcription_type = random.choice(["interview", "lecture", "meeting", "podcast", "speech"])
    
    # Generate transcription segments
    segments = _generate_transcription_segments(
        transcription_type,
        language,
        speaker_diarization,
        max_speakers,
        include_timestamps,
        include_confidence,
        duration
    )
    
    # Combine segments into full text
    full_text = ""
    for segment in segments:
        if speaker_diarization and "speaker" in segment:
            full_text += f"Speaker {segment['speaker']}: "
        full_text += segment["text"] + " "
    
    full_text = full_text.strip()
    
    return {
        "full_text": full_text,
        "segments": segments,
        "language": language,
        "duration": duration,
        "word_count": len(full_text.split())
    }

def _generate_transcription_segments(
    transcription_type: str,
    language: str,
    speaker_diarization: bool,
    max_speakers: int,
    include_timestamps: bool,
    include_confidence: bool,
    duration: int
) -> List[Dict[str, Any]]:
    """
    Generate simulated transcription segments.
    
    Args:
        transcription_type: Type of transcription to generate
        language: Language code for transcription
        speaker_diarization: Whether to identify different speakers
        max_speakers: Maximum number of speakers to identify
        include_timestamps: Whether to include timestamps
        include_confidence: Whether to include confidence scores
        duration: Duration of the audio in seconds
        
    Returns:
        List of simulated transcription segments
    """
    # Define templates for different types of transcriptions
    templates = {
        "interview": _get_interview_template(),
        "lecture": _get_lecture_template(),
        "meeting": _get_meeting_template(),
        "podcast": _get_podcast_template(),
        "speech": _get_speech_template()
    }
    
    # Get the appropriate template
    template = templates.get(transcription_type, templates["interview"])
    
    # Determine number of speakers
    if speaker_diarization:
        if transcription_type == "interview":
            num_speakers = min(2, max_speakers)
        elif transcription_type == "meeting":
            num_speakers = min(random.randint(3, 6), max_speakers)
        elif transcription_type == "podcast":
            num_speakers = min(random.randint(2, 4), max_speakers)
        else:
            num_speakers = 1
    else:
        num_speakers = 1
    
    # Generate segments
    segments = []
    current_time = 0
    
    for i, text in enumerate(template):
        # Determine speaker if using diarization
        if speaker_diarization and num_speakers > 1:
            if transcription_type == "interview":
                # Alternate between interviewer and interviewee
                speaker = (i % 2) + 1
            elif transcription_type in ["meeting", "podcast"]:
                # Random speaker for meetings and podcasts
                speaker = random.randint(1, num_speakers)
            else:
                speaker = 1
        else:
            speaker = 1
        
        # Calculate segment duration based on text length
        # Assume average speaking rate of 150 words per minute
        words = len(text.split())
        segment_duration = (words / 150) * 60  # in seconds
        
        # Ensure we don't exceed total duration
        if current_time + segment_duration > duration:
            segment_duration = max(1, duration - current_time)
            
        # Create segment
        segment = {
            "text": text
        }
        
        # Add speaker if using diarization
        if speaker_diarization:
            segment["speaker"] = speaker
        
        # Add timestamps if requested
        if include_timestamps:
            start_time = current_time
            end_time = current_time + segment_duration
            
            segment["start_time"] = round(start_time, 2)
            segment["end_time"] = round(end_time, 2)
        
        # Add confidence if requested
        if include_confidence:
            # Generate a high confidence score with some variation
            segment["confidence"] = round(random.uniform(0.85, 0.98), 2)
        
        segments.append(segment)
        
        # Update current time
        current_time += segment_duration
        
        # Break if we've reached the duration
        if current_time >= duration:
            break
    
    return segments

def _detect_topics(text: str) -> Dict[str, Any]:
    """
    Detect main topics in the transcribed content.
    
    Args:
        text: Transcribed text
        
    Returns:
        Dictionary with detected topics
    """
    # In a real implementation, this would use NLP techniques
    # For now, we'll simulate topic detection
    
    # Generate a deterministic but seemingly random seed based on the text
    seed = sum(ord(c) for c in text[:100])
    random.seed(seed)
    
    # Potential topics based on common domains
    potential_topics = [
        "Technology", "Business", "Science", "Health", "Education",
        "Politics", "Environment", "Entertainment", "Sports", "Finance",
        "Art", "History", "Travel", "Food", "Fashion"
    ]
    
    # Select 2-4 topics
    num_topics = random.randint(2, 4)
    topics = random.sample(potential_topics, num_topics)
    
    # Generate topic details
    topic_details = []
    for topic in topics:
        # Extract "relevant" keywords from the text
        words = text.split()
        keywords = random.sample(words, min(5, len(words)))
        
        topic_details.append({
            "topic": topic,
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "keywords": keywords
        })
    
    # Sort by confidence
    topic_details.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "topics": [topic["topic"] for topic in topic_details],
        "details": topic_details
    }

def _analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment in the transcribed content.
    
    Args:
        text: Transcribed text
        
    Returns:
        Dictionary with sentiment analysis results
    """
    # In a real implementation, this would use NLP techniques
    # For now, we'll simulate sentiment analysis
    
    # Generate a deterministic but seemingly random seed based on the text
    seed = sum(ord(c) for c in text[:100])
    random.seed(seed)
    
    # Generate overall sentiment
    sentiment_score = random.uniform(-1.0, 1.0)
    
    if sentiment_score > 0.3:
        overall_sentiment = "positive"
    elif sentiment_score < -0.3:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    # Generate sentiment breakdown
    sentiment_breakdown = {
        "positive": round(max(0, (sentiment_score + 1) / 2), 2),
        "neutral": round(1 - abs(sentiment_score), 2),
        "negative": round(max(0, (-sentiment_score + 1) / 2), 2)
    }
    
    # Normalize to ensure they sum to 1
    total = sum(sentiment_breakdown.values())
    sentiment_breakdown = {k: round(v / total, 2) for k, v in sentiment_breakdown.items()}
    
    # Generate segment-level sentiment
    segments = []
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    for i, sentence in enumerate(sentences[:10]):  # Limit to first 10 sentences
        if not sentence:
            continue
            
        # Generate sentiment for this segment
        segment_score = sentiment_score + random.uniform(-0.4, 0.4)
        segment_score = max(-1.0, min(1.0, segment_score))  # Clamp to [-1, 1]
        
        if segment_score > 0.3:
            segment_sentiment = "positive"
        elif segment_score < -0.3:
            segment_sentiment = "negative"
        else:
            segment_sentiment = "neutral"
        
        segments.append({
            "text": sentence,
            "sentiment": segment_sentiment,
            "score": round(segment_score, 2)
        })
    
    return {
        "overall_sentiment": overall_sentiment,
        "sentiment_score": round(sentiment_score, 2),
        "sentiment_breakdown": sentiment_breakdown,
        "segments": segments
    }

def _format_output(
    transcription: Dict[str, Any],
    topics: Optional[Dict[str, Any]],
    sentiment: Optional[Dict[str, Any]],
    output_format: str
) -> str:
    """
    Format the transcription and analysis results in the specified format.
    
    Args:
        transcription: Transcription results
        topics: Topic detection results
        sentiment: Sentiment analysis results
        output_format: Output format (text, json, srt, vtt)
        
    Returns:
        Formatted output
    """
    if output_format == "json":
        # Return a JSON-compatible structure
        result = {
            "transcription": transcription,
            "topics": topics,
            "sentiment": sentiment
        }
        return result
    
    elif output_format == "text":
        # Format as plain text
        output = []
        
        # Add transcription
        output.append("=== TRANSCRIPTION ===")
        output.append("")
        
        for segment in transcription["segments"]:
            line = ""
            
            # Add timestamps if available
            if "start_time" in segment and "end_time" in segment:
                line += f"[{_format_timestamp(segment['start_time'])} - {_format_timestamp(segment['end_time'])}] "
            
            # Add speaker if available
            if "speaker" in segment:
                line += f"Speaker {segment['speaker']}: "
            
            # Add text
            line += segment["text"]
            
            # Add confidence if available
            if "confidence" in segment:
                line += f" (Confidence: {segment['confidence']:.2f})"
            
            output.append(line)
        
        # Add topics if available
        if topics:
            output.append("")
            output.append("=== DETECTED TOPICS ===")
            for topic in topics["details"]:
                output.append(f"- {topic['topic']} (Confidence: {topic['confidence']:.2f})")
                output.append(f"  Keywords: {', '.join(topic['keywords'])}")
            output.append("")
        
        # Add sentiment if available
        if sentiment:
            output.append("")
            output.append("=== SENTIMENT ANALYSIS ===")
            output.append(f"Overall sentiment: {sentiment['overall_sentiment']} (Score: {sentiment['sentiment_score']:.2f})")
            output.append(f"Breakdown: Positive: {sentiment['sentiment_breakdown']['positive']:.2f}, " +
                         f"Neutral: {sentiment['sentiment_breakdown']['neutral']:.2f}, " +
                         f"Negative: {sentiment['sentiment_breakdown']['negative']:.2f}")
            output.append("")
        
        return "\n".join(output)
    
    elif output_format == "srt":
        # Format as SubRip (SRT) subtitle format
        output = []
        
        for i, segment in enumerate(transcription["segments"]):
            if "start_time" not in segment or "end_time" not in segment:
                continue
                
            # Add subtitle index
            output.append(str(i + 1))
            
            # Add timestamps
            start_time = _format_srt_timestamp(segment["start_time"])
            end_time = _format_srt_timestamp(segment["end_time"])
            output.append(f"{start_time} --> {end_time}")
            
            # Add text (with speaker if available)
            text = segment["text"]
            if "speaker" in segment:
                text = f"Speaker {segment['speaker']}: {text}"
            
            output.append(text)
            output.append("")  # Empty line between subtitles
        
        return "\n".join(output)
    
    elif output_format == "vtt":
        # Format as WebVTT subtitle format
        output = ["WEBVTT", ""]
        
        for i, segment in enumerate(transcription["segments"]):
            if "start_time" not in segment or "end_time" not in segment:
                continue
                
            # Add optional cue identifier
            output.append(f"cue-{i+1}")
            
            # Add timestamps
            start_time = _format_vtt_timestamp(segment["start_time"])
            end_time = _format_vtt_timestamp(segment["end_time"])
            output.append(f"{start_time} --> {end_time}")
            
            # Add text (with speaker if available)
            text = segment["text"]
            if "speaker" in segment:
                text = f"Speaker {segment['speaker']}: {text}"
            
            output.append(text)
            output.append("")  # Empty line between cues
        
        return "\n".join(output)
    
    else:
        # Default to text format
        return _format_output(transcription, topics, sentiment, "text")

def _format_timestamp(seconds: float) -> str:
    """
    Format seconds as MM:SS.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def _format_srt_timestamp(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS,mmm for SRT format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    seconds_int = int(seconds_remainder)
    milliseconds = int((seconds_remainder - seconds_int) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d},{milliseconds:03d}"

def _format_vtt_timestamp(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS.mmm for WebVTT format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    seconds_int = int(seconds_remainder)
    milliseconds = int((seconds_remainder - seconds_int) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}.{milliseconds:03d}"

def _get_interview_template() -> List[str]:
    """
    Get a template for an interview transcription.
    
    Returns:
        List of text segments for an interview
    """
    return [
        "Thank you for joining us today. Could you start by introducing yourself and your background?",
        "Thank you for having me. I'm a researcher in the field of artificial intelligence, focusing on natural language processing and machine learning applications.",
        "What sparked your interest in this field?",
        "I've always been fascinated by the intersection of language and technology. During my undergraduate studies, I worked on a project that involved analyzing text data, and I was amazed by the potential applications of NLP in solving real-world problems.",
        "Can you tell us about your current research projects?",
        "Currently, I'm working on improving conversational AI systems to make them more contextually aware and capable of understanding nuanced human communication. We're developing models that can better grasp implicit meaning and cultural references.",
        "What do you see as the biggest challenges in your field right now?",
        "One of the major challenges is developing AI systems that are both powerful and ethical. We need to ensure these technologies are fair, transparent, and respect user privacy. Another challenge is creating systems that can truly understand context and common sense reasoning, which humans take for granted.",
        "How do you think AI will impact society in the next decade?",
        "I believe we'll see AI becoming more integrated into our daily lives, from healthcare to education to creative fields. The technology will become more accessible to non-experts, enabling new applications we haven't even imagined yet. However, this also means we need thoughtful policies and ethical guidelines to ensure these tools benefit humanity.",
        "What advice would you give to students interested in pursuing a career in AI?",
        "I'd recommend building a strong foundation in mathematics and computer science, but also studying fields like psychology, linguistics, or philosophy. Interdisciplinary knowledge is incredibly valuable. Also, don't just focus on the technical aspects—consider the ethical and societal implications of the technology you're developing.",
        "Thank you for sharing your insights with us today.",
        "It was my pleasure. Thank you for the thoughtful questions."
    ]

def _get_lecture_template() -> List[str]:
    """
    Get a template for a lecture transcription.
    
    Returns:
        List of text segments for a lecture
    """
    return [
        "Welcome to today's lecture on data science fundamentals. We'll be covering key concepts that form the foundation of modern data analysis and machine learning applications.",
        "Let's start with defining what data science actually is. At its core, data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data.",
        "The data science workflow typically consists of several key steps. First, we have data collection, where we gather relevant data from various sources. This could include databases, APIs, web scraping, or even manual data entry.",
        "Next comes data cleaning and preprocessing. Real-world data is often messy, with missing values, outliers, and inconsistencies. This step involves handling these issues to prepare the data for analysis.",
        "After preprocessing, we move to exploratory data analysis, or EDA. This involves visualizing and summarizing the data to understand its main characteristics, patterns, and relationships between variables.",
        "Feature engineering is another crucial step, where we create new features or transform existing ones to improve the performance of our models. This requires domain knowledge and creativity.",
        "Then we have model selection and training, where we choose appropriate algorithms based on our problem type and train them using our prepared data. This might involve techniques like cross-validation to ensure our models generalize well to new data.",
        "Model evaluation follows, where we assess how well our models perform using various metrics. For classification problems, we might look at accuracy, precision, recall, and F1 score. For regression problems, we might use mean squared error or R-squared.",
        "Finally, we have model deployment and monitoring, where we integrate our models into production systems and continuously monitor their performance over time.",
        "Let's now dive deeper into some key statistical concepts that underpin data science. Understanding probability distributions, hypothesis testing, and regression analysis is essential for effective data analysis.",
        "For next week's lecture, please read chapters 3 and 4 from the textbook, which cover regression techniques and classification algorithms. We'll be implementing these concepts in our lab session.",
        "Are there any questions before we wrap up today's lecture?"
    ]

def _get_meeting_template() -> List[str]:
    """
    Get a template for a meeting transcription.
    
    Returns:
        List of text segments for a meeting
    """
    return [
        "Good morning everyone. Thank you for joining today's project status meeting. Let's start by going through the agenda.",
        "First, we'll review the progress on key deliverables. Then we'll discuss any blockers or challenges. Finally, we'll outline next steps and action items.",
        "Sarah, could you please update us on the development progress?",
        "Sure. We've completed about 80% of the planned features for this sprint. The user authentication module is now working properly, and we've fixed the major bugs in the reporting dashboard. We're still working on the data export functionality, which has been more complex than we initially estimated.",
        "Thanks Sarah. Do you anticipate any delays in completing the remaining features?",
        "We might need an extra day or two for the data export feature. We discovered some edge cases that weren't covered in the initial requirements, and we want to make sure we handle them properly.",
        "That's understandable. Let's plan for that buffer. Michael, how are things going with the QA testing?",
        "We've completed testing for all the implemented features and logged about 15 bugs, most of which are minor UI issues. The development team has already fixed 10 of them. We're on track to complete all testing by the end of the sprint.",
        "Great. And Jennifer, any updates on the client feedback from the last demo?",
        "Yes, the client was generally positive about the progress. They particularly liked the new dashboard design. They did request one change to the reporting filters, which I've already discussed with the development team. It's a relatively small change that we can incorporate in this sprint.",
        "That's good to hear. Now, let's discuss any blockers or challenges. Does anyone have issues that need addressing?",
        "I have one concern about the API integration with the third-party payment system. Their documentation is incomplete, and we're waiting for their support team to provide additional information. This might impact our timeline if we don't hear back soon.",
        "Thanks for flagging that. I'll reach out to our contact at the payment provider today to escalate this. Anyone else?",
        "No other major blockers from the development side.",
        "Alright, let's move on to next steps and action items. Based on our discussion, here's what we need to focus on for the next week.",
        "Sarah and team will continue work on the data export feature. Michael will complete the remaining QA testing. I'll follow up with the payment provider about the API documentation. And Jennifer will communicate the updated timeline to the client.",
        "Let's schedule our next status meeting for the same time next week. Does that work for everyone?",
        "Works for me.",
        "Yes, that's fine.",
        "Great. Thank you all for your updates. If any new issues arise before our next meeting, please don't hesitate to reach out. Have a productive week!"
    ]

def _get_podcast_template() -> List[str]:
    """
    Get a template for a podcast transcription.
    
    Returns:
        List of text segments for a podcast
    """
    return [
        "Welcome to another episode of Tech Horizons, where we explore emerging technologies and their impact on our future. I'm your host, Alex, and today we're diving into the fascinating world of quantum computing.",
        "Joining me today is Dr. Sarah Chen, a quantum physicist and researcher at Quantum Innovations Lab. Sarah, welcome to the show!",
        "Thanks for having me, Alex. I'm excited to chat about quantum computing today.",
        "For our listeners who might be new to this topic, could you start by explaining what quantum computing is and how it differs from classical computing?",
        "Absolutely. Classical computers, which we all use daily, process information in bits—binary digits that can be either 0 or 1. Quantum computers, on the other hand, use quantum bits or qubits, which can exist in multiple states simultaneously thanks to a quantum property called superposition.",
        "This means quantum computers can process vast amounts of information in parallel, potentially solving certain problems much faster than even the most powerful classical supercomputers.",
        "That's fascinating. What kinds of problems are quantum computers particularly good at solving?",
        "Quantum computers excel at problems involving optimization, simulation, and cryptography. For example, they could revolutionize drug discovery by simulating molecular interactions at a quantum level, something classical computers struggle with.",
        "They're also well-suited for optimization problems like route planning or supply chain management, and they could potentially break many of the encryption algorithms that secure our digital communications today.",
        "Speaking of encryption, I've heard concerns about quantum computers threatening current security systems. Is this something we should be worried about?",
        "It's definitely something we need to prepare for, but not panic about. Current quantum computers aren't yet powerful enough to break widely-used encryption methods. However, researchers are already developing quantum-resistant cryptography to stay ahead of the curve.",
        "The cybersecurity community is working on what we call 'post-quantum cryptography'—encryption methods that even quantum computers couldn't easily crack.",
        "That's reassuring. Where do we stand currently with quantum computing development? Are these still mainly research projects, or are we seeing practical applications?",
        "We're in an interesting transition period. Major tech companies like IBM, Google, and Microsoft have operational quantum computers, though they're still limited in capabilities. IBM even offers cloud access to their quantum systems for researchers and developers.",
        "We've seen some impressive demonstrations, like Google's quantum supremacy experiment in 2019, where their quantum computer performed a specific calculation much faster than the world's most powerful supercomputer could.",
        "But we're still years away from quantum computers that can reliably solve real-world problems better than classical computers. The technology faces significant engineering challenges, particularly in maintaining quantum coherence—keeping qubits stable enough to perform reliable calculations.",
        "For our listeners who are excited about quantum computing, what resources would you recommend to learn more?",
        "There are some excellent online courses available through platforms like Coursera and edX. IBM's Quantum Experience lets you actually run simple programs on real quantum computers. And for those who prefer books, 'Quantum Computing for Everyone' by Chris Bernhardt is a great introduction that doesn't require an advanced physics background.",
        "Wonderful recommendations. Before we wrap up, what's your vision for the future of quantum computing? Where do you see this field in 10 or 20 years?",
        "I believe quantum computing will become an essential part of our computing ecosystem, working alongside classical computers rather than replacing them. We'll likely see quantum computers solving specific problems in fields like materials science, pharmaceuticals, and finance.",
        "I'm particularly excited about hybrid approaches that combine quantum and classical computing to tackle complex real-world problems. And I think quantum computing will drive new discoveries in fundamental science by allowing us to simulate quantum systems that we currently can't model effectively.",
        "That's a compelling vision. Thank you so much for sharing your expertise with us today, Sarah.",
        "It's been a pleasure, Alex. Thanks for having me on the show.",
        "And thank you to our listeners for tuning in to this episode of Tech Horizons. If you enjoyed our discussion, please subscribe to our podcast and leave a review. Until next time, I'm Alex, encouraging you to keep exploring the technologies shaping our future."
    ]

def _get_speech_template() -> List[str]:
    """
    Get a template for a speech transcription.
    
    Returns:
        List of text segments for a speech
    """
    return [
        "Distinguished guests, faculty members, and graduating students, it is an honor to address you today on this momentous occasion.",
        "As you stand at the threshold of a new chapter in your lives, I want to share some thoughts on navigating the rapidly changing world that awaits you.",
        "The diploma you will receive today represents not just the culmination of years of hard work, but also the beginning of a lifelong journey of learning and growth.",
        "We live in an era of unprecedented change. Technologies that seemed like science fiction just a decade ago are now integral parts of our daily lives. The pace of innovation continues to accelerate, reshaping industries, economies, and societies.",
        "In this context, the most valuable skill you can cultivate is adaptability—the ability to learn, unlearn, and relearn as circumstances evolve. Your education has provided you with a foundation of knowledge, but perhaps more importantly, it has taught you how to think critically, solve problems creatively, and communicate effectively.",
        "These fundamental capabilities will serve you well regardless of how your chosen field transforms in the years ahead.",
        "As you embark on your professional journeys, I encourage you to embrace challenges and view setbacks as opportunities for growth. Remember that failure is not the opposite of success—it's a stepping stone on the path to achievement.",
        "Some of the most successful individuals and organizations in history have faced numerous failures before making breakthrough contributions. What distinguished them was their resilience and willingness to learn from each experience.",
        "I also urge you to consider the broader impact of your work. The complex challenges facing humanity—from climate change to healthcare access to digital privacy—require not just technical expertise but also ethical consideration and cross-disciplinary collaboration.",
        "You have the opportunity to contribute to solutions that improve lives and create a more equitable, sustainable world. This is both a tremendous responsibility and an exciting possibility.",
        "As you leave this institution, remember that you are part of a community that extends beyond these walls. The connections you've formed here—with professors, mentors, and fellow students—represent a network of support and inspiration that will endure throughout your lives.",
        "Stay connected, not just with this institution, but with the values of intellectual curiosity, integrity, and service that it embodies.",
        "In closing, I want to congratulate each of you on your remarkable achievement. The path that brought you here wasn't easy, particularly given the unique challenges of recent years. Your perseverance in the face of adversity speaks volumes about your character and potential.",
        "As you go forward from this day, carry with you the knowledge, skills, and relationships you've developed here. Face the future not with fear but with confidence in your ability to adapt, learn, and make meaningful contributions.",
        "Thank you, and congratulations to the graduating class!"
    ]
