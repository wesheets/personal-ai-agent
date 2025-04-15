"""
Test NOVA's UI Preview Generation

This module tests NOVA's UI preview generation functionality with the provided test case.
"""

import json
from ui_preview import generate_preview

def test_with_provided_case():
    """
    Test the UI preview generation with the provided test case.
    
    The test case simulates HAL's reverse_and_measure function output for the input:
    "Build a Python script that takes a sentence and returns the words in reverse order, along with their lengths."
    
    Returns:
        Dictionary containing test results
    """
    # Simulate HAL's reverse_and_measure function output for "hello world"
    test_output = [("world", 5), ("hello", 5)]
    
    # Generate UI preview
    result = generate_preview(test_output)
    
    # Expected output format
    expected_keys = ["ui.preview", "reflection"]
    expected_html = '<div class="result">\n  <h3>Reversed Words</h3>\n  <ul>\n    <li>world (5)</li>\n    <li>hello (5)</li>\n  </ul>\n</div>'
    expected_reflection = "Generated a UI preview that matches HAL's result."
    
    # Validate result
    validation = {
        "success": True,
        "messages": []
    }
    
    # Check if all expected keys are present
    for key in expected_keys:
        if key not in result:
            validation["success"] = False
            validation["messages"].append(f"Missing key: {key}")
    
    # Check if HTML matches expected format
    if "ui.preview" in result and result["ui.preview"] != expected_html:
        validation["success"] = False
        validation["messages"].append("HTML output does not match expected format")
        validation["expected_html"] = expected_html
        validation["actual_html"] = result["ui.preview"]
    
    # Check if reflection matches expected format
    if "reflection" in result and result["reflection"] != expected_reflection:
        validation["success"] = False
        validation["messages"].append("Reflection does not match expected format")
        validation["expected_reflection"] = expected_reflection
        validation["actual_reflection"] = result["reflection"]
    
    # Add the result to the validation
    validation["result"] = result
    
    return validation

if __name__ == "__main__":
    # Run test
    test_result = test_with_provided_case()
    
    # Print test result
    print(json.dumps(test_result, indent=2))
    
    # Print success/failure message
    if test_result["success"]:
        print("\n✅ Test passed! NOVA's UI preview generation is working correctly.")
    else:
        print("\n❌ Test failed! See messages above for details.")
