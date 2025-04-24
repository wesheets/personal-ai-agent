"""
Memory Embed Module

This module implements the functionality for embedding memory entries for vector-based retrieval.
"""

import logging
import json
import uuid
import random
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("memory_embed")

# In-memory storage for embedded memories
# In a production environment, this would be a vector database
_embedded_memories: Dict[str, Dict[str, Any]] = {}

def embed_memory(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Embed content for vector-based retrieval.
    
    Args:
        request_data: Request data containing content, model, dimension, tags, etc.
        
    Returns:
        Dictionary containing the embedding result
    """
    try:
        content = request_data.get("content")
        model = request_data.get("model", "default")
        dimension = request_data.get("dimension")
        tags = request_data.get("tags", [])
        agent_id = request_data.get("agent_id")
        loop_id = request_data.get("loop_id")
        
        # Validate content
        if not content:
            return {
                "message": "Content must not be empty",
                "model": model,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Determine embedding dimension based on model if not specified
        if not dimension:
            dimension = _get_default_dimension(model)
        
        # Generate embedding (in a real implementation, this would use a model)
        embedding = _generate_embedding(content, model, dimension)
        
        # Generate memory ID
        memory_id = f"mem_embed_{uuid.uuid4().hex[:8]}"
        
        # Store the embedded memory
        _embedded_memories[memory_id] = {
            "content": content,
            "embedding": embedding,
            "model": model,
            "dimension": dimension,
            "tags": tags,
            "agent_id": agent_id,
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the embedding to memory
        _log_memory_embed(memory_id, model, dimension, tags)
        
        # Return the result
        return {
            "memory_id": memory_id,
            "embedding_size": dimension,
            "model_used": model,
            "tags": tags,
            "agent_id": agent_id,
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error embedding memory: {str(e)}")
        return {
            "message": f"Failed to embed memory: {str(e)}",
            "model": request_data.get("model"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def embed_memory_batch(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Embed multiple content items for vector-based retrieval.
    
    Args:
        request_data: Request data containing list of items to embed
        
    Returns:
        Dictionary containing the batch embedding results
    """
    try:
        items = request_data.get("items", [])
        
        # Validate items
        if not items:
            return {
                "message": "Items list must not be empty",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        if len(items) > 100:
            return {
                "message": "Maximum 100 items allowed per batch",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Process each item
        results = []
        errors = []
        successful_items = 0
        
        for item in items:
            result = embed_memory(item)
            
            # Check if the result is an error
            if "message" in result:
                errors.append({
                    "message": result["message"],
                    "item": item
                })
            else:
                results.append(result)
                successful_items += 1
        
        # Log the batch embedding to memory
        _log_memory_embed_batch(len(items), successful_items)
        
        # Return the results
        return {
            "results": results,
            "errors": errors,
            "total_items": len(items),
            "successful_items": successful_items,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error embedding memory batch: {str(e)}")
        return {
            "message": f"Failed to embed memory batch: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def _get_default_dimension(model: str) -> int:
    """
    Get the default embedding dimension for a model.
    
    Args:
        model: Model name
        
    Returns:
        Default embedding dimension
    """
    # In a real implementation, this would be based on the model
    model_dimensions = {
        "default": 512,
        "small": 256,
        "medium": 512,
        "large": 768,
        "multilingual": 512
    }
    
    return model_dimensions.get(model, 512)

def _generate_embedding(content: Union[str, Dict[str, Any]], model: str, dimension: int) -> List[float]:
    """
    Generate an embedding for the provided content.
    
    Args:
        content: Content to embed
        model: Model to use for embedding
        dimension: Dimension of the embedding
        
    Returns:
        List of embedding values
    """
    # In a real implementation, this would use a model to generate the embedding
    # For this implementation, we'll generate random values
    
    # Convert content to string if it's a dictionary
    if isinstance(content, dict):
        content = json.dumps(content)
    
    # Use content hash as seed for reproducibility
    seed = hash(content) % 10000
    random.seed(seed)
    
    # Generate random embedding
    embedding = [random.uniform(-1.0, 1.0) for _ in range(dimension)]
    
    # Normalize the embedding
    magnitude = sum(x * x for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]
    
    return embedding

def _log_memory_embed(memory_id: str, model: str, dimension: int, tags: List[str]) -> None:
    """
    Log memory embedding to memory.
    
    Args:
        memory_id: Memory ID
        model: Model used
        dimension: Embedding dimension
        tags: Tags associated with the memory
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "memory_embed",
            "memory_id": memory_id,
            "model": model,
            "dimension": dimension,
            "tags": tags,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Memory embedding logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: memory_embed_{memory_id}")
    
    except Exception as e:
        logger.error(f"Error logging memory embedding: {str(e)}")

def _log_memory_embed_batch(total_items: int, successful_items: int) -> None:
    """
    Log memory batch embedding to memory.
    
    Args:
        total_items: Total number of items in the batch
        successful_items: Number of items successfully embedded
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "memory_embed_batch",
            "total_items": total_items,
            "successful_items": successful_items,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Memory batch embedding logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: memory_embed_batch_{datetime.utcnow().isoformat()}")
    
    except Exception as e:
        logger.error(f"Error logging memory batch embedding: {str(e)}")
