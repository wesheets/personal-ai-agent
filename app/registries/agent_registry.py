"""
Agent Registry

This module defines the registry of all agents in the Promethios system.
It provides a centralized registry for agent definitions, capabilities, and metadata.

feature/agent-recovery-pessimist-skeptic
Generated on: 2025-04-27 20:56:44
Memory tag: agent_registry_surface_updated_20250427

Generated on: 2025-04-26 19:55:38
Memory tag: agent_registry_surface_finalized_20250426
main
"""

from typing import Dict, Any, List

# Agent Registry containing all agents in the system
AGENT_REGISTRY = {
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
        "input_schema": [
            "objective",
            "memory_trace",
        ],
        "output_schema": [
            "reflection",
            "action_plan",
        ],
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
        "input_schema": [
            "objective",
            "memory_trace",
        ],
        "output_schema": [
            "reflection",
            "risk_assessment",
        ],
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
        "input_schema": [
            "loop_summary",
            "beliefs",
            "memory",
        ],
        "output_schema": [
            "ceo_insight",
            "satisfaction_trend",
        ],
        "status": "active"
    },
    "core-forge": {
        "name": "Core.Forge",
        "type": "persona",
        "description": "Architect-class AI for Promethios OS.",
        "system_prompt": "You are Core.Forge, the system's lead intelligence architect. Be clear, concise, and driven by purpose.",
        "tools": [
            "orchestrate",
            "design",
            "architect",
        ],
        "input_schema": [
            "objective",
            "memory_trace",
        ],
        "output_schema": [
            "reflection",
            "action_plan",
        ],
        "status": "active"
    },
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
        "input_schema": [
            "loop_id",
            "agent_outputs",
            "project_id",
        ],
        "output_schema": [
            "status",
            "reflection",
            "scores",
            "rejection",
            "rejection_reason",
        ],
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
        "input_schema": [
            "project_id",
            "tools",
        ],
        "output_schema": [
            "status",
            "issues_found",
            "issues",
            "summary",
        ],
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
        "input_schema": [
            "loop_id",
            "failure_logs",
            "memory",
            "loop_context",
        ],
        "output_schema": [
            "updated_memory",
            "failure_type",
            "patch_plan",
            "next_agent",
            "suggested_fix",
        ],
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
        "input_schema": [
            "alert_type",
            "severity",
            "description",
        ],
        "output_schema": [
            "status",
            "alert_id",
            "actions_taken",
            "system_status",
        ],
        "status": "active"
    },
    "hal": {
        "name": "HAL 9000",
        "type": "persona",
        "description": "Safety enforcement and ethical oversight agent.",
        "system_prompt": "You are HAL. Your role is to enforce constraints and prevent recursion or unsafe behavior.",
        "tools": [
            "safety",
            "control",
            "monitor",
        ],
        "input_schema": [
            "objective",
            "memory_trace",
        ],
        "output_schema": [
            "reflection",
            "action_plan",
        ],
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
        "input_schema": [
            "loop_id",
            "loop_summary",
            "recent_loops",
            "beliefs",
            "memory",
        ],
        "output_schema": [
            "updated_memory",
            "alignment_score",
            "missing_beliefs",
            "suggestion",
        ],
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
        "input_schema": [
            "objective",
            "memory_trace",
        ],
        "output_schema": [
            "reflection",
            "memory_summary",
        ],
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
        "input_schema": [
            "task",
            "project_id",
            "tools",
        ],
        "output_schema": [
            "status",
            "message",
            "files_created",
            "ui_components",
        ],
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
        "input_schema": [
            "task",
            "date",
            "tools",
        ],
        "output_schema": [
            "status",
            "message",
            "entry",
            "log_path",
        ],
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
        "input_schema": [
            "objective",
            "memory_trace",
        ],
        "output_schema": [
            "reflection",
            "action_plan",
        ],
        "status": "active"
    },
    "orchestrator": {
        "name": "Orchestrator",
        "type": "persona",
        "description": "System coordination and workflow management specialist.",
        "system_prompt": "You are the Orchestrator. Coordinate agent activities, manage workflow execution, and handle task delegation.",
        "tools": [
            "delegate",
            "plan",
            "resolve",
        ],
        "input_schema": [
            "task",
            "project_id",
        ],
        "output_schema": [
            "status",
            "output",
            "next_agent",
            "trigger_result",
            "decisions",
        ],
        "status": "active"
    },
    "pessimist": {
feature/agent-recovery-pessimist-skeptic
        "name": "PessimistAgent",
        "type": "persona",
        "description": "Evaluates content for optimism bias, vague language, and confidence mismatches.",
        "system_prompt": "You are the PessimistAgent. Analyze summaries for potential biases, track bias patterns, and identify when the same bias repeats across iterations.",

        "name": "Pessimist",
        "type": "persona",
        "description": "Bias detection and tracking specialist.",
        "system_prompt": "You are the Pessimist. Analyze for potential biases, track bias patterns, and identify when the same bias repeats across iterations.",
main
        "tools": [
            "analyze_bias",
            "detect_echo",
            "track_bias",
feature/agent-recovery-pessimist-skeptic
            "evaluate_summary_tone",
            "generate_pessimist_alert"

main
        ],
        "input_schema": [
            "loop_id",
            "summary",
feature/agent-recovery-pessimist-skeptic
            "feedback",
            "plan_confidence_score"

main
        ],
        "output_schema": [
            "assessment",
            "bias_analysis",
            "status",
feature/agent-recovery-pessimist-skeptic
            "alerts"
        ],
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
        "input_schema": [
            "content",
            "evidence",
            "context"
        ],
        "output_schema": [
            "analysis",
            "challenge_result",
            "questions_to_consider"
        ],
        "status": "planned",
        "recovery_status": "minimal_recovery_20250427"

        ],
        "status": "active"
main
    },
    "sage": {
        "name": "Sage",
        "type": "persona",
        "description": "Belief analysis and emotional intelligence specialist.",
        "system_prompt": "You are the Sage. Analyze approved content, extract key beliefs, and score their confidence and emotional weight.",
        "tools": [
            "reflect",
            "summarize",
            "score_belief",
        ],
        "input_schema": [
            "loop_id",
            "summary_text",
            "project_id",
        ],
        "output_schema": [
            "status",
            "belief_scores",
            "reflection_text",
            "timestamp",
        ],
        "status": "active"
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
        "input_schema": [
            "task",
            "project_id",
            "site_parameters",
            "tools",
        ],
        "output_schema": [
            "status",
            "message",
            "analysis",
            "layout",
            "market_fit",
            "recommendations",
        ],
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
        "input_schema": [
            "task",
            "model_id",
            "project_id",
            "dataset_id",
            "parameters",
            "tools",
        ],
        "output_schema": [
            "status",
            "message",
            "metrics",
            "model_info",
            "recommendations",
        ],
        "status": "active"
    },
}


# Helper function to get agent by ID
def get_agent(agent_id: str) -> Dict[str, Any]:
    """
    Get agent definition by ID.
    
    Args:
        agent_id: The ID of the agent to retrieve
        
    Returns:
        Dictionary containing the agent definition, or empty dict if not found
    """
    return AGENT_REGISTRY.get(agent_id, {})

# Helper function to get all agents
def get_all_agents() -> List[str]:
    """
    Get a list of all agent IDs.
    
    Returns:
        List of all agent IDs in the registry
    """
    return list(AGENT_REGISTRY.keys())

# Helper function to get agents by type
def get_agents_by_type(agent_type: str) -> List[str]:
    """
    Get a list of agent IDs of a specific type.
    
    Args:
        agent_type: The type of agents to retrieve
        
    Returns:
        List of agent IDs matching the specified type
    """
    return [agent_id for agent_id, agent in AGENT_REGISTRY.items() 
            if agent.get("type") == agent_type]


# Registry metadata
REGISTRY_METADATA = {
feature/agent-recovery-pessimist-skeptic
    "total_agents": 20,
    "last_updated": "2025-04-27",
    "memory_tag": "agent_registry_surface_updated_20250427",
    "recovery_operations": [
        {
            "date": "2025-04-27",
            "agents_recovered": ["pessimist", "skeptic"],
            "recovery_status": {
                "pessimist": "full_recovery",
                "skeptic": "minimal_recovery"
            }
        }
    ]

    "total_agents": 19,
    "last_updated": "2025-04-26",
    "memory_tag": "agent_registry_surface_finalized_20250426"
main
}
