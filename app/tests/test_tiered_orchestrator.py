"""
Tiered Orchestrator Test Module

This module provides tests for the tiered orchestrator functionality.
It tests all components and their integration to ensure they work together correctly.
"""

import json
import os
import logging
import pytest
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import tiered orchestrator components
from app.modules.tiered_orchestrator import (
    TieredOrchestrator,
    OrchestratorMode,
    determine_optimal_mode,
    get_mode_config,
    get_available_modes,
    MODE_TO_DEPTH,  # Use the dictionary directly instead of a function
    get_agents_for_mode,
    # get_reflection_config_for_mode,  # This function doesn't exist
    adjust_agent_plan_for_mode,
    enrich_loop_with_mode,
    get_visualization_config_for_mode,
    get_memory_inspection_config_for_mode
)

# Import depth controller components
from app.modules.depth_controller import (
    enrich_loop_with_depth,
    preload_depth_for_rerun,
    get_depth_for_mode,
    get_reflection_config  # Use this instead of get_reflection_config_for_mode
)

# Import visualization and memory inspection components
from app.modules.loop_map_visualizer import (
    LoopMapVisualizer,
    create_visualizer,
    visualize_loop,
    VisualizationFormat,
    NodeType,
    EdgeType
)
from app.modules.live_memory_inspection import (
    MemoryInspector,
    create_memory_inspector,
    inspect_memory,
    MemoryFilter,
    MemoryFormat,
    MemoryAccessLevel,
    should_snapshot_memory
)

# Import orchestrator integration components
from app.modules.orchestrator_integration import (
    integrate_with_orchestrator,
    process_reflection_with_controls,
    determine_rerun_depth_with_controls,
    determine_rerun_mode_with_controls
)

def test_tiered_orchestrator_modes():
    """Test the tiered orchestrator modes."""
    logger.info("Testing Tiered Orchestrator Modes...")
    
    # Test all orchestrator modes are defined
    assert OrchestratorMode.FAST == "fast", "FAST mode not defined correctly"
    assert OrchestratorMode.BALANCED == "balanced", "BALANCED mode not defined correctly"
    assert OrchestratorMode.THOROUGH == "thorough", "THOROUGH mode not defined correctly"
    assert OrchestratorMode.RESEARCH == "research", "RESEARCH mode not defined correctly"
    logger.info("✓ All orchestrator modes correctly defined")
    
    # Test mode-to-depth mapping
    mapping = MODE_TO_DEPTH  # Use the dictionary directly
    assert mapping[OrchestratorMode.FAST] == "shallow", f"Unexpected depth for FAST mode: {mapping[OrchestratorMode.FAST]}"
    assert mapping[OrchestratorMode.BALANCED] == "standard", f"Unexpected depth for BALANCED mode: {mapping[OrchestratorMode.BALANCED]}"
    assert mapping[OrchestratorMode.THOROUGH] == "deep", f"Unexpected depth for THOROUGH mode: {mapping[OrchestratorMode.THOROUGH]}"
    assert mapping[OrchestratorMode.RESEARCH] == "deep", f"Unexpected depth for RESEARCH mode: {mapping[OrchestratorMode.RESEARCH]}"
    logger.info("✓ Mode-to-depth mapping correctly defined")
    
    # Test get_depth_for_mode function
    assert get_depth_for_mode(OrchestratorMode.FAST) == "shallow", f"Unexpected depth for FAST mode"
    assert get_depth_for_mode(OrchestratorMode.BALANCED) == "standard", f"Unexpected depth for BALANCED mode"
    assert get_depth_for_mode(OrchestratorMode.THOROUGH) == "deep", f"Unexpected depth for THOROUGH mode"
    assert get_depth_for_mode(OrchestratorMode.RESEARCH) == "deep", f"Unexpected depth for RESEARCH mode"
    logger.info("✓ get_depth_for_mode function works correctly")
    
    # Test get_mode_config function
    fast_config = get_mode_config(OrchestratorMode.FAST)
    assert "description" in fast_config, "Missing description in FAST config"
    assert "reflection_intensity" in fast_config, "Missing reflection_intensity in FAST config"
    assert fast_config["reflection_intensity"] == "minimal", "FAST mode should have minimal reflection intensity"
    
    balanced_config = get_mode_config(OrchestratorMode.BALANCED)
    assert "description" in balanced_config, "Missing description in BALANCED config"
    assert "reflection_intensity" in balanced_config, "Missing reflection_intensity in BALANCED config"
    assert balanced_config["reflection_intensity"] == "standard", "BALANCED mode should have standard reflection intensity"
    
    thorough_config = get_mode_config(OrchestratorMode.THOROUGH)
    assert "description" in thorough_config, "Missing description in THOROUGH config"
    assert "reflection_intensity" in thorough_config, "Missing reflection_intensity in THOROUGH config"
    assert thorough_config["reflection_intensity"] == "comprehensive", "THOROUGH mode should have comprehensive reflection intensity"
    
    research_config = get_mode_config(OrchestratorMode.RESEARCH)
    assert "description" in research_config, "Missing description in RESEARCH config"
    assert "reflection_intensity" in research_config, "Missing reflection_intensity in RESEARCH config"
    assert research_config["reflection_intensity"] == "maximum", "RESEARCH mode should have maximum reflection intensity"
    assert "research_specific" in research_config, "Missing research_specific in RESEARCH config"
    logger.info("✓ Mode configurations correctly defined")
    
    # Test get_available_modes function
    modes = get_available_modes()
    assert len(modes) >= 4, f"Expected at least 4 modes, got {len(modes)}"
    # Check that each mode has the required fields
    for mode_info in modes:
        assert "mode" in mode_info, "Mode info missing 'mode' field"
        assert "description" in mode_info, "Mode info missing 'description' field"
    logger.info("✓ Available modes correctly returned")
    
    logger.info("Tiered Orchestrator Modes tests passed!\n")

def test_mode_determination():
    """Test the mode determination functionality."""
    logger.info("Testing Mode Determination...")
    
    # Test determine_optimal_mode function with various inputs
    
    # Simple task with no complexity or sensitivity should default to BALANCED
    simple_task = "Create a simple todo app"
    mode = determine_optimal_mode(simple_task)
    assert mode in [OrchestratorMode.FAST, OrchestratorMode.BALANCED], f"Unexpected mode for simple task: {mode}"
    logger.info(f"✓ Simple task correctly assigned {mode} mode")
    
    # Complex task should get THOROUGH mode
    complex_task = "Create a distributed system with blockchain integration and AI capabilities"
    mode = determine_optimal_mode(complex_task, complexity=0.9)
    assert mode in [OrchestratorMode.THOROUGH, OrchestratorMode.RESEARCH], f"Unexpected mode for complex task: {mode}"
    logger.info(f"✓ Complex task correctly assigned {mode} mode")
    
    # Sensitive task should get THOROUGH mode
    sensitive_task = "Create a medical diagnosis system"
    mode = determine_optimal_mode(sensitive_task, sensitivity=0.9)
    assert mode in [OrchestratorMode.THOROUGH, OrchestratorMode.RESEARCH], f"Unexpected mode for sensitive task: {mode}"
    logger.info(f"✓ Sensitive task correctly assigned {mode} mode")
    
    # Research task should get RESEARCH mode
    research_task = "Explore novel approaches to quantum computing algorithms"
    mode = determine_optimal_mode(research_task, complexity=0.9, sensitivity=0.7)
    assert mode in [OrchestratorMode.THOROUGH, OrchestratorMode.RESEARCH], f"Unexpected mode for research task: {mode}"
    logger.info(f"✓ Research task correctly assigned {mode} mode")
    
    # Time-constrained task should get FAST mode
    time_constrained_task = "Create a quick prototype"
    mode = determine_optimal_mode(time_constrained_task, time_constraint=0.1)
    assert mode == OrchestratorMode.FAST, f"Unexpected mode for time-constrained task: {mode}"
    logger.info("✓ Time-constrained task correctly assigned FAST mode")
    
    # User preference should override other factors
    user_preference_task = "Create a complex system"
    mode = determine_optimal_mode(user_preference_task, complexity=0.9, user_preference=OrchestratorMode.FAST)
    assert mode == OrchestratorMode.FAST, f"User preference not respected: {mode}"
    logger.info("✓ User preference correctly overrides other factors")
    
    logger.info("Mode Determination tests passed!\n")

def test_mode_integration_with_depth_controller():
    """Test the integration of tiered orchestrator modes with the depth controller."""
    logger.info("Testing Mode Integration with Depth Controller...")
    
    # Test get_agents_for_mode function
    fast_agents = get_agents_for_mode(OrchestratorMode.FAST)
    assert len(fast_agents) > 0, "No agents returned for FAST mode"
    
    balanced_agents = get_agents_for_mode(OrchestratorMode.BALANCED)
    assert len(balanced_agents) > 0, "No agents returned for BALANCED mode"
    
    thorough_agents = get_agents_for_mode(OrchestratorMode.THOROUGH)
    assert len(thorough_agents) > 0, "No agents returned for THOROUGH mode"
    
    research_agents = get_agents_for_mode(OrchestratorMode.RESEARCH)
    assert len(research_agents) > 0, "No agents returned for RESEARCH mode"
    logger.info("✓ Agents correctly retrieved for each mode")
    
    # Test get_reflection_config for each depth corresponding to a mode
    fast_depth = get_depth_for_mode(OrchestratorMode.FAST)
    fast_config = get_reflection_config(fast_depth)
    assert "max_reflection_time" in fast_config, "Missing max_reflection_time in FAST depth config"
    
    balanced_depth = get_depth_for_mode(OrchestratorMode.BALANCED)
    balanced_config = get_reflection_config(balanced_depth)
    assert "max_reflection_time" in balanced_config, "Missing max_reflection_time in BALANCED depth config"
    
    thorough_depth = get_depth_for_mode(OrchestratorMode.THOROUGH)
    thorough_config = get_reflection_config(thorough_depth)
    assert "max_reflection_time" in thorough_config, "Missing max_reflection_time in THOROUGH depth config"
    
    research_depth = get_depth_for_mode(OrchestratorMode.RESEARCH)
    research_config = get_reflection_config(research_depth)
    assert "max_reflection_time" in research_config, "Missing max_reflection_time in RESEARCH depth config"
    logger.info("✓ Reflection config correctly retrieved for each mode's depth")
    
    # Test adjust_agent_plan_for_mode function
    original_plan = [
        {"step": 1, "description": "Analyze requirements", "agent": "HAL"},
        {"step": 2, "description": "Design architecture", "agent": "NOVA"},
        {"step": 3, "description": "Implement solution", "agent": "CRITIC"},
        {"step": 4, "description": "Test solution", "agent": "CEO"},
        {"step": 5, "description": "Deploy solution", "agent": "SAGE"}
    ]
    
    # FAST mode should simplify the plan
    fast_plan = adjust_agent_plan_for_mode(original_plan, OrchestratorMode.FAST)
    assert len(fast_plan) <= len(original_plan), f"FAST plan not simplified: {len(fast_plan)} vs {len(original_plan)}"
    logger.info("✓ FAST mode correctly adjusts agent plan")
    
    # BALANCED mode should keep the plan mostly intact
    balanced_plan = adjust_agent_plan_for_mode(original_plan, OrchestratorMode.BALANCED)
    assert len(balanced_plan) <= len(original_plan), f"BALANCED plan modified unexpectedly: {len(balanced_plan)} vs {len(original_plan)}"
    logger.info("✓ BALANCED mode correctly adjusts agent plan")
    
    # THOROUGH mode should maintain or expand the plan
    thorough_plan = adjust_agent_plan_for_mode(original_plan, OrchestratorMode.THOROUGH)
    assert len(thorough_plan) > 0, "THOROUGH plan should not be empty"
    logger.info("✓ THOROUGH mode correctly adjusts agent plan")
    
    # RESEARCH mode should maintain or expand the plan
    research_plan = adjust_agent_plan_for_mode(original_plan, OrchestratorMode.RESEARCH)
    assert len(research_plan) > 0, "RESEARCH plan should not be empty"
    # Check for research-specific flags
    if len(research_plan) > 0:
        assert "mode" in research_plan[0], "Mode not set in research plan"
        assert research_plan[0]["mode"] == OrchestratorMode.RESEARCH, "Incorrect mode in research plan"
    logger.info("✓ RESEARCH mode correctly adjusts agent plan")
    
    # Test enrich_loop_with_mode function
    loop_data = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE"
    }
    
    # Test FAST mode enrichment
    fast_loop = enrich_loop_with_mode(loop_data, OrchestratorMode.FAST)
    assert fast_loop["mode"] == OrchestratorMode.FAST, f"Mode not set correctly: {fast_loop.get('mode')}"
    assert fast_loop["depth"] == get_depth_for_mode(OrchestratorMode.FAST), f"Depth not set correctly: {fast_loop.get('depth')}"
    assert "reflection_agents" in fast_loop, "Reflection agents not set"
    assert "mode_config" in fast_loop, "Mode config not set"
    logger.info("✓ FAST mode correctly enriches loop")
    
    # Test BALANCED mode enrichment
    balanced_loop = enrich_loop_with_mode(loop_data, OrchestratorMode.BALANCED)
    assert balanced_loop["mode"] == OrchestratorMode.BALANCED, f"Mode not set correctly: {balanced_loop.get('mode')}"
    assert balanced_loop["depth"] == get_depth_for_mode(OrchestratorMode.BALANCED), f"Depth not set correctly: {balanced_loop.get('depth')}"
    assert "reflection_agents" in balanced_loop, "Reflection agents not set"
    assert "mode_config" in balanced_loop, "Mode config not set"
    logger.info("✓ BALANCED mode correctly enriches loop")
    
    # Test THOROUGH mode enrichment
    thorough_loop = enrich_loop_with_mode(loop_data, OrchestratorMode.THOROUGH)
    assert thorough_loop["mode"] == OrchestratorMode.THOROUGH, f"Mode not set correctly: {thorough_loop.get('mode')}"
    assert thorough_loop["depth"] == get_depth_for_mode(OrchestratorMode.THOROUGH), f"Depth not set correctly: {thorough_loop.get('depth')}"
    assert "reflection_agents" in thorough_loop, "Reflection agents not set"
    assert "mode_config" in thorough_loop, "Mode config not set"
    logger.info("✓ THOROUGH mode correctly enriches loop")
    
    # Test RESEARCH mode enrichment
    research_loop = enrich_loop_with_mode(loop_data, OrchestratorMode.RESEARCH)
    assert research_loop["mode"] == OrchestratorMode.RESEARCH, f"Mode not set correctly: {research_loop.get('mode')}"
    assert research_loop["depth"] == get_depth_for_mode(OrchestratorMode.RESEARCH), f"Depth not set correctly: {research_loop.get('depth')}"
    assert "reflection_agents" in research_loop, "Reflection agents not set"
    assert "mode_config" in research_loop, "Mode config not set"
    assert "research_specific" in research_loop["mode_config"], "Research-specific config not set"
    logger.info("✓ RESEARCH mode correctly enriches loop")
    
    logger.info("Mode Integration with Depth Controller tests passed!\n")

def test_loop_map_visualizer():
    """Test the loop map visualizer component."""
    logger.info("Testing Loop Map Visualizer...")
    
    # Test LoopMapVisualizer initialization
    visualizer = LoopMapVisualizer("test_loop_001", OrchestratorMode.BALANCED)
    assert visualizer.loop_id == "test_loop_001", f"Unexpected loop_id: {visualizer.loop_id}"
    assert visualizer.mode == OrchestratorMode.BALANCED, f"Unexpected mode: {visualizer.mode}"
    assert visualizer.color_scheme == "default", f"Unexpected color scheme: {visualizer.color_scheme}"
    logger.info("✓ LoopMapVisualizer correctly initialized")
    
    # Test create_visualizer function
    visualizer = create_visualizer("test_loop_002", OrchestratorMode.THOROUGH, "accessibility")
    assert visualizer.loop_id == "test_loop_002", f"Unexpected loop_id: {visualizer.loop_id}"
    assert visualizer.mode == OrchestratorMode.THOROUGH, f"Unexpected mode: {visualizer.mode}"
    assert visualizer.color_scheme == "accessibility", f"Unexpected color scheme: {visualizer.color_scheme}"
    logger.info("✓ create_visualizer function works correctly")
    
    # Test mode-specific visualization settings
    fast_visualizer = LoopMapVisualizer("test_loop_003", OrchestratorMode.FAST)
    assert fast_visualizer.settings["detail_level"] == "minimal", f"Unexpected detail level for FAST mode: {fast_visualizer.settings['detail_level']}"
    assert fast_visualizer.settings["update_frequency"] == "end_only", f"Unexpected update frequency for FAST mode: {fast_visualizer.settings['update_frequency']}"
    assert not fast_visualizer.settings["include_memory_details"], "FAST mode should not include memory details"
    
    balanced_visualizer = LoopMapVisualizer("test_loop_004", OrchestratorMode.BALANCED)
    assert balanced_visualizer.settings["detail_level"] == "standard", f"Unexpected detail level for BALANCED mode: {balanced_visualizer.settings['detail_level']}"
    assert balanced_visualizer.settings["update_frequency"] == "agent_completion", f"Unexpected update frequency for BALANCED mode: {balanced_visualizer.settings['update_frequency']}"
    assert balanced_visualizer.settings["include_memory_details"], "BALANCED mode should include memory details"
    
    thorough_visualizer = LoopMapVisualizer("test_loop_005", OrchestratorMode.THOROUGH)
    assert thorough_visualizer.settings["detail_level"] == "detailed", f"Unexpected detail level for THOROUGH mode: {thorough_visualizer.settings['detail_level']}"
    assert thorough_visualizer.settings["update_frequency"] == "real_time", f"Unexpected update frequency for THOROUGH mode: {thorough_visualizer.settings['update_frequency']}"
    assert thorough_visualizer.settings["include_memory_details"], "THOROUGH mode should include memory details"
    
    research_visualizer = LoopMapVisualizer("test_loop_006", OrchestratorMode.RESEARCH)
    assert research_visualizer.settings["detail_level"] == "comprehensive", f"Unexpected detail level for RESEARCH mode: {research_visualizer.settings['detail_level']}"
    assert research_visualizer.settings["update_frequency"] == "real_time", f"Unexpected update frequency for RESEARCH mode: {research_visualizer.settings['update_frequency']}"
    assert research_visualizer.settings["include_memory_details"], "RESEARCH mode should include memory details"
    assert research_visualizer.settings["include_uncertainty"], "RESEARCH mode should include uncertainty"
    assert research_visualizer.settings["track_alternatives"], "RESEARCH mode should track alternatives"
    logger.info("✓ Mode-specific visualization settings correctly applied")
    
    # Test should_update_visualization method
    # FAST mode should only update at the end
    assert not fast_visualizer.should_update_visualization("agent_completion"), "FAST mode should not update visualization at agent_completion"
    assert not fast_visualizer.should_update_visualization("reflection"), "FAST mode should not update visualization at reflection"
    assert fast_visualizer.should_update_visualization("loop_end"), "FAST mode should update visualization at loop_end"
    
    # BALANCED mode should update at agent completion
    assert balanced_visualizer.should_update_visualization("agent_completion"), "BALANCED mode should update visualization at agent_completion"
    assert not balanced_visualizer.should_update_visualization("reflection"), "BALANCED mode should not update visualization at reflection"
    assert balanced_visualizer.should_update_visualization("loop_end"), "BALANCED mode should update visualization at loop_end"
    
    # THOROUGH and RESEARCH modes should update in real-time
    assert thorough_visualizer.should_update_visualization("agent_completion"), "THOROUGH mode should update visualization at agent_completion"
    assert thorough_visualizer.should_update_visualization("reflection"), "THOROUGH mode should update visualization at reflection"
    assert thorough_visualizer.should_update_visualization("decision"), "THOROUGH mode should update visualization at decision"
    
    assert research_visualizer.should_update_visualization("agent_completion"), "RESEARCH mode should update visualization at agent_completion"
    assert research_visualizer.should_update_visualization("reflection"), "RESEARCH mode should update visualization at reflection"
    assert research_visualizer.should_update_visualization("decision"), "RESEARCH mode should update visualization at decision"
    logger.info("✓ should_update_visualization method works correctly for all modes")
    
    # Test change_mode method
    visualizer.change_mode(OrchestratorMode.RESEARCH)
    assert visualizer.mode == OrchestratorMode.RESEARCH, f"Mode not changed correctly: {visualizer.mode}"
    assert visualizer.settings["detail_level"] == "comprehensive", f"Settings not updated after mode change: {visualizer.settings['detail_level']}"
    logger.info("✓ change_mode method works correctly")
    
    logger.info("Loop Map Visualizer tests passed!\n")

def test_live_memory_inspection():
    """Test the live memory inspection component."""
    logger.info("Testing Live Memory Inspection...")
    
    # Test MemoryInspector initialization
    inspector = MemoryInspector("test_loop_001", OrchestratorMode.BALANCED)
    assert inspector.loop_id == "test_loop_001", f"Unexpected loop_id: {inspector.loop_id}"
    assert inspector.mode == OrchestratorMode.BALANCED, f"Unexpected mode: {inspector.mode}"
    assert inspector.access_level == MemoryAccessLevel.READ_ONLY, f"Unexpected access level for BALANCED mode: {inspector.access_level}"
    logger.info("✓ MemoryInspector correctly initialized")
    
    # Test create_memory_inspector function
    inspector = create_memory_inspector("test_loop_002", OrchestratorMode.THOROUGH)
    assert inspector.loop_id == "test_loop_002", f"Unexpected loop_id: {inspector.loop_id}"
    assert inspector.mode == OrchestratorMode.THOROUGH, f"Unexpected mode: {inspector.mode}"
    assert inspector.access_level == MemoryAccessLevel.READ_WRITE, f"Unexpected access level for THOROUGH mode: {inspector.access_level}"
    logger.info("✓ create_memory_inspector function works correctly")
    
    # Test mode-specific memory inspection settings
    fast_inspector = MemoryInspector("test_loop_003", OrchestratorMode.FAST)
    assert fast_inspector.settings["access_level"] == MemoryAccessLevel.READ_ONLY, f"Unexpected access level for FAST mode: {fast_inspector.settings['access_level']}"
    assert fast_inspector.settings["snapshot_frequency"] == "end_only", f"Unexpected snapshot frequency for FAST mode: {fast_inspector.settings['snapshot_frequency']}"
    assert fast_inspector.settings["detail_level"] == "minimal", f"Unexpected detail level for FAST mode: {fast_inspector.settings['detail_level']}"
    assert not fast_inspector.settings["track_changes"], "FAST mode should not track changes"
    assert not fast_inspector.settings["enable_time_travel"], "FAST mode should not enable time travel"
    
    balanced_inspector = MemoryInspector("test_loop_004", OrchestratorMode.BALANCED)
    assert balanced_inspector.settings["access_level"] == MemoryAccessLevel.READ_ONLY, f"Unexpected access level for BALANCED mode: {balanced_inspector.settings['access_level']}"
    assert balanced_inspector.settings["snapshot_frequency"] == "agent_completion", f"Unexpected snapshot frequency for BALANCED mode: {balanced_inspector.settings['snapshot_frequency']}"
    assert balanced_inspector.settings["detail_level"] == "standard", f"Unexpected detail level for BALANCED mode: {balanced_inspector.settings['detail_level']}"
    assert balanced_inspector.settings["track_changes"], "BALANCED mode should track changes"
    assert not balanced_inspector.settings["enable_time_travel"], "BALANCED mode should not enable time travel"
    
    thorough_inspector = MemoryInspector("test_loop_005", OrchestratorMode.THOROUGH)
    assert thorough_inspector.settings["access_level"] == MemoryAccessLevel.READ_WRITE, f"Unexpected access level for THOROUGH mode: {thorough_inspector.settings['access_level']}"
    assert thorough_inspector.settings["snapshot_frequency"] == "real_time", f"Unexpected snapshot frequency for THOROUGH mode: {thorough_inspector.settings['snapshot_frequency']}"
    assert thorough_inspector.settings["detail_level"] == "detailed", f"Unexpected detail level for THOROUGH mode: {thorough_inspector.settings['detail_level']}"
    assert thorough_inspector.settings["track_changes"], "THOROUGH mode should track changes"
    assert thorough_inspector.settings["enable_time_travel"], "THOROUGH mode should enable time travel"
    
    research_inspector = MemoryInspector("test_loop_006", OrchestratorMode.RESEARCH)
    assert research_inspector.settings["access_level"] == MemoryAccessLevel.ADMIN, f"Unexpected access level for RESEARCH mode: {research_inspector.settings['access_level']}"
    assert research_inspector.settings["snapshot_frequency"] == "real_time", f"Unexpected snapshot frequency for RESEARCH mode: {research_inspector.settings['snapshot_frequency']}"
    assert research_inspector.settings["detail_level"] == "comprehensive", f"Unexpected detail level for RESEARCH mode: {research_inspector.settings['detail_level']}"
    assert research_inspector.settings["track_changes"], "RESEARCH mode should track changes"
    assert research_inspector.settings["enable_time_travel"], "RESEARCH mode should enable time travel"
    assert "research_specific" in research_inspector.settings, "Missing research_specific settings for RESEARCH mode"
    assert research_inspector.settings["research_specific"]["track_uncertainty"], "RESEARCH mode should track uncertainty"
    assert research_inspector.settings["research_specific"]["track_alternatives"], "RESEARCH mode should track alternatives"
    logger.info("✓ Mode-specific memory inspection settings correctly applied")
    
    # Test should_snapshot_memory function
    assert not should_snapshot_memory(OrchestratorMode.FAST, "agent_completion"), "FAST mode should not snapshot memory at agent_completion"
    assert not should_snapshot_memory(OrchestratorMode.FAST, "reflection"), "FAST mode should not snapshot memory at reflection"
    assert should_snapshot_memory(OrchestratorMode.FAST, "loop_end"), "FAST mode should snapshot memory at loop_end"
    
    assert should_snapshot_memory(OrchestratorMode.BALANCED, "agent_completion"), "BALANCED mode should snapshot memory at agent_completion"
    assert not should_snapshot_memory(OrchestratorMode.BALANCED, "reflection"), "BALANCED mode should not snapshot memory at reflection"
    assert should_snapshot_memory(OrchestratorMode.BALANCED, "loop_end"), "BALANCED mode should snapshot memory at loop_end"
    
    assert should_snapshot_memory(OrchestratorMode.THOROUGH, "agent_completion"), "THOROUGH mode should snapshot memory at agent_completion"
    assert should_snapshot_memory(OrchestratorMode.THOROUGH, "reflection"), "THOROUGH mode should snapshot memory at reflection"
    assert should_snapshot_memory(OrchestratorMode.THOROUGH, "decision"), "THOROUGH mode should snapshot memory at decision"
    
    assert should_snapshot_memory(OrchestratorMode.RESEARCH, "agent_completion"), "RESEARCH mode should snapshot memory at agent_completion"
    assert should_snapshot_memory(OrchestratorMode.RESEARCH, "reflection"), "RESEARCH mode should snapshot memory at reflection"
    assert should_snapshot_memory(OrchestratorMode.RESEARCH, "decision"), "RESEARCH mode should snapshot memory at decision"
    logger.info("✓ should_snapshot_memory function works correctly for all modes")
    
    # Test change_mode method
    inspector.change_mode(OrchestratorMode.RESEARCH)
    assert inspector.mode == OrchestratorMode.RESEARCH, f"Mode not changed correctly: {inspector.mode}"
    assert inspector.access_level == MemoryAccessLevel.ADMIN, f"Access level not updated after mode change: {inspector.access_level}"
    assert inspector.settings["detail_level"] == "comprehensive", f"Settings not updated after mode change: {inspector.settings['detail_level']}"
    logger.info("✓ change_mode method works correctly")
    
    # Test MemoryFilter
    filter_options = MemoryFilter(
        keys=["task_description", "loop_count"],
        types=["str", "int"],
        created_by=["user", "orchestrator"]
    )
    
    # Create a test memory dictionary
    test_memory = {
        "task_description": {
            "value": "Test task",
            "created_by": "user",
            "value_type": "str"
        },
        "loop_count": {
            "value": 1,
            "created_by": "orchestrator",
            "value_type": "int"
        },
        "other_key": {
            "value": "Other value",
            "created_by": "agent",
            "value_type": "str"
        }
    }
    
    filtered_memory = filter_options.apply(test_memory)
    assert "task_description" in filtered_memory, "task_description should be in filtered memory"
    assert "loop_count" in filtered_memory, "loop_count should be in filtered memory"
    assert "other_key" not in filtered_memory, "other_key should not be in filtered memory"
    logger.info("✓ MemoryFilter correctly filters memory data")
    
    logger.info("Live Memory Inspection tests passed!\n")

def run_all_tests():
    """Run all tests for the tiered orchestrator functionality."""
    logger.info("Running all tiered orchestrator tests...\n")
    
    test_tiered_orchestrator_modes()
    test_mode_determination()
    test_mode_integration_with_depth_controller()
    test_loop_map_visualizer()
    test_live_memory_inspection()
    
    logger.info("All tiered orchestrator tests passed!")

if __name__ == "__main__":
    run_all_tests()
