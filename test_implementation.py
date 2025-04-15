"""
Test script for Kickass Agent Sprint implementation

This script tests the toolkit registry and CriticAgent implementation.
"""

import sys
import os
import json

# Add parent directory to path to allow imports
sys.path.append('/home/ubuntu/personal-ai-agent')

# Test toolkit registry
def test_toolkit_registry():
    print("\n=== Testing Toolkit Registry ===\n")
    
    try:
        # Import toolkit registry
        from toolkit.registry import get_toolkit, get_agent_role, format_tools_prompt
        
        # Test get_toolkit function
        print("Testing get_toolkit function...")
        
        # Test HAL toolkit
        hal_tools = get_toolkit("hal", "saas")
        print(f"HAL tools: {hal_tools}")
        assert "scope.shaper" in hal_tools, "HAL toolkit missing scope.shaper"
        assert "mvp.planner" in hal_tools, "HAL toolkit missing mvp.planner"
        assert "feature.writer" in hal_tools, "HAL toolkit missing feature.writer"
        assert "pricing.modeler" in hal_tools, "HAL toolkit missing pricing.modeler"
        
        # Test ASH toolkit
        ash_tools = get_toolkit("ash", "saas")
        print(f"ASH tools: {ash_tools}")
        assert "architecture.explainer" in ash_tools, "ASH toolkit missing architecture.explainer"
        assert "api.docifier" in ash_tools, "ASH toolkit missing api.docifier"
        assert "onboarding.writer" in ash_tools, "ASH toolkit missing onboarding.writer"
        
        # Test NOVA toolkit
        nova_tools = get_toolkit("nova", "saas")
        print(f"NOVA tools: {nova_tools}")
        assert "layout.builder" in nova_tools, "NOVA toolkit missing layout.builder"
        assert "tailwind.ui" in nova_tools, "NOVA toolkit missing tailwind.ui"
        assert "brand.style" in nova_tools, "NOVA toolkit missing brand.style"
        assert "copy.prompter" in nova_tools, "NOVA toolkit missing copy.prompter"
        
        # Test get_agent_role function
        print("\nTesting get_agent_role function...")
        
        # Test HAL role
        hal_role = get_agent_role("hal")
        print(f"HAL role: {hal_role}")
        assert hal_role == "SaaS Architect", f"HAL role incorrect: {hal_role}"
        
        # Test ASH role
        ash_role = get_agent_role("ash")
        print(f"ASH role: {ash_role}")
        assert ash_role == "Documentation & UX Explainer", f"ASH role incorrect: {ash_role}"
        
        # Test NOVA role
        nova_role = get_agent_role("nova")
        print(f"NOVA role: {nova_role}")
        assert nova_role == "UI Designer & Copy Generator", f"NOVA role incorrect: {nova_role}"
        
        # Test format_tools_prompt function
        print("\nTesting format_tools_prompt function...")
        
        # Test with HAL tools
        hal_prompt = format_tools_prompt(hal_tools)
        print(f"HAL prompt: {hal_prompt}")
        assert "scope.shaper" in hal_prompt, "HAL prompt missing scope.shaper"
        assert "mvp.planner" in hal_prompt, "HAL prompt missing mvp.planner"
        assert "feature.writer" in hal_prompt, "HAL prompt missing feature.writer"
        assert "pricing.modeler" in hal_prompt, "HAL prompt missing pricing.modeler"
        
        print("\n✅ Toolkit Registry tests passed!")
        return True
    
    except Exception as e:
        print(f"\n❌ Toolkit Registry test failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

# Test CriticAgent
def test_critic_agent():
    print("\n=== Testing CriticAgent ===\n")
    
    try:
        # Import CriticAgent
        from app.modules.review.critic_agent import CriticAgent
        
        # Create test goal and outputs
        goal = "Create a SaaS product for team collaboration"
        agent_outputs = {
            "hal": "I recommend building a real-time collaboration platform with the following features:\n1. Document editing with version control\n2. Task management with assignments\n3. Chat and video conferencing\n4. API for integrations\n\nThe architecture will use a microservices approach with separate services for each core feature.",
            "ash": "The platform should have a clear onboarding flow that guides new users through creating their first project. Documentation should include video tutorials for each feature and a comprehensive API reference.",
            "nova": "The UI should use a clean, minimal design with a blue and white color scheme. The layout should prioritize the document workspace with collapsible sidebars for chat and task management."
        }
        
        # Create agent
        print("Creating CriticAgent instance...")
        agent = CriticAgent()
        
        # Run the agent
        print("Running CriticAgent with test data...")
        result = agent.evaluate(goal, agent_outputs)
        
        # Print the result
        print(f"\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Reflection: {result.get('reflection', 'No reflection')[:100]}...")
        if "scores" in result:
            print(f"Scores: {json.dumps(result['scores'], indent=2)}")
        
        # Check result structure
        assert result.get("status") == "success", f"CriticAgent evaluation failed: {result.get('reflection')}"
        assert "reflection" in result, "CriticAgent result missing reflection"
        assert "scores" in result, "CriticAgent result missing scores"
        
        required_scores = ["technical_accuracy", "ux_clarity", "visual_design", "monetization_strategy"]
        for score in required_scores:
            assert score in result["scores"], f"CriticAgent result missing score: {score}"
            assert isinstance(result["scores"][score], (int, float)), f"CriticAgent score {score} is not a number"
            assert 0 <= result["scores"][score] <= 10, f"CriticAgent score {score} is not between 0 and 10"
        
        print("\n✅ CriticAgent tests passed!")
        return True
    
    except Exception as e:
        print(f"\n❌ CriticAgent test failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

# Create sample prompt logs
def create_sample_prompt_logs():
    print("\n=== Creating Sample Prompt Logs ===\n")
    
    try:
        # Import toolkit registry
        from toolkit.registry import get_toolkit, get_agent_role, format_tools_prompt
        
        # Get HAL toolkit and role
        hal_tools = get_toolkit("hal", "saas")
        hal_role = get_agent_role("hal")
        
        # Format tools prompt
        tools_prompt = format_tools_prompt(hal_tools)
        
        # Create sample system message
        system_message = f"You are a {hal_role}.\n\n{tools_prompt}"
        
        # Create sample user message
        user_message = "Design a SaaS product for team collaboration"
        
        # Create sample prompt logs
        prompt_logs = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }
        
        # Save prompt logs to file
        with open('/home/ubuntu/personal-ai-agent/sample_prompt_logs.json', 'w') as f:
            json.dump(prompt_logs, f, indent=2)
        
        print(f"Sample prompt logs saved to: /home/ubuntu/personal-ai-agent/sample_prompt_logs.json")
        print(f"System message: {system_message[:100]}...")
        
        print("\n✅ Sample prompt logs created!")
        return True
    
    except Exception as e:
        print(f"\n❌ Failed to create sample prompt logs: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Run tests
    toolkit_registry_success = test_toolkit_registry()
    critic_agent_success = test_critic_agent()
    prompt_logs_success = create_sample_prompt_logs()
    
    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"Toolkit Registry: {'✅ PASSED' if toolkit_registry_success else '❌ FAILED'}")
    print(f"CriticAgent: {'✅ PASSED' if critic_agent_success else '❌ FAILED'}")
    print(f"Sample Prompt Logs: {'✅ CREATED' if prompt_logs_success else '❌ FAILED'}")
    
    # Exit with appropriate status code
    if toolkit_registry_success and critic_agent_success and prompt_logs_success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
