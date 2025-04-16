"""
Tool Availability Checker for the System Integration Validator Agent.

This module scans the /app/tools/ directory to verify all expected tools are present.
"""

import os
import json
from typing import Dict, List, Any

def check_tool_availability() -> Dict[str, Any]:
    """
    Scan the /app/tools/ directory for expected modules based on the Day 3 build list.
    
    Returns:
        Dictionary containing validation results
    """
    # Define expected tools based on Day 3 build list
    expected_tools = [
        # Knowledge & Research
        "web_search.py",
        "news_fetcher.py",
        "url_summarizer.py",
        "pdf_ingest.py",
        "api_request.py",
        
        # Code & Execution
        "code_executor.py",
        "github_commit.py",
        "code_explainer.py",
        
        # Document / Spreadsheet
        "notion_writer.py",
        "spreadsheet_analyzer.py",
        "resume_parser.py",
        
        # Real-World Awareness
        "weather_checker.py",
        "stock_checker.py",
        "event_tracker.py",
        "calendar_scheduler.py",
        
        # Media Understanding
        "image_caption.py",
        "screenshot_reader.py",
        "audio_transcriber.py",
        "video_summarizer.py",
        
        # Communication & Language
        "email_drafter.py",
        "slack_messenger.py",
        "tone_converter.py",
        "pitch_optimizer.py",
        
        # Meta Agents
        "autonomous_research_chain.py",
        "agent_builder.py",
        "belief_calibrator.py",
        "multi_agent_debater.py"
    ]
    
    # Get the absolute path to the tools directory
    tools_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "app", "tools"
    ))
    
    # Get list of actual tool files
    actual_tools = [f for f in os.listdir(tools_dir) if f.endswith('.py') and not f.startswith('__')]
    
    # Find missing tools
    missing_tools = [tool for tool in expected_tools if tool not in actual_tools]
    
    # Find unexpected tools (might be misnamed)
    unexpected_tools = [tool for tool in actual_tools if tool not in expected_tools]
    
    # Prepare result
    result = {
        "check_name": "Tool Availability Check",
        "success": len(missing_tools) == 0,
        "expected_tool_count": len(expected_tools),
        "actual_tool_count": len(actual_tools),
        "missing_tools": missing_tools,
        "unexpected_tools": unexpected_tools,
        "details": {
            "expected_tools": expected_tools,
            "actual_tools": actual_tools
        }
    }
    
    # Add recommendations if there are issues
    if not result["success"]:
        recommendations = []
        
        if missing_tools:
            recommendations.append(f"Implement the missing tools: {', '.join(missing_tools)}")
        
        if unexpected_tools:
            recommendations.append(f"Check if these unexpected tools are misnamed or additional: {', '.join(unexpected_tools)}")
        
        result["recommendations"] = recommendations
    
    return result

if __name__ == "__main__":
    # Run the check directly if this script is executed
    result = check_tool_availability()
    print(json.dumps(result, indent=2))
