"""
Public Use Transparency Layer Module

This module is responsible for generating public-facing transparency reports,
sanitizing sensitive information, and providing audit trails for loops.
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
            "operator_id": "operator_001"
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
            "operator_id": "operator_001"
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

def sanitize_sensitive_information(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive information from data.
    
    Args:
        data: The data to sanitize
        
    Returns:
        Sanitized data
    """
    # Create a deep copy of the data
    sanitized = json.loads(json.dumps(data))
    
    # Define sensitive keys to remove
    sensitive_keys = [
        "operator_id",
        "user_id",
        "email",
        "phone",
        "address",
        "ip_address",
        "password",
        "token",
        "api_key",
        "secret",
        "private_key",
        "credentials"
    ]
    
    # Define keys to anonymize
    anonymize_keys = [
        "name",
        "username",
        "user_name",
        "first_name",
        "last_name",
        "full_name"
    ]
    
    # Define function to recursively sanitize data
    def sanitize_recursive(obj):
        if isinstance(obj, dict):
            # Create a new dict to avoid modifying during iteration
            new_obj = {}
            
            for key, value in obj.items():
                # Remove sensitive keys
                if key.lower() in sensitive_keys:
                    continue
                
                # Anonymize certain keys
                if key.lower() in anonymize_keys and isinstance(value, str):
                    new_obj[key] = f"User_{hash(value) % 10000:04d}"
                else:
                    # Recursively sanitize value
                    new_obj[key] = sanitize_recursive(value)
            
            return new_obj
        elif isinstance(obj, list):
            # Recursively sanitize list items
            return [sanitize_recursive(item) for item in obj]
        else:
            # Return primitive values as is
            return obj
    
    # Sanitize the data
    return sanitize_recursive(sanitized)

async def generate_transparency_report(loop_id: str) -> Dict[str, Any]:
    """
    Generate a transparency report for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with transparency report
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Sanitize sensitive information
    sanitized_trace = sanitize_sensitive_information(trace)
    
    # Extract key information
    loop_info = {
        "loop_id": loop_id,
        "timestamp": sanitized_trace.get("timestamp", ""),
        "status": sanitized_trace.get("status", ""),
        "orchestrator_persona": sanitized_trace.get("orchestrator_persona", ""),
        "alignment_score": sanitized_trace.get("alignment_score", 0.0),
        "drift_score": sanitized_trace.get("drift_score", 0.0),
        "rerun_count": sanitized_trace.get("rerun_count", 0)
    }
    
    # Add summary if available
    if "summary" in sanitized_trace:
        loop_info["summary"] = sanitized_trace["summary"]
    
    # Add rerun information if available
    if "rerun_trigger" in sanitized_trace:
        loop_info["rerun_trigger"] = sanitized_trace["rerun_trigger"]
    
    if "rerun_reason" in sanitized_trace:
        loop_info["rerun_reason"] = sanitized_trace["rerun_reason"]
    
    # Add belief drift information if available
    if "belief_drift" in sanitized_trace:
        loop_info["belief_drift"] = sanitized_trace["belief_drift"]
    
    # Add summary validation if available
    if "summary_validation" in sanitized_trace:
        loop_info["summary_validation"] = sanitized_trace["summary_validation"]
    
    # Add symbolic memory encoding if available
    if "symbolic_memory_encoding" in sanitized_trace:
        loop_info["symbolic_memory_encoding"] = sanitized_trace["symbolic_memory_encoding"]
    
    # Create transparency report
    report = {
        "loop_id": loop_id,
        "report_type": "transparency_report",
        "report_version": "1.0",
        "report_timestamp": datetime.utcnow().isoformat(),
        "loop_info": loop_info,
        "transparency_metrics": {
            "alignment_score": sanitized_trace.get("alignment_score", 0.0),
            "drift_score": sanitized_trace.get("drift_score", 0.0),
            "rerun_count": sanitized_trace.get("rerun_count", 0),
            "summary_integrity_score": sanitized_trace.get("summary_integrity_score", 0.0)
        }
    }
    
    return report

async def generate_transparency_report_to_file(loop_id: str, format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Generate a transparency report for a loop and save it to a file.
    
    Args:
        loop_id: The ID of the loop
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the file
        
    Returns:
        Dict with export result
    """
    # Generate the transparency report
    report = await generate_transparency_report(loop_id)
    if "error" in report:
        return {
            "success": False,
            "error": report["error"],
            "loop_id": loop_id
        }
    
    # Format the report
    if format_type.lower() == "json":
        content = json.dumps(report, indent=2)
        file_extension = "json"
    elif format_type.lower() == "md":
        # Create Markdown version
        loop_info = report["loop_info"]
        metrics = report["transparency_metrics"]
        
        md = f"""
# Transparency Report: {loop_id}

*Generated on {report["report_timestamp"]}*

## Loop Information

- **Loop ID:** {loop_id}
- **Timestamp:** {loop_info["timestamp"]}
- **Status:** {loop_info["status"]}
- **Orchestrator:** {loop_info["orchestrator_persona"]}
- **Alignment Score:** {loop_info["alignment_score"]}
- **Drift Score:** {loop_info["drift_score"]}
- **Rerun Count:** {loop_info["rerun_count"]}

### Summary

{loop_info.get("summary", "No summary available.")}

## Transparency Metrics

- **Alignment Score:** {metrics["alignment_score"]}
- **Drift Score:** {metrics["drift_score"]}
- **Rerun Count:** {metrics["rerun_count"]}
- **Summary Integrity Score:** {metrics["summary_integrity_score"]}
"""
        
        # Add rerun information if available
        if "rerun_trigger" in loop_info:
            md += f"\n### Rerun Information\n\n- **Rerun Trigger:** {', '.join(loop_info['rerun_trigger'])}\n"
        
        if "rerun_reason" in loop_info:
            md += f"- **Rerun Reason:** {loop_info['rerun_reason']}\n"
        
        # Add belief drift information if available
        if "belief_drift" in loop_info:
            md += f"\n### Belief Drift\n\n"
            belief_drift = loop_info["belief_drift"]
            
            if "drift_detected" in belief_drift:
                md += f"- **Drift Detected:** {belief_drift['drift_detected']}\n"
            
            if "drift_score" in belief_drift:
                md += f"- **Drift Score:** {belief_drift['drift_score']}\n"
            
            if "drift_areas" in belief_drift:
                md += f"- **Drift Areas:** {', '.join(belief_drift['drift_areas'])}\n"
        
        content = md
        file_extension = "md"
    elif format_type.lower() == "html":
        # Create HTML version
        loop_info = report["loop_info"]
        metrics = report["transparency_metrics"]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transparency Report: {loop_id}</title>
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
        .metrics {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }}
        .metric {{
            flex-basis: 48%;
            margin-bottom: 15px;
            padding: 10px;
            background-color: #f0f7fb;
            border-radius: 5px;
        }}
        .metric-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #3498db;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>Transparency Report: {loop_id}</h1>
    
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
        <p>{loop_info.get("summary", "No summary available.")}</p>
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
        
        # Add belief drift information if available
        if "belief_drift" in loop_info:
            html += """
        <h3>Belief Drift</h3>
"""
            
            belief_drift = loop_info["belief_drift"]
            
            if "drift_detected" in belief_drift:
                html += f"""
        <div class="info-item">
            <span class="info-label">Drift Detected:</span> {belief_drift['drift_detected']}
        </div>
"""
            
            if "drift_score" in belief_drift:
                html += f"""
        <div class="info-item">
            <span class="info-label">Drift Score:</span> {belief_drift['drift_score']}
        </div>
"""
            
            if "drift_areas" in belief_drift:
                html += f"""
        <div class="info-item">
            <span class="info-label">Drift Areas:</span> {', '.join(belief_drift['drift_areas'])}
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="section">
        <h2>Transparency Metrics</h2>
        
        <div class="metrics">
            <div class="metric">
                <div class="info-label">Alignment Score</div>
                <div class="metric-value">{metrics["alignment_score"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">Drift Score</div>
                <div class="metric-value">{metrics["drift_score"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">Rerun Count</div>
                <div class="metric-value">{metrics["rerun_count"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">Summary Integrity Score</div>
                <div class="metric-value">{metrics["summary_integrity_score"]}</div>
            </div>
        </div>
    </div>
    
    <div class="timestamp">
        Generated on {report["report_timestamp"]}
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
    filename = f"transparency_{loop_id}_{timestamp}.{file_extension}"
    
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

async def generate_multiple_transparency_reports(loop_ids: List[str], format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Generate transparency reports for multiple loops.
    
    Args:
        loop_ids: List of loop IDs to generate reports for
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the files
        
    Returns:
        Dict with export results
    """
    results = {}
    
    for loop_id in loop_ids:
        result = await generate_transparency_report_to_file(loop_id, format_type, output_dir)
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

async def generate_audit_trail(loop_id: str) -> Dict[str, Any]:
    """
    Generate an audit trail for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with audit trail
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Extract key information
    loop_info = {
        "loop_id": loop_id,
        "timestamp": trace.get("timestamp", ""),
        "status": trace.get("status", ""),
        "orchestrator_persona": trace.get("orchestrator_persona", ""),
        "alignment_score": trace.get("alignment_score", 0.0),
        "drift_score": trace.get("drift_score", 0.0),
        "rerun_count": trace.get("rerun_count", 0)
    }
    
    # Create audit events
    audit_events = []
    
    # Add loop creation event
    audit_events.append({
        "event_type": "loop_created",
        "timestamp": trace.get("timestamp", ""),
        "details": {
            "orchestrator_persona": trace.get("orchestrator_persona", ""),
            "status": "created"
        }
    })
    
    # Add rerun events if available
    if trace.get("rerun_count", 0) > 0:
        for i in range(trace.get("rerun_count", 0)):
            audit_events.append({
                "event_type": "loop_rerun",
                "timestamp": trace.get("rerun_timestamp", trace.get("timestamp", "")),
                "details": {
                    "rerun_number": i + 1,
                    "rerun_trigger": trace.get("rerun_trigger", []),
                    "rerun_reason": trace.get("rerun_reason", "")
                }
            })
    
    # Add finalization event
    audit_events.append({
        "event_type": "loop_finalized",
        "timestamp": trace.get("finalized_timestamp", trace.get("timestamp", "")),
        "details": {
            "alignment_score": trace.get("alignment_score", 0.0),
            "drift_score": trace.get("drift_score", 0.0),
            "status": "finalized"
        }
    })
    
    # Add belief drift event if available
    if "belief_drift" in trace:
        audit_events.append({
            "event_type": "belief_drift_analysis",
            "timestamp": trace.get("belief_drift", {}).get("timestamp", trace.get("timestamp", "")),
            "details": {
                "drift_detected": trace.get("belief_drift", {}).get("drift_detected", False),
                "drift_score": trace.get("belief_drift", {}).get("drift_score", 0.0),
                "drift_areas": trace.get("belief_drift", {}).get("drift_areas", [])
            }
        })
    
    # Add summary validation event if available
    if "summary_validation" in trace:
        audit_events.append({
            "event_type": "summary_validation",
            "timestamp": trace.get("summary_validation", {}).get("timestamp", trace.get("timestamp", "")),
            "details": {
                "summary_integrity_score": trace.get("summary_validation", {}).get("summary_integrity_score", 0.0),
                "validation_status": trace.get("summary_validation", {}).get("validation_status", ""),
                "summary_warning": trace.get("summary_validation", {}).get("summary_warning", None)
            }
        })
    
    # Add symbolic memory encoding event if available
    if "symbolic_memory_encoding" in trace:
        audit_events.append({
            "event_type": "symbolic_memory_encoding",
            "timestamp": trace.get("symbolic_memory_encoding", {}).get("timestamp", trace.get("timestamp", "")),
            "details": {
                "concepts_encoded": trace.get("symbolic_memory_encoding", {}).get("concepts_encoded", 0),
                "relationships_encoded": trace.get("symbolic_memory_encoding", {}).get("relationships_encoded", 0),
                "insights_encoded": trace.get("symbolic_memory_encoding", {}).get("insights_encoded", 0)
            }
        })
    
    # Sort audit events by timestamp
    audit_events.sort(key=lambda x: x["timestamp"])
    
    # Create audit trail
    audit_trail = {
        "loop_id": loop_id,
        "audit_trail_version": "1.0",
        "audit_trail_timestamp": datetime.utcnow().isoformat(),
        "loop_info": loop_info,
        "audit_events": audit_events
    }
    
    return audit_trail

async def generate_audit_trail_to_file(loop_id: str, format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Generate an audit trail for a loop and save it to a file.
    
    Args:
        loop_id: The ID of the loop
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the file
        
    Returns:
        Dict with export result
    """
    # Generate the audit trail
    audit_trail = await generate_audit_trail(loop_id)
    if "error" in audit_trail:
        return {
            "success": False,
            "error": audit_trail["error"],
            "loop_id": loop_id
        }
    
    # Format the audit trail
    if format_type.lower() == "json":
        content = json.dumps(audit_trail, indent=2)
        file_extension = "json"
    elif format_type.lower() == "md":
        # Create Markdown version
        loop_info = audit_trail["loop_info"]
        audit_events = audit_trail["audit_events"]
        
        md = f"""
# Audit Trail: {loop_id}

*Generated on {audit_trail["audit_trail_timestamp"]}*

## Loop Information

- **Loop ID:** {loop_id}
- **Timestamp:** {loop_info["timestamp"]}
- **Status:** {loop_info["status"]}
- **Orchestrator:** {loop_info["orchestrator_persona"]}
- **Alignment Score:** {loop_info["alignment_score"]}
- **Drift Score:** {loop_info["drift_score"]}
- **Rerun Count:** {loop_info["rerun_count"]}

## Audit Events

"""
        
        for i, event in enumerate(audit_events):
            md += f"### Event {i+1}: {event['event_type']}\n\n"
            md += f"- **Timestamp:** {event['timestamp']}\n"
            
            for key, value in event["details"].items():
                md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            
            md += "\n"
        
        content = md
        file_extension = "md"
    elif format_type.lower() == "html":
        # Create HTML version
        loop_info = audit_trail["loop_info"]
        audit_events = audit_trail["audit_events"]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Trail: {loop_id}</title>
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
        .event {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f0f7fb;
        }}
        .event-header {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            color: #3498db;
        }}
        .event-timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .event-details {{
            margin-left: 15px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>Audit Trail: {loop_id}</h1>
    
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
    </div>
    
    <div class="section">
        <h2>Audit Events</h2>
"""
        
        for i, event in enumerate(audit_events):
            html += f"""
        <div class="event">
            <div class="event-header">Event {i+1}: {event['event_type']}</div>
            <div class="event-timestamp">Timestamp: {event['timestamp']}</div>
            <div class="event-details">
"""
            
            for key, value in event["details"].items():
                html += f"""
                <div class="info-item">
                    <span class="info-label">{key.replace('_', ' ').title()}:</span> {value}
                </div>
"""
            
            html += """
            </div>
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="timestamp">
        Generated on {audit_trail["audit_trail_timestamp"]}
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
    filename = f"audit_trail_{loop_id}_{timestamp}.{file_extension}"
    
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

async def inject_explanation_into_loop_trace(loop_id: str, decision_type: str) -> bool:
    """
    Inject decision explanation into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        decision_type: The type of decision to explain
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Generate the decision explanation
    explanation = await generate_decision_explanation(loop_id, decision_type)
    if "error" in explanation:
        return False
    
    # Update the trace with the decision explanation
    if "decision_explanations" not in trace:
        trace["decision_explanations"] = {}
    
    trace["decision_explanations"][decision_type] = explanation
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True

async def generate_decision_explanation(loop_id: str, decision_type: str) -> Dict[str, Any]:
    """
    Generate an explanation for a decision made in a loop.
    
    Args:
        loop_id: The ID of the loop
        decision_type: The type of decision to explain (e.g., "rerun", "alignment", "drift")
        
    Returns:
        Dict with decision explanation
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Initialize explanation
    explanation = {
        "loop_id": loop_id,
        "decision_type": decision_type,
        "timestamp": datetime.utcnow().isoformat(),
        "explanation": "",
        "factors": {},
        "confidence": 0.0
    }
    
    # Generate explanation based on decision type
    if decision_type == "rerun":
        # Check if loop was rerun
        rerun_count = trace.get("rerun_count", 0)
        rerun_trigger = trace.get("rerun_trigger", [])
        rerun_reason = trace.get("rerun_reason", "")
        
        if rerun_count > 0:
            explanation["explanation"] = f"Loop {loop_id} was rerun {rerun_count} time(s) due to {', '.join(rerun_trigger)}. The specific reason was: {rerun_reason}."
            explanation["factors"] = {
                "rerun_count": rerun_count,
                "rerun_trigger": rerun_trigger,
                "rerun_reason": rerun_reason
            }
            explanation["confidence"] = 0.95
        else:
            explanation["explanation"] = f"Loop {loop_id} was not rerun. The initial execution was deemed sufficient."
            explanation["factors"] = {
                "rerun_count": 0
            }
            explanation["confidence"] = 0.9
    
    elif decision_type == "alignment":
        # Explain alignment score
        alignment_score = trace.get("alignment_score", 0.0)
        
        if alignment_score >= 0.8:
            explanation["explanation"] = f"Loop {loop_id} achieved high alignment (score: {alignment_score}), indicating strong adherence to core beliefs and objectives."
            explanation["confidence"] = 0.9
        elif alignment_score >= 0.6:
            explanation["explanation"] = f"Loop {loop_id} achieved moderate alignment (score: {alignment_score}), with some minor deviations from core beliefs and objectives."
            explanation["confidence"] = 0.8
        else:
            explanation["explanation"] = f"Loop {loop_id} achieved low alignment (score: {alignment_score}), indicating significant deviations from core beliefs and objectives."
            explanation["confidence"] = 0.7
        
        explanation["factors"] = {
            "alignment_score": alignment_score,
            "threshold_high": 0.8,
            "threshold_moderate": 0.6
        }
    
    elif decision_type == "drift":
        # Explain drift score
        drift_score = trace.get("drift_score", 0.0)
        
        if "belief_drift" in trace:
            belief_drift = trace["belief_drift"]
            drift_detected = belief_drift.get("drift_detected", False)
            drift_areas = belief_drift.get("drift_areas", [])
            
            if drift_detected:
                explanation["explanation"] = f"Loop {loop_id} exhibited belief drift (score: {drift_score}) in the following areas: {', '.join(drift_areas)}."
                explanation["confidence"] = 0.85
            else:
                explanation["explanation"] = f"Loop {loop_id} maintained belief consistency with minimal drift (score: {drift_score})."
                explanation["confidence"] = 0.9
            
            explanation["factors"] = {
                "drift_score": drift_score,
                "drift_detected": drift_detected,
                "drift_areas": drift_areas
            }
        else:
            if drift_score > 0.3:
                explanation["explanation"] = f"Loop {loop_id} exhibited significant belief drift (score: {drift_score})."
                explanation["confidence"] = 0.7
            else:
                explanation["explanation"] = f"Loop {loop_id} maintained belief consistency with minimal drift (score: {drift_score})."
                explanation["confidence"] = 0.8
            
            explanation["factors"] = {
                "drift_score": drift_score,
                "threshold": 0.3
            }
    
    elif decision_type == "summary":
        # Explain summary validation
        if "summary_validation" in trace:
            validation = trace["summary_validation"]
            integrity_score = validation.get("summary_integrity_score", 0.0)
            validation_status = validation.get("validation_status", "")
            
            if validation_status == "valid":
                explanation["explanation"] = f"Loop {loop_id} summary was validated as high quality (integrity score: {integrity_score})."
                explanation["confidence"] = 0.95
            elif validation_status == "acceptable":
                explanation["explanation"] = f"Loop {loop_id} summary was validated as acceptable quality (integrity score: {integrity_score}) with minor issues."
                explanation["confidence"] = 0.85
            elif validation_status == "questionable":
                explanation["explanation"] = f"Loop {loop_id} summary was validated as questionable quality (integrity score: {integrity_score}) with moderate issues."
                explanation["confidence"] = 0.7
            else:
                explanation["explanation"] = f"Loop {loop_id} summary was validated as low quality (integrity score: {integrity_score}) with significant issues."
                explanation["confidence"] = 0.6
            
            explanation["factors"] = {
                "summary_integrity_score": integrity_score,
                "validation_status": validation_status,
                "issues": validation.get("issues_detected", [])
            }
        else:
            explanation["explanation"] = f"Loop {loop_id} summary has not been validated."
            explanation["confidence"] = 0.5
            explanation["factors"] = {}
    
    else:
        explanation["explanation"] = f"Unknown decision type: {decision_type}"
        explanation["confidence"] = 0.1
    
    return explanation

async def inject_transparency_report_into_loop_trace(loop_id: str) -> bool:
    """
    Inject transparency report into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Generate the transparency report
    report = await generate_transparency_report(loop_id)
    if "error" in report:
        return False
    
    # Update the trace with the transparency report
    trace["transparency_report"] = report
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True

async def generate_system_transparency_report() -> Dict[str, Any]:
    """
    Generate a system-wide transparency report.
    
    Returns:
        Dict with system transparency report
    """
    # Get current timestamp
    timestamp = datetime.utcnow().isoformat()
    
    # Initialize system metrics
    system_metrics = {
        "total_loops": 0,
        "finalized_loops": 0,
        "rerun_loops": 0,
        "average_alignment_score": 0.0,
        "average_drift_score": 0.0,
        "high_alignment_loops": 0,
        "high_drift_loops": 0
    }
    
    # Mock data for testing
    # In a real implementation, this would query all loops from a database
    loop_ids = ["loop_001", "loop_002"]
    
    # Process each loop
    loop_data = []
    alignment_scores = []
    drift_scores = []
    
    for loop_id in loop_ids:
        trace = await get_loop_trace(loop_id)
        if "error" in trace:
            continue
        
        system_metrics["total_loops"] += 1
        
        if trace.get("status", "") == "finalized":
            system_metrics["finalized_loops"] += 1
        
        if trace.get("rerun_count", 0) > 0:
            system_metrics["rerun_loops"] += 1
        
        alignment_score = trace.get("alignment_score", 0.0)
        drift_score = trace.get("drift_score", 0.0)
        
        alignment_scores.append(alignment_score)
        drift_scores.append(drift_score)
        
        if alignment_score >= 0.8:
            system_metrics["high_alignment_loops"] += 1
        
        if drift_score >= 0.3:
            system_metrics["high_drift_loops"] += 1
        
        # Add sanitized loop data
        sanitized_trace = sanitize_sensitive_information(trace)
        loop_data.append({
            "loop_id": loop_id,
            "timestamp": sanitized_trace.get("timestamp", ""),
            "status": sanitized_trace.get("status", ""),
            "orchestrator_persona": sanitized_trace.get("orchestrator_persona", ""),
            "alignment_score": alignment_score,
            "drift_score": drift_score,
            "rerun_count": sanitized_trace.get("rerun_count", 0)
        })
    
    # Calculate averages
    if alignment_scores:
        system_metrics["average_alignment_score"] = sum(alignment_scores) / len(alignment_scores)
    
    if drift_scores:
        system_metrics["average_drift_score"] = sum(drift_scores) / len(drift_scores)
    
    # Create system transparency report
    report = {
        "report_type": "system_transparency_report",
        "report_version": "1.0",
        "report_timestamp": timestamp,
        "timestamp": timestamp,
        "system_metrics": system_metrics,
        "loop_data": loop_data,
        "agent_trust_scores": {
            "SAGE": 0.78,
            "NOVA": 0.82,
            "CRITIC": 0.75,
            "CEO": 0.81,
            "HAL": 0.79,
            "PESSIMIST": 0.73
        }
    }
    
    return report

async def save_system_transparency_report(format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Generate a system-wide transparency report and save it to a file.
    
    Args:
        format_type: The format to export as ("json", "md", or "html")
        output_dir: Directory to save the file
        
    Returns:
        Dict with export result
    """
    # Generate the system transparency report
    report = await generate_system_transparency_report()
    
    # Format the report
    if format_type.lower() == "json":
        content = json.dumps(report, indent=2)
        file_extension = "json"
    elif format_type.lower() == "md":
        # Create Markdown version
        system_metrics = report["system_metrics"]
        loop_data = report["loop_data"]
        
        md = f"""
# System Transparency Report

*Generated on {report["report_timestamp"]}*

## System Metrics

- **Total Loops:** {system_metrics["total_loops"]}
- **Finalized Loops:** {system_metrics["finalized_loops"]}
- **Rerun Loops:** {system_metrics["rerun_loops"]}
- **Average Alignment Score:** {system_metrics["average_alignment_score"]:.2f}
- **Average Drift Score:** {system_metrics["average_drift_score"]:.2f}
- **High Alignment Loops:** {system_metrics["high_alignment_loops"]}
- **High Drift Loops:** {system_metrics["high_drift_loops"]}

## Loop Data

"""
        
        for i, loop in enumerate(loop_data):
            md += f"### Loop {i+1}: {loop['loop_id']}\n\n"
            md += f"- **Timestamp:** {loop['timestamp']}\n"
            md += f"- **Status:** {loop['status']}\n"
            md += f"- **Orchestrator:** {loop['orchestrator_persona']}\n"
            md += f"- **Alignment Score:** {loop['alignment_score']}\n"
            md += f"- **Drift Score:** {loop['drift_score']}\n"
            md += f"- **Rerun Count:** {loop['rerun_count']}\n\n"
        
        content = md
        file_extension = "md"
    elif format_type.lower() == "html":
        # Create HTML version
        system_metrics = report["system_metrics"]
        loop_data = report["loop_data"]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Transparency Report</title>
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
        .metrics {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }}
        .metric {{
            flex-basis: 48%;
            margin-bottom: 15px;
            padding: 10px;
            background-color: #f0f7fb;
            border-radius: 5px;
        }}
        .metric-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #3498db;
        }}
        .loop {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f0f7fb;
        }}
        .loop-header {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            color: #3498db;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>System Transparency Report</h1>
    
    <div class="section">
        <h2>System Metrics</h2>
        
        <div class="metrics">
            <div class="metric">
                <div class="info-label">Total Loops</div>
                <div class="metric-value">{system_metrics["total_loops"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">Finalized Loops</div>
                <div class="metric-value">{system_metrics["finalized_loops"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">Rerun Loops</div>
                <div class="metric-value">{system_metrics["rerun_loops"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">Average Alignment Score</div>
                <div class="metric-value">{system_metrics["average_alignment_score"]:.2f}</div>
            </div>
            <div class="metric">
                <div class="info-label">Average Drift Score</div>
                <div class="metric-value">{system_metrics["average_drift_score"]:.2f}</div>
            </div>
            <div class="metric">
                <div class="info-label">High Alignment Loops</div>
                <div class="metric-value">{system_metrics["high_alignment_loops"]}</div>
            </div>
            <div class="metric">
                <div class="info-label">High Drift Loops</div>
                <div class="metric-value">{system_metrics["high_drift_loops"]}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Loop Data</h2>
"""
        
        for i, loop in enumerate(loop_data):
            html += f"""
        <div class="loop">
            <div class="loop-header">Loop {i+1}: {loop['loop_id']}</div>
            <div class="info-item">
                <span class="info-label">Timestamp:</span> {loop['timestamp']}
            </div>
            <div class="info-item">
                <span class="info-label">Status:</span> {loop['status']}
            </div>
            <div class="info-item">
                <span class="info-label">Orchestrator:</span> {loop['orchestrator_persona']}
            </div>
            <div class="info-item">
                <span class="info-label">Alignment Score:</span> {loop['alignment_score']}
            </div>
            <div class="info-item">
                <span class="info-label">Drift Score:</span> {loop['drift_score']}
            </div>
            <div class="info-item">
                <span class="info-label">Rerun Count:</span> {loop['rerun_count']}
            </div>
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="timestamp">
        Generated on {report["report_timestamp"]}
    </div>
</body>
</html>
"""
        
        content = html
        file_extension = "html"
    else:
        return {
            "success": False,
            "error": f"Unsupported format: {format_type}"
        }
    
    # Create a timestamp for the filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Create the filename
    filename = f"system_transparency_report_{timestamp}.{file_extension}"
    
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
            "format": format_type,
            "file_path": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write file: {str(e)}"
        }

async def generate_decision_explanation(loop_id: str, decision_type: str = "rerun") -> Dict[str, Any]:
    """
    Generate an explanation for a decision made in a loop.
    
    Args:
        loop_id: The ID of the loop
        decision_type: The type of decision to explain (e.g., "rerun", "alignment", "drift")
        
    Returns:
        Dict with explanation
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id,
            "success": False
        }
    
    # Initialize explanation
    explanation = {
        "loop_id": loop_id,
        "decision_type": decision_type,
        "timestamp": datetime.utcnow().isoformat(),
        "explanation_text": "",
        "factors": {},
        "success": True,
        "explanation": {
            "basic_explanation": "",
            "detailed_factors": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Generate explanation based on decision type
    if decision_type == "rerun":
        rerun_count = trace.get("rerun_count", 0)
        rerun_reason = trace.get("rerun_reason", "")
        rerun_trigger = trace.get("rerun_trigger", [])
        
        explanation["factors"] = {
            "rerun_count": rerun_count,
            "rerun_reason": rerun_reason,
            "rerun_trigger": rerun_trigger
        }
        
        if rerun_reason == "alignment_threshold_not_met":
            explanation["explanation_text"] = f"Loop {loop_id} was rerun because the alignment score did not meet the required threshold. This was rerun attempt #{rerun_count}."
        elif rerun_reason == "drift_threshold_exceeded":
            explanation["explanation_text"] = f"Loop {loop_id} was rerun because the drift score exceeded the acceptable threshold. This was rerun attempt #{rerun_count}."
        elif rerun_reason == "validation_failed":
            explanation["explanation_text"] = f"Loop {loop_id} was rerun because the summary validation failed. This was rerun attempt #{rerun_count}."
        else:
            explanation["explanation_text"] = f"Loop {loop_id} was rerun for the following reason: {rerun_reason}. This was rerun attempt #{rerun_count}."
    
    elif decision_type == "alignment":
        alignment_score = trace.get("alignment_score", 0.0)
        threshold = 0.75  # Example threshold
        
        explanation["factors"] = {
            "alignment_score": alignment_score,
            "threshold": threshold,
            "meets_threshold": alignment_score >= threshold
        }
        
        if alignment_score >= threshold:
            explanation["explanation_text"] = f"Loop {loop_id} has an alignment score of {alignment_score}, which meets the required threshold of {threshold}."
        else:
            explanation["explanation_text"] = f"Loop {loop_id} has an alignment score of {alignment_score}, which does not meet the required threshold of {threshold}."
    
    elif decision_type == "drift":
        drift_score = trace.get("drift_score", 0.0)
        threshold = 0.25  # Example threshold
        
        explanation["factors"] = {
            "drift_score": drift_score,
            "threshold": threshold,
            "exceeds_threshold": drift_score > threshold
        }
        
        if drift_score > threshold:
            explanation["explanation_text"] = f"Loop {loop_id} has a drift score of {drift_score}, which exceeds the acceptable threshold of {threshold}."
        else:
            explanation["explanation_text"] = f"Loop {loop_id} has a drift score of {drift_score}, which is within the acceptable threshold of {threshold}."
    
    else:
        explanation["explanation_text"] = f"No explanation available for decision type '{decision_type}' in loop {loop_id}."
        explanation["success"] = False
    
    return explanation

async def inject_explanation_into_loop_trace(loop_id: str, decision_type: str = "rerun") -> Dict[str, Any]:
    """
    Inject a decision explanation into a loop trace.
    
    Args:
        loop_id: The ID of the loop
        decision_type: The type of decision to explain
        
    Returns:
        Dict with injection result
    """
    # Generate explanation
    explanation = await generate_decision_explanation(loop_id, decision_type)
    if "error" in explanation:
        return explanation
    
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id,
            "success": False
        }
    
    # Add explanation to trace
    if "explanations" not in trace:
        trace["explanations"] = {}
    
    trace["explanations"][decision_type] = {
        "timestamp": explanation["timestamp"],
        "explanation_text": explanation["explanation_text"],
        "factors": explanation["factors"]
    }
    
    # Write updated trace to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return {
        "loop_id": loop_id,
        "decision_type": decision_type,
        "explanation_injected": True,
        "success": True
    }
