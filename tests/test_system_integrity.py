import pytest
from datetime import datetime
from app.memory import PROJECT_MEMORY
from app.utils.schema_utils import validate_project_memory

def test_project_memory_schema():
    """
    Validate project memory against schema for all projects.
    """
    for pid in PROJECT_MEMORY:
        errors = validate_project_memory(pid, PROJECT_MEMORY)
        assert not errors, f"Schema errors for {pid}: {errors}"

def test_reflection_confidence():
    """
    Ensure reflection confidence is above minimum threshold.
    """
    for pid in PROJECT_MEMORY:
        if not PROJECT_MEMORY[pid].get("reflection_scores", []):
            pytest.skip(f"No reflection scores found for {pid}")
        
        score = PROJECT_MEMORY[pid].get("reflection_scores", [])[-1]["score"]
        assert score >= 0.6, f"Weak reflection in {pid}: {score}"

def test_snapshot_presence():
    """
    Verify that loop snapshots exist for all projects.
    """
    for pid in PROJECT_MEMORY:
        assert "last_snapshot" in PROJECT_MEMORY[pid], f"No snapshot found for {pid}"

def test_orchestrator_decisions():
    """
    Confirm orchestrator decisions exist and are traceable.
    """
    for pid in PROJECT_MEMORY:
        decisions = PROJECT_MEMORY[pid].get("orchestrator_decisions", [])
        assert decisions, f"No orchestrator decisions found for {pid}"
        
        # Check most recent decision has required fields
        if decisions:
            latest = decisions[-1]
            assert "timestamp" in latest, "Decision missing timestamp"
            assert "action" in latest, "Decision missing action"
            assert "reasoning" in latest, "Decision missing reasoning"

def test_system_health_score():
    """
    Verify CTO system health is above minimum threshold.
    """
    for pid in PROJECT_MEMORY:
        score = PROJECT_MEMORY[pid].get("system_health_score", 1.0)
        assert score > 0.6, f"System health warning for {pid}: {score}"

def test_drift_logs_status():
    """
    Confirm drift logs are empty or non-critical.
    """
    for pid in PROJECT_MEMORY:
        drift_logs = PROJECT_MEMORY[pid].get("drift_logs", [])
        
        # If there are drift logs, ensure they're not critical
        if drift_logs:
            critical_count = sum(1 for log in drift_logs if log.get("severity") == "critical")
            assert critical_count == 0, f"Critical drift logs found for {pid}: {critical_count}"

def test_agent_dependency_order():
    """
    Validate agents are triggered in correct dependency order.
    """
    from app.schema_registry import SCHEMA_REGISTRY
    
    for pid in PROJECT_MEMORY:
        agent_executions = PROJECT_MEMORY[pid].get("agent_executions", [])
        
        if not agent_executions:
            pytest.skip(f"No agent executions found for {pid}")
        
        # Build dependency map from schema registry
        dependency_map = {}
        for agent, config in SCHEMA_REGISTRY.get("agents", {}).items():
            dependency_map[agent] = config.get("dependencies", [])
        
        # Check each agent execution against its dependencies
        executed_agents = set()
        for execution in agent_executions:
            agent = execution.get("agent")
            if agent:
                # Check if all dependencies were executed before this agent
                dependencies = dependency_map.get(agent, [])
                for dep in dependencies:
                    assert dep in executed_agents, f"Agent {agent} executed before its dependency {dep} in {pid}"
                executed_agents.add(agent)

def test_loop_snapshot_consistency():
    """
    Check loop snapshot consistency across time.
    """
    for pid in PROJECT_MEMORY:
        snapshots = PROJECT_MEMORY[pid].get("loop_snapshots", [])
        
        if len(snapshots) < 2:
            pytest.skip(f"Not enough snapshots for consistency check in {pid}")
        
        # Check that loop counts are sequential
        for i in range(1, len(snapshots)):
            prev_loop = snapshots[i-1].get("loop_count", 0)
            curr_loop = snapshots[i].get("loop_count", 0)
            assert curr_loop > prev_loop, f"Non-sequential loop counts in {pid}: {prev_loop} -> {curr_loop}"

def test_memory_growth_rate():
    """
    Ensure memory growth rate is within acceptable limits.
    """
    import sys
    import json
    
    for pid in PROJECT_MEMORY:
        # Estimate memory size by serializing to JSON
        memory_size = sys.getsizeof(json.dumps(PROJECT_MEMORY[pid]))
        
        # Check if memory size is tracked
        size_history = PROJECT_MEMORY[pid].get("memory_size_history", [])
        
        if not size_history:
            # Start tracking memory size
            PROJECT_MEMORY[pid]["memory_size_history"] = [
                {"timestamp": datetime.utcnow().isoformat(), "size": memory_size}
            ]
            pytest.skip(f"Started tracking memory size for {pid}")
        
        # Add current size to history
        PROJECT_MEMORY[pid]["memory_size_history"].append(
            {"timestamp": datetime.utcnow().isoformat(), "size": memory_size}
        )
        
        # Check growth rate if we have enough history
        if len(size_history) >= 5:
            initial_size = size_history[-5]["size"]
            growth_rate = (memory_size - initial_size) / initial_size
            
            # Alert if memory has more than doubled in last 5 measurements
            assert growth_rate < 1.0, f"Excessive memory growth in {pid}: {growth_rate:.2f}x increase"
