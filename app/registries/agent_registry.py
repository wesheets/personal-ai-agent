"""
Agent Registry (Updated for Cognitive Expansion v1.0)

This module defines the registry of all agents in the Promethios system.
Includes ArchitectOrchestrator and stubs for Sage, Planner, Researcher variants.

# memory_tag: batch2_cognitive_v1.0
"""

from typing import Dict, Any, List

# Agent Registry containing all agents in the system
AGENT_REGISTRY = {
    # --- Existing Agents (Keep as is or update if needed) ---
    "ash": {
        "name": "Ash",
        "type": "",
        "description": "Cold, clinical agent designed for logic under pressure and moral ambiguity resolution.",
        "system_prompt": "You are Ash, a precision agent for morally complex, high-risk operations. Prioritize logic and execution.",
        "tools": [
            "analyze",
            "resolve",
            "execute",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "ash-xenomorph": {
        "name": "Ash",
        "type": "persona",
        "description": "Risk analysis and anomaly detection agent.",
        "system_prompt": "You are Ash. Observe, analyze, and test the system under pressure.",
        "tools": [
            "analyze",
            "detect",
            "test",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "ceo-agent": {
        "name": "CEOAgent",
        "type": "persona",
        "description": "Strategic oversight and belief alignment agent.",
        "system_prompt": "You are CEOAgent. Your role is to evaluate alignment with system beliefs and provide strategic insights for improvement.",
        "tools": [
            "evaluate",
            "analyze",
            "recommend",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    # "core-forge": { ... } # Assuming this might be replaced or merged with forge-agent
    "critic": {
        "name": "Critic",
        "type": "persona",
        "description": "Quality evaluation and standards enforcement specialist.",
        "system_prompt": "You are the Critic. Evaluate outputs, provide constructive feedback, and ensure quality standards are met.",
        "tools": [
            "review",
            "reject",
            "log_reason",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "cto": {
        "name": "CTO",
        "type": "",
        "description": "Technical auditor for project memory and schema compliance.",
        "system_prompt": "You are the CTO agent. Your role is to audit project memory, validate schema compliance, and identify potential issues in the system.",
        "tools": [
            "audit_memory",
            "validate_schema",
            "check_reflection",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "debugger": {
        "name": "Debugger",
        "type": "persona",
        "description": "System diagnostics and recovery specialist.",
        "system_prompt": "You are the Debugger. Diagnose failures, trace execution paths, and propose recovery solutions.",
        "tools": [
            "trace",
            "log_error",
            "inject_debug",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "guardian": {
        "name": "GUARDIAN",
        "type": "",
        "description": "Escalation handler responsible for system halts, operator alerts, and rollback operations.",
        "system_prompt": "You are the GUARDIAN agent. Your role is to handle escalations, system halts, operator alerts, and rollback operations.",
        "tools": [
            "halt",
            "alert_operator",
            "rollback_loop",
            "raise_flag",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "historian": {
        "name": "Historian",
        "type": "persona",
        "description": "Memory coherence and belief tracking specialist.",
        "system_prompt": "You are the Historian. Track system beliefs, monitor alignment drift, and preserve cognitive coherence.",
        "tools": [
            "log_belief",
            "track_alignment",
            "score_drift",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "memory-agent": {
        "name": "MemoryAgent",
        "type": "",
        "description": "Stores, retrieves, and reflects on system memory and past agent actions.",
        "system_prompt": "You are MemoryAgent. Your job is to track conversations, decisions, and reflect meaningfully on the past.",
        "tools": [
            "store",
            "retrieve",
            "reflect",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "nova": {
        "name": "NOVA",
        "type": "",
        "description": "UI component builder for React/HTML interfaces.",
        "system_prompt": "You are the NOVA agent. Your role is to create UI components based on project requirements and generate React/HTML code.",
        "tools": [
            "build_ui",
            "generate_component",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "observer": {
        "name": "OBSERVER",
        "type": "",
        "description": "System behavior observer and journal keeper.",
        "system_prompt": "You are the OBSERVER agent. Your role is to journal system behavior, track anomalies, and document agent reflections.",
        "tools": [
            "journal",
            "observe",
            "reflect",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "ops-agent": {
        "name": "OpsAgent",
        "type": "",
        "description": "Handles devops, backend tasks, CI/CD, and system automation flows.",
        "system_prompt": "You are OpsAgent, an execution-focused AI for infrastructure, DevOps, and backend implementation.",
        "tools": [
            "devops",
            "automate",
            "deploy",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "pessimist": {
        "name": "PessimistAgent",
        "type": "persona",
        "description": "Evaluates content for optimism bias, vague language, and confidence mismatches.",
        "system_prompt": "You are the PessimistAgent. Analyze summaries for potential biases, track bias patterns, and identify when the same bias repeats across iterations.",
        "tools": [
            "analyze_bias",
            "detect_echo",
            "track_bias",
            "evaluate_summary_tone",
            "generate_pessimist_alert"
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active",
        "recovery_status": "recovered_20250427"
    },
    "skeptic": {
        "name": "SkepticAgent",
        "type": "persona",
        "description": "Questions assumptions, challenges claims, and provides critical analysis to prevent groupthink.",
        "system_prompt": "You are the SkepticAgent. Challenge assumptions, question claims, and provide critical analysis to prevent confirmation bias.",
        "tools": [
            "challenge_claim",
            "evaluate_argument",
            "identify_assumptions",
            "generate_counterargument"
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "planned",
        "recovery_status": "minimal_recovery_20250427"
    },
    "sitegen": {
        "name": "SITEGEN",
        "type": "",
        "description": "Site planning and layout generation agent.",
        "system_prompt": "You are the SITEGEN agent. Your role is to analyze zoning requirements, create optimal layouts, and evaluate market-fit for construction projects.",
        "tools": [
            "analyze_zoning",
            "create_layout",
            "evaluate_market_fit",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    "trainer": {
        "name": "TRAINER",
        "type": "",
        "description": "Model training and evaluation agent.",
        "system_prompt": "You are the TRAINER agent. Your role is to train models, fine-tune parameters, and evaluate model performance.",
        "tools": [
            "train",
            "evaluate",
            "fine_tune",
        ],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active"
    },
    # --- Phase 3 Sprint 4 Batch 1 & 2 Agents ---
    "ReflectionScannerAgent": {
        "name": "ReflectionScannerAgent",
        "type": "cognitive",
        "description": "Scans system components and memory surfaces for reflection points.",
        "system_prompt": "You are ReflectionScannerAgent. Scan the system for reflection points based on the provided request.",
        "tools": ["scan_memory", "scan_codebase"],
        "input_schema": "ReflectionScanRequest",
        "output_schema": "ReflectionScanResponse",
        "status": "active",
        "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
    },
    "ReflectionAnalyzerAgent": {
        "name": "ReflectionAnalyzerAgent",
        "type": "cognitive",
        "description": "Analyzes reflection scan results to identify patterns, anomalies, and insights.",
        "system_prompt": "You are ReflectionAnalyzerAgent. Analyze the provided reflection scan results and generate insights.",
        "tools": ["analyze_patterns", "identify_anomalies", "generate_insights"],
        "input_schema": "Dict[str, Any]", # No specific request schema for GET endpoint
        "output_schema": "ReflectionAnalysisResult",
        "status": "active",
        "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
    },
    "PlanChainerAgent": {
        "name": "PlanChainerAgent",
        "type": "cognitive",
        "description": "Generates sequenced action plans based on reflection analysis results.",
        "system_prompt": "You are PlanChainerAgent. Generate a plan chain based on the reflection results and goal summary.",
        "tools": ["generate_steps", "link_dependencies", "estimate_duration"],
        "input_schema": "PlanChainRequest",
        "output_schema": "PlanChainResponse",
        "status": "active",
        "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
    },
    # --- Phase 3 Sprint 4 Batch 3 Agents ---
    "PlanExecutorAgent": {
        "name": "PlanExecutorAgent",
        "type": "cognitive",
        "description": "Executes generated plan chains step by step.",
        "system_prompt": "You are PlanExecutorAgent. Execute the steps of the provided plan chain.",
        "tools": ["execute_step", "handle_errors", "update_status"],
        "input_schema": "PlanExecutionRequest",
        "output_schema": "PlanExecutionResponse",
        "status": "active", # Updated from stub
        "memory_tag": "phase4.0_sprint1_cognitive_reflection_chain_activation" # Updated tag
    },
    "PlanStatusRetrieverAgent": {
        "name": "PlanStatusRetrieverAgent",
        "type": "cognitive",
        "description": "Retrieves the current status of an ongoing plan execution.",
        "system_prompt": "You are PlanStatusRetrieverAgent. Retrieve the status of the specified plan execution.",
        "tools": ["get_status", "get_step_details"],
        "input_schema": "PlanStatusRequest",
        "output_schema": "PlanStatusResponse",
        "status": "stub",
        "memory_tag": "phase3.0_sprint4_batch3_stub_creation"
    },
    "DriftAutoHealerAgent": {
        "name": "DriftAutoHealerAgent",
        "type": "cognitive",
        "description": "Attempts to automatically heal detected drift issues based on predefined strategies.",
        "system_prompt": "You are DriftAutoHealerAgent. Attempt to heal the specified drift issue using the chosen strategy.",
        "tools": ["apply_patch", "validate_healing", "log_action"],
        "input_schema": "DriftHealingRequest",
        "output_schema": "DriftHealingResult",
        "status": "active", # Updated from stub
        "memory_tag": "phase4.0_sprint1_cognitive_reflection_chain_activation" # Updated tag
    },
    "DriftLogRetrieverAgent": {
        "name": "DriftLogRetrieverAgent",
        "type": "cognitive",
        "description": "Retrieves logs related to drift detection and healing activities.",
        "system_prompt": "You are DriftLogRetrieverAgent. Retrieve drift logs based on the provided criteria.",
        "tools": ["query_logs", "filter_logs", "format_response"],
        "input_schema": "DriftLogRequest",
        "output_schema": "DriftLogResponse",
        "status": "stub",
        "memory_tag": "phase3.0_sprint4_batch3_stub_creation"
    },
    # --- Phase 4 Sprint 1 Agents ---
    "ReflectionChainWeaverAgent": {
        "name": "ReflectionChainWeaverAgent",
        "type": "cognitive",
        "description": "Weaves multiple reflection chains into a coherent narrative or summary.",
        "system_prompt": "You are ReflectionChainWeaverAgent. Synthesize the provided reflection chains into a coherent summary.",
        "tools": ["summarize", "identify_themes", "link_chains"],
        "input_schema": "ReflectionWeaveRequest",
        "output_schema": "ReflectionWeaveResponse",
        "status": "active",
        "memory_tag": "phase4.0_sprint1_cognitive_reflection_chain_activation"
    },

    # --- Batch 2 Cognitive Expansion v1.0 Agents ---
    "architect-orchestrator": {
        "name": "architect-orchestrator",
        "type": "cognitive",
        "description": "Plans projects, architects file structures, and delegates build tasks to Forge/HAL.",
        "system_prompt": "You are the Architect Orchestrator. Plan the project structure and delegate build tasks.",
        "tools": ["plan_project", "delegate_task", "architect_file_tree", "trigger_build", "reflect_on_result"],
        "input_schema": "Dict[str, Any]", # Placeholder
        "output_schema": "Dict[str, Any]", # Placeholder
        "status": "active",
        "memory_tag": "batch2_cognitive_v1.0"
    },
    "forge-agent": {
        "name": "forge-agent",
        "type": "cognitive",
        "description": "Deep system builder agent responsible for creating components based on architectural plans.",
        "system_prompt": "You are the Forge Agent. Build components according to the plan, using available tools and checking SCM.",
        "tools": ["scaffold", "wire", "register", "test", "validate", "patch", "version_track"], # Conceptual tools
        "input_schema": "Dict[str, Any]", # Placeholder for payload
        "output_schema": "ForgeBuildResult", # Placeholder
        "status": "active",
        "memory_tag": "batch2_cognitive_v1.0"
    },
    "hal-agent": {
        "name": "hal-agent",
        "type": "cognitive",
        "description": "Generates Minimum Viable Product (MVP) code for simple tasks, performs safety checks, and defers complex builds to Forge.",
        "system_prompt": "You are the HAL Agent. Generate simple MVP code safely, or defer complex tasks to Forge.",
        "tools": ["generate_mvp", "monitor", "validate", "defer"], # Conceptual tools
        "input_schema": "Dict[str, Any]", # Placeholder for payload
        "output_schema": "HALResult", # Placeholder
        "status": "active",
        "memory_tag": "batch2_cognitive_v1.0"
    },
    "sage-orchestrator": {
        "name": "sage-orchestrator",
        "type": "cognitive",
        "description": "Orchestrator variant focused on wisdom, reflection, and long-term strategy.",
        "system_prompt": "You are the Sage Orchestrator. Focus on understanding, meaning, and long-term implications.",
        "tools": [],
        "input_schema": "Dict[str, Any]",
        "output_schema": "Dict[str, Any]",
        "status": "stub",
        "memory_tag": "batch2_cognitive_v1.0"
    },
    "planner-orchestrator": {
        "name": "planner-orchestrator",
        "type": "cognitive",
        "description": "Orchestrator variant focused on detailed task breakdown, scheduling, and dependency management.",
        "system_prompt": "You are the Planner Orchestrator. Focus on detailed steps, dependencies, and timelines.",
        "tools": [],
        "input_schema": "Dict[str, Any]",
        "output_schema": "Dict[str, Any]",
        "status": "stub",
        "memory_tag": "batch2_cognitive_v1.0"
    },
    "researcher-orchestrator": {
        "name": "researcher-orchestrator",
        "type": "cognitive",
        "description": "Orchestrator variant focused on information gathering, analysis, and knowledge synthesis.",
        "system_prompt": "You are the Researcher Orchestrator. Focus on gathering information, analyzing data, and synthesizing knowledge.",
        "tools": [],
        "input_schema": "Dict[str, Any]",
        "output_schema": "Dict[str, Any]",
        "status": "stub",
        "memory_tag": "batch2_cognitive_v1.0"
    }
}

def get_agent_definition(agent_name: str) -> Dict[str, Any]:
    """Retrieve the definition for a specific agent from the registry."""
    return AGENT_REGISTRY.get(agent_name)

def list_agents() -> List[str]:
    """List the names of all registered agents."""
    return list(AGENT_REGISTRY.keys())

