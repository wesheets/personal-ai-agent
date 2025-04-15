"""
Test NOVA's Error Handling

This module tests NOVA's UI preview error handling functionality.
"""

import json
from ui_preview import generate_preview

def test_error_handling():
    """
    Test the error handling in UI preview generation.
    
    Returns:
        Dictionary containing test results
    """
    # Test cases with invalid inputs
    test_cases = [
        {
            "name": "None input",
            "input": None
        },
        {
            "name": "Empty list",
            "input": []
        },
        {
            "name": "Invalid format",
            "input": ["not a tuple", 123]
        }
    ]
    
    results = {}
    all_passed = True
    
    for case in test_cases:
        # Generate UI preview with invalid input
        result = generate_preview(case["input"])
        
        # Check if both keys are present
        has_preview = "ui.preview" in result
        has_reflection = "reflection" in result
        
        # Check if error is properly handled
        is_error_handled = has_preview and has_reflection and "error" in result["ui.preview"].lower()
        
        # Store result
        case_result = {
            "passed": is_error_handled,
            "result": result
        }
        
        results[case["name"]] = case_result
        
        if not is_error_handled:
            all_passed = False
    
    return {
        "success": all_passed,
        "results": results
    }

if __name__ == "__main__":
    # Run test
    test_result = test_error_handling()
    
    # Print test result
    print(json.dumps(test_result, indent=2))
    
    # Print success/failure message
    if test_result["success"]:
        print("\n✅ Error handling tests passed! NOVA's error handling is working correctly.")
    else:
        print("\n❌ Error handling tests failed! See results above for details.")
