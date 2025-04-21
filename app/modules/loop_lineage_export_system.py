"""
Loop Lineage Export System Module

This module is responsible for exporting loop lineage information,
including parent-child relationships, rerun history, and drift trends.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import asyncio
import json
from datetime import datetime
import re
import os
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
            "rerun_count": 0,
            "parent_loop_id": None,
            "child_loop_ids": ["loop_002"]
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
            "rerun_reason": "alignment_threshold_not_met",
            "parent_loop_id": "loop_001",
            "child_loop_ids": []
        }
    
    return None

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

async def get_parent_loop(loop_id: str) -> Optional[str]:
    """
    Get the parent loop ID for a given loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Parent loop ID or None if no parent
    """
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return None
    
    return trace.get("parent_loop_id")

async def get_child_loops(loop_id: str) -> List[str]:
    """
    Get the child loop IDs for a given loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        List of child loop IDs
    """
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return []
    
    return trace.get("child_loop_ids", [])

async def get_loop_family(loop_id: str) -> Dict[str, Any]:
    """
    Get the entire family tree for a loop, including ancestors and descendants.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with family tree information
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Initialize family tree
    family = {
        "loop_id": loop_id,
        "ancestors": [],
        "descendants": [],
        "siblings": []
    }
    
    # Get ancestors
    current_id = loop_id
    while True:
        parent_id = await get_parent_loop(current_id)
        if not parent_id:
            break
        
        family["ancestors"].append(parent_id)
        current_id = parent_id
    
    # Get descendants (recursively)
    async def get_descendants(parent_id: str) -> List[str]:
        children = await get_child_loops(parent_id)
        descendants = list(children)
        
        for child_id in children:
            child_descendants = await get_descendants(child_id)
            descendants.extend(child_descendants)
        
        return descendants
    
    family["descendants"] = await get_descendants(loop_id)
    
    # Get siblings (loops with the same parent)
    parent_id = await get_parent_loop(loop_id)
    if parent_id:
        siblings = await get_child_loops(parent_id)
        family["siblings"] = [sibling for sibling in siblings if sibling != loop_id]
    
    return family

async def export_loop_lineage(loop_id: str) -> Dict[str, Any]:
    """
    Export lineage information for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with lineage information
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Get family tree
    family = await get_loop_family(loop_id)
    if "error" in family:
        return {
            "error": family["error"],
            "loop_id": loop_id
        }
    
    # Extract key information from trace
    loop_info = {
        "loop_id": loop_id,
        "timestamp": trace.get("timestamp", ""),
        "status": trace.get("status", ""),
        "orchestrator_persona": trace.get("orchestrator_persona", ""),
        "alignment_score": trace.get("alignment_score", 0.0),
        "drift_score": trace.get("drift_score", 0.0),
        "rerun_count": trace.get("rerun_count", 0),
        "summary": trace.get("summary", "")
    }
    
    # Add rerun information if available
    if "rerun_trigger" in trace:
        loop_info["rerun_trigger"] = trace["rerun_trigger"]
    
    if "rerun_reason" in trace:
        loop_info["rerun_reason"] = trace["rerun_reason"]
    
    # Create lineage export
    lineage = {
        "loop_id": loop_id,
        "export_timestamp": datetime.utcnow().isoformat(),
        "loop_info": loop_info,
        "lineage": {
            "parent_id": trace.get("parent_loop_id"),
            "child_ids": trace.get("child_loop_ids", []),
            "ancestor_ids": family["ancestors"],
            "descendant_ids": family["descendants"],
            "sibling_ids": family["siblings"]
        }
    }
    
    return lineage

async def export_loop_lineage_to_file(loop_id: str, format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Export lineage information for a loop to a file.
    
    Args:
        loop_id: The ID of the loop
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the file
        
    Returns:
        Dict with export result
    """
    # Export the lineage
    lineage = await export_loop_lineage(loop_id)
    if "error" in lineage:
        return {
            "success": False,
            "error": lineage["error"],
            "loop_id": loop_id
        }
    
    # Format the lineage
    if format_type.lower() == "json":
        content = json.dumps(lineage, indent=2)
        file_extension = "json"
    elif format_type.lower() == "md":
        # Create Markdown version
        loop_info = lineage["loop_info"]
        lineage_info = lineage["lineage"]
        
        md = f"""
# Loop Lineage: {loop_id}

*Exported on {lineage["export_timestamp"]}*

## Loop Information

- **Loop ID:** {loop_id}
- **Timestamp:** {loop_info["timestamp"]}
- **Status:** {loop_info["status"]}
- **Orchestrator:** {loop_info["orchestrator_persona"]}
- **Alignment Score:** {loop_info["alignment_score"]}
- **Drift Score:** {loop_info["drift_score"]}
- **Rerun Count:** {loop_info["rerun_count"]}

### Summary

{loop_info["summary"]}

## Lineage Information

- **Parent Loop:** {lineage_info["parent_id"] or "None"}
- **Child Loops:** {", ".join(lineage_info["child_ids"]) or "None"}
- **Ancestors:** {", ".join(lineage_info["ancestor_ids"]) or "None"}
- **Descendants:** {", ".join(lineage_info["descendant_ids"]) or "None"}
- **Siblings:** {", ".join(lineage_info["sibling_ids"]) or "None"}
"""
        
        # Add rerun information if available
        if "rerun_trigger" in loop_info:
            md += f"\n### Rerun Information\n\n- **Rerun Trigger:** {', '.join(loop_info['rerun_trigger'])}\n"
        
        if "rerun_reason" in loop_info:
            md += f"- **Rerun Reason:** {loop_info['rerun_reason']}\n"
        
        content = md
        file_extension = "md"
    elif format_type.lower() == "html":
        # Create HTML version
        loop_info = lineage["loop_info"]
        lineage_info = lineage["lineage"]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loop Lineage: {loop_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .section {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .info-item {{
            margin-bottom: 10px;
        }}
        .info-label {{
            font-weight: bold;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>Loop Lineage: {loop_id}</h1>
    
    <div class="section">
        <h2>Loop Information</h2>
        
        <div class="info-item">
            <span class="info-label">Loop ID:</span> {loop_id}
        </div>
        <div class="info-item">
            <span class="info-label">Timestamp:</span> {loop_info["timestamp"]}
        </div>
        <div class="info-item">
            <span class="info-label">Status:</span> {loop_info["status"]}
        </div>
        <div class="info-item">
            <span class="info-label">Orchestrator:</span> {loop_info["orchestrator_persona"]}
        </div>
        <div class="info-item">
            <span class="info-label">Alignment Score:</span> {loop_info["alignment_score"]}
        </div>
        <div class="info-item">
            <span class="info-label">Drift Score:</span> {loop_info["drift_score"]}
        </div>
        <div class="info-item">
            <span class="info-label">Rerun Count:</span> {loop_info["rerun_count"]}
        </div>
        
        <h3>Summary</h3>
        <p>{loop_info["summary"]}</p>
"""
        
        # Add rerun information if available
        if "rerun_trigger" in loop_info or "rerun_reason" in loop_info:
            html += """
        <h3>Rerun Information</h3>
"""
            
            if "rerun_trigger" in loop_info:
                html += f"""
        <div class="info-item">
            <span class="info-label">Rerun Trigger:</span> {', '.join(loop_info['rerun_trigger'])}
        </div>
"""
            
            if "rerun_reason" in loop_info:
                html += f"""
        <div class="info-item">
            <span class="info-label">Rerun Reason:</span> {loop_info['rerun_reason']}
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="section">
        <h2>Lineage Information</h2>
        
        <div class="info-item">
            <span class="info-label">Parent Loop:</span> {lineage_info["parent_id"] or "None"}
        </div>
        <div class="info-item">
            <span class="info-label">Child Loops:</span> {", ".join(lineage_info["child_ids"]) or "None"}
        </div>
        <div class="info-item">
            <span class="info-label">Ancestors:</span> {", ".join(lineage_info["ancestor_ids"]) or "None"}
        </div>
        <div class="info-item">
            <span class="info-label">Descendants:</span> {", ".join(lineage_info["descendant_ids"]) or "None"}
        </div>
        <div class="info-item">
            <span class="info-label">Siblings:</span> {", ".join(lineage_info["sibling_ids"]) or "None"}
        </div>
    </div>
    
    <div class="timestamp">
        Exported on {lineage["export_timestamp"]}
    </div>
</body>
</html>
"""
        
        content = html
        file_extension = "html"
    else:
        return {
            "success": False,
            "error": f"Unsupported format: {format_type}",
            "loop_id": loop_id
        }
    
    # Create a timestamp for the filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Create the filename
    filename = f"lineage_{loop_id}_{timestamp}.{file_extension}"
    
    # Create the full file path
    file_path = os.path.join(output_dir, filename)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Write the content to the file
    try:
        with open(file_path, "w") as f:
            f.write(content)
        
        return {
            "success": True,
            "loop_id": loop_id,
            "format": format_type,
            "file_path": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write file: {str(e)}",
            "loop_id": loop_id
        }

async def export_multiple_loops(loop_ids: List[str], format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Export lineage information for multiple loops.
    
    Args:
        loop_ids: List of loop IDs to export
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the files
        
    Returns:
        Dict with export results
    """
    results = {}
    
    for loop_id in loop_ids:
        result = await export_loop_lineage_to_file(loop_id, format_type, output_dir)
        results[loop_id] = result
    
    # Calculate success rate
    total_loops = len(results)
    successful_exports = sum(1 for r in results.values() if r.get("success", False))
    
    return {
        "total_loops": total_loops,
        "successful_exports": successful_exports,
        "success_rate": f"{successful_exports}/{total_loops}",
        "format": format_type,
        "output_directory": output_dir,
        "results": results
    }

async def export_loop_family(loop_id: str, format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Export lineage information for a loop and its entire family.
    
    Args:
        loop_id: The ID of the loop
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the files
        
    Returns:
        Dict with export results
    """
    # Get family tree
    family = await get_loop_family(loop_id)
    if "error" in family:
        return {
            "success": False,
            "error": family["error"],
            "loop_id": loop_id
        }
    
    # Create list of all loops in the family
    family_loops = [loop_id] + family["ancestors"] + family["descendants"]
    
    # Export all loops in the family
    results = await export_multiple_loops(family_loops, format_type, output_dir)
    
    # Create a timestamp for the index filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Create an index file
    if format_type.lower() == "json":
        index = {
            "root_loop_id": loop_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "family_size": len(family_loops),
            "loops": family_loops,
            "results": results
        }
        
        content = json.dumps(index, indent=2)
        file_extension = "json"
    elif format_type.lower() == "md":
        md = f"""
# Loop Family: {loop_id}

*Exported on {datetime.utcnow().isoformat()}*

## Family Overview

- **Root Loop:** {loop_id}
- **Family Size:** {len(family_loops)}
- **Ancestors:** {", ".join(family["ancestors"]) or "None"}
- **Descendants:** {", ".join(family["descendants"]) or "None"}

## Exported Loops

"""
        
        for loop in family_loops:
            result = results["results"].get(loop, {})
            file_path = result.get("file_path", "")
            
            if result.get("success", False) and file_path:
                md += f"- [{loop}]({os.path.basename(file_path)})\n"
            else:
                md += f"- {loop} (export failed)\n"
        
        content = md
        file_extension = "md"
    elif format_type.lower() == "html":
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loop Family: {loop_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .section {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .info-item {{
            margin-bottom: 10px;
        }}
        .info-label {{
            font-weight: bold;
        }}
        .loop-list {{
            list-style-type: none;
            padding: 0;
        }}
        .loop-list li {{
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f0f7fb;
            border-radius: 5px;
        }}
        .loop-list li a {{
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }}
        .loop-list li a:hover {{
            text-decoration: underline;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>Loop Family: {loop_id}</h1>
    
    <div class="section">
        <h2>Family Overview</h2>
        
        <div class="info-item">
            <span class="info-label">Root Loop:</span> {loop_id}
        </div>
        <div class="info-item">
            <span class="info-label">Family Size:</span> {len(family_loops)}
        </div>
        <div class="info-item">
            <span class="info-label">Ancestors:</span> {", ".join(family["ancestors"]) or "None"}
        </div>
        <div class="info-item">
            <span class="info-label">Descendants:</span> {", ".join(family["descendants"]) or "None"}
        </div>
    </div>
    
    <div class="section">
        <h2>Exported Loops</h2>
        
        <ul class="loop-list">
"""
        
        for loop in family_loops:
            result = results["results"].get(loop, {})
            file_path = result.get("file_path", "")
            
            if result.get("success", False) and file_path:
                html += f"""
            <li><a href="{os.path.basename(file_path)}">{loop}</a></li>
"""
            else:
                html += f"""
            <li>{loop} (export failed)</li>
"""
        
        html += f"""
        </ul>
    </div>
    
    <div class="timestamp">
        Exported on {datetime.utcnow().isoformat()}
    </div>
</body>
</html>
"""
        
        content = html
        file_extension = "html"
    else:
        return {
            "success": False,
            "error": f"Unsupported format: {format_type}",
            "loop_id": loop_id
        }
    
    # Create the index filename
    index_filename = f"family_index_{loop_id}_{timestamp}.{file_extension}"
    
    # Create the full file path
    index_file_path = os.path.join(output_dir, index_filename)
    
    # Write the index file
    try:
        with open(index_file_path, "w") as f:
            f.write(content)
        
        return {
            "success": True,
            "loop_id": loop_id,
            "format": format_type,
            "family_size": len(family_loops),
            "file_path": index_file_path,
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write index file: {str(e)}",
            "loop_id": loop_id
        }

async def inject_symbolic_memory_into_loop_trace(loop_id: str) -> bool:
    """
    Inject symbolic memory representation into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Get lineage information
    lineage = await export_loop_lineage(loop_id)
    if "error" in lineage:
        return False
    
    # Create symbolic memory representation
    symbolic_memory = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "lineage_symbols": {
            "self": loop_id,
            "parent": lineage["lineage"]["parent_id"],
            "children": lineage["lineage"]["child_ids"],
            "ancestors": lineage["lineage"]["ancestor_ids"],
            "descendants": lineage["lineage"]["descendant_ids"],
            "siblings": lineage["lineage"]["sibling_ids"]
        },
        "metadata_symbols": {
            "orchestrator": trace.get("orchestrator_persona", ""),
            "alignment": trace.get("alignment_score", 0.0),
            "drift": trace.get("drift_score", 0.0),
            "rerun_count": trace.get("rerun_count", 0),
            "status": trace.get("status", "")
        },
        "content_symbols": {
            "summary": trace.get("summary", ""),
            "rerun_reason": trace.get("rerun_reason", ""),
            "rerun_triggers": trace.get("rerun_trigger", [])
        }
    }
    
    # Update the trace with the symbolic memory
    trace["symbolic_memory"] = symbolic_memory
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True
