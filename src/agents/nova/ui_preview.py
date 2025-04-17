__version__ = "3.5.0"
__agent__ = "NOVA"
__role__ = "strategist"

"""
NOVA UI Preview Generator

This module implements NOVA's UI preview generation functionality.
It generates HTML previews based on function outputs and provides reflection on the results.
"""

import json
from typing import Dict, Any, List, Tuple, Optional, Union


def generate_preview(function_output: Any) -> Dict[str, str]:
    """
    Generate a UI preview HTML block based on function output and reflect on the result.
    
    Args:
        function_output: The output from a function (e.g., HAL's reverse_and_measure function)
        
    Returns:
        Dictionary containing the UI preview HTML and reflection
    """
    try:
        # Process the function output
        if not function_output:
            return {
                "ui.preview": "<div class=\"error\">No output to display</div>",
                "reflection": "Failed to generate UI preview due to empty function output."
            }
        
        # For reverse_and_measure function, output is a list of (word, length) tuples
        if isinstance(function_output, list) and all(isinstance(item, tuple) and len(item) == 2 and 
                                                    isinstance(item[0], str) and isinstance(item[1], int) 
                                                    for item in function_output):
            # Generate HTML for the word-length pairs
            html = "<div class=\"result\">\n"
            html += "  <h3>Reversed Words</h3>\n"
            html += "  <ul>\n"
            
            for word, length in function_output:
                html += f"    <li>{word} ({length})</li>\n"
                
            html += "  </ul>\n"
            html += "</div>"
            
            return {
                "ui.preview": html,
                "reflection": "Generated a UI preview that matches HAL's result."
            }
        elif isinstance(function_output, list) and len(function_output) > 0 and not all(isinstance(item, tuple) and len(item) == 2 for item in function_output):
            # Invalid format for reverse_and_measure output
            error_html = "<div class=\"error\">Invalid format: Expected list of (word, length) tuples</div>"
            return {
                "ui.preview": error_html,
                "reflection": "Failed to generate UI preview: Invalid input format. Expected list of (word, length) tuples."
            }
        else:
            # Handle other types of function outputs
            html = "<div class=\"result\">\n"
            html += "  <h3>Function Output</h3>\n"
            
            if isinstance(function_output, dict):
                html += "  <ul>\n"
                for key, value in function_output.items():
                    html += f"    <li><strong>{key}:</strong> {value}</li>\n"
                html += "  </ul>\n"
            elif isinstance(function_output, list):
                html += "  <ul>\n"
                for item in function_output:
                    html += f"    <li>{item}</li>\n"
                html += "  </ul>\n"
            else:
                html += f"  <p>{function_output}</p>\n"
                
            html += "</div>"
            
            return {
                "ui.preview": html,
                "reflection": "Generated a UI preview for the function output."
            }
    except Exception as e:
        # Handle errors
        error_html = f"<div class=\"error\">Error generating preview: {str(e)}</div>"
        return {
            "ui.preview": error_html,
            "reflection": f"Failed to generate UI preview: {str(e)}. The output must be recoverable by other agents."
        }


def test_preview_generation():
    """
    Test the UI preview generation with sample data.
    
    Returns:
        Dictionary containing test results
    """
    # Test with the example from the requirements
    test_output = [("world", 5), ("hello", 5)]
    result = generate_preview(test_output)
    
    expected_html = '<div class=\"result\">\n  <h3>Reversed Words</h3>\n  <ul>\n    <li>world (5)</li>\n    <li>hello (5)</li>\n  </ul>\n</div>'
    
    if result["ui.preview"] == expected_html:
        return {
            "success": True,
            "message": "Preview generation test passed",
            "result": result
        }
    else:
        return {
            "success": False,
            "message": "Preview generation test failed",
            "expected": expected_html,
            "actual": result["ui.preview"]
        }


if __name__ == "__main__":
    # Run test when module is executed directly
    test_result = test_preview_generation()
    print(json.dumps(test_result, indent=2))
