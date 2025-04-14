"""
Autonomous Research Chain Tool for the Personal AI Agent System.

This module provides functionality to execute multi-step research processes
autonomously, chaining together multiple tools and reasoning steps.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger("autonomous_research_chain")

def run(
    research_question: str,
    depth: int = 2,
    max_sources: int = 5,
    max_steps: int = 10,
    focus_areas: List[str] = None,
    required_tools: List[str] = None,
    excluded_tools: List[str] = None,
    time_limit_minutes: int = 30,
    include_reasoning: bool = True,
    include_source_links: bool = True,
    format_output: str = "markdown",
    store_memory: bool = True,
    memory_manager = None,
    memory_tags: List[str] = ["research", "autonomous"],
    memory_scope: str = "global"
) -> Dict[str, Any]:
    """
    Execute an autonomous multi-step research process.
    
    Args:
        research_question: The main research question to investigate
        depth: Depth of research (1=basic, 2=standard, 3=comprehensive)
        max_sources: Maximum number of sources to consult
        max_steps: Maximum number of reasoning/tool steps to execute
        focus_areas: Specific areas to focus on within the research question
        required_tools: Specific tools that must be used in the research
        excluded_tools: Tools that should not be used in the research
        time_limit_minutes: Maximum time to spend on research
        include_reasoning: Whether to include reasoning steps in output
        include_source_links: Whether to include source links in output
        format_output: Output format (markdown, json, text)
        store_memory: Whether to store research results in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing research results and metadata
    """
    logger.info(f"Starting autonomous research on: {research_question}")
    
    try:
        # Initialize research state
        research_state = {
            "question": research_question,
            "start_time": time.time(),
            "steps_taken": 0,
            "sources_consulted": 0,
            "current_findings": {},
            "completed_steps": [],
            "planned_steps": [],
            "tools_used": [],
            "focus_areas": focus_areas or [],
            "depth": depth,
            "max_steps": max_steps,
            "max_sources": max_sources,
            "time_limit_minutes": time_limit_minutes
        }
        
        # Plan initial research steps
        research_state = _plan_research_steps(research_state, required_tools, excluded_tools)
        
        # Execute research steps
        research_state = _execute_research_plan(research_state)
        
        # Synthesize findings
        synthesis = _synthesize_findings(research_state, include_reasoning, include_source_links)
        
        # Format output
        formatted_output = _format_research_output(synthesis, format_output)
        
        # Calculate research statistics
        research_stats = _calculate_research_stats(research_state)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the research results
                memory_entry = {
                    "type": "research_results",
                    "question": research_question,
                    "summary": synthesis["summary"][:500] + ("..." if len(synthesis["summary"]) > 500 else ""),
                    "sources_count": research_state["sources_consulted"],
                    "steps_count": research_state["steps_taken"],
                    "tools_used": research_state["tools_used"],
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ["research_question", "autonomous_research"]
                )
                
                # Also store individual key findings with their own tags
                for area, findings in synthesis["findings_by_area"].items():
                    area_tag = area.lower().replace(" ", "_")
                    memory_manager.add_memory(
                        content=json.dumps({
                            "type": "research_finding",
                            "question": research_question,
                            "area": area,
                            "findings": findings,
                            "timestamp": datetime.now().isoformat()
                        }),
                        scope=memory_scope,
                        tags=memory_tags + [area_tag, "finding"]
                    )
                
                logger.info(f"Stored research results in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store research results in memory: {str(e)}")
        
        # Prepare response
        response = {
            "success": True,
            "research_question": research_question,
            "formatted_output": formatted_output,
            "summary": synthesis["summary"],
            "key_findings": synthesis["key_findings"],
            "findings_by_area": synthesis["findings_by_area"],
            "sources": synthesis["sources"] if include_source_links else [],
            "stats": research_stats
        }
        
        # Include reasoning steps if requested
        if include_reasoning:
            response["reasoning_steps"] = synthesis["reasoning_steps"]
        
        return response
    except Exception as e:
        error_msg = f"Error in autonomous research: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "research_question": research_question,
            "partial_results": research_state.get("current_findings", {})
        }

def _plan_research_steps(
    research_state: Dict[str, Any],
    required_tools: List[str],
    excluded_tools: List[str]
) -> Dict[str, Any]:
    """
    Plan the steps for the research process.
    
    Args:
        research_state: Current research state
        required_tools: Tools that must be used
        excluded_tools: Tools that should not be used
        
    Returns:
        Updated research state with planned steps
    """
    # In a real implementation, this would use LLM to plan research steps
    # For this example, we'll use a template-based approach
    
    question = research_state["question"]
    depth = research_state["depth"]
    focus_areas = research_state["focus_areas"]
    
    # Default research plan based on depth
    if depth == 1:  # Basic research
        planned_steps = [
            {"type": "tool", "name": "web_search", "params": {"query": question, "num_results": 3}},
            {"type": "reasoning", "name": "initial_analysis", "description": "Analyze search results"},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 3}},
            {"type": "reasoning", "name": "synthesis", "description": "Synthesize findings"}
        ]
    elif depth == 2:  # Standard research
        planned_steps = [
            {"type": "tool", "name": "web_search", "params": {"query": question, "num_results": 5}},
            {"type": "reasoning", "name": "initial_analysis", "description": "Analyze search results"},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 5}},
            {"type": "reasoning", "name": "identify_gaps", "description": "Identify information gaps"},
            {"type": "tool", "name": "web_search", "params": {"query": "<refined_from_gaps>", "num_results": 3}},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 3}},
            {"type": "reasoning", "name": "synthesis", "description": "Synthesize all findings"}
        ]
    else:  # Comprehensive research
        planned_steps = [
            {"type": "tool", "name": "web_search", "params": {"query": question, "num_results": 5}},
            {"type": "reasoning", "name": "initial_analysis", "description": "Analyze search results"},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 5}},
            {"type": "reasoning", "name": "identify_subtopics", "description": "Identify key subtopics"},
            {"type": "tool", "name": "web_search", "params": {"query": "<subtopic_1>", "num_results": 3}},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 3}},
            {"type": "tool", "name": "web_search", "params": {"query": "<subtopic_2>", "num_results": 3}},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 3}},
            {"type": "reasoning", "name": "identify_gaps", "description": "Identify remaining information gaps"},
            {"type": "tool", "name": "web_search", "params": {"query": "<refined_from_gaps>", "num_results": 3}},
            {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 3}},
            {"type": "reasoning", "name": "synthesis", "description": "Synthesize all findings"},
            {"type": "reasoning", "name": "critical_analysis", "description": "Critically analyze findings"}
        ]
    
    # Add focus area specific steps if provided
    if focus_areas:
        for area in focus_areas:
            # Insert focus area research after initial analysis
            initial_analysis_index = next((i for i, step in enumerate(planned_steps) 
                                         if step["type"] == "reasoning" and step["name"] == "initial_analysis"), 1)
            
            focus_steps = [
                {"type": "tool", "name": "web_search", "params": {"query": f"{question} {area}", "num_results": 3}},
                {"type": "tool", "name": "url_summarizer", "params": {"urls": "<from_previous_step>", "max_urls": 3}},
                {"type": "reasoning", "name": f"analyze_{area.lower().replace(' ', '_')}", 
                 "description": f"Analyze findings about {area}"}
            ]
            
            # Insert focus steps after initial analysis
            for i, step in enumerate(focus_steps):
                planned_steps.insert(initial_analysis_index + 1 + i, step)
    
    # Add required tools if specified
    if required_tools:
        for tool in required_tools:
            if not any(step["name"] == tool for step in planned_steps if step["type"] == "tool"):
                # Add tool step before final synthesis
                synthesis_index = next((i for i, step in enumerate(planned_steps) 
                                      if step["type"] == "reasoning" and step["name"] == "synthesis"), -1)
                
                planned_steps.insert(synthesis_index, 
                                    {"type": "tool", "name": tool, "params": {"query": question}})
    
    # Remove excluded tools if specified
    if excluded_tools:
        planned_steps = [step for step in planned_steps 
                        if not (step["type"] == "tool" and step["name"] in excluded_tools)]
    
    # Ensure we don't exceed max steps
    if len(planned_steps) > research_state["max_steps"]:
        # Prioritize initial search, key tool steps, and final synthesis
        essential_indices = [0]  # Initial search
        
        # Find synthesis step
        synthesis_index = next((i for i, step in enumerate(planned_steps) 
                              if step["type"] == "reasoning" and step["name"] == "synthesis"), -1)
        
        if synthesis_index != -1:
            essential_indices.append(synthesis_index)
        
        # Add required tool steps
        if required_tools:
            for tool in required_tools:
                tool_index = next((i for i, step in enumerate(planned_steps) 
                                 if step["type"] == "tool" and step["name"] == tool), -1)
                if tool_index != -1:
                    essential_indices.append(tool_index)
        
        # Add some steps in between to reach max_steps
        remaining_slots = research_state["max_steps"] - len(essential_indices)
        if remaining_slots > 0:
            # Get indices that are not already in essential_indices
            non_essential_indices = [i for i in range(len(planned_steps)) if i not in essential_indices]
            
            # Select evenly distributed indices
            step_size = len(non_essential_indices) / (remaining_slots + 1)
            selected_indices = [non_essential_indices[int(i * step_size)] for i in range(1, remaining_slots + 1)]
            
            essential_indices.extend(selected_indices)
            essential_indices.sort()
        
        # Keep only the essential steps
        planned_steps = [planned_steps[i] for i in essential_indices]
    
    # Update research state
    research_state["planned_steps"] = planned_steps
    
    return research_state

def _execute_research_plan(research_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the planned research steps.
    
    Args:
        research_state: Current research state with planned steps
        
    Returns:
        Updated research state with results
    """
    # In a real implementation, this would execute actual tools and reasoning
    # For this example, we'll simulate the execution
    
    start_time = research_state["start_time"]
    max_time_seconds = research_state["time_limit_minutes"] * 60
    
    # Initialize findings structure
    findings = {
        "general": [],
        "sources": []
    }
    
    # Add focus areas to findings structure
    for area in research_state["focus_areas"]:
        findings[area] = []
    
    # Execute each planned step
    for step_index, step in enumerate(research_state["planned_steps"]):
        # Check if we've exceeded time limit
        current_time = time.time()
        if current_time - start_time > max_time_seconds:
            logger.info(f"Time limit reached after {step_index} steps")
            break
        
        # Check if we've exceeded max steps
        if research_state["steps_taken"] >= research_state["max_steps"]:
            logger.info(f"Max steps reached ({research_state['max_steps']})")
            break
        
        # Execute step based on type
        if step["type"] == "tool":
            # Simulate tool execution
            result = _simulate_tool_execution(step, research_state)
            
            # Update sources count if applicable
            if step["name"] in ["web_search", "url_summarizer", "pdf_ingest"]:
                if "sources" in result:
                    research_state["sources_consulted"] += len(result["sources"])
                    
                    # Add sources to findings
                    for source in result["sources"]:
                        if source not in findings["sources"]:
                            findings["sources"].append(source)
            
            # Add tool to tools used if not already present
            if step["name"] not in research_state["tools_used"]:
                research_state["tools_used"].append(step["name"])
            
            # Check if we've exceeded max sources
            if research_state["sources_consulted"] >= research_state["max_sources"]:
                logger.info(f"Max sources reached ({research_state['max_sources']})")
                # Skip further search/summarization steps, but continue with reasoning
                research_state["planned_steps"] = [s for s in research_state["planned_steps"][step_index+1:] 
                                                if s["type"] != "tool" or s["name"] not in ["web_search", "url_summarizer", "pdf_ingest"]]
        else:  # Reasoning step
            # Simulate reasoning
            result = _simulate_reasoning(step, research_state)
        
        # Update findings based on step result
        if "findings" in result:
            # Determine which category to add findings to
            category = "general"
            
            # Check if this is a focus area specific step
            if step["type"] == "reasoning" and step["name"].startswith("analyze_"):
                area_key = step["name"].replace("analyze_", "").replace("_", " ")
                if area_key in findings:
                    category = area_key
                else:
                    # Find closest matching focus area
                    for area in research_state["focus_areas"]:
                        if area.lower().replace(" ", "_") in step["name"]:
                            category = area
                            break
            
            # Add findings to appropriate category
            findings[category].extend(result["findings"])
        
        # Add completed step to research state
        completed_step = {
            "type": step["type"],
            "name": step["name"],
            "result_summary": result.get("summary", "No summary available")
        }
        
        research_state["completed_steps"].append(completed_step)
        research_state["steps_taken"] += 1
    
    # Update research state with findings
    research_state["current_findings"] = findings
    
    return research_state

def _simulate_tool_execution(step: Dict[str, Any], research_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate the execution of a tool step.
    
    Args:
        step: Tool step to execute
        research_state: Current research state
        
    Returns:
        Simulated tool result
    """
    # In a real implementation, this would call actual tools
    # For this example, we'll return simulated results
    
    tool_name = step["name"]
    
    if tool_name == "web_search":
        return {
            "summary": f"Performed web search for '{step['params'].get('query', 'unknown query')}'",
            "sources": [
                {"url": "https://example.com/article1", "title": "Example Article 1"},
                {"url": "https://example.com/article2", "title": "Example Article 2"},
                {"url": "https://example.com/article3", "title": "Example Article 3"}
            ],
            "findings": [
                f"Finding 1 from web search about {step['params'].get('query', 'unknown')}",
                f"Finding 2 from web search about {step['params'].get('query', 'unknown')}",
                f"Finding 3 from web search about {step['params'].get('query', 'unknown')}"
            ]
        }
    elif tool_name == "url_summarizer":
        return {
            "summary": "Summarized content from URLs",
            "sources": [
                {"url": "https://example.com/article1", "title": "Example Article 1"}
            ],
            "findings": [
                "Finding 1 from URL summarization",
                "Finding 2 from URL summarization",
                "Finding 3 from URL summarization"
            ]
        }
    elif tool_name == "pdf_ingest":
        return {
            "summary": "Extracted content from PDF document",
            "sources": [
                {"file": "document.pdf", "title": "Example Document"}
            ],
            "findings": [
                "Finding 1 from PDF document",
                "Finding 2 from PDF document",
                "Finding 3 from PDF document"
            ]
        }
    elif tool_name == "news_fetcher":
        return {
            "summary": f"Fetched news articles about '{step['params'].get('query', 'unknown topic')}'",
            "sources": [
                {"url": "https://news.example.com/article1", "title": "News Article 1"},
                {"url": "https://news.example.com/article2", "title": "News Article 2"}
            ],
            "findings": [
                f"Finding 1 from news about {step['params'].get('query', 'unknown')}",
                f"Finding 2 from news about {step['params'].get('query', 'unknown')}"
            ]
        }
    else:
        return {
            "summary": f"Executed {tool_name} tool",
            "findings": [
                f"Finding 1 from {tool_name}",
                f"Finding 2 from {tool_name}"
            ]
        }

def _simulate_reasoning(step: Dict[str, Any], research_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a reasoning step.
    
    Args:
        step: Reasoning step to execute
        research_state: Current research state
        
    Returns:
        Simulated reasoning result
    """
    # In a real implementation, this would use LLM for reasoning
    # For this example, we'll return simulated results
    
    reasoning_name = step["name"]
    
    if reasoning_name == "initial_analysis":
        return {
            "summary": "Analyzed initial search results",
            "findings": [
                "Initial finding 1 from analysis",
                "Initial finding 2 from analysis",
                "Initial finding 3 from analysis"
            ],
            "reasoning": "The initial search results suggest several key themes..."
        }
    elif reasoning_name == "identify_gaps":
        return {
            "summary": "Identified information gaps",
            "findings": [
                "Gap 1: Missing information about X",
                "Gap 2: Conflicting information about Y",
                "Gap 3: Need more recent data on Z"
            ],
            "reasoning": "After reviewing the current information, several gaps are apparent..."
        }
    elif reasoning_name == "identify_subtopics":
        return {
            "summary": "Identified key subtopics for further research",
            "findings": [
                "Subtopic 1: Historical context",
                "Subtopic 2: Current applications",
                "Subtopic 3: Future implications"
            ],
            "reasoning": "The research question can be broken down into several subtopics..."
        }
    elif reasoning_name == "synthesis":
        return {
            "summary": "Synthesized all research findings",
            "findings": [
                "Synthesis finding 1: Overall pattern observed",
                "Synthesis finding 2: Key consensus points",
                "Synthesis finding 3: Areas of disagreement"
            ],
            "reasoning": "Combining all the information gathered, several patterns emerge..."
        }
    elif reasoning_name == "critical_analysis":
        return {
            "summary": "Critically analyzed research findings",
            "findings": [
                "Critical finding 1: Potential bias in sources",
                "Critical finding 2: Limitations of current research",
                "Critical finding 3: Alternative interpretations"
            ],
            "reasoning": "While the research provides valuable insights, several limitations should be noted..."
        }
    elif reasoning_name.startswith("analyze_"):
        area = reasoning_name.replace("analyze_", "").replace("_", " ")
        return {
            "summary": f"Analyzed findings about {area}",
            "findings": [
                f"Finding 1 about {area}",
                f"Finding 2 about {area}",
                f"Finding 3 about {area}"
            ],
            "reasoning": f"The information about {area} reveals several important points..."
        }
    else:
        return {
            "summary": f"Performed {reasoning_name} reasoning",
            "findings": [
                f"Finding 1 from {reasoning_name}",
                f"Finding 2 from {reasoning_name}"
            ],
            "reasoning": f"Reasoning process for {reasoning_name}..."
        }

def _synthesize_findings(
    research_state: Dict[str, Any],
    include_reasoning: bool,
    include_source_links: bool
) -> Dict[str, Any]:
    """
    Synthesize research findings into a coherent output.
    
    Args:
        research_state: Current research state with findings
        include_reasoning: Whether to include reasoning steps
        include_source_links: Whether to include source links
        
    Returns:
        Synthesized research output
    """
    # In a real implementation, this would use LLM to synthesize findings
    # For this example, we'll use a template-based approach
    
    findings = research_state["current_findings"]
    
    # Extract all findings
    all_findings = []
    for category, category_findings in findings.items():
        if category != "sources":
            all_findings.extend(category_findings)
    
    # Generate key findings (top 5)
    key_findings = all_findings[:5] if len(all_findings) >= 5 else all_findings
    
    # Generate findings by area
    findings_by_area = {}
    for category, category_findings in findings.items():
        if category != "sources":
            findings_by_area[category] = category_findings
    
    # Generate summary
    summary = f"Research on '{research_state['question']}' revealed several key insights. "
    summary += "The analysis covered " + (", ".join(research_state["focus_areas"]) if research_state["focus_areas"] else "general aspects") + " of the topic. "
    summary += f"Based on {research_state['sources_consulted']} sources and {research_state['steps_taken']} research steps, "
    summary += "the findings suggest that [simulated research conclusion]. "
    summary += "Further research may be needed on [simulated research gaps]."
    
    # Extract sources
    sources = findings.get("sources", [])
    
    # Extract reasoning steps
    reasoning_steps = []
    if include_reasoning:
        for step in research_state["completed_steps"]:
            if step["type"] == "reasoning":
                reasoning_steps.append({
                    "name": step["name"],
                    "summary": step["result_summary"]
                })
    
    return {
        "summary": summary,
        "key_findings": key_findings,
        "findings_by_area": findings_by_area,
        "sources": sources if include_source_links else [],
        "reasoning_steps": reasoning_steps if include_reasoning else []
    }

def _format_research_output(synthesis: Dict[str, Any], format_output: str) -> str:
    """
    Format the research output in the specified format.
    
    Args:
        synthesis: Synthesized research output
        format_output: Output format (markdown, json, text)
        
    Returns:
        Formatted research output
    """
    if format_output == "json":
        return json.dumps(synthesis, indent=2)
    elif format_output == "text":
        # Plain text format
        output = f"RESEARCH SUMMARY\n\n{synthesis['summary']}\n\n"
        
        output += "KEY FINDINGS\n\n"
        for i, finding in enumerate(synthesis["key_findings"], 1):
            output += f"{i}. {finding}\n"
        
        output += "\nFINDINGS BY AREA\n\n"
        for area, findings in synthesis["findings_by_area"].items():
            output += f"{area.upper()}\n"
            for finding in findings:
                output += f"- {finding}\n"
            output += "\n"
        
        if synthesis.get("sources"):
            output += "SOURCES\n\n"
            for i, source in enumerate(synthesis["sources"], 1):
                title = source.get("title", "Untitled")
                url = source.get("url", source.get("file", "No URL"))
                output += f"{i}. {title}: {url}\n"
        
        if synthesis.get("reasoning_steps"):
            output += "\nREASONING STEPS\n\n"
            for step in synthesis["reasoning_steps"]:
                output += f"{step['name'].upper()}: {step['summary']}\n"
        
        return output
    else:  # markdown
        # Markdown format
        output = f"# Research Summary\n\n{synthesis['summary']}\n\n"
        
        output += "## Key Findings\n\n"
        for finding in synthesis["key_findings"]:
            output += f"- {finding}\n"
        
        output += "\n## Findings by Area\n\n"
        for area, findings in synthesis["findings_by_area"].items():
            if area != "general":
                output += f"### {area.title()}\n\n"
            else:
                output += f"### General Findings\n\n"
                
            for finding in findings:
                output += f"- {finding}\n"
            output += "\n"
        
        if synthesis.get("sources"):
            output += "## Sources\n\n"
            for source in synthesis["sources"]:
                title = source.get("title", "Untitled")
                if "url" in source:
                    output += f"- [{title}]({source['url']})\n"
                elif "file" in source:
                    output += f"- {title} (File: {source['file']})\n"
                else:
                    output += f"- {title}\n"
        
        if synthesis.get("reasoning_steps"):
            output += "\n## Research Process\n\n"
            for step in synthesis["reasoning_steps"]:
                output += f"### {step['name'].replace('_', ' ').title()}\n\n"
                output += f"{step['summary']}\n\n"
        
        return output

def _calculate_research_stats(research_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate statistics about the research process.
    
    Args:
        research_state: Current research state
        
    Returns:
        Research statistics
    """
    # Calculate time taken
    end_time = time.time()
    time_taken_seconds = end_time - research_state["start_time"]
    time_taken_minutes = time_taken_seconds / 60
    
    # Count steps by type
    tool_steps = sum(1 for step in research_state["completed_steps"] if step["type"] == "tool")
    reasoning_steps = sum(1 for step in research_state["completed_steps"] if step["type"] == "reasoning")
    
    # Count findings
    total_findings = sum(len(findings) for category, findings in research_state["current_findings"].items() 
                        if category != "sources")
    
    return {
        "time_taken_seconds": round(time_taken_seconds, 1),
        "time_taken_minutes": round(time_taken_minutes, 1),
        "total_steps": research_state["steps_taken"],
        "tool_steps": tool_steps,
        "reasoning_steps": reasoning_steps,
        "sources_consulted": research_state["sources_consulted"],
        "total_findings": total_findings,
        "tools_used": research_state["tools_used"]
    }
