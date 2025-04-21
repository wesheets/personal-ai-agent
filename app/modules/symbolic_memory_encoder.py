"""
Symbolic Memory Encoder Module

This module is responsible for converting loop summaries into structured symbolic memory,
extracting concepts, relationships, and insights, and enabling memory querying.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import asyncio
import json
from datetime import datetime
import re
from collections import defaultdict

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "loop_trace[loop_001]":
        return {
            "loop_id": "loop_001",
            "status": "finalized",
            "timestamp": "2025-04-20T10:00:00Z",
            "summary": "Analyzed quantum computing concepts with thorough examination of qubits, superposition, and entanglement. Identified potential applications in cryptography and optimization problems.",
            "orchestrator_persona": "SAGE",
            "alignment_score": 0.82,
            "drift_score": 0.18,
            "rerun_count": 0
        }
    elif key == "loop_trace[loop_002]":
        return {
            "loop_id": "loop_002",
            "status": "finalized",
            "timestamp": "2025-04-20T14:00:00Z",
            "summary": "Researched machine learning algorithms with focus on neural networks and deep learning. Evaluated performance characteristics and application domains.",
            "orchestrator_persona": "NOVA",
            "alignment_score": 0.79,
            "drift_score": 0.21,
            "rerun_count": 1,
            "rerun_trigger": ["alignment"],
            "rerun_reason": "alignment_threshold_not_met"
        }
    elif key == "symbolic_memory":
        return {
            "concepts": {
                "quantum_computing": {
                    "id": "concept:quantum_computing",
                    "name": "Quantum Computing",
                    "description": "Computing paradigm that uses quantum-mechanical phenomena to perform operations on data",
                    "related_concepts": ["concept:qubits", "concept:superposition", "concept:entanglement"],
                    "source_loops": ["loop_001"],
                    "confidence": 0.95,
                    "last_updated": "2025-04-20T10:30:00Z"
                },
                "qubits": {
                    "id": "concept:qubits",
                    "name": "Qubits",
                    "description": "Quantum bits that can exist in multiple states simultaneously",
                    "related_concepts": ["concept:quantum_computing", "concept:superposition"],
                    "source_loops": ["loop_001"],
                    "confidence": 0.92,
                    "last_updated": "2025-04-20T10:30:00Z"
                }
            },
            "relationships": {
                "enables": [
                    {
                        "id": "rel:quantum_computing_enables_cryptography",
                        "source": "concept:quantum_computing",
                        "target": "concept:quantum_cryptography",
                        "type": "enables",
                        "description": "Quantum computing enables new forms of cryptography",
                        "source_loops": ["loop_001"],
                        "confidence": 0.88,
                        "last_updated": "2025-04-20T10:30:00Z"
                    }
                ]
            },
            "insights": {
                "quantum_speedup": {
                    "id": "insight:quantum_speedup",
                    "name": "Quantum Speedup",
                    "description": "Quantum algorithms can provide exponential speedup for certain problems compared to classical algorithms",
                    "related_concepts": ["concept:quantum_computing", "concept:quantum_algorithms"],
                    "source_loops": ["loop_001"],
                    "confidence": 0.85,
                    "last_updated": "2025-04-20T10:30:00Z"
                }
            }
        }
    
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

async def get_loop_trace(loop_id: str) -> Dict[str, Any]:
    """
    Get the trace for a specific loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with loop trace data
    """
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    if not isinstance(trace, dict):
        return {
            "error": f"Loop trace not found for {loop_id}",
            "loop_id": loop_id
        }
    
    return trace

async def get_symbolic_memory() -> Dict[str, Any]:
    """
    Get the current symbolic memory.
    
    Returns:
        Dict with symbolic memory
    """
    memory = await read_from_memory("symbolic_memory")
    if not isinstance(memory, dict):
        # Create default memory structure if none exists
        memory = {
            "concepts": {},
            "relationships": {},
            "insights": {},
            "last_updated": datetime.utcnow().isoformat()
        }
    
    return memory

def extract_concepts_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extract concepts from text.
    
    Args:
        text: The text to extract concepts from
        
    Returns:
        List of extracted concepts
    """
    # In a real implementation, this would use NLP techniques
    # For this mock implementation, we'll use a simple approach
    
    # Define some common concept patterns
    concept_patterns = [
        r"(\w+) computing",
        r"(\w+) algorithms",
        r"(\w+) learning",
        r"(\w+) intelligence",
        r"(\w+) networks",
        r"(\w+) systems",
        r"(\w+) security",
        r"(\w+) analysis",
        r"(\w+) optimization",
        r"(\w+) programming"
    ]
    
    # Extract concepts
    concepts = []
    
    for pattern in concept_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            concept_name = match.group(0)
            concept_id = concept_name.lower().replace(" ", "_")
            
            # Check if concept already exists
            if not any(c["id"] == concept_id for c in concepts):
                concepts.append({
                    "id": concept_id,
                    "name": concept_name,
                    "confidence": 0.9,
                    "text_span": match.span()
                })
    
    # Extract specific concepts based on keywords
    keyword_concepts = {
        "quantum computing": "Computing paradigm that uses quantum-mechanical phenomena to perform operations on data",
        "qubits": "Quantum bits that can exist in multiple states simultaneously",
        "superposition": "Quantum state where particles exist in multiple states simultaneously",
        "entanglement": "Quantum phenomenon where particles become correlated and share properties",
        "machine learning": "Field of AI that enables systems to learn from data",
        "neural networks": "Computing systems inspired by biological neural networks",
        "deep learning": "Subset of machine learning using neural networks with multiple layers",
        "cryptography": "Practice of secure communication techniques",
        "optimization": "Process of finding the best solution from all feasible solutions"
    }
    
    for keyword, description in keyword_concepts.items():
        if keyword.lower() in text.lower():
            concept_id = keyword.lower().replace(" ", "_")
            
            # Check if concept already exists
            if not any(c["id"] == concept_id for c in concepts):
                concepts.append({
                    "id": concept_id,
                    "name": keyword,
                    "description": description,
                    "confidence": 0.95
                })
    
    return concepts

def extract_relationships_from_text(text: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract relationships between concepts from text.
    
    Args:
        text: The text to extract relationships from
        concepts: List of concepts to find relationships between
        
    Returns:
        List of extracted relationships
    """
    # In a real implementation, this would use NLP techniques
    # For this mock implementation, we'll use a simple approach
    
    # Define relationship patterns
    relationship_patterns = [
        (r"(\w+) enables (\w+)", "enables"),
        (r"(\w+) uses (\w+)", "uses"),
        (r"(\w+) requires (\w+)", "requires"),
        (r"(\w+) improves (\w+)", "improves"),
        (r"(\w+) is part of (\w+)", "is_part_of"),
        (r"(\w+) contains (\w+)", "contains"),
        (r"(\w+) is a type of (\w+)", "is_a"),
        (r"(\w+) is related to (\w+)", "is_related_to")
    ]
    
    # Extract relationships
    relationships = []
    
    # Get concept IDs
    concept_ids = [c["id"] for c in concepts]
    
    # Check for relationships between concepts
    for i, concept1 in enumerate(concepts):
        for j, concept2 in enumerate(concepts):
            if i != j:
                # Check if concepts are mentioned close to each other
                concept1_name = concept1["name"].lower()
                concept2_name = concept2["name"].lower()
                
                # Check if both concepts appear in the text
                if concept1_name in text.lower() and concept2_name in text.lower():
                    # Check for specific relationship patterns
                    for pattern, rel_type in relationship_patterns:
                        if re.search(f"{concept1_name}.*{pattern}.*{concept2_name}", text, re.IGNORECASE) or \
                           re.search(f"{concept2_name}.*{pattern}.*{concept1_name}", text, re.IGNORECASE):
                            
                            rel_id = f"rel:{concept1['id']}_{rel_type}_{concept2['id']}"
                            
                            # Check if relationship already exists
                            if not any(r["id"] == rel_id for r in relationships):
                                relationships.append({
                                    "id": rel_id,
                                    "source": f"concept:{concept1['id']}",
                                    "target": f"concept:{concept2['id']}",
                                    "type": rel_type,
                                    "description": f"{concept1['name']} {rel_type.replace('_', ' ')} {concept2['name']}",
                                    "confidence": 0.85
                                })
    
    # Add default relationships based on concept types
    for concept1 in concepts:
        for concept2 in concepts:
            if concept1["id"] != concept2["id"]:
                # Add "is_related_to" relationship if no other relationship exists
                if not any(r["source"] == f"concept:{concept1['id']}" and r["target"] == f"concept:{concept2['id']}" for r in relationships) and \
                   not any(r["source"] == f"concept:{concept2['id']}" and r["target"] == f"concept:{concept1['id']}" for r in relationships):
                    
                    # Only add relationship if concepts are likely related
                    if concept1["id"] in concept2.get("related_concepts", []) or \
                       concept2["id"] in concept1.get("related_concepts", []):
                        
                        rel_id = f"rel:{concept1['id']}_is_related_to_{concept2['id']}"
                        
                        relationships.append({
                            "id": rel_id,
                            "source": f"concept:{concept1['id']}",
                            "target": f"concept:{concept2['id']}",
                            "type": "is_related_to",
                            "description": f"{concept1['name']} is related to {concept2['name']}",
                            "confidence": 0.7
                        })
    
    return relationships

def extract_insights_from_text(text: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract insights from text.
    
    Args:
        text: The text to extract insights from
        concepts: List of concepts to associate insights with
        
    Returns:
        List of extracted insights
    """
    # In a real implementation, this would use NLP techniques
    # For this mock implementation, we'll use a simple approach
    
    # Define insight patterns
    insight_patterns = [
        r"([\w\s]+) can provide ([\w\s]+)",
        r"([\w\s]+) enables ([\w\s]+)",
        r"([\w\s]+) improves ([\w\s]+)",
        r"([\w\s]+) solves ([\w\s]+)",
        r"([\w\s]+) addresses ([\w\s]+)",
        r"([\w\s]+) is better for ([\w\s]+)",
        r"([\w\s]+) outperforms ([\w\s]+)"
    ]
    
    # Extract insights
    insights = []
    
    for pattern in insight_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            insight_text = match.group(0)
            insight_id = re.sub(r'[^\w]', '_', insight_text.lower())[:50]
            
            # Find related concepts
            related_concepts = []
            for concept in concepts:
                if concept["name"].lower() in insight_text.lower():
                    related_concepts.append(f"concept:{concept['id']}")
            
            # Only add insight if it has related concepts
            if related_concepts:
                # Check if insight already exists
                if not any(i["id"] == insight_id for i in insights):
                    insights.append({
                        "id": insight_id,
                        "name": insight_text,
                        "description": insight_text,
                        "related_concepts": related_concepts,
                        "confidence": 0.8
                    })
    
    # Add specific insights based on keywords
    keyword_insights = {
        "quantum speedup": "Quantum algorithms can provide exponential speedup for certain problems compared to classical algorithms",
        "quantum security": "Quantum computing offers new approaches to cryptography and security",
        "neural network performance": "Neural networks perform well on pattern recognition tasks with large datasets",
        "deep learning applications": "Deep learning excels in image recognition, natural language processing, and speech recognition"
    }
    
    for keyword, description in keyword_insights.items():
        if keyword.lower() in text.lower():
            insight_id = keyword.lower().replace(" ", "_")
            
            # Find related concepts
            related_concepts = []
            for concept in concepts:
                if any(word in concept["name"].lower() for word in keyword.lower().split()):
                    related_concepts.append(f"concept:{concept['id']}")
            
            # Only add insight if it has related concepts
            if related_concepts:
                # Check if insight already exists
                if not any(i["id"] == insight_id for i in insights):
                    insights.append({
                        "id": insight_id,
                        "name": keyword,
                        "description": description,
                        "related_concepts": related_concepts,
                        "confidence": 0.9
                    })
    
    return insights

def generate_concept_description(concept_name: str) -> str:
    """
    Generate a description for a concept.
    
    Args:
        concept_name: The name of the concept
        
    Returns:
        Generated description
    """
    # In a real implementation, this would use LLM or knowledge base
    # For this mock implementation, we'll use a simple approach
    
    # Define descriptions for common concepts
    concept_descriptions = {
        "quantum computing": "Computing paradigm that uses quantum-mechanical phenomena to perform operations on data",
        "qubits": "Quantum bits that can exist in multiple states simultaneously",
        "superposition": "Quantum state where particles exist in multiple states simultaneously",
        "entanglement": "Quantum phenomenon where particles become correlated and share properties",
        "machine learning": "Field of AI that enables systems to learn from data",
        "neural networks": "Computing systems inspired by biological neural networks",
        "deep learning": "Subset of machine learning using neural networks with multiple layers",
        "cryptography": "Practice of secure communication techniques",
        "optimization": "Process of finding the best solution from all feasible solutions"
    }
    
    # Check if concept has a predefined description
    concept_lower = concept_name.lower()
    for key, description in concept_descriptions.items():
        if key in concept_lower:
            return description
    
    # Generate a generic description
    return f"Concept related to {concept_name}"

def find_related_concepts(concept_id: str, concepts: List[Dict[str, Any]]) -> List[str]:
    """
    Find concepts related to a given concept.
    
    Args:
        concept_id: The ID of the concept
        concepts: List of all concepts
        
    Returns:
        List of related concept IDs
    """
    # In a real implementation, this would use semantic similarity
    # For this mock implementation, we'll use a simple approach
    
    related_concepts = []
    
    # Find the target concept
    target_concept = None
    for concept in concepts:
        if concept["id"] == concept_id:
            target_concept = concept
            break
    
    if not target_concept:
        return []
    
    # Find concepts with similar names
    target_name = target_concept["name"].lower()
    for concept in concepts:
        if concept["id"] != concept_id:
            concept_name = concept["name"].lower()
            
            # Check if names share words
            target_words = set(target_name.split())
            concept_words = set(concept_name.split())
            
            if target_words.intersection(concept_words):
                related_concepts.append(f"concept:{concept['id']}")
    
    return related_concepts

async def encode_loop_to_symbolic_memory(loop_id: str) -> Dict[str, Any]:
    """
    Encode a loop to symbolic memory.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with encoding results
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Extract summary
    summary = trace.get("summary", "")
    if not summary:
        return {
            "error": "No summary found in loop trace",
            "loop_id": loop_id
        }
    
    # Extract concepts
    concepts = extract_concepts_from_text(summary)
    
    # Add concept IDs
    for concept in concepts:
        concept["id"] = f"concept:{concept['id']}"
    
    # Extract relationships
    relationships = extract_relationships_from_text(summary, concepts)
    
    # Extract insights
    insights = extract_insights_from_text(summary, concepts)
    
    # Add insight IDs
    for insight in insights:
        insight["id"] = f"insight:{insight['id']}"
    
    # Get current symbolic memory
    memory = await get_symbolic_memory()
    
    # Update memory with new concepts
    for concept in concepts:
        concept_id = concept["id"].replace("concept:", "")
        full_id = f"concept:{concept_id}"
        
        # Check if concept already exists
        if concept_id in memory["concepts"]:
            # Update existing concept
            existing_concept = memory["concepts"][concept_id]
            
            # Add loop ID to source loops if not already present
            if loop_id not in existing_concept["source_loops"]:
                existing_concept["source_loops"].append(loop_id)
            
            # Update confidence if new confidence is higher
            if concept["confidence"] > existing_concept["confidence"]:
                existing_concept["confidence"] = concept["confidence"]
            
            # Update last updated timestamp
            existing_concept["last_updated"] = datetime.utcnow().isoformat()
        else:
            # Create new concept
            memory["concepts"][concept_id] = {
                "id": full_id,
                "name": concept["name"],
                "description": concept.get("description", generate_concept_description(concept["name"])),
                "related_concepts": concept.get("related_concepts", find_related_concepts(concept_id, concepts)),
                "source_loops": [loop_id],
                "confidence": concept["confidence"],
                "last_updated": datetime.utcnow().isoformat()
            }
    
    # Update memory with new relationships
    for relationship in relationships:
        rel_type = relationship["type"]
        
        # Ensure relationship type exists
        if rel_type not in memory["relationships"]:
            memory["relationships"][rel_type] = []
        
        # Check if relationship already exists
        rel_id = relationship["id"].replace("rel:", "")
        existing_rel = None
        
        for rel in memory["relationships"][rel_type]:
            if rel["id"] == f"rel:{rel_id}":
                existing_rel = rel
                break
        
        if existing_rel:
            # Update existing relationship
            
            # Add loop ID to source loops if not already present
            if loop_id not in existing_rel["source_loops"]:
                existing_rel["source_loops"].append(loop_id)
            
            # Update confidence if new confidence is higher
            if relationship["confidence"] > existing_rel["confidence"]:
                existing_rel["confidence"] = relationship["confidence"]
            
            # Update last updated timestamp
            existing_rel["last_updated"] = datetime.utcnow().isoformat()
        else:
            # Create new relationship
            memory["relationships"][rel_type].append({
                "id": relationship["id"],
                "source": relationship["source"],
                "target": relationship["target"],
                "type": relationship["type"],
                "description": relationship["description"],
                "source_loops": [loop_id],
                "confidence": relationship["confidence"],
                "last_updated": datetime.utcnow().isoformat()
            })
    
    # Update memory with new insights
    for insight in insights:
        insight_id = insight["id"].replace("insight:", "")
        full_id = f"insight:{insight_id}"
        
        # Check if insight already exists
        if insight_id in memory["insights"]:
            # Update existing insight
            existing_insight = memory["insights"][insight_id]
            
            # Add loop ID to source loops if not already present
            if loop_id not in existing_insight["source_loops"]:
                existing_insight["source_loops"].append(loop_id)
            
            # Update confidence if new confidence is higher
            if insight["confidence"] > existing_insight["confidence"]:
                existing_insight["confidence"] = insight["confidence"]
            
            # Update last updated timestamp
            existing_insight["last_updated"] = datetime.utcnow().isoformat()
        else:
            # Create new insight
            memory["insights"][insight_id] = {
                "id": full_id,
                "name": insight["name"],
                "description": insight["description"],
                "related_concepts": insight["related_concepts"],
                "source_loops": [loop_id],
                "confidence": insight["confidence"],
                "last_updated": datetime.utcnow().isoformat()
            }
    
    # Update memory last updated timestamp
    memory["last_updated"] = datetime.utcnow().isoformat()
    
    # Write updated memory to storage
    await write_to_memory("symbolic_memory", memory)
    
    # Create encoding result
    result = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "concepts_encoded": len(concepts),
        "relationships_encoded": len(relationships),
        "insights_encoded": len(insights),
        "concept_ids": [c["id"] for c in concepts],
        "relationship_ids": [r["id"] for r in relationships],
        "insight_ids": [i["id"] for i in insights]
    }
    
    return result

async def encode_all_loops_to_symbolic_memory(loop_ids: List[str]) -> Dict[str, Any]:
    """
    Encode multiple loops to symbolic memory.
    
    Args:
        loop_ids: List of loop IDs to encode
        
    Returns:
        Dict mapping loop IDs to encoding results
    """
    results = {}
    
    for loop_id in loop_ids:
        result = await encode_loop_to_symbolic_memory(loop_id)
        results[loop_id] = result
    
    return results

async def inject_symbolic_memory_into_loop_trace(loop_id: str) -> bool:
    """
    Inject symbolic memory encoding results into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Encode the loop to symbolic memory
    encoding_result = await encode_loop_to_symbolic_memory(loop_id)
    if "error" in encoding_result:
        return False
    
    # Update the trace with the encoding result
    trace["symbolic_memory_encoding"] = encoding_result
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True

async def query_symbolic_memory(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Query symbolic memory for relevant concepts, relationships, and insights.
    
    Args:
        query: The query string
        limit: Maximum number of results to return per category
        
    Returns:
        Dict with query results
    """
    # Get symbolic memory
    memory = await get_symbolic_memory()
    
    # Extract query terms
    query_terms = set(query.lower().split())
    
    # Find matching concepts
    matching_concepts = []
    for concept_id, concept in memory["concepts"].items():
        concept_name = concept["name"].lower()
        concept_desc = concept.get("description", "").lower()
        
        # Check if any query term is in the concept name or description
        if any(term in concept_name or term in concept_desc for term in query_terms):
            matching_concepts.append(concept)
    
    # Sort concepts by confidence
    matching_concepts.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Limit number of concepts
    matching_concepts = matching_concepts[:limit]
    
    # Find matching insights
    matching_insights = []
    for insight_id, insight in memory["insights"].items():
        insight_name = insight["name"].lower()
        insight_desc = insight.get("description", "").lower()
        
        # Check if any query term is in the insight name or description
        if any(term in insight_name or term in insight_desc for term in query_terms):
            matching_insights.append(insight)
    
    # Sort insights by confidence
    matching_insights.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Limit number of insights
    matching_insights = matching_insights[:limit]
    
    # Find matching relationships
    matching_relationships = []
    for rel_type, relationships in memory["relationships"].items():
        for relationship in relationships:
            rel_desc = relationship.get("description", "").lower()
            
            # Check if any query term is in the relationship description
            if any(term in rel_desc for term in query_terms):
                matching_relationships.append(relationship)
    
    # Sort relationships by confidence
    matching_relationships.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Limit number of relationships
    matching_relationships = matching_relationships[:limit]
    
    # Create query result
    result = {
        "query": query,
        "timestamp": datetime.utcnow().isoformat(),
        "concepts": matching_concepts,
        "insights": matching_insights,
        "relationships": matching_relationships
    }
    
    return result
