"""
Video Summarizer Tool for the Personal AI Agent System.

This module provides functionality to analyze and summarize video content,
extracting key information, scenes, and insights.
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("video_summarizer")

def run(
    video_path: str,
    summary_type: str = "comprehensive",
    include_timestamps: bool = True,
    extract_frames: bool = False,
    frames_output_dir: Optional[str] = None,
    frames_interval: int = 60,
    detect_scenes: bool = False,
    detect_faces: bool = False,
    detect_objects: bool = False,
    detect_text: bool = False,
    detect_topics: bool = True,
    transcribe_audio: bool = True,
    language: str = "en",
    max_summary_length: int = 500,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["video", "summary", "multimedia"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Analyze and summarize video content.
    
    Args:
        video_path: Path to the video file
        summary_type: Type of summary to generate (brief, comprehensive, detailed)
        include_timestamps: Whether to include timestamps in the summary
        extract_frames: Whether to extract key frames from the video
        frames_output_dir: Directory to save extracted frames (required if extract_frames is True)
        frames_interval: Interval in seconds between extracted frames
        detect_scenes: Whether to detect and analyze scene changes
        detect_faces: Whether to detect and identify faces in the video
        detect_objects: Whether to detect objects in the video
        detect_text: Whether to detect and extract text visible in the video
        detect_topics: Whether to identify main topics discussed in the video
        transcribe_audio: Whether to transcribe speech in the video
        language: Language code for transcription and text analysis
        max_summary_length: Maximum length of the generated summary in words
        store_memory: Whether to store the summary in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the video summary and analysis results
    """
    logger.info(f"Analyzing video file: {video_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        # Validate inputs
        if summary_type not in ["brief", "comprehensive", "detailed"]:
            raise ValueError(f"Invalid summary type: {summary_type}. Supported types: brief, comprehensive, detailed")
        
        if extract_frames and not frames_output_dir:
            raise ValueError("frames_output_dir must be provided when extract_frames is True")
        
        if extract_frames and frames_output_dir and not os.path.exists(frames_output_dir):
            os.makedirs(frames_output_dir, exist_ok=True)
            logger.info(f"Created frames output directory: {frames_output_dir}")
        
        # Get video metadata
        video_metadata = _get_video_metadata(video_path)
        
        # In a real implementation, this would use computer vision and audio processing
        # For now, we'll simulate the video analysis
        
        # Initialize results
        results = {
            "metadata": video_metadata
        }
        
        # Simulate scene detection if requested
        if detect_scenes:
            results["scenes"] = _simulate_scene_detection(video_path, video_metadata["duration"])
        
        # Simulate face detection if requested
        if detect_faces:
            results["faces"] = _simulate_face_detection(video_path)
        
        # Simulate object detection if requested
        if detect_objects:
            results["objects"] = _simulate_object_detection(video_path)
        
        # Simulate text detection if requested
        if detect_text:
            results["text"] = _simulate_text_detection(video_path, language)
        
        # Simulate audio transcription if requested
        if transcribe_audio:
            results["transcription"] = _simulate_audio_transcription(video_path, language)
        
        # Simulate topic detection if requested
        if detect_topics:
            # Use transcription if available, otherwise generate topics directly
            if transcribe_audio and "transcription" in results:
                transcript_text = results["transcription"]["full_text"]
                results["topics"] = _simulate_topic_detection(video_path, transcript_text)
            else:
                results["topics"] = _simulate_topic_detection(video_path)
        
        # Simulate frame extraction if requested
        if extract_frames:
            results["frames"] = _simulate_frame_extraction(
                video_path,
                frames_output_dir,
                frames_interval,
                video_metadata["duration"]
            )
        
        # Generate summary based on all collected information
        summary = _generate_summary(
            video_path,
            results,
            summary_type,
            include_timestamps,
            max_summary_length
        )
        
        results["summary"] = summary
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the video summary
                memory_entry = {
                    "type": "video_summary",
                    "video_path": video_path,
                    "summary": summary["text"],
                    "duration": video_metadata["duration"],
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add topics if available
                if "topics" in results and results["topics"]["main_topics"]:
                    memory_entry["topics"] = results["topics"]["main_topics"]
                
                # Add key scenes if available
                if "scenes" in results and len(results["scenes"]["scenes"]) > 0:
                    memory_entry["key_scenes"] = [
                        {
                            "time": scene["start_time"],
                            "description": scene["description"]
                        }
                        for scene in results["scenes"]["scenes"][:3]  # Include top 3 scenes
                    ]
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + [f"lang_{language}"]
                )
                
                logger.info(f"Stored video summary in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store video summary in memory: {str(e)}")
        
        return {
            "success": True,
            "video_path": video_path,
            "results": results
        }
    except Exception as e:
        error_msg = f"Error analyzing video: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "video_path": video_path
        }

def _get_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with video metadata
    """
    # In a real implementation, this would use libraries like ffmpeg or moviepy
    # For now, we'll extract basic file information
    
    file_stats = os.stat(video_path)
    file_name = os.path.basename(video_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Map common extensions to formats
    format_map = {
        ".mp4": "MP4",
        ".avi": "AVI",
        ".mov": "MOV",
        ".mkv": "MKV",
        ".webm": "WebM",
        ".flv": "FLV",
        ".wmv": "WMV"
    }
    
    video_format = format_map.get(file_ext, "Unknown")
    
    # Generate a deterministic but seemingly random duration based on the file path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    duration = random.randint(60, 1800)  # Between 1 minute and 30 minutes
    
    # Generate random but plausible video properties
    width = random.choice([640, 720, 1280, 1920, 3840])
    height = random.choice([360, 480, 720, 1080, 2160])
    fps = random.choice([24, 25, 30, 60])
    
    return {
        "file_name": file_name,
        "file_path": video_path,
        "file_size": file_stats.st_size,
        "format": video_format,
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "bitrate": random.randint(1000, 8000),
        "has_audio": random.random() > 0.1,  # 90% chance of having audio
        "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
    }

def _simulate_scene_detection(video_path: str, duration: int) -> Dict[str, Any]:
    """
    Simulate scene detection in a video.
    
    Args:
        video_path: Path to the video file
        duration: Duration of the video in seconds
        
    Returns:
        Dictionary with simulated scene detection results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Determine the type of video based on the file name
    file_name = os.path.basename(video_path).lower()
    
    # Determine number of scenes based on video duration
    # Assume roughly one scene every 20-40 seconds on average
    min_scenes = max(1, duration // 40)
    max_scenes = max(2, duration // 20)
    num_scenes = random.randint(min_scenes, max_scenes)
    
    # Generate scene timestamps
    scene_timestamps = sorted([random.randint(0, duration) for _ in range(num_scenes - 1)])
    scene_timestamps = [0] + scene_timestamps + [duration]
    
    # Generate scenes
    scenes = []
    
    for i in range(len(scene_timestamps) - 1):
        start_time = scene_timestamps[i]
        end_time = scene_timestamps[i + 1]
        
        # Generate scene description based on video type
        if "interview" in file_name or "talk" in file_name:
            description = random.choice([
                "Person speaking to the camera",
                "Interview with subject",
                "Speaker addressing audience",
                "Close-up of speaker",
                "Wide shot of interview setting"
            ])
        elif "nature" in file_name or "landscape" in file_name:
            description = random.choice([
                "Panoramic landscape view",
                "Close-up of wildlife",
                "Flowing water in stream",
                "Sunset over horizon",
                "Forest canopy",
                "Mountain vista"
            ])
        elif "tutorial" in file_name or "howto" in file_name:
            description = random.choice([
                "Demonstration of technique",
                "Close-up of materials",
                "Step-by-step instruction",
                "Results of process",
                "Presenter explaining concept"
            ])
        elif "sports" in file_name or "game" in file_name:
            description = random.choice([
                "Wide shot of playing field",
                "Player action sequence",
                "Crowd reaction",
                "Slow-motion replay",
                "Team celebration",
                "Coach giving instructions"
            ])
        else:
            # Generic scene descriptions
            description = random.choice([
                "Indoor setting with people",
                "Outdoor location",
                "Action sequence",
                "Conversation between individuals",
                "Close-up of subject",
                "Wide establishing shot",
                "Transition sequence"
            ])
        
        # Generate scene data
        scene = {
            "scene_id": i + 1,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "description": description,
            "confidence": round(random.uniform(0.75, 0.98), 2)
        }
        
        scenes.append(scene)
    
    return {
        "scenes": scenes,
        "count": len(scenes),
        "average_scene_duration": round(duration / len(scenes), 2)
    }

def _simulate_face_detection(video_path: str) -> Dict[str, Any]:
    """
    Simulate face detection in a video.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with simulated face detection results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Determine the type of video based on the file name
    file_name = os.path.basename(video_path).lower()
    
    # Determine if the video likely contains faces
    has_faces = (
        "interview" in file_name or
        "talk" in file_name or
        "people" in file_name or
        "vlog" in file_name or
        "tutorial" in file_name or
        random.random() < 0.7  # 70% chance for other videos
    )
    
    if not has_faces:
        return {
            "faces": [],
            "count": 0
        }
    
    # Determine number of unique faces
    if "interview" in file_name:
        num_faces = random.randint(1, 3)
    elif "meeting" in file_name or "group" in file_name:
        num_faces = random.randint(3, 8)
    else:
        num_faces = random.randint(1, 5)
    
    # Generate face data
    faces = []
    
    for i in range(num_faces):
        # Generate face appearance timestamps
        # Some faces might appear multiple times
        num_appearances = random.randint(1, 3)
        appearances = []
        
        for _ in range(num_appearances):
            start_time = random.randint(0, 500)
            duration = random.randint(5, 120)
            
            appearances.append({
                "start_time": start_time,
                "end_time": start_time + duration,
                "duration": duration,
                "confidence": round(random.uniform(0.8, 0.98), 2)
            })
        
        # Generate face data
        face = {
            "face_id": i + 1,
            "appearances": appearances,
            "total_screen_time": sum(a["duration"] for a in appearances),
            "recognition_confidence": round(random.uniform(0.75, 0.95), 2)
        }
        
        # Add identity if it's a known face (50% chance)
        if random.random() < 0.5:
            face["identity"] = f"Person {i+1}"
            face["identity_confidence"] = round(random.uniform(0.7, 0.9), 2)
        
        faces.append(face)
    
    # Sort faces by total screen time
    faces.sort(key=lambda x: x["total_screen_time"], reverse=True)
    
    return {
        "faces": faces,
        "count": len(faces),
        "main_face": faces[0] if faces else None
    }

def _simulate_object_detection(video_path: str) -> Dict[str, Any]:
    """
    Simulate object detection in a video.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with simulated object detection results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Determine the type of video based on the file name
    file_name = os.path.basename(video_path).lower()
    
    # Define potential objects based on video type
    if "nature" in file_name or "wildlife" in file_name:
        potential_objects = ["tree", "plant", "animal", "bird", "water", "sky", "mountain", "flower", "insect", "cloud"]
    elif "city" in file_name or "urban" in file_name:
        potential_objects = ["building", "car", "person", "road", "sign", "traffic light", "bicycle", "bus", "store", "phone"]
    elif "cooking" in file_name or "food" in file_name:
        potential_objects = ["bowl", "plate", "food", "utensil", "knife", "oven", "stove", "ingredient", "pan", "cutting board"]
    elif "tech" in file_name or "gadget" in file_name:
        potential_objects = ["computer", "phone", "keyboard", "screen", "mouse", "cable", "device", "charger", "speaker", "camera"]
    elif "sports" in file_name or "game" in file_name:
        potential_objects = ["ball", "player", "field", "court", "goal", "equipment", "uniform", "referee", "audience", "scoreboard"]
    else:
        # Generic objects
        potential_objects = ["person", "chair", "table", "car", "building", "phone", "book", "cup", "door", "window"]
    
    # Determine number of unique objects
    num_objects = random.randint(3, 8)
    
    # Select random objects
    selected_objects = random.sample(potential_objects, min(num_objects, len(potential_objects)))
    
    # Generate object data
    objects = []
    
    for i, obj_name in enumerate(selected_objects):
        # Generate object appearances
        num_appearances = random.randint(1, 5)
        total_instances = 0
        
        appearances = []
        for _ in range(num_appearances):
            start_time = random.randint(0, 500)
            duration = random.randint(5, 120)
            instances = random.randint(1, 5)
            total_instances += instances
            
            appearances.append({
                "start_time": start_time,
                "end_time": start_time + duration,
                "duration": duration,
                "instances": instances,
                "confidence": round(random.uniform(0.75, 0.98), 2)
            })
        
        # Generate object data
        object_data = {
            "object_id": i + 1,
            "name": obj_name,
            "appearances": appearances,
            "total_instances": total_instances,
            "average_confidence": round(random.uniform(0.8, 0.95), 2)
        }
        
        objects.append(object_data)
    
    # Sort objects by total instances
    objects.sort(key=lambda x: x["total_instances"], reverse=True)
    
    return {
        "objects": objects,
        "count": len(objects),
        "main_objects": [obj["name"] for obj in objects[:3]] if objects else []
    }

def _simulate_text_detection(video_path: str, language: str) -> Dict[str, Any]:
    """
    Simulate text detection in a video.
    
    Args:
        video_path: Path to the video file
        language: Language code for text detection
        
    Returns:
        Dictionary with simulated text detection results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Determine the type of video based on the file name
    file_name = os.path.basename(video_path).lower()
    
    # Determine if the video likely contains text
    has_text = (
        "presentation" in file_name or
        "tutorial" in file_name or
        "lecture" in file_name or
        "news" in file_name or
        "ad" in file_name or
        random.random() < 0.5  # 50% chance for other videos
    )
    
    if not has_text:
        return {
            "text_instances": [],
            "count": 0
        }
    
    # Determine number of text instances
    num_text_instances = random.randint(2, 8)
    
    # Generate text instances
    text_instances = []
    
    for i in range(num_text_instances):
        # Generate text content based on video type
        if "presentation" in file_name or "lecture" in file_name:
            text_content = random.choice([
                "Key Points", "Summary", "Introduction", "Conclusion",
                "Data Analysis", "Research Findings", "Methodology",
                "Future Work", "References", "Questions?"
            ])
        elif "tutorial" in file_name:
            text_content = random.choice([
                "Step 1", "Step 2", "Important Note", "Tips & Tricks",
                "Materials Needed", "Common Mistakes", "Final Result",
                "Advanced Technique", "Beginner Level", "Expert Level"
            ])
        elif "news" in file_name:
            text_content = random.choice([
                "Breaking News", "Live", "Exclusive", "Coming Up Next",
                "Weather Forecast", "Stock Market Update", "Sports Highlights",
                "Interview", "Special Report", "Local News"
            ])
        elif "ad" in file_name:
            text_content = random.choice([
                "Limited Time Offer", "New Product", "Sale Ends Soon",
                "Free Shipping", "Best Seller", "Award Winning",
                "Customer Favorite", "Exclusive Deal", "Learn More", "Order Now"
            ])
        else:
            # Generic text
            text_content = random.choice([
                "Title", "Caption", "Information", "Description",
                "Warning", "Note", "Contact", "Website", "Date", "Location"
            ])
        
        # Generate text appearance
        start_time = random.randint(0, 500)
        duration = random.randint(3, 60)
        
        # Generate text instance data
        text_instance = {
            "text_id": i + 1,
            "content": text_content,
            "start_time": start_time,
            "end_time": start_time + duration,
            "duration": duration,
            "confidence": round(random.uniform(0.8, 0.98), 2),
            "language": language
        }
        
        text_instances.append(text_instance)
    
    # Sort text instances by start time
    text_instances.sort(key=lambda x: x["start_time"])
    
    return {
        "text_instances": text_instances,
        "count": len(text_instances),
        "languages_detected": [language]
    }

def _simulate_audio_transcription(video_path: str, language: str) -> Dict[str, Any]:
    """
    Simulate audio transcription from a video.
    
    Args:
        video_path: Path to the video file
        language: Language code for transcription
        
    Returns:
        Dictionary with simulated transcription results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Determine the type of video based on the file name
    file_name = os.path.basename(video_path).lower()
    
    # Determine if the video likely contains speech
    has_speech = (
        "interview" in file_name or
        "talk" in file_name or
        "lecture" in file_name or
        "tutorial" in file_name or
        "vlog" in file_name or
        "presentation" in file_name or
        random.random() < 0.7  # 70% chance for other videos
    )
    
    if not has_speech:
        return {
            "full_text": "",
            "segments": [],
            "has_speech": False
        }
    
    # Generate transcription content based on video type
    if "interview" in file_name or "talk" in file_name:
        transcript_template = _get_interview_template()
    elif "lecture" in file_name or "educational" in file_name:
        transcript_template = _get_lecture_template()
    elif "tutorial" in file_name or "howto" in file_name:
        transcript_template = _get_tutorial_template()
    elif "vlog" in file_name or "personal" in file_name:
        transcript_template = _get_vlog_template()
    elif "presentation" in file_name or "business" in file_name:
        transcript_template = _get_presentation_template()
    else:
        # Generic transcript
        transcript_template = random.choice([
            _get_interview_template(),
            _get_lecture_template(),
            _get_tutorial_template(),
            _get_vlog_template(),
            _get_presentation_template()
        ])
    
    # Generate transcript segments
    segments = []
    current_time = 0
    
    for i, text in enumerate(transcript_template):
        # Calculate segment duration based on text length
        # Assume average speaking rate of 150 words per minute
        words = len(text.split())
        segment_duration = (words / 150) * 60  # in seconds
        
        # Create segment
        segment = {
            "text": text,
            "start_time": round(current_time, 2),
            "end_time": round(current_time + segment_duration, 2),
            "duration": round(segment_duration, 2),
            "confidence": round(random.uniform(0.85, 0.98), 2)
        }
        
        segments.append(segment)
        
        # Update current time
        current_time += segment_duration
    
    # Combine segments into full text
    full_text = " ".join([segment["text"] for segment in segments])
    
    return {
        "full_text": full_text,
        "segments": segments,
        "language": language,
        "has_speech": True,
        "word_count": len(full_text.split())
    }

def _simulate_topic_detection(video_path: str, transcript_text: str = None) -> Dict[str, Any]:
    """
    Simulate topic detection in a video.
    
    Args:
        video_path: Path to the video file
        transcript_text: Transcribed text (if available)
        
    Returns:
        Dictionary with simulated topic detection results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Determine the type of video based on the file name
    file_name = os.path.basename(video_path).lower()
    
    # Define potential topics based on video type
    if "tech" in file_name or "technology" in file_name:
        potential_topics = ["Artificial Intelligence", "Machine Learning", "Software Development", 
                           "Hardware Review", "Cybersecurity", "Data Science", "Cloud Computing", 
                           "Mobile Technology", "Programming", "Tech Industry"]
    elif "science" in file_name:
        potential_topics = ["Physics", "Chemistry", "Biology", "Astronomy", "Environmental Science", 
                           "Research Methods", "Scientific Discovery", "Laboratory Techniques", 
                           "Theoretical Science", "Applied Science"]
    elif "business" in file_name or "finance" in file_name:
        potential_topics = ["Market Analysis", "Investment Strategies", "Entrepreneurship", 
                           "Business Management", "Financial Planning", "Economic Trends", 
                           "Corporate Strategy", "Marketing", "Leadership", "Industry Insights"]
    elif "health" in file_name or "medical" in file_name:
        potential_topics = ["Nutrition", "Exercise", "Mental Health", "Medical Research", 
                           "Healthcare Systems", "Disease Prevention", "Wellness", 
                           "Medical Treatments", "Public Health", "Personal Care"]
    elif "education" in file_name or "learning" in file_name:
        potential_topics = ["Teaching Methods", "Learning Strategies", "Educational Technology", 
                           "Curriculum Development", "Student Assessment", "Educational Psychology", 
                           "Classroom Management", "Online Learning", "Educational Policy", "Academic Research"]
    elif "entertainment" in file_name or "media" in file_name:
        potential_topics = ["Film Analysis", "Music Review", "Celebrity News", "Media Industry", 
                           "Entertainment Trends", "Streaming Platforms", "Gaming", 
                           "Pop Culture", "Arts", "Media Production"]
    elif "sports" in file_name or "fitness" in file_name:
        potential_topics = ["Team Sports", "Individual Sports", "Athletic Performance", 
                           "Sports Analysis", "Fitness Training", "Sports Medicine", 
                           "Competition Strategy", "Sports Industry", "Athlete Profiles", "Coaching Techniques"]
    elif "food" in file_name or "cooking" in file_name:
        potential_topics = ["Cooking Techniques", "Recipe Demonstration", "Ingredient Analysis", 
                           "Culinary Traditions", "Food Culture", "Nutrition", 
                           "Restaurant Reviews", "Food Industry", "Dietary Considerations", "Beverage Pairing"]
    elif "travel" in file_name or "tourism" in file_name:
        potential_topics = ["Destination Guides", "Travel Tips", "Cultural Experiences", 
                           "Adventure Travel", "Accommodation Reviews", "Transportation", 
                           "Local Cuisine", "Tourist Attractions", "Travel Photography", "Travel Industry"]
    else:
        # Generic topics
        potential_topics = ["Information", "Analysis", "Tutorial", "Review", "Discussion", 
                           "Demonstration", "Explanation", "Presentation", "Interview", "Commentary"]
    
    # Determine number of topics
    num_topics = random.randint(2, 4)
    
    # Select random topics
    selected_topics = random.sample(potential_topics, min(num_topics, len(potential_topics)))
    
    # Generate topic data
    topics = []
    
    for i, topic in enumerate(selected_topics):
        # Generate topic data
        topic_data = {
            "topic_id": i + 1,
            "name": topic,
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "relevance": round(random.uniform(0.7, 1.0), 2)
        }
        
        # Add keywords
        keywords = []
        for _ in range(random.randint(3, 6)):
            if transcript_text:
                # Extract random words from transcript
                words = [word for word in transcript_text.split() if len(word) > 4]
                if words:
                    keyword = random.choice(words)
                    keywords.append(keyword)
            else:
                # Generate generic keywords
                keyword = f"keyword_{random.randint(1, 100)}"
                keywords.append(keyword)
        
        topic_data["keywords"] = keywords
        
        topics.append(topic_data)
    
    # Sort topics by confidence
    topics.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "topics": topics,
        "count": len(topics),
        "main_topics": [topic["name"] for topic in topics]
    }

def _simulate_frame_extraction(
    video_path: str,
    output_dir: str,
    interval: int,
    duration: int
) -> Dict[str, Any]:
    """
    Simulate frame extraction from a video.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        interval: Interval in seconds between extracted frames
        duration: Duration of the video in seconds
        
    Returns:
        Dictionary with simulated frame extraction results
    """
    # Generate a deterministic but seemingly random seed based on the video path
    seed = sum(ord(c) for c in video_path)
    random.seed(seed)
    
    # Calculate number of frames to extract
    num_frames = duration // interval
    
    # Generate frame data
    frames = []
    
    for i in range(num_frames):
        # Calculate frame timestamp
        timestamp = i * interval
        
        # Generate frame filename
        frame_filename = f"frame_{timestamp:04d}.jpg"
        frame_path = os.path.join(output_dir, frame_filename)
        
        # In a real implementation, this would actually extract and save the frame
        # For simulation, we'll just create an empty file
        with open(frame_path, 'w') as f:
            f.write(f"Simulated frame at {timestamp} seconds")
        
        # Generate frame data
        frame = {
            "frame_id": i + 1,
            "timestamp": timestamp,
            "path": frame_path,
            "filename": frame_filename
        }
        
        frames.append(frame)
    
    return {
        "frames": frames,
        "count": len(frames),
        "interval": interval,
        "output_directory": output_dir
    }

def _generate_summary(
    video_path: str,
    results: Dict[str, Any],
    summary_type: str,
    include_timestamps: bool,
    max_length: int
) -> Dict[str, Any]:
    """
    Generate a summary of the video based on analysis results.
    
    Args:
        video_path: Path to the video file
        results: Analysis results
        summary_type: Type of summary to generate
        include_timestamps: Whether to include timestamps
        max_length: Maximum length of the summary in words
        
    Returns:
        Dictionary with generated summary
    """
    # Extract key information from results
    metadata = results.get("metadata", {})
    duration = metadata.get("duration", 0)
    
    # Format duration as MM:SS or HH:MM:SS
    if duration < 3600:
        duration_str = f"{duration // 60}:{duration % 60:02d}"
    else:
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
    
    # Get video type from filename
    file_name = os.path.basename(video_path).lower()
    
    # Determine video type
    if "interview" in file_name or "talk" in file_name:
        video_type = "interview"
    elif "lecture" in file_name or "educational" in file_name:
        video_type = "lecture"
    elif "tutorial" in file_name or "howto" in file_name:
        video_type = "tutorial"
    elif "vlog" in file_name or "personal" in file_name:
        video_type = "vlog"
    elif "presentation" in file_name or "business" in file_name:
        video_type = "presentation"
    elif "nature" in file_name or "wildlife" in file_name:
        video_type = "nature documentary"
    elif "sports" in file_name or "game" in file_name:
        video_type = "sports video"
    elif "news" in file_name:
        video_type = "news segment"
    elif "ad" in file_name or "commercial" in file_name:
        video_type = "advertisement"
    else:
        video_type = "video"
    
    # Extract topics
    topics = []
    if "topics" in results and results["topics"]["main_topics"]:
        topics = results["topics"]["main_topics"]
    
    # Extract key scenes
    key_scenes = []
    if "scenes" in results and results["scenes"]["scenes"]:
        # Sort scenes by duration (descending)
        sorted_scenes = sorted(results["scenes"]["scenes"], key=lambda x: x["duration"], reverse=True)
        # Take top 3 scenes
        key_scenes = sorted_scenes[:3]
    
    # Extract main objects
    main_objects = []
    if "objects" in results and results["objects"]["main_objects"]:
        main_objects = results["objects"]["main_objects"]
    
    # Extract main faces
    main_faces = []
    if "faces" in results and results["faces"]["faces"]:
        for face in results["faces"]["faces"][:2]:  # Top 2 faces
            if "identity" in face:
                main_faces.append(face["identity"])
            else:
                main_faces.append("unidentified person")
    
    # Extract transcript
    transcript = ""
    if "transcription" in results and results["transcription"]["has_speech"]:
        transcript = results["transcription"]["full_text"]
    
    # Generate summary based on summary type
    if summary_type == "brief":
        summary_text = _generate_brief_summary(
            video_type,
            duration_str,
            topics,
            main_faces,
            main_objects,
            transcript
        )
    elif summary_type == "comprehensive":
        summary_text = _generate_comprehensive_summary(
            video_type,
            duration_str,
            topics,
            key_scenes,
            main_faces,
            main_objects,
            transcript,
            include_timestamps
        )
    else:  # detailed
        summary_text = _generate_detailed_summary(
            video_type,
            duration_str,
            topics,
            key_scenes,
            main_faces,
            main_objects,
            transcript,
            include_timestamps,
            results
        )
    
    # Truncate summary if needed
    words = summary_text.split()
    if len(words) > max_length:
        summary_text = " ".join(words[:max_length]) + "..."
    
    return {
        "text": summary_text,
        "type": summary_type,
        "word_count": len(summary_text.split()),
        "topics": topics
    }

def _generate_brief_summary(
    video_type: str,
    duration: str,
    topics: List[str],
    main_faces: List[str],
    main_objects: List[str],
    transcript: str
) -> str:
    """
    Generate a brief summary of the video.
    
    Args:
        video_type: Type of video
        duration: Formatted duration string
        topics: Main topics
        main_faces: Main faces/people
        main_objects: Main objects
        transcript: Transcript text
        
    Returns:
        Brief summary text
    """
    # Start with video type and duration
    summary = f"This {duration} {video_type} "
    
    # Add topics if available
    if topics:
        if len(topics) == 1:
            summary += f"focuses on {topics[0]}. "
        else:
            topics_str = ", ".join(topics[:-1]) + f" and {topics[-1]}"
            summary += f"covers topics including {topics_str}. "
    else:
        summary += "contains the following content. "
    
    # Add main people if available
    if main_faces:
        if len(main_faces) == 1:
            summary += f"It features {main_faces[0]}. "
        else:
            faces_str = " and ".join(main_faces)
            summary += f"It features {faces_str}. "
    
    # Add key objects if available and no faces mentioned
    if main_objects and not main_faces:
        if len(main_objects) == 1:
            summary += f"It prominently shows {main_objects[0]}. "
        else:
            objects_str = ", ".join(main_objects[:-1]) + f" and {main_objects[-1]}"
            summary += f"It prominently shows {objects_str}. "
    
    # Add brief content summary based on transcript if available
    if transcript:
        # Extract first 20 words from transcript
        first_words = " ".join(transcript.split()[:20])
        summary += f"The content begins with: \"{first_words}...\""
    
    return summary

def _generate_comprehensive_summary(
    video_type: str,
    duration: str,
    topics: List[str],
    key_scenes: List[Dict[str, Any]],
    main_faces: List[str],
    main_objects: List[str],
    transcript: str,
    include_timestamps: bool
) -> str:
    """
    Generate a comprehensive summary of the video.
    
    Args:
        video_type: Type of video
        duration: Formatted duration string
        topics: Main topics
        key_scenes: Key scenes
        main_faces: Main faces/people
        main_objects: Main objects
        transcript: Transcript text
        include_timestamps: Whether to include timestamps
        
    Returns:
        Comprehensive summary text
    """
    # Start with video type, duration, and topics
    summary = f"This {duration} {video_type} "
    
    if topics:
        if len(topics) == 1:
            summary += f"focuses on {topics[0]}. "
        else:
            topics_str = ", ".join(topics[:-1]) + f" and {topics[-1]}"
            summary += f"covers topics including {topics_str}. "
    else:
        summary += "contains the following content. "
    
    # Add main people and objects
    if main_faces or main_objects:
        summary += "The video features "
        
        if main_faces:
            if len(main_faces) == 1:
                summary += f"{main_faces[0]}"
            else:
                faces_str = ", ".join(main_faces[:-1]) + f" and {main_faces[-1]}"
                summary += f"{faces_str}"
            
            if main_objects:
                summary += ", along with "
        
        if main_objects:
            if len(main_objects) == 1:
                summary += f"{main_objects[0]}"
            else:
                objects_str = ", ".join(main_objects[:-1]) + f" and {main_objects[-1]}"
                summary += f"{objects_str}"
        
        summary += ". "
    
    # Add key scenes if available
    if key_scenes:
        summary += "Key segments include: "
        
        for i, scene in enumerate(key_scenes):
            if include_timestamps:
                start_time = scene["start_time"]
                minutes = start_time // 60
                seconds = start_time % 60
                timestamp = f"[{minutes}:{seconds:02d}]"
                summary += f"{timestamp} {scene['description']}"
            else:
                summary += f"{scene['description']}"
            
            if i < len(key_scenes) - 1:
                summary += ", "
            else:
                summary += ". "
    
    # Add content summary based on transcript if available
    if transcript:
        # Extract key sentences from transcript
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        
        if len(sentences) > 3:
            # Take first, middle, and last meaningful sentences
            key_sentences = [
                sentences[0],
                sentences[len(sentences) // 2],
                sentences[-1]
            ]
            
            summary += "The content covers: "
            for i, sentence in enumerate(key_sentences):
                summary += f"\"{sentence}\""
                
                if i < len(key_sentences) - 1:
                    summary += "; "
                else:
                    summary += "."
        elif sentences:
            # Use all available sentences
            summary += "The content includes: "
            for i, sentence in enumerate(sentences):
                summary += f"\"{sentence}\""
                
                if i < len(sentences) - 1:
                    summary += "; "
                else:
                    summary += "."
    
    return summary

def _generate_detailed_summary(
    video_type: str,
    duration: str,
    topics: List[str],
    key_scenes: List[Dict[str, Any]],
    main_faces: List[str],
    main_objects: List[str],
    transcript: str,
    include_timestamps: bool,
    results: Dict[str, Any]
) -> str:
    """
    Generate a detailed summary of the video.
    
    Args:
        video_type: Type of video
        duration: Formatted duration string
        topics: Main topics
        key_scenes: Key scenes
        main_faces: Main faces/people
        main_objects: Main objects
        transcript: Transcript text
        include_timestamps: Whether to include timestamps
        results: Full analysis results
        
    Returns:
        Detailed summary text
    """
    # Start with video overview
    summary = f"## Video Summary: {os.path.basename(results['video_path'])}\n\n"
    
    # Add metadata
    metadata = results.get("metadata", {})
    summary += f"**Duration:** {duration}\n"
    summary += f"**Format:** {metadata.get('format', 'Unknown')}\n"
    summary += f"**Resolution:** {metadata.get('width', 0)}x{metadata.get('height', 0)}\n\n"
    
    # Add topics
    if topics:
        summary += "**Main Topics:**\n"
        for topic in topics:
            summary += f"- {topic}\n"
        summary += "\n"
    
    # Add content overview
    summary += f"**Content Overview:**\n"
    summary += f"This {video_type} "
    
    if main_faces:
        if len(main_faces) == 1:
            summary += f"features {main_faces[0]}"
        else:
            faces_str = ", ".join(main_faces[:-1]) + f" and {main_faces[-1]}"
            summary += f"features {faces_str}"
        
        if main_objects:
            summary += ", along with "
    
    if main_objects:
        if len(main_objects) == 1:
            summary += f"{main_objects[0]}"
        else:
            objects_str = ", ".join(main_objects[:-1]) + f" and {main_objects[-1]}"
            summary += f"{objects_str}"
    
    summary += ".\n\n"
    
    # Add scene breakdown if available
    if "scenes" in results and results["scenes"]["scenes"]:
        summary += "**Scene Breakdown:**\n"
        
        for scene in results["scenes"]["scenes"]:
            if include_timestamps:
                start_time = scene["start_time"]
                end_time = scene["end_time"]
                start_minutes = start_time // 60
                start_seconds = start_time % 60
                end_minutes = end_time // 60
                end_seconds = end_time % 60
                
                timestamp = f"[{start_minutes}:{start_seconds:02d} - {end_minutes}:{end_seconds:02d}]"
                summary += f"- {timestamp} {scene['description']}\n"
            else:
                summary += f"- {scene['description']}\n"
        
        summary += "\n"
    
    # Add detailed object analysis if available
    if "objects" in results and results["objects"]["objects"]:
        summary += "**Key Objects/Elements:**\n"
        
        # Sort objects by total instances
        sorted_objects = sorted(results["objects"]["objects"], key=lambda x: x["total_instances"], reverse=True)
        
        for obj in sorted_objects[:5]:  # Top 5 objects
            summary += f"- {obj['name']} (appears {obj['total_instances']} times)\n"
        
        summary += "\n"
    
    # Add text detected if available
    if "text" in results and results["text"]["text_instances"]:
        summary += "**On-screen Text:**\n"
        
        for text in results["text"]["text_instances"]:
            if include_timestamps:
                start_time = text["start_time"]
                minutes = start_time // 60
                seconds = start_time % 60
                timestamp = f"[{minutes}:{seconds:02d}]"
                summary += f"- {timestamp} \"{text['content']}\"\n"
            else:
                summary += f"- \"{text['content']}\"\n"
        
        summary += "\n"
    
    # Add transcript summary if available
    if transcript:
        summary += "**Content Transcript Highlights:**\n"
        
        # Extract key sentences from transcript
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        
        if len(sentences) > 5:
            # Take first, some middle, and last sentences
            indices = [0, len(sentences) // 4, len(sentences) // 2, (3 * len(sentences)) // 4, -1]
            key_sentences = [sentences[i] for i in indices if 0 <= i < len(sentences)]
            
            for sentence in key_sentences:
                summary += f"- \"{sentence}.\"\n"
        elif sentences:
            # Use all available sentences
            for sentence in sentences:
                summary += f"- \"{sentence}.\"\n"
        
        summary += "\n"
    
    # Add conclusion
    summary += "**Summary:**\n"
    if topics:
        topics_str = ", ".join(topics[:-1]) + f" and {topics[-1]}" if len(topics) > 1 else topics[0]
        summary += f"This {duration} {video_type} provides information on {topics_str}. "
    else:
        summary += f"This {duration} {video_type} contains various content as detailed above. "
    
    # Add recommendation or insight
    if "topics" in results and results["topics"]["topics"]:
        top_topic = results["topics"]["topics"][0]["name"]
        summary += f"It is particularly relevant for those interested in {top_topic}."
    
    return summary

def _get_interview_template() -> List[str]:
    """
    Get a template for an interview video transcript.
    
    Returns:
        List of text segments for an interview
    """
    return [
        "Welcome to our show. Today we're joined by a special guest to discuss recent developments in the industry.",
        "Thank you for having me. It's a pleasure to be here and share my thoughts on these important topics.",
        "Let's start with your background. Could you tell our viewers a bit about your experience in this field?",
        "Of course. I've been working in this industry for over 15 years, starting as a researcher and eventually moving into a leadership position. Throughout my career, I've focused on innovation and finding practical applications for emerging technologies.",
        "That's impressive. What do you see as the biggest changes in the industry over the past few years?",
        "The pace of change has accelerated dramatically. We're seeing technologies that used to take a decade to mature now reaching market in just a few years. The barriers to entry have also decreased, allowing smaller players to make significant contributions.",
        "How do you think these changes will affect businesses in the coming years?",
        "Companies will need to become more agile and responsive. The traditional five-year planning cycle is becoming obsolete. Organizations that can quickly adapt to new technologies and changing market conditions will have a significant advantage.",
        "Are there specific technologies that you're particularly excited about?",
        "Several, actually. I'm especially interested in the convergence of artificial intelligence and edge computing, which is enabling new applications that weren't possible before. I'm also watching developments in sustainable energy solutions, which I believe will transform multiple industries.",
        "What advice would you give to professionals who are just starting their careers in this field?",
        "Focus on developing a broad skill set rather than specializing too narrowly too soon. The most valuable team members are those who can bridge different domains and translate between technical and business considerations. Also, cultivate curiosity and a willingness to continuously learn.",
        "Thank you for sharing these insights. Before we wrap up, is there anything else you'd like to add?",
        "I'd just emphasize that while technology is changing rapidly, the fundamental principles of good business and ethical practice remain constant. Focus on creating real value for customers and society, and the rest will follow.",
        "Thank you again for joining us today. It's been a fascinating conversation.",
        "Thank you for having me. It's been my pleasure."
    ]

def _get_lecture_template() -> List[str]:
    """
    Get a template for a lecture video transcript.
    
    Returns:
        List of text segments for a lecture
    """
    return [
        "Welcome to today's lecture. We'll be covering key concepts that form the foundation of our subject matter.",
        "Before we dive into the details, let's review what we covered in our previous session. We discussed the historical context and basic principles that underpin our current understanding of the field.",
        "Today, we'll build on that foundation by exploring the theoretical framework in more depth and examining some practical applications.",
        "Let's start with the core theoretical model. As you can see on this slide, there are three primary components that interact in a dynamic system.",
        "The first component represents the structural elements, which provide stability and define the boundaries of the system.",
        "The second component encompasses the functional processes that operate within and across these structures, enabling the system to perform its intended purpose.",
        "The third component involves the regulatory mechanisms that maintain balance and allow the system to adapt to changing conditions.",
        "Now, let's consider how these components interact in real-world scenarios. I'll walk through several case studies that illustrate these principles in action.",
        "Our first case study demonstrates how structural weaknesses can compromise the entire system, even when functional processes are operating correctly.",
        "The second case study shows the opposite situation: strong structures but inefficient processes leading to suboptimal outcomes.",
        "The third case study is particularly interesting because it reveals how effective regulatory mechanisms can compensate for moderate deficiencies in both structure and function.",
        "Let's now turn to some practical applications of these concepts. In your professional work, you'll encounter systems at various stages of development and with different patterns of strengths and weaknesses.",
        "The analytical framework we've discussed provides a systematic approach to diagnosing problems and identifying potential interventions.",
        "Remember that real-world systems are always more complex than theoretical models, so you'll need to adapt these concepts to specific contexts.",
        "For next week's session, please read chapters 7 and 8 in the textbook, which explore advanced applications of these principles. Also, begin thinking about potential topics for your final project.",
        "Are there any questions before we conclude today's lecture?"
    ]

def _get_tutorial_template() -> List[str]:
    """
    Get a template for a tutorial video transcript.
    
    Returns:
        List of text segments for a tutorial
    """
    return [
        "Hello everyone, and welcome to this tutorial. Today I'll be showing you how to complete this project from start to finish.",
        "Before we begin, let's go over the materials you'll need. You should have all these items ready before starting the process.",
        "First, you'll need the main components that form the core of the project. Second, you'll need the tools listed on the screen. And finally, make sure you have a clean, well-lit workspace.",
        "Let's start with step one. This is the foundation of the entire project, so take your time and make sure you get it right.",
        "Notice how I'm positioning everything carefully. The alignment at this stage is critical for the later steps to work properly.",
        "Now for step two. Here we'll be connecting the main components. Make sure the connections are secure but don't apply too much pressure.",
        "A common mistake at this point is rushing through the connections. Take your time and double-check your work before moving on.",
        "Moving on to step three. This is where we start to see the project taking shape. We'll add the secondary elements that enhance functionality.",
        "As you can see, I'm working systematically from left to right. This approach helps ensure that you don't miss any components.",
        "Now for step four, which involves calibrating the system. This step is often overlooked, but it's essential for optimal performance.",
        "Pay close attention to the indicators I'm pointing out. They'll tell you whether the calibration is successful.",
        "Step five is where we test the basic functionality. Don't worry if you need to make adjustments – that's a normal part of the process.",
        "For step six, we'll fine-tune the settings based on the test results. This customization is what makes each project unique.",
        "Finally, step seven is the finishing touch. These final adjustments might seem minor, but they make a significant difference in the quality of the end result.",
        "Let's review what we've accomplished. We've successfully completed all seven steps of the process, resulting in a fully functional project.",
        "If you encounter any issues, the most common problems and their solutions are listed in the downloadable guide linked in the description.",
        "Thank you for following along with this tutorial. If you found it helpful, please consider subscribing to the channel for more content like this."
    ]

def _get_vlog_template() -> List[str]:
    """
    Get a template for a vlog video transcript.
    
    Returns:
        List of text segments for a vlog
    """
    return [
        "Hey everyone! Welcome back to my channel. I'm so excited to share today's video with you all.",
        "Before we get started, I want to thank you all for the amazing support on my last video. The comments were so thoughtful and encouraging.",
        "So today, I wanted to take you along with me as I explore something new that I've been wanting to try for a while now.",
        "I've been planning this for weeks, and I'm really looking forward to sharing this experience with you all.",
        "First things first, let me show you what I've prepared for today's adventure. I've got everything packed and ready to go.",
        "The weather is absolutely perfect today – couldn't have asked for better conditions for what we're about to do.",
        "Alright, so we've arrived at our destination. Look at this place – isn't it amazing? I'm already feeling inspired.",
        "Let me give you a quick tour around so you can get a feel for the environment. The atmosphere here is exactly what I was hoping for.",
        "Now, let's get into the main activity for today. I'm a complete beginner at this, so we'll be learning together.",
        "Okay, I'm getting some instructions now on how to proceed. It seems pretty straightforward, but we'll see how it goes.",
        "Wow, this is actually more challenging than it looked! But I'm enjoying the process of figuring it out as I go.",
        "I just had a minor setback, but that's all part of the learning experience, right? Let's try a different approach.",
        "Yes! I think I'm getting the hang of it now. It's so satisfying when you start to see progress after the initial struggle.",
        "I'm actually really proud of what I've accomplished today. It wasn't perfect, but it was definitely worth trying.",
        "Let me share some reflections on the experience while it's still fresh. There were definitely some unexpected challenges.",
        "Would I do this again? Absolutely! In fact, I'm already thinking about how I could build on this experience next time.",
        "Before I wrap up this video, I want to thank you all again for coming along on this journey with me. Your support means everything.",
        "If you enjoyed this video, please give it a thumbs up, and don't forget to subscribe if you haven't already. I've got lots more adventures planned.",
        "See you all in the next video!"
    ]

def _get_presentation_template() -> List[str]:
    """
    Get a template for a presentation video transcript.
    
    Returns:
        List of text segments for a presentation
    """
    return [
        "Good morning everyone. Thank you for joining this presentation on our quarterly results and strategic outlook.",
        "Today's agenda covers three main areas: First, we'll review our financial performance for the past quarter. Second, we'll discuss key market trends affecting our industry. And finally, we'll outline our strategic priorities for the coming year.",
        "Let's begin with our financial highlights. I'm pleased to report that we've exceeded our targets for the quarter, with revenue growth of 12% year-over-year.",
        "This slide shows the breakdown by business unit. As you can see, our core products continue to perform strongly, while our new initiatives are beginning to gain traction in the market.",
        "Operating margin has improved by 2 percentage points compared to the same period last year, reflecting our ongoing efficiency initiatives and economies of scale.",
        "Cash flow remains robust, allowing us to continue investing in growth opportunities while returning value to shareholders through our dividend program.",
        "Now, let's turn to market trends. We're seeing significant shifts in customer preferences, with increasing demand for sustainable and digitally-enabled solutions.",
        "Competitive intensity remains high, with new entrants leveraging technology to disrupt traditional business models. However, our established market position and brand equity continue to provide competitive advantages.",
        "Regulatory changes in key markets present both challenges and opportunities. We're actively engaging with policymakers to shape outcomes that benefit our industry and customers.",
        "Looking at regional performance, we're seeing strong growth in emerging markets, particularly in the Asia-Pacific region, which grew by 18% year-over-year.",
        "North America and Europe showed more modest growth but maintained solid profitability. We're implementing targeted strategies to accelerate growth in these mature markets.",
        "Now for our strategic priorities. We've identified three key areas of focus for the coming year.",
        "First, we'll accelerate our digital transformation, enhancing our customer experience and operational efficiency through advanced analytics and automation.",
        "Second, we'll expand our product portfolio to address emerging customer needs, with a particular focus on sustainability and connectivity.",
        "Third, we'll continue to optimize our global footprint, ensuring we have the right capabilities in the right locations to serve our customers effectively and efficiently.",
        "In conclusion, we're well-positioned for continued success despite market challenges. Our strong financial foundation, clear strategic direction, and talented team give me confidence in our ability to deliver sustainable growth.",
        "Thank you for your attention. I'd be happy to take any questions you might have."
    ]
