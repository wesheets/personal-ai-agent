"""
Image Caption Tool for the Personal AI Agent System.

This module provides functionality to generate descriptive captions
for images using computer vision techniques.
"""

import os
import json
import time
import random
import base64
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("image_caption")

def run(
    image_path: str,
    detail_level: str = "standard",
    include_objects: bool = True,
    include_colors: bool = True,
    include_style: bool = False,
    include_emotions: bool = False,
    max_caption_length: int = 100,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["image", "caption", "vision"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Generate a descriptive caption for an image.
    
    Args:
        image_path: Path to the image file
        detail_level: Level of detail for the caption (brief, standard, detailed)
        include_objects: Whether to identify and include objects in the caption
        include_colors: Whether to identify and include colors in the caption
        include_style: Whether to identify and include artistic style in the caption
        include_emotions: Whether to identify and include emotional content in the caption
        max_caption_length: Maximum length of the generated caption
        store_memory: Whether to store the caption in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the generated caption and related information
    """
    logger.info(f"Generating caption for image: {image_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Validate inputs
        if detail_level not in ["brief", "standard", "detailed"]:
            raise ValueError(f"Invalid detail level: {detail_level}. Supported levels: brief, standard, detailed")
            
        if max_caption_length < 10 or max_caption_length > 500:
            raise ValueError(f"Invalid max caption length: {max_caption_length}. Must be between 10 and 500.")
        
        # In a real implementation, this would use computer vision models
        # For now, we'll simulate the image captioning
        
        # Get image metadata
        image_metadata = _get_image_metadata(image_path)
        
        # Simulate image analysis
        analysis_result = _simulate_image_analysis(
            image_path,
            detail_level,
            include_objects,
            include_colors,
            include_style,
            include_emotions
        )
        
        # Generate caption based on analysis
        caption = _generate_caption_from_analysis(
            analysis_result,
            detail_level,
            max_caption_length
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the caption and image reference
                memory_entry = {
                    "type": "image_caption",
                    "image_path": image_path,
                    "caption": caption,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add analysis details if available
                if "objects" in analysis_result and analysis_result["objects"]:
                    memory_entry["objects"] = analysis_result["objects"]
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ["image_caption"]
                )
                
                logger.info(f"Stored image caption in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store image caption in memory: {str(e)}")
        
        return {
            "success": True,
            "image_path": image_path,
            "caption": caption,
            "metadata": image_metadata,
            "analysis": analysis_result
        }
    except Exception as e:
        error_msg = f"Error generating image caption: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "image_path": image_path
        }

def _get_image_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image metadata
    """
    # In a real implementation, this would use libraries like PIL or exifread
    # For now, we'll extract basic file information
    
    file_stats = os.stat(image_path)
    file_name = os.path.basename(image_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Map common extensions to formats
    format_map = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".gif": "GIF",
        ".bmp": "BMP",
        ".webp": "WebP",
        ".tiff": "TIFF",
        ".tif": "TIFF"
    }
    
    image_format = format_map.get(file_ext, "Unknown")
    
    return {
        "file_name": file_name,
        "file_path": image_path,
        "file_size": file_stats.st_size,
        "format": image_format,
        "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
    }

def _simulate_image_analysis(
    image_path: str,
    detail_level: str,
    include_objects: bool,
    include_colors: bool,
    include_style: bool,
    include_emotions: bool
) -> Dict[str, Any]:
    """
    Simulate image analysis using computer vision techniques.
    
    Args:
        image_path: Path to the image file
        detail_level: Level of detail for the analysis
        include_objects: Whether to identify objects
        include_colors: Whether to identify colors
        include_style: Whether to identify artistic style
        include_emotions: Whether to identify emotional content
        
    Returns:
        Dictionary with simulated image analysis results
    """
    # Generate a deterministic but seemingly random seed based on the image path
    seed = sum(ord(c) for c in image_path)
    random.seed(seed)
    
    # Initialize analysis result
    analysis_result = {}
    
    # Simulate scene classification
    scenes = [
        "outdoor", "indoor", "urban", "rural", "nature", "beach", "mountain",
        "forest", "city", "office", "home", "restaurant", "park", "street"
    ]
    
    scene_confidences = {scene: random.uniform(0.1, 0.9) for scene in random.sample(scenes, 3)}
    top_scene = max(scene_confidences, key=scene_confidences.get)
    
    analysis_result["scene"] = {
        "top": top_scene,
        "confidence": scene_confidences[top_scene],
        "alternatives": {k: v for k, v in scene_confidences.items() if k != top_scene}
    }
    
    # Simulate object detection if requested
    if include_objects:
        # Common objects by scene type
        objects_by_scene = {
            "outdoor": ["tree", "sky", "grass", "cloud", "person", "car", "building", "flower", "bird", "dog"],
            "indoor": ["chair", "table", "sofa", "lamp", "book", "television", "plant", "person", "cup", "painting"],
            "urban": ["building", "car", "person", "traffic light", "sign", "bus", "bicycle", "road", "sidewalk", "store"],
            "rural": ["field", "tree", "farm", "animal", "fence", "barn", "tractor", "house", "sky", "grass"],
            "nature": ["tree", "river", "mountain", "flower", "rock", "sky", "cloud", "animal", "grass", "lake"],
            "beach": ["sand", "ocean", "wave", "person", "umbrella", "towel", "boat", "sky", "cloud", "seashell"],
            "mountain": ["mountain", "rock", "tree", "sky", "cloud", "snow", "hiker", "path", "forest", "lake"],
            "forest": ["tree", "leaf", "plant", "moss", "animal", "bird", "path", "sunlight", "shadow", "flower"],
            "city": ["building", "skyscraper", "car", "person", "road", "traffic light", "sign", "bus", "store", "bridge"],
            "office": ["desk", "chair", "computer", "paper", "pen", "person", "phone", "notebook", "plant", "calendar"],
            "home": ["sofa", "table", "television", "chair", "lamp", "book", "plant", "picture", "rug", "pillow"],
            "restaurant": ["table", "chair", "food", "plate", "glass", "person", "menu", "waiter", "light", "utensil"],
            "park": ["tree", "bench", "grass", "path", "person", "flower", "playground", "dog", "pond", "bird"],
            "street": ["road", "car", "person", "building", "sign", "traffic light", "sidewalk", "bicycle", "store", "tree"]
        }
        
        # Select objects based on the top scene
        scene_objects = objects_by_scene.get(top_scene, objects_by_scene["outdoor"])
        
        # Determine number of objects based on detail level
        if detail_level == "brief":
            num_objects = random.randint(2, 4)
        elif detail_level == "standard":
            num_objects = random.randint(3, 6)
        else:  # detailed
            num_objects = random.randint(5, 8)
        
        # Select random objects
        selected_objects = random.sample(scene_objects, min(num_objects, len(scene_objects)))
        
        # Generate object details
        objects = []
        for obj in selected_objects:
            objects.append({
                "name": obj,
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "bounding_box": {
                    "x": round(random.uniform(0, 0.8), 2),
                    "y": round(random.uniform(0, 0.8), 2),
                    "width": round(random.uniform(0.1, 0.5), 2),
                    "height": round(random.uniform(0.1, 0.5), 2)
                }
            })
        
        analysis_result["objects"] = objects
    
    # Simulate color analysis if requested
    if include_colors:
        # Common colors
        colors = [
            "red", "green", "blue", "yellow", "orange", "purple", "pink",
            "brown", "black", "white", "gray", "teal", "navy", "maroon"
        ]
        
        # Determine number of colors based on detail level
        if detail_level == "brief":
            num_colors = random.randint(2, 3)
        elif detail_level == "standard":
            num_colors = random.randint(3, 4)
        else:  # detailed
            num_colors = random.randint(4, 6)
        
        # Select random colors
        selected_colors = random.sample(colors, num_colors)
        
        # Generate color details
        color_analysis = []
        total_percentage = 100
        
        for i, color in enumerate(selected_colors):
            # Last color gets the remaining percentage
            if i == len(selected_colors) - 1:
                percentage = total_percentage
            else:
                percentage = random.randint(5, min(total_percentage - 5 * (len(selected_colors) - i - 1), 60))
                total_percentage -= percentage
            
            color_analysis.append({
                "color": color,
                "percentage": percentage,
                "hex": _get_color_hex(color)
            })
        
        # Sort by percentage (descending)
        color_analysis.sort(key=lambda x: x["percentage"], reverse=True)
        
        analysis_result["colors"] = color_analysis
    
    # Simulate style analysis if requested
    if include_style:
        # Artistic styles
        styles = [
            "photograph", "painting", "sketch", "digital art", "cartoon",
            "minimalist", "abstract", "realistic", "vintage", "modern",
            "black and white", "colorful", "surreal", "impressionist"
        ]
        
        # Select a primary style and possibly secondary styles
        primary_style = random.choice(styles)
        styles.remove(primary_style)
        
        style_analysis = {
            "primary": {
                "style": primary_style,
                "confidence": round(random.uniform(0.7, 0.95), 2)
            }
        }
        
        # Add secondary styles based on detail level
        if detail_level != "brief":
            num_secondary = 1 if detail_level == "standard" else 2
            secondary_styles = []
            
            for _ in range(num_secondary):
                if styles:
                    style = random.choice(styles)
                    styles.remove(style)
                    secondary_styles.append({
                        "style": style,
                        "confidence": round(random.uniform(0.4, 0.7), 2)
                    })
            
            if secondary_styles:
                style_analysis["secondary"] = secondary_styles
        
        analysis_result["style"] = style_analysis
    
    # Simulate emotion analysis if requested
    if include_emotions:
        # Emotions
        emotions = [
            "happy", "sad", "neutral", "excited", "calm",
            "tense", "peaceful", "energetic", "melancholic", "joyful"
        ]
        
        # Determine number of emotions based on detail level
        if detail_level == "brief":
            num_emotions = 1
        elif detail_level == "standard":
            num_emotions = 2
        else:  # detailed
            num_emotions = 3
        
        # Select random emotions
        selected_emotions = random.sample(emotions, num_emotions)
        
        # Generate emotion details
        emotion_analysis = []
        total_percentage = 100
        
        for i, emotion in enumerate(selected_emotions):
            # Last emotion gets the remaining percentage
            if i == len(selected_emotions) - 1:
                percentage = total_percentage
            else:
                percentage = random.randint(20, min(total_percentage - 20 * (len(selected_emotions) - i - 1), 70))
                total_percentage -= percentage
            
            emotion_analysis.append({
                "emotion": emotion,
                "percentage": percentage
            })
        
        # Sort by percentage (descending)
        emotion_analysis.sort(key=lambda x: x["percentage"], reverse=True)
        
        analysis_result["emotions"] = emotion_analysis
    
    return analysis_result

def _generate_caption_from_analysis(
    analysis: Dict[str, Any],
    detail_level: str,
    max_caption_length: int
) -> str:
    """
    Generate a descriptive caption based on image analysis.
    
    Args:
        analysis: Image analysis results
        detail_level: Level of detail for the caption
        max_caption_length: Maximum length of the generated caption
        
    Returns:
        Generated caption
    """
    # Extract key information from analysis
    scene = analysis.get("scene", {}).get("top", "scene")
    
    objects = []
    if "objects" in analysis:
        objects = [obj["name"] for obj in analysis["objects"]]
    
    colors = []
    if "colors" in analysis:
        colors = [color["color"] for color in analysis["colors"]]
    
    style = None
    if "style" in analysis:
        style = analysis["style"].get("primary", {}).get("style")
    
    emotion = None
    if "emotions" in analysis:
        emotion = analysis["emotions"][0]["emotion"] if analysis["emotions"] else None
    
    # Generate caption based on detail level
    if detail_level == "brief":
        caption = _generate_brief_caption(scene, objects, colors, style, emotion)
    elif detail_level == "standard":
        caption = _generate_standard_caption(scene, objects, colors, style, emotion)
    else:  # detailed
        caption = _generate_detailed_caption(scene, objects, colors, style, emotion)
    
    # Truncate caption if needed
    if len(caption) > max_caption_length:
        caption = caption[:max_caption_length - 3] + "..."
    
    return caption

def _generate_brief_caption(
    scene: str,
    objects: List[str],
    colors: List[str],
    style: Optional[str],
    emotion: Optional[str]
) -> str:
    """
    Generate a brief caption.
    
    Args:
        scene: Scene type
        objects: Detected objects
        colors: Dominant colors
        style: Artistic style
        emotion: Dominant emotion
        
    Returns:
        Brief caption
    """
    # Start with the scene
    caption = f"A {scene} scene"
    
    # Add main objects (up to 2)
    if objects:
        main_objects = objects[:2]
        if len(main_objects) == 1:
            caption += f" with a {main_objects[0]}"
        else:
            caption += f" with a {main_objects[0]} and a {main_objects[1]}"
    
    # Add main color if available
    if colors:
        caption += f", predominantly {colors[0]}"
    
    # Add style if available
    if style:
        caption += f" in {style} style"
    
    # Add period
    caption += "."
    
    return caption

def _generate_standard_caption(
    scene: str,
    objects: List[str],
    colors: List[str],
    style: Optional[str],
    emotion: Optional[str]
) -> str:
    """
    Generate a standard caption.
    
    Args:
        scene: Scene type
        objects: Detected objects
        colors: Dominant colors
        style: Artistic style
        emotion: Dominant emotion
        
    Returns:
        Standard caption
    """
    # Start with the scene and style
    if style:
        caption = f"A {style} {scene} scene"
    else:
        caption = f"A {scene} scene"
    
    # Add objects (up to 4)
    if objects:
        main_objects = objects[:4]
        if len(main_objects) == 1:
            caption += f" featuring a {main_objects[0]}"
        elif len(main_objects) == 2:
            caption += f" featuring a {main_objects[0]} and a {main_objects[1]}"
        else:
            object_list = ", ".join(f"a {obj}" for obj in main_objects[:-1])
            caption += f" featuring {object_list}, and a {main_objects[-1]}"
    
    # Add colors (up to 2)
    if colors and len(colors) >= 2:
        caption += f", with {colors[0]} and {colors[1]} tones"
    elif colors:
        caption += f", with {colors[0]} tones"
    
    # Add emotion if available
    if emotion:
        caption += f", conveying a {emotion} mood"
    
    # Add period
    caption += "."
    
    return caption

def _generate_detailed_caption(
    scene: str,
    objects: List[str],
    colors: List[str],
    style: Optional[str],
    emotion: Optional[str]
) -> str:
    """
    Generate a detailed caption.
    
    Args:
        scene: Scene type
        objects: Detected objects
        colors: Dominant colors
        style: Artistic style
        emotion: Dominant emotion
        
    Returns:
        Detailed caption
    """
    # Start with a more descriptive scene introduction
    scene_descriptions = {
        "outdoor": "An expansive outdoor setting",
        "indoor": "A cozy indoor environment",
        "urban": "A bustling urban landscape",
        "rural": "A serene rural setting",
        "nature": "A picturesque natural landscape",
        "beach": "A beautiful beach scene",
        "mountain": "A majestic mountain landscape",
        "forest": "A lush forest setting",
        "city": "A vibrant city scene",
        "office": "A professional office space",
        "home": "A comfortable home interior",
        "restaurant": "An inviting restaurant setting",
        "park": "A relaxing park scene",
        "street": "A dynamic street view"
    }
    
    scene_desc = scene_descriptions.get(scene, f"A {scene} scene")
    
    # Add style if available
    if style:
        caption = f"{scene_desc} captured in {style} style"
    else:
        caption = scene_desc
    
    # Add objects (all)
    if objects:
        if len(objects) == 1:
            caption += f", prominently featuring a {objects[0]}"
        elif len(objects) == 2:
            caption += f", prominently featuring a {objects[0]} and a {objects[1]}"
        else:
            object_list = ", ".join(f"a {obj}" for obj in objects[:-1])
            caption += f", prominently featuring {object_list}, and a {objects[-1]}"
    
    # Add colors (all)
    if colors:
        if len(colors) == 1:
            caption += f". The image is dominated by {colors[0]} tones"
        elif len(colors) == 2:
            caption += f". The image features a palette of {colors[0]} and {colors[1]} tones"
        else:
            color_list = ", ".join(colors[:-1])
            caption += f". The image features a rich palette of {color_list}, and {colors[-1]} tones"
    
    # Add emotion if available
    if emotion:
        emotion_descriptions = {
            "happy": "a sense of joy and happiness",
            "sad": "a melancholic and somber mood",
            "neutral": "a balanced and neutral atmosphere",
            "excited": "an exciting and energetic atmosphere",
            "calm": "a peaceful and calm ambiance",
            "tense": "a tense and dramatic feeling",
            "peaceful": "a serene and peaceful mood",
            "energetic": "a vibrant and energetic spirit",
            "melancholic": "a nostalgic and melancholic sentiment",
            "joyful": "an uplifting and joyful emotion"
        }
        
        emotion_desc = emotion_descriptions.get(emotion, f"a {emotion} mood")
        caption += f", conveying {emotion_desc}"
    
    # Add period if needed
    if not caption.endswith("."):
        caption += "."
    
    return caption

def _get_color_hex(color_name: str) -> str:
    """
    Get a hex color code for a color name.
    
    Args:
        color_name: Color name
        
    Returns:
        Hex color code
    """
    color_hex_map = {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "purple": "#800080",
        "pink": "#FFC0CB",
        "brown": "#A52A2A",
        "black": "#000000",
        "white": "#FFFFFF",
        "gray": "#808080",
        "teal": "#008080",
        "navy": "#000080",
        "maroon": "#800000"
    }
    
    return color_hex_map.get(color_name, "#CCCCCC")
