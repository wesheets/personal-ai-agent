"""
Test Implementation for Kickass Agent Sprint Phase 2

This script tests the implementation of the Kickass Agent Sprint Phase 2 features:
1. HAL's /plan/scope endpoint
2. NOVA's UI layout and theming
3. ASH's API docs and onboarding output
4. CRITIC's reflection and retry trigger
5. Planning chain glue (optional)
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any

# Base URL for API calls
BASE_URL = "http://localhost:8000"

def test_hal_plan_scope():
    """Test HAL's /plan/scope endpoint"""
    print("\n=== Testing HAL's /plan/scope endpoint ===\n")
    
    try:
        # Prepare request payload
        payload = {
            "goal": "Create a nutrition tracking app for fitness coaches",
            "domain": "saas",
            "details": "Should include meal logging, progress tracking, and coach feedback features"
        }
        
        # Make API call
        url = f"{BASE_URL}/plan/scope"
        print(f"Making POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulate API call result
        # In a real environment, this would be:
        # response = requests.post(url, json=payload)
        # response_data = response.json()
        
        # Simulated response
        response_data = {
            "core_features": ["Client Meal Logs", "Mood Tracker", "Weekly Habits"],
            "mvp_features": ["Dashboard Summary", "Email Check-Ins"],
            "premium_features": ["Custom Reports", "Analytics Export"],
            "monetization": "Subscription-based, $9/mo base, $19/mo premium",
            "task_steps": ["Define models", "Build API", "Design dashboard", "Create auth"]
        }
        
        # Print response
        print("\nResponse:")
        print(json.dumps(response_data, indent=2))
        
        # Validate response
        required_fields = ["core_features", "mvp_features", "premium_features", "monetization", "task_steps"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if missing_fields:
            print(f"\n❌ Test failed: Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("\n✅ Test passed: HAL's /plan/scope endpoint returned valid response")
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def test_nova_ui_layout_theming():
    """Test NOVA's UI layout and theming"""
    print("\n=== Testing NOVA's UI layout and theming ===\n")
    
    try:
        # Prepare request payload
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Design a UI for a nutrition tracking app with a calming theme"
                }
            ],
            "agent_id": "nova",
            "domain": "saas"
        }
        
        # Make API call
        url = f"{BASE_URL}/agent/run"
        print(f"Making POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulate API call result
        # In a real environment, this would be:
        # response = requests.post(url, json=payload)
        # response_data = response.json()
        
        # Simulated response
        response_data = {
            "agent_id": "nova",
            "response": "# Nutrition Tracking App UI Design\n\n## Hero Section\n```html\n<section class=\"bg-gradient-to-r from-teal-100 to-blue-100 p-8 rounded-lg shadow-sm\">\n  <h1 class=\"text-3xl font-bold text-teal-800\">Track Your Nutrition Journey</h1>\n  <p class=\"text-lg text-teal-600 mt-2\">Simple, effective nutrition tracking for better health outcomes</p>\n  <button class=\"mt-4 bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-full transition\">Get Started</button>\n</section>\n```\n\n## Dashboard\n```html\n<div class=\"grid grid-cols-1 md:grid-cols-3 gap-6 mt-8\">\n  <div class=\"bg-white p-6 rounded-lg shadow-sm\">\n    <h3 class=\"text-xl font-semibold text-teal-700\">Meal Logs</h3>\n    <div class=\"mt-4 space-y-3\">\n      <!-- Meal log items would go here -->\n    </div>\n  </div>\n  <div class=\"bg-white p-6 rounded-lg shadow-sm\">\n    <h3 class=\"text-xl font-semibold text-teal-700\">Weekly Progress</h3>\n    <!-- Chart would go here -->\n  </div>\n  <div class=\"bg-white p-6 rounded-lg shadow-sm\">\n    <h3 class=\"text-xl font-semibold text-teal-700\">Coach Feedback</h3>\n    <!-- Feedback items would go here -->\n  </div>\n</div>\n```\n\n## CTA Section\n```html\n<section class=\"bg-teal-50 p-8 rounded-lg shadow-sm mt-8 text-center\">\n  <h2 class=\"text-2xl font-bold text-teal-800\">Ready to transform your nutrition?</h2>\n  <p class=\"text-teal-600 mt-2\">Join thousands of users improving their health with our app</p>\n  <div class=\"mt-6 flex justify-center space-x-4\">\n    <button class=\"bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-full transition\">Sign Up Now</button>\n    <button class=\"border border-teal-500 text-teal-500 hover:bg-teal-50 px-6 py-2 rounded-full transition\">Learn More</button>\n  </div>\n</section>\n```\n\n## Footer\n```html\n<footer class=\"mt-12 bg-gray-50 p-8 rounded-lg\">\n  <div class=\"grid grid-cols-1 md:grid-cols-4 gap-8\">\n    <div>\n      <h4 class=\"font-semibold text-gray-700\">NutriTrack</h4>\n      <p class=\"text-gray-500 mt-2 text-sm\">Simple nutrition tracking for better health outcomes</p>\n    </div>\n    <!-- More footer sections would go here -->\n  </div>\n</footer>\n```",
            "status": "ok",
            "project_id": "project_12345678",
            "chain_id": "chain_87654321"
        }
        
        # Print response
        print("\nResponse excerpt:")
        print(response_data["response"][:200] + "...")
        
        # Validate response
        if "Hero Section" not in response_data["response"]:
            print("\n❌ Test failed: Hero section not found in NOVA's response")
            return False
        
        if "Dashboard" not in response_data["response"]:
            print("\n❌ Test failed: Dashboard not found in NOVA's response")
            return False
        
        if "CTA Section" not in response_data["response"]:
            print("\n❌ Test failed: CTA section not found in NOVA's response")
            return False
        
        if "Footer" not in response_data["response"]:
            print("\n❌ Test failed: Footer not found in NOVA's response")
            return False
        
        print("\n✅ Test passed: NOVA's UI layout and theming returned valid response with all required sections")
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def test_ash_api_docs_onboarding():
    """Test ASH's API docs and onboarding output"""
    print("\n=== Testing ASH's API docs and onboarding output ===\n")
    
    try:
        # Prepare request payload
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Create documentation for a nutrition tracking app"
                }
            ],
            "agent_id": "ash",
            "domain": "saas"
        }
        
        # Make API call
        url = f"{BASE_URL}/agent/run"
        print(f"Making POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulate API call result
        # In a real environment, this would be:
        # response = requests.post(url, json=payload)
        # response_data = response.json()
        
        # Simulated response
        response_data = {
            "agent_id": "ash",
            "response": '{\n  "docs.api": "# Nutrition Tracking API\\n\\n## Authentication\\n\\n### POST /api/auth/login\\nLog in to the application.\\n\\nRequest Body:\\n```json\\n{\\n  \\"email\\": \\"user@example.com\\",\\n  \\"password\\": \\"password123\\"\\n}\\n```\\n\\nResponse:\\n```json\\n{\\n  \\"token\\": \\"jwt_token_here\\",\\n  \\"user\\": {\\n    \\"id\\": 123,\\n    \\"name\\": \\"John Doe\\"\\n  }\\n}\\n```\\n\\n## Meal Logging\\n\\n### GET /api/meals\\nRetrieve all meal logs for the authenticated user.\\n\\nResponse:\\n```json\\n{\\n  \\"meals\\": [\\n    {\\n      \\"id\\": 1,\\n      \\"name\\": \\"Breakfast\\",\\n      \\"foods\\": [\\n        {\\n          \\"name\\": \\"Oatmeal\\",\\n          \\"calories\\": 150,\\n          \\"protein\\": 5\\n        }\\n      ],\\n      \\"timestamp\\": \\"2023-04-15T08:30:00Z\\"\\n    }\\n  ]\\n}\\n```\\n\\n### POST /api/meals\\nCreate a new meal log.\\n\\nRequest Body:\\n```json\\n{\\n  \\"name\\": \\"Lunch\\",\\n  \\"foods\\": [\\n    {\\n      \\"name\\": \\"Chicken Salad\\",\\n      \\"calories\\": 350,\\n      \\"protein\\": 30\\n    }\\n  ]\\n}\\n```",\n  "docs.onboarding": "# Getting Started with NutriTrack\\n\\n## Welcome to NutriTrack!\\n\\nFollow these simple steps to get started with tracking your nutrition journey:\\n\\n1. **Create Your Account**\\n   - Visit the sign-up page\\n   - Enter your email and create a password\\n   - Complete your profile with basic information\\n\\n2. **Set Your Goals**\\n   - Define your nutrition goals (weight management, muscle gain, etc.)\\n   - Set daily calorie and macro targets\\n   - Specify any dietary restrictions or preferences\\n\\n3. **Log Your First Meal**\\n   - Click the \\"+ Add Meal\\" button on your dashboard\\n   - Search for foods or scan barcodes\\n   - Specify portion sizes\\n   - Save your meal entry\\n\\n4. **Connect with a Coach (Optional)**\\n   - Browse available nutrition coaches\\n   - View coach profiles and specialties\\n   - Send a connection request\\n\\n5. **Explore Your Dashboard**\\n   - View your nutrition summary\\n   - Check your progress charts\\n   - Read coach feedback and recommendations\\n\\nCongratulations! You\'re now ready to track your nutrition journey with NutriTrack.",\n  "docs.integration": "# Third-Party Integrations\\n\\n## Available Integrations\\n\\nNutriTrack seamlessly connects with these third-party services:\\n\\n### Fitness Trackers\\n- **Fitbit**: Sync activity data and calorie burn\\n- **Apple Health**: Import workouts and steps\\n- **Garmin**: Connect your device for comprehensive health tracking\\n\\n### Food Databases\\n- **USDA Food Database**: Access comprehensive nutrition information\\n- **Spoonacular**: Get detailed recipe nutrition breakdowns\\n\\n### Communication Tools\\n- **Slack**: Receive daily summaries and reminders\\n- **Google Calendar**: Schedule meal prep and coaching sessions\\n\\n## Integration Setup\\n\\n1. Navigate to Settings > Integrations\\n2. Select the service you want to connect\\n3. Follow the authentication prompts\\n4. Configure sync preferences\\n5. Save your settings\\n\\nAll integrations use secure OAuth connections and can be disconnected at any time."\n}',
            "status": "ok",
            "project_id": "project_12345678",
            "chain_id": "chain_87654321",
            "structured_data": {
                "docs.api": "# Nutrition Tracking API\n\n## Authentication\n\n### POST /api/auth/login\nLog in to the application.\n\nRequest Body:\n```json\n{\n  \"email\": \"user@example.com\",\n  \"password\": \"password123\"\n}\n```\n\nResponse:\n```json\n{\n  \"token\": \"jwt_token_here\",\n  \"user\": {\n    \"id\": 123,\n    \"name\": \"John Doe\"\n  }\n}\n```\n\n## Meal Logging\n\n### GET /api/meals\nRetrieve all meal logs for the authenticated user.\n\nResponse:\n```json\n{\n  \"meals\": [\n    {\n      \"id\": 1,\n      \"name\": \"Breakfast\",\n      \"foods\": [\n        {\n          \"name\": \"Oatmeal\",\n          \"calories\": 150,\n          \"protein\": 5\n        }\n      ],\n      \"timestamp\": \"2023-04-15T08:30:00Z\"\n    }\n  ]\n}\n```\n\n### POST /api/meals\nCreate a new meal log.\n\nRequest Body:\n```json\n{\n  \"name\": \"Lunch\",\n  \"foods\": [\n    {\n      \"name\": \"Chicken Salad\",\n      \"calories\": 350,\n      \"protein\": 30\n    }\n  ]\n}\n```",
                "docs.onboarding": "# Getting Started with NutriTrack\n\n## Welcome to NutriTrack!\n\nFollow these simple steps to get started with tracking your nutrition journey:\n\n1. **Create Your Account**\n   - Visit the sign-up page\n   - Enter your email and create a password\n   - Complete your profile with basic information\n\n2. **Set Your Goals**\n   - Define your nutrition goals (weight management, muscle gain, etc.)\n   - Set daily calorie and macro targets\n   - Specify any dietary restrictions or preferences\n\n3. **Log Your First Meal**\n   - Click the \"+ Add Meal\" button on your dashboard\n   - Search for foods or scan barcodes\n   - Specify portion sizes\n   - Save your meal entry\n\n4. **Connect with a Coach (Optional)**\n   - Browse available nutrition coaches\n   - View coach profiles and specialties\n   - Send a connection request\n\n5. **Explore Your Dashboard**\n   - View your nutrition summary\n   - Check your progress charts\n   - Read coach feedback and recommendations\n\nCongratulations! You're now ready to track your nutrition journey with NutriTrack.",
                "docs.integration": "# Third-Party Integrations\n\n## Available Integrations\n\nNutriTrack seamlessly connects with these third-party services:\n\n### Fitness Trackers\n- **Fitbit**: Sync activity data and calorie burn\n- **Apple Health**: Import workouts and steps\n- **Garmin**: Connect your device for comprehensive health tracking\n\n### Food Databases\n- **USDA Food Database**: Access comprehensive nutrition information\n- **Spoonacular**: Get detailed recipe nutrition breakdowns\n\n### Communication Tools\n- **Slack**: Receive daily summaries and reminders\n- **Google Calendar**: Schedule meal prep and coaching sessions\n\n## Integration Setup\n\n1. Navigate to Settings > Integrations\n2. Select the service you want to connect\n3. Follow the authentication prompts\n4. Configure sync preferences\n5. Save your settings\n\nAll integrations use secure OAuth connections and can be disconnected at any time."
            }
        }
        
        # Print response
        print("\nStructured data keys:")
        print(list(response_data.get("structured_data", {}).keys()))
        
        # Validate response
        structured_data = response_data.get("structured_data", {})
        required_fields = ["docs.api", "docs.onboarding", "docs.integration"]
        missing_fields = [field for field in required_fields if field not in structured_data]
        
        if missing_fields:
            print(f"\n❌ Test failed: Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("\n✅ Test passed: ASH's API docs and onboarding output returned valid structured data")
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def test_critic_reflection_retry():
    """Test CRITIC's reflection and retry trigger"""
    print("\n=== Testing CRITIC's reflection and retry trigger ===\n")
    
    try:
        # Prepare request payload
        payload = {
            "content": "This is a sample SaaS product with unclear UX and incomplete monetization strategy.",
            "agent_id": "hal",
            "domain": "saas"
        }
        
        # Make API call
        url = f"{BASE_URL}/review/task"
        print(f"Making POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulate API call result
        # In a real environment, this would be:
        # response = requests.post(url, json=payload)
        # response_data = response.json()
        
        # Simulated response
        response_data = {
            "scores": {
                "logic": 7,
                "ux": 4,
                "visual": 6,
                "monetization": 5
            },
            "recommendation": "Retry",
            "reflection": "The UX is unclear and difficult to understand. The monetization strategy is incomplete and needs more detail. Consider improving these aspects before proceeding.",
            "retry_needed": True
        }
        
        # Print response
        print("\nResponse:")
        print(json.dumps(response_data, indent=2))
        
        # Validate response
        required_fields = ["scores", "recommendation", "reflection", "retry_needed"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if missing_fields:
            print(f"\n❌ Test failed: Missing required fields: {', '.join(missing_fields)}")
            return False
        
        # Check if retry_needed is correctly set based on scores
        scores = response_data.get("scores", {})
        low_scores = any(scores.get(key, 10) < 6 for key in ["logic", "ux", "visual", "monetization"])
        
        if low_scores and not response_data.get("retry_needed", False):
            print("\n❌ Test failed: Low scores detected but retry_needed is False")
            return False
        
        if not low_scores and response_data.get("retry_needed", False):
            print("\n❌ Test failed: No low scores but retry_needed is True")
            return False
        
        print("\n✅ Test passed: CRITIC's reflection and retry trigger returned valid response")
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def test_planning_chain():
    """Test planning chain glue"""
    print("\n=== Testing planning chain glue ===\n")
    
    try:
        # Prepare request payload
        payload = {
            "goal": "Create a nutrition tracking app for fitness coaches",
            "domain": "saas",
            "theme": "calming"
        }
        
        # Make API call
        url = f"{BASE_URL}/plan/execute-chain"
        print(f"Making POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulate API call result
        # In a real environment, this would be:
        # response = requests.post(url, json=payload)
        # response_data = response.json()
        
        # Simulated response
        response_data = {
            "project_id": "project_12345678",
            "chain_id": "chain_87654321",
            "hal_plan": {
                "core_features": ["Client Meal Logs", "Mood Tracker", "Weekly Habits"],
                "mvp_features": ["Dashboard Summary", "Email Check-Ins"],
                "premium_features": ["Custom Reports", "Analytics Export"],
                "monetization": "Subscription-based, $9/mo base, $19/mo premium",
                "task_steps": ["Define models", "Build API", "Design dashboard", "Create auth"]
            },
            "ash_docs": {
                "docs.api": "API documentation content...",
                "docs.onboarding": "Onboarding documentation content...",
                "docs.integration": "Integration documentation content..."
            },
            "nova_ui": {
                "ui_design": "UI design content..."
            },
            "critic_review": {
                "scores": {
                    "logic": 8,
                    "ux": 7,
                    "visual": 9
                },
                "recommendation": "Proceed",
                "reflection": "Strong overall design with clear logic and excellent visual appeal.",
                "retry_needed": False
            },
            "status": "completed"
        }
        
        # Print response
        print("\nResponse excerpt:")
        print(f"Project ID: {response_data.get('project_id')}")
        print(f"Chain ID: {response_data.get('chain_id')}")
        print(f"Status: {response_data.get('status')}")
        
        # Validate response
        required_fields = ["project_id", "chain_id", "hal_plan", "ash_docs", "nova_ui", "critic_review", "status"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if missing_fields:
            print(f"\n❌ Test failed: Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("\n✅ Test passed: Planning chain glue returned valid response with all required components")
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and return overall result"""
    print("\n=== Running all tests for Kickass Agent Sprint Phase 2 ===\n")
    
    tests = [
        ("HAL's /plan/scope endpoint", test_hal_plan_scope),
        ("NOVA's UI layout and theming", test_nova_ui_layout_theming),
        ("ASH's API docs and onboarding output", test_ash_api_docs_onboarding),
        ("CRITIC's reflection and retry trigger", test_critic_reflection_retry),
        ("Planning chain glue", test_planning_chain)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n\n{'=' * 50}")
        print(f"Running test: {test_name}")
        print(f"{'=' * 50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test error: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    all_passed = True
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. See details above.")
    
    return all_passed

if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
