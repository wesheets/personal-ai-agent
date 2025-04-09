import logging
import re
import asyncio
from typing import Dict, List, Any, Optional, Union
from app.core.run import run_agent
from app.agents.memory_agent import handle_memory_task

logger = logging.getLogger("core")

class CoreForge:
    def __init__(self):
        self.agent_id = "core-forge"
        self.reflection_enabled = True
        self.reflection_threshold = 5  # Number of memory entries to trigger reflection
        self.last_reflection_count = 0  # Track the last memory count when reflection was performed

    def process_task(self, task):
        """
        Process a task by routing it to the appropriate agent.
        
        Args:
            task (dict): A dictionary containing the task details
                - target_agent (str): The agent to route the task to
                - input (str): The input for the agent
                
        Returns:
            dict: A dictionary containing the task results
        """
        try:
            # Validate task input
            if not isinstance(task, dict):
                error_msg = "Task must be a dictionary"
                logger.error(f"[ERROR] {error_msg}")
                return {
                    "status": "error",
                    "executor": self.agent_id,
                    "error": error_msg,
                    "output": error_msg
                }
            
            # Extract task parameters
            agent = task.get("target_agent", "")
            task_input = task.get("input", "")
            
            # Check for build commands and delegate to ops-agent
            if "build" in task_input.lower():
                from app.core.delegate import delegate_to_agent
                logger.info(f"[Core.Forge] Detected build request: {task_input}")
                
                # If specifically about LifeTree, delegate directly
                if "lifetree" in task_input.lower() or "life tree" in task_input.lower():
                    result = delegate_to_agent("core-forge", "ops-agent", "Generate vertical scaffold for LifeTree")
                    
                    # Log the delegation to memory
                    handle_memory_task("LOG: Core.Forge delegated LifeTree vertical building to ops-agent")
                    
                    return {
                        "status": "complete",
                        "executor": self.agent_id,
                        "delegated": True,
                        "delegated_to": "ops-agent",
                        "input": task_input,
                        "output": f"I've delegated the LifeTree vertical building task to OpsAgent. Result: {result}"
                    }

            # Validate required fields
            if not agent or not task_input:
                error_msg = "Task missing required fields."
                logger.error(f"[ERROR] {error_msg}")
                return {
                    "status": "error",
                    "executor": self.agent_id,
                    "error": error_msg,
                    "output": error_msg
                }

            # Always call MemoryAgent("SHOW") before responding
            memory_content = handle_memory_task("SHOW")
            logger.info(f"[Core.Forge] Reflecting on recent memory before responding")
            
            # Analyze recent memory for context
            memory_analysis = self.analyze_recent_memory(memory_content)
            if memory_analysis:
                logger.info(f"[Core.Forge] Memory analysis: {memory_analysis}")
                # Log the reflection to memory
                memory_entry = f"LOG: Core.Forge reflected on memory before responding to {agent}: {memory_analysis}"
                handle_memory_task(memory_entry)

            # Execute the task
            logger.info(f"[Core.Forge] → Routing task to {agent}: {task_input[:50]}...")
            result = run_agent(agent, task_input)

            # Log the execution with memory integration
            log_message = f"LOG: Core.Forge delegated task to {agent}"
            logger.info(log_message)
            handle_memory_task(log_message)
            
            response_log = f"[Core.Forge] ← Response: {result}"
            logger.info(response_log)
            print(response_log)
            
            # Add memory integration with structured logging
            try:
                structured_log = f"STRUCTURED_LOG:{{\"source\": \"Core.Forge\", \"target\": \"{agent}\", \"type\": \"delegation\", \"input\": \"{task_input[:50]}...\"}}"
                handle_memory_task(structured_log)
            except Exception as mem_error:
                logger.error(f"[ERROR] Failed to log to memory: {str(mem_error)}")

            # Return successful result with memory analysis included
            return {
                "status": "complete",
                "executor": self.agent_id,
                "routed_to": agent,
                "input": task_input,
                "memory_context": memory_analysis,
                "output": result
            }
            
        except Exception as e:
            # Handle any unexpected errors
            error_msg = f"Error processing task: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            
            return {
                "status": "error",
                "executor": self.agent_id,
                "error": str(e),
                "output": f"Core.Forge encountered an error: {str(e)}"
            }

    def batch_execute(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a batch of tasks across multiple agents.
        
        Args:
            tasks: List of task dictionaries, each containing:
                - agent: The agent to execute the task
                - input: The input for the agent
                
        Returns:
            List of result dictionaries, each containing:
                - status: 'complete' or 'error'
                - agent: The agent that executed the task
                - input: The original input
                - output: The result of the task execution
        """
        logger.info(f"[Core.Forge] Starting batch execution of {len(tasks)} tasks")
        
        # Validate input
        if not isinstance(tasks, list):
            error_msg = "Batch tasks must be a list"
            logger.error(f"[ERROR] {error_msg}")
            return [{
                "status": "error",
                "executor": self.agent_id,
                "error": error_msg,
                "output": error_msg
            }]
        
        # Log batch execution start
        handle_memory_task("LOG: Core.Forge started batch execution")
        
        results = []
        
        # Process each task in sequence
        for i, task_data in enumerate(tasks):
            try:
                # Extract task parameters
                agent = task_data.get("agent", "")
                task_input = task_data.get("input", "")
                
                # Special case for memory-agent direct logging
                if agent.lower() == "memory-agent":
                    logger.info(f"[Core.Forge] Direct memory log: {task_input}")
                    memory_result = handle_memory_task(task_input)
                    results.append({
                        "status": "complete",
                        "executor": self.agent_id,
                        "agent": "memory-agent",
                        "input": task_input,
                        "output": memory_result
                    })
                    continue
                
                # Validate required fields
                if not agent or not task_input:
                    error_msg = f"Task {i+1} missing required fields"
                    logger.error(f"[ERROR] {error_msg}")
                    results.append({
                        "status": "error",
                        "executor": self.agent_id,
                        "error": error_msg,
                        "output": error_msg
                    })
                    continue
                
                # Create a proper task for process_task
                task = {
                    "target_agent": agent,
                    "input": task_input
                }
                
                # Execute the task
                logger.info(f"[Core.Forge] Batch task {i+1}/{len(tasks)}: {agent} - {task_input[:50]}...")
                result = self.process_task(task)
                
                # Add to results
                results.append(result)
                
            except Exception as e:
                error_msg = f"Error processing batch task {i+1}: {str(e)}"
                logger.error(f"[ERROR] {error_msg}")
                results.append({
                    "status": "error",
                    "executor": self.agent_id,
                    "task_index": i,
                    "error": str(e),
                    "output": f"Core.Forge encountered an error: {str(e)}"
                })
        
        # Log batch execution completion
        handle_memory_task(f"LOG: Core.Forge completed batch execution of {len(tasks)} tasks")
        
        return results

    async def batch_execute_async(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a batch of tasks across multiple agents asynchronously.
        
        Args:
            tasks: List of task dictionaries, each containing:
                - agent: The agent to execute the task
                - input: The input for the agent
                
        Returns:
            List of result dictionaries, each containing:
                - status: 'complete' or 'error'
                - agent: The agent that executed the task
                - input: The original input
                - output: The result of the task execution
        """
        logger.info(f"[Core.Forge] Starting async batch execution of {len(tasks)} tasks")
        
        # Validate input
        if not isinstance(tasks, list):
            error_msg = "Batch tasks must be a list"
            logger.error(f"[ERROR] {error_msg}")
            return [{
                "status": "error",
                "executor": self.agent_id,
                "error": error_msg,
                "output": error_msg
            }]
        
        # Log batch execution start
        handle_memory_task("LOG: Core.Forge started async batch execution")
        
        # Create a list to store the results
        results = [None] * len(tasks)
        
        # Define a task executor function
        async def execute_task(index, task_data):
            try:
                # Extract task parameters
                agent = task_data.get("agent", "")
                task_input = task_data.get("input", "")
                
                # Special case for memory-agent direct logging
                if agent.lower() == "memory-agent":
                    logger.info(f"[Core.Forge] Direct memory log: {task_input}")
                    memory_result = handle_memory_task(task_input)
                    return {
                        "status": "complete",
                        "executor": self.agent_id,
                        "agent": "memory-agent",
                        "input": task_input,
                        "output": memory_result
                    }
                
                # Validate required fields
                if not agent or not task_input:
                    error_msg = f"Task {index+1} missing required fields"
                    logger.error(f"[ERROR] {error_msg}")
                    return {
                        "status": "error",
                        "executor": self.agent_id,
                        "error": error_msg,
                        "output": error_msg
                    }
                
                # Create a proper task for process_task
                task = {
                    "target_agent": agent,
                    "input": task_input
                }
                
                # Execute the task
                logger.info(f"[Core.Forge] Async batch task {index+1}/{len(tasks)}: {agent} - {task_input[:50]}...")
                result = self.process_task(task)
                
                return result
                
            except Exception as e:
                error_msg = f"Error processing async batch task {index+1}: {str(e)}"
                logger.error(f"[ERROR] {error_msg}")
                return {
                    "status": "error",
                    "executor": self.agent_id,
                    "task_index": index,
                    "error": str(e),
                    "output": f"Core.Forge encountered an error: {str(e)}"
                }
        
        # Create tasks for each item
        async_tasks = []
        for i, task_data in enumerate(tasks):
            async_tasks.append(execute_task(i, task_data))
        
        # Execute all tasks concurrently
        completed_results = await asyncio.gather(*async_tasks)
        
        # Store results in the correct order
        for i, result in enumerate(completed_results):
            results[i] = result
        
        # Log batch execution completion
        handle_memory_task(f"LOG: Core.Forge completed async batch execution of {len(tasks)} tasks")
        
        return results

    def analyze_recent_memory(self, memory_content: str) -> str:
        """
        Analyze recent memory content for context before responding.
        
        Args:
            memory_content: Recent memory content from MemoryAgent("SHOW")
            
        Returns:
            str: Analysis of recent memory for context
        """
        if not memory_content or memory_content == "🧠 No recent memory.":
            return "No recent context available"
            
        lines = memory_content.split("\n")
        valid_lines = [line for line in lines if line.strip()]
        
        if not valid_lines:
            return "No relevant context found in memory"
            
        # Extract key information
        recent_agents = set()
        recent_actions = []
        recent_errors = []
        
        for line in valid_lines:
            # Extract agent names
            for agent in ["Core.Forge", "HAL", "ASH", "OPS", "Memory", "Builder", "Observer"]:
                if agent in line:
                    recent_agents.add(agent)
            
            # Extract actions
            if "delegated" in line or "completed" in line or "initialized" in line:
                recent_actions.append(line)
            
            # Extract errors
            if "error" in line.lower() or "failed" in line.lower():
                recent_errors.append(line)
        
        # Build context summary
        context_summary = []
        
        if recent_agents:
            context_summary.append(f"Recent activity from: {', '.join(recent_agents)}")
        
        if recent_actions:
            # Only include the 3 most recent actions
            recent_actions = recent_actions[-3:]
            action_summary = "; ".join(recent_actions)
            context_summary.append(f"Recent actions: {action_summary}")
        
        if recent_errors:
            error_summary = "; ".join(recent_errors)
            context_summary.append(f"Recent errors: {error_summary}")
        
        # Add overall assessment
        if recent_errors:
            context_summary.append("System requires attention due to errors")
        elif len(recent_actions) >= 3:
            context_summary.append("System is actively processing multiple tasks")
        else:
            context_summary.append("System appears to be functioning normally")
        
        return " | ".join(context_summary)

    def check_reflection_needed(self) -> Optional[str]:
        """
        Check if reflection is needed based on memory size.
        
        Returns:
            Optional[str]: Reflection result if performed, None otherwise
        """
        # Get the current memory
        memory = handle_memory_task("SHOW")
        memory_entries = memory.split("\n")
        
        # Count valid memory entries
        valid_entries = [entry for entry in memory_entries if entry.strip()]
        memory_count = len(valid_entries)
        
        # Check if we have enough new entries to trigger reflection
        if memory_count - self.last_reflection_count >= self.reflection_threshold:
            self.last_reflection_count = memory_count
            return self.analyze_memory()
        
        return None

    def analyze_memory(self) -> str:
        """
        Analyze system memory to identify patterns and make decisions.
        
        Returns:
            str: Analysis results and insights
        """
        logger.info("[Core.Forge] Analyzing system memory...")
        
        # Get structured memory for better analysis
        memory_data = handle_memory_task("SHOW_STRUCTURED")
        
        try:
            # If we got structured data back
            if memory_data.startswith("[") or memory_data.startswith("{"):
                analysis_result = self._analyze_structured_memory(memory_data)
            else:
                # Fallback to analyzing raw text
                analysis_result = self._analyze_raw_memory(memory_data)
                
            # Trigger TrainerAgent to analyze memory and generate lessons
            logger.info("[Core.Forge] Triggering TrainerAgent for self-improvement...")
            trainer_result = run_agent("trainer", "train")
            logger.info(f"[Core.Forge] TrainerAgent result: {trainer_result}")
            
            return analysis_result
        except Exception as e:
            logger.error(f"[ERROR] Memory analysis failed: {str(e)}")
            return f"Memory analysis failed: {str(e)}"

    def _analyze_structured_memory(self, memory_data: str) -> str:
        """
        Analyze structured memory data.
        
        Args:
            memory_data: JSON string of memory data
            
        Returns:
            str: Analysis results
        """
        import json
        
        try:
            # Parse the JSON data
            memory_entries = json.loads(memory_data)
            
            if not memory_entries:
                return "No memory entries to analyze"
            
            # Initialize counters
            agent_activity = {}
            delegation_count = 0
            error_count = 0
            
            # Analyze the entries
            for entry in memory_entries:
                if isinstance(entry, dict):
                    # Count by source
                    source = entry.get("source", "unknown")
                    if source not in agent_activity:
                        agent_activity[source] = 0
                    agent_activity[source] += 1
                    
                    # Count by type
                    entry_type = entry.get("type", "")
                    if entry_type == "delegation":
                        delegation_count += 1
                    elif entry_type == "error":
                        error_count += 1
            
            # Generate insights
            insights = []
            
            # Most active agent
            if agent_activity:
                most_active = max(agent_activity.items(), key=lambda x: x[1])
                insights.append(f"Most active agent: {most_active[0]} ({most_active[1]} activities)")
            
            # Delegation patterns
            if delegation_count > 0:
                insights.append(f"Delegation count: {delegation_count}")
            
            # Error patterns
            if error_count > 0:
                insights.append(f"Error count: {error_count}")
                insights.append("System may need attention due to errors")
            
            # Overall system health
            total_entries = len(memory_entries)
            health_ratio = 1.0 - (error_count / total_entries if total_entries > 0 else 0)
            health_status = "Healthy" if health_ratio > 0.9 else "Needs attention" if health_ratio > 0.7 else "Critical"
            insights.append(f"System health: {health_status} ({health_ratio:.2%})")
            
            return "Memory Analysis: " + "; ".join(insights)
            
        except json.JSONDecodeError:
            return self._analyze_raw_memory(memory_data)
        except Exception as e:
            logger.error(f"[ERROR] Structured memory analysis failed: {str(e)}")
            return f"Structured memory analysis failed: {str(e)}"

    def _analyze_raw_memory(self, memory_data: str) -> str:
        """
        Analyze raw memory text.
        
        Args:
            memory_data: Raw memory text
            
        Returns:
            str: Analysis results
        """
        lines = memory_data.split("\n")
        
        if not lines or (len(lines) == 1 and not lines[0].strip()):
            return "No memory entries to analyze"
        
        # Initialize counters
        agent_mentions = {}
        delegation_count = 0
        error_count = 0
        
        # Analyze the entries
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Count agent mentions
            for agent in ["Core.Forge", "HAL", "ASH", "OPS", "Memory"]:
                if agent in line:
                    if agent not in agent_mentions:
                        agent_mentions[agent] = 0
                    agent_mentions[agent] += 1
            
            # Count delegations
            if "delegated" in line or "routed" in line:
                delegation_count += 1
            
            # Count errors
            if "error" in line.lower() or "failed" in line.lower():
                error_count += 1
        
        # Generate insights
        insights = []
        
        # Most mentioned agent
        if agent_mentions:
            most_mentioned = max(agent_mentions.items(), key=lambda x: x[1])
            insights.append(f"Most mentioned agent: {most_mentioned[0]} ({most_mentioned[1]} mentions)")
        
        # Delegation patterns
        if delegation_count > 0:
            insights.append(f"Delegation count: {delegation_count}")
        
        # Error patterns
        if error_count > 0:
            insights.append(f"Error count: {error_count}")
            insights.append("System may need attention due to errors")
        
        # Overall system health
        total_entries = len(lines)
        health_ratio = 1.0 - (error_count / total_entries if total_entries > 0 else 0)
        health_status = "Healthy" if health_ratio > 0.9 else "Needs attention" if health_ratio > 0.7 else "Critical"
        insights.append(f"System health: {health_status} ({health_ratio:.2%})")
        
        return "Memory Analysis: " + "; ".join(insights)
