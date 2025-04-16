"""
Dev + Testing Tools

This module provides tools for development and testing tasks including code reading,
commenting, unit test generation and execution, debugging, API building, and database schema generation.
"""

import re
import json
import random
import inspect
from typing import Dict, List, Any, Optional, Union

# Import the registry for tool registration
from ...registry import register_tool


def code_read(file_path: str, extract_comments: bool = True, summarize: bool = True) -> Dict[str, Any]:
    """
    Extract method summaries and comments from code.
    
    Args:
        file_path: Path to the code file
        extract_comments: Whether to extract comments
        summarize: Whether to generate a summary of the code
        
    Returns:
        A dictionary containing the code analysis results
    """
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read file: {str(e)}",
            "file_path": file_path
        }
    
    # Determine language based on file extension
    language = "unknown"
    if file_path.endswith(".py"):
        language = "python"
    elif file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
        language = "javascript"
    elif file_path.endswith((".java")):
        language = "java"
    elif file_path.endswith((".c", ".cpp", ".h", ".hpp")):
        language = "c/c++"
    elif file_path.endswith((".rb")):
        language = "ruby"
    elif file_path.endswith((".go")):
        language = "go"
    elif file_path.endswith((".php")):
        language = "php"
    
    # Extract functions/methods
    functions = []
    if language == "python":
        # Match Python function definitions
        function_pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)(?:\s*->\s*([a-zA-Z0-9_\[\],\s]*))?\s*:"
        for match in re.finditer(function_pattern, code):
            name = match.group(1)
            params = match.group(2)
            return_type = match.group(3) if match.group(3) else "None"
            
            # Get function docstring if available
            start_pos = match.end()
            docstring = ""
            
            # Look for triple-quoted docstring
            docstring_match = re.search(r'"""(.*?)"""', code[start_pos:start_pos + 500], re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
            
            functions.append({
                "name": name,
                "params": params,
                "return_type": return_type,
                "docstring": docstring
            })
    
    elif language in ["javascript", "typescript"]:
        # Match JavaScript/TypeScript function definitions
        function_pattern = r"(?:function|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=?\s*(?:\([^)]*\)|[a-zA-Z0-9_, ]*)\s*=>\s*{|function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        for match in re.finditer(function_pattern, code):
            name = match.group(1) if match.group(1) else match.group(2)
            
            # Get JSDoc if available
            start_pos = max(0, match.start() - 500)  # Look up to 500 chars before
            end_pos = match.start()
            jsdoc_match = re.search(r'/\*\*(.*?)\*/', code[start_pos:end_pos], re.DOTALL)
            docstring = ""
            if jsdoc_match:
                docstring = jsdoc_match.group(1).strip()
            
            functions.append({
                "name": name,
                "docstring": docstring
            })
    
    # Extract comments
    comments = []
    if extract_comments:
        if language == "python":
            # Single line comments
            for match in re.finditer(r"#\s*(.*?)$", code, re.MULTILINE):
                comments.append(match.group(1).strip())
            
            # Multi-line docstrings (not attached to functions)
            for match in re.finditer(r'"""(.*?)"""', code, re.DOTALL):
                # Check if this is a function docstring we already captured
                is_func_docstring = False
                for func in functions:
                    if func["docstring"] and match.group(1).strip() == func["docstring"]:
                        is_func_docstring = True
                        break
                
                if not is_func_docstring:
                    comments.append(match.group(1).strip())
        
        elif language in ["javascript", "typescript", "java", "c/c++", "php"]:
            # Single line comments
            for match in re.finditer(r"//\s*(.*?)$", code, re.MULTILINE):
                comments.append(match.group(1).strip())
            
            # Multi-line comments
            for match in re.finditer(r"/\*(.*?)\*/", code, re.DOTALL):
                comments.append(match.group(1).strip())
    
    # Generate summary
    summary = ""
    if summarize:
        # Count lines of code
        loc = len(code.split('\n'))
        
        # Basic summary
        summary = f"This {language} file contains {loc} lines of code with {len(functions)} functions/methods"
        if comments:
            summary += f" and {len(comments)} comments"
        summary += "."
        
        # Add function overview
        if functions:
            summary += "\n\nKey functions/methods:"
            for func in functions[:5]:  # Limit to first 5 functions
                summary += f"\n- {func['name']}"
                if "params" in func and func["params"]:
                    summary += f"({func['params']})"
                if func["docstring"]:
                    # Extract first line of docstring
                    first_line = func["docstring"].split('\n')[0].strip()
                    summary += f": {first_line}"
            
            if len(functions) > 5:
                summary += f"\n- ... and {len(functions) - 5} more functions"
    
    return {
        "success": True,
        "file_path": file_path,
        "language": language,
        "functions": functions,
        "comments": comments,
        "summary": summary,
        "line_count": len(code.split('\n'))
    }


def code_comment(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Generate comments for a given code snippet.
    
    Args:
        code: The code snippet to comment
        language: The programming language of the code
        
    Returns:
        A dictionary containing the commented code and metadata
    """
    # Define comment syntax for different languages
    comment_syntax = {
        "python": {
            "line": "# ",
            "block_start": '"""',
            "block_end": '"""',
            "docstring_start": '"""',
            "docstring_end": '"""'
        },
        "javascript": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "/**",
            "docstring_end": "*/"
        },
        "typescript": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "/**",
            "docstring_end": "*/"
        },
        "java": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "/**",
            "docstring_end": "*/"
        },
        "c": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "/**",
            "docstring_end": "*/"
        },
        "cpp": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "/**",
            "docstring_end": "*/"
        },
        "ruby": {
            "line": "# ",
            "block_start": "=begin",
            "block_end": "=end",
            "docstring_start": "# ",
            "docstring_end": ""
        },
        "go": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "// ",
            "docstring_end": ""
        },
        "php": {
            "line": "// ",
            "block_start": "/*",
            "block_end": "*/",
            "docstring_start": "/**",
            "docstring_end": "*/"
        }
    }
    
    # Use python as default if language not supported
    if language not in comment_syntax:
        language = "python"
    
    syntax = comment_syntax[language]
    
    # Split code into lines
    code_lines = code.split('\n')
    
    # Identify functions/methods for docstring generation
    functions = []
    
    if language == "python":
        # Match Python function definitions
        for i, line in enumerate(code_lines):
            match = re.match(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)(?:\s*->\s*([a-zA-Z0-9_\[\],\s]*))?\s*:", line)
            if match:
                name = match.group(1)
                params = match.group(2)
                return_type = match.group(3) if match.group(3) else "None"
                
                # Check if function already has a docstring
                has_docstring = False
                if i + 1 < len(code_lines):
                    docstring_match = re.match(r'\s*""".*?"""', code_lines[i+1], re.DOTALL)
                    if docstring_match:
                        has_docstring = True
                
                if not has_docstring:
                    functions.append({
                        "line": i,
                        "name": name,
                        "params": params,
                        "return_type": return_type
                    })
    
    elif language in ["javascript", "typescript"]:
        # Match JavaScript/TypeScript function definitions
        for i, line in enumerate(code_lines):
            match = re.match(r"(?:function|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=?\s*(?:\([^)]*\)|[a-zA-Z0-9_, ]*)\s*=>\s*{|function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
            if match:
                name = match.group(1) if match.group(1) else match.group(2)
                
                # Check if function already has a JSDoc
                has_docstring = False
                if i > 0:
                    docstring_match = re.match(r'\s*/\*\*.*?\*/', code_lines[i-1], re.DOTALL)
                    if docstring_match:
                        has_docstring = True
                
                if not has_docstring:
                    functions.append({
                        "line": i,
                        "name": name
                    })
    
    # Generate commented code
    commented_code = []
    
    # Add file header comment
    if language == "python":
        commented_code.append(f"{syntax['block_start']}")
        commented_code.append(f"File: [Filename]")
        commented_code.append(f"Description: This file contains code for [purpose].")
        commented_code.append(f"Author: [Author]")
        commented_code.append(f"Date: [Date]")
        commented_code.append(f"{syntax['block_end']}")
        commented_code.append("")  # Empty line after header
    else:
        commented_code.append(f"{syntax['block_start']}")
        commented_code.append(f" * File: [Filename]")
        commented_code.append(f" * Description: This file contains code for [purpose].")
        commented_code.append(f" * Author: [Author]")
        commented_code.append(f" * Date: [Date]")
        commented_code.append(f" {syntax['block_end']}")
        commented_code.append("")  # Empty line after header
    
    # Process code lines
    i = 0
    while i < len(code_lines):
        # Check if we need to insert a function docstring
        docstring_inserted = False
        for func in functions:
            if func["line"] == i:
                # Insert docstring for this function
                if language == "python":
                    # Add the function definition line first
                    commented_code.append(code_lines[i])
                    i += 1
                    
                    # Add Python docstring
                    indent = re.match(r"(\s*)", code_lines[i] if i < len(code_lines) else "").group(1)
                    commented_code.append(f"{indent}{syntax['docstring_start']}")
                    commented_code.append(f"{indent}[Function description]")
                    commented_code.append(f"{indent}")
                    
                    # Add parameters
                    if "params" in func and func["params"]:
                        params = [p.strip() for p in func["params"].split(",")]
                        for param in params:
                            if param:  # Skip empty params
                                param_name = param.split(":")[0].strip()
                                commented_code.append(f"{indent}Args:")
                                commented_code.append(f"{indent}    {param_name}: [Parameter description]")
                                break  # Just add the Args: header once
                    
                    # Add return value
                    if "return_type" in func and func["return_type"] and func["return_type"] != "None":
                        commented_code.append(f"{indent}Returns:")
                        commented_code.append(f"{indent}    [Return value description]")
                    
                    commented_code.append(f"{indent}{syntax['docstring_end']}")
                    docstring_inserted = True
                
                elif language in ["javascript", "typescript"]:
                    # Add JSDoc before the function
                    commented_code.append(f"{syntax['docstring_start']}")
                    commented_code.append(f" * [Function description]")
                    commented_code.append(f" *")
                    commented_code.append(f" * @param {{any}} [param] - [Parameter description]")
                    commented_code.append(f" * @returns {{any}} [Return value description]")
                    commented_code.append(f" {syntax['docstring_end']}")
                    
                    # Add the function definition line
                    commented_code.append(code_lines[i])
                    i += 1
                    docstring_inserted = True
                
                break
        
        if not docstring_inserted:
            # Regular line, add with inline comment for important-looking lines
            line = code_lines[i]
            
            # Detect if line might need a comment (e.g., complex logic, conditionals)
            needs_comment = False
            if re.search(r"if\s+|while\s+|for\s+|switch\s+|case\s+|return\s+\w+", line):
                needs_comment = True
            elif re.search(r"=\s*\w+\(.*\)", line):  # Function call with assignment
                needs_comment = True
            elif re.search(r"[+\-*/]=", line):  # Compound assignment
                needs_comment = True
            
            if needs_comment and not line.strip().startswith(syntax["line"].strip()):
                # Add inline comment for important lines
                commented_code.append(f"{line}  {syntax['line']}[Description of what this line does]")
            else:
                # Pass through unchanged
                commented_code.append(line)
            
            i += 1
    
    # Join the commented code
    result = "\n".join(commented_code)
    
    return {
        "original_code": code,
        "commented_code": result,
        "language": language,
        "functions_commented": len(functions),
        "comment_syntax": syntax
    }


def unit_test_generate(code: str, language: str = "python", framework: str = "pytest") -> Dict[str, Any]:
    """
    Generate unit tests for a given code snippet.
    
    Args:
        code: The code snippet to generate tests for
        language: The programming language of the code
        framework: The testing framework to use
        
    Returns:
        A dictionary containing the generated unit tests and metadata
    """
    # Define supported frameworks for each language
    supported_frameworks = {
        "python": ["pytest", "unittest"],
        "javascript": ["jest", "mocha"],
        "typescript": ["jest", "mocha"],
        "java": ["junit"],
        "c#": ["nunit", "xunit"],
        "go": ["testing"],
        "ruby": ["rspec"]
    }
    
    # Validate language and framework
    if language not in supported_frameworks:
        return {
            "success": False,
            "error": f"Unsupported language: {language}",
            "supported_languages": list(supported_frameworks.keys())
        }
    
    if framework not in supported_frameworks[language]:
        framework = supported_frameworks[language][0]  # Use default framework for language
    
    # Extract functions/methods to test
    functions = []
    
    if language == "python":
        # Match Python function definitions
        function_pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)(?:\s*->\s*([a-zA-Z0-9_\[\],\s]*))?\s*:"
        for match in re.finditer(function_pattern, code):
            name = match.group(1)
            params = match.group(2)
            return_type = match.group(3) if match.group(3) else "None"
            
            # Skip test functions
            if name.startswith("test_"):
                continue
            
            # Parse parameters
            param_list = []
            if params:
                for param in params.split(","):
                    param = param.strip()
                    if param and param != "self" and param != "cls":
                        # Extract parameter name (without type annotation)
                        param_name = param.split(":")[0].strip()
                        param_list.append(param_name)
            
            functions.append({
                "name": name,
                "params": param_list,
                "return_type": return_type
            })
    
    elif language in ["javascript", "typescript"]:
        # Match JavaScript/TypeScript function definitions
        function_pattern = r"(?:function|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=?\s*\(([^)]*)\)|function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)"
        for match in re.finditer(function_pattern, code):
            name = match.group(1) if match.group(1) else match.group(3)
            params = match.group(2) if match.group(2) else match.group(4) if match.group(4) else ""
            
            # Skip test functions
            if name and name.startsWith("test"):
                continue
            
            # Parse parameters
            param_list = []
            if params:
                for param in params.split(","):
                    param = param.strip()
                    if param:
                        # Extract parameter name (without type annotation)
                        param_name = param.split(":")[0].strip()
                        param_list.append(param_name)
            
            functions.append({
                "name": name,
                "params": param_list
            })
    
    # Generate test code based on language and framework
    test_code = ""
    
    if language == "python":
        if framework == "pytest":
            # Generate pytest tests
            test_code = """import pytest
from module_under_test import *  # Replace with actual module name

"""
            for func in functions:
                test_code += f"""
def test_{func['name']}_basic():
    \"\"\"Test basic functionality of {func['name']}\"\"\"
    # Arrange
    # TODO: Set up test inputs
"""
                
                # Add parameters
                if func["params"]:
                    for param in func["params"]:
                        test_code += f"    {param} = None  # TODO: Replace with appropriate test value\n"
                
                # Add test execution and assertion
                if func["params"]:
                    params_str = ", ".join(func["params"])
                    test_code += f"""
    # Act
    result = {func['name']}({params_str})
    
    # Assert
    # TODO: Replace with actual assertions
    assert result is not None
"""
                else:
                    test_code += f"""
    # Act
    result = {func['name']}()
    
    # Assert
    # TODO: Replace with actual assertions
    assert result is not None
"""
                
                # Add edge case test
                test_code += f"""

def test_{func['name']}_edge_case():
    \"\"\"Test edge case for {func['name']}\"\"\"
    # Arrange
    # TODO: Set up edge case inputs
"""
                
                # Add parameters for edge case
                if func["params"]:
                    for param in func["params"]:
                        test_code += f"    {param} = None  # TODO: Replace with edge case value\n"
                
                # Add test execution and assertion for edge case
                if func["params"]:
                    params_str = ", ".join(func["params"])
                    test_code += f"""
    # Act
    result = {func['name']}({params_str})
    
    # Assert
    # TODO: Replace with actual assertions
    assert result is not None
"""
                else:
                    test_code += f"""
    # Act
    result = {func['name']}()
    
    # Assert
    # TODO: Replace with actual assertions
    assert result is not None
"""
        
        elif framework == "unittest":
            # Generate unittest tests
            test_code = """import unittest
from module_under_test import *  # Replace with actual module name

class TestFunctions(unittest.TestCase):
"""
            for func in functions:
                test_code += f"""
    def test_{func['name']}_basic(self):
        \"\"\"Test basic functionality of {func['name']}\"\"\"
        # Arrange
        # TODO: Set up test inputs
"""
                
                # Add parameters
                if func["params"]:
                    for param in func["params"]:
                        test_code += f"        {param} = None  # TODO: Replace with appropriate test value\n"
                
                # Add test execution and assertion
                if func["params"]:
                    params_str = ", ".join(func["params"])
                    test_code += f"""
        # Act
        result = {func['name']}({params_str})
        
        # Assert
        # TODO: Replace with actual assertions
        self.assertIsNotNone(result)
"""
                else:
                    test_code += f"""
        # Act
        result = {func['name']}()
        
        # Assert
        # TODO: Replace with actual assertions
        self.assertIsNotNone(result)
"""
                
                # Add edge case test
                test_code += f"""
    def test_{func['name']}_edge_case(self):
        \"\"\"Test edge case for {func['name']}\"\"\"
        # Arrange
        # TODO: Set up edge case inputs
"""
                
                # Add parameters for edge case
                if func["params"]:
                    for param in func["params"]:
                        test_code += f"        {param} = None  # TODO: Replace with edge case value\n"
                
                # Add test execution and assertion for edge case
                if func["params"]:
                    params_str = ", ".join(func["params"])
                    test_code += f"""
        # Act
        result = {func['name']}({params_str})
        
        # Assert
        # TODO: Replace with actual assertions
        self.assertIsNotNone(result)
"""
                else:
                    test_code += f"""
        # Act
        result = {func['name']}()
        
        # Assert
        # TODO: Replace with actual assertions
        self.assertIsNotNone(result)
"""
            
            # Add main block
            test_code += """

if __name__ == '__main__':
    unittest.main()
"""
    
    elif language in ["javascript", "typescript"]:
        if framework == "jest":
            # Generate Jest tests
            test_code = """// Import the module under test
const moduleUnderTest = require('./module-under-test');  // Replace with actual module path

"""
            for func in functions:
                test_code += f"""
describe('{func['name']}', () => {{
  test('basic functionality', () => {{
    // Arrange
    // TODO: Set up test inputs
"""
                
                # Add parameters
                if func["params"]:
                    for param in func["params"]:
                        test_code += f"    const {param} = null;  // TODO: Replace with appropriate test value\n"
                
                # Add test execution and assertion
                if func["params"]:
                    params_str = ", ".join(func["params"])
                    test_code += f"""
    // Act
    const result = moduleUnderTest.{func['name']}({params_str});
    
    // Assert
    // TODO: Replace with actual assertions
    expect(result).not.toBeNull();
  }});

  test('edge case', () => {{
    // Arrange
    // TODO: Set up edge case inputs
"""
                else:
                    test_code += f"""
    // Act
    const result = moduleUnderTest.{func['name']}();
    
    // Assert
    // TODO: Replace with actual assertions
    expect(result).not.toBeNull();
  }});

  test('edge case', () => {{
    // Arrange
    // TODO: Set up edge case inputs
"""
                
                # Add parameters for edge case
                if func["params"]:
                    for param in func["params"]:
                        test_code += f"    const {param} = null;  // TODO: Replace with edge case value\n"
                
                # Add test execution and assertion for edge case
                if func["params"]:
                    params_str = ", ".join(func["params"])
                    test_code += f"""
    // Act
    const result = moduleUnderTest.{func['name']}({params_str});
    
    // Assert
    // TODO: Replace with actual assertions
    expect(result).not.toBeNull();
  }});
}});
"""
                else:
                    test_code += f"""
    // Act
    const result = moduleUnderTest.{func['name']}();
    
    // Assert
    // TODO: Replace with actual assertions
    expect(result).not.toBeNull();
  }});
}});
"""
    
    return {
        "success": True,
        "language": language,
        "framework": framework,
        "functions_tested": len(functions),
        "test_code": test_code,
        "functions": functions
    }


def unit_test_run(test_code: str, language: str = "python", framework: str = "pytest") -> Dict[str, Any]:
    """
    Simulate running unit tests and return pass/fail output with logs.
    
    Args:
        test_code: The test code to run
        language: The programming language of the test code
        framework: The testing framework used
        
    Returns:
        A dictionary containing the test results and logs
    """
    # Define supported frameworks for each language
    supported_frameworks = {
        "python": ["pytest", "unittest"],
        "javascript": ["jest", "mocha"],
        "typescript": ["jest", "mocha"],
        "java": ["junit"],
        "c#": ["nunit", "xunit"],
        "go": ["testing"],
        "ruby": ["rspec"]
    }
    
    # Validate language and framework
    if language not in supported_frameworks:
        return {
            "success": False,
            "error": f"Unsupported language: {language}",
            "supported_languages": list(supported_frameworks.keys())
        }
    
    if framework not in supported_frameworks[language]:
        framework = supported_frameworks[language][0]  # Use default framework for language
    
    # Extract test functions/methods
    test_functions = []
    
    if language == "python":
        if framework == "pytest":
            # Match pytest test functions
            test_pattern = r"def\s+(test_[a-zA-Z_][a-zA-Z0-9_]*)\s*\("
            for match in re.finditer(test_pattern, test_code):
                test_functions.append(match.group(1))
        elif framework == "unittest":
            # Match unittest test methods
            test_pattern = r"def\s+(test_[a-zA-Z_][a-zA-Z0-9_]*)\s*\(self"
            for match in re.finditer(test_pattern, test_code):
                test_functions.append(match.group(1))
    
    elif language in ["javascript", "typescript"]:
        if framework == "jest":
            # Match Jest test functions
            test_pattern = r"test\(['\"](.+?)['\"]"
            for match in re.finditer(test_pattern, test_code):
                test_functions.append(match.group(1))
    
    # Generate simulated test results
    results = []
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        # Randomly determine if test passes or fails (80% pass rate)
        success = random.random() < 0.8
        
        if success:
            passed += 1
            status = "PASSED"
            log = f"Test {test_func} completed successfully"
        else:
            failed += 1
            status = "FAILED"
            
            # Generate random failure reason
            failure_reasons = [
                "AssertionError: expected value did not match actual value",
                "TypeError: cannot process argument of type NoneType",
                "ValueError: invalid input parameter",
                "IndexError: list index out of range",
                "KeyError: key not found in dictionary"
            ]
            log = f"Test {test_func} failed: {random.choice(failure_reasons)}"
        
        results.append({
            "test_name": test_func,
            "status": status,
            "log": log
        })
    
    # Generate output format based on framework
    output = ""
    
    if language == "python":
        if framework == "pytest":
            output = f"""============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
rootdir: /path/to/tests
collected {len(test_functions)} items

"""
            for result in results:
                if result["status"] == "PASSED":
                    output += f"test_module.py::{result['test_name']} PASSED                     [ {results.index(result) + 1}/{len(results)} ]\n"
                else:
                    output += f"test_module.py::{result['test_name']} FAILED                     [ {results.index(result) + 1}/{len(results)} ]\n"
            
            output += f"""
=================================== FAILURES ===================================
"""
            
            # Add details for failed tests
            for result in results:
                if result["status"] == "FAILED":
                    output += f"""
_________________________ {result['test_name']} __________________________

    def {result['test_name']}():
>       assert expected == actual
E       {result['log']}

test_module.py:line_number
"""
            
            output += f"""
========================= {failed} failed, {passed} passed in 0.12s =========================
"""
        
        elif framework == "unittest":
            output = f"""Ran {len(test_functions)} tests in 0.123s

"""
            if failed > 0:
                output += f"FAILED (failures={failed})\n"
                
                # Add details for failed tests
                for result in results:
                    if result["status"] == "FAILED":
                        output += f"""
FAIL: {result['test_name']}
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_module.py", line line_number, in {result['test_name']}
    self.assertEqual(expected, actual)
{result['log']}
"""
            else:
                output += "OK\n"
    
    elif language in ["javascript", "typescript"]:
        if framework == "jest":
            output = f"""PASS  __tests__/module.test.js
"""
            
            for result in results:
                if result["status"] == "PASSED":
                    output += f"  ✓ {result['test_name']} (2 ms)\n"
                else:
                    output += f"  ✕ {result['test_name']} (3 ms)\n"
            
            if failed > 0:
                output += f"""
  ● {results[0]['test_name']} › {[r for r in results if r['status'] == 'FAILED'][0]['test_name']}

    {[r for r in results if r['status'] == 'FAILED'][0]['log']}

      at Object.<anonymous> (__tests__/module.test.js:line_number:column_number)
"""
            
            output += f"""

Test Suites: {1 if failed > 0 else 0} failed, {1 if passed > 0 else 0} passed, 1 total
Tests:       {failed} failed, {passed} passed, {len(test_functions)} total
Snapshots:   0 total
Time:        1.234 s
Ran all test suites.
"""
    
    return {
        "success": True,
        "language": language,
        "framework": framework,
        "tests_run": len(test_functions),
        "tests_passed": passed,
        "tests_failed": failed,
        "results": results,
        "output": output
    }


def debug_trace(code: str, input_data: Optional[Dict[str, Any]] = None, language: str = "python") -> Dict[str, Any]:
    """
    Generate a simulated execution trace for debugging.
    
    Args:
        code: The code to trace
        input_data: Optional input data for the code
        language: The programming language of the code
        
    Returns:
        A dictionary containing the execution trace and metadata
    """
    # Default input data if none provided
    if not input_data:
        input_data = {"x": 5, "y": 10, "text": "hello"}
    
    # Split code into lines
    code_lines = code.split('\n')
    
    # Generate trace steps
    trace = []
    variables = dict(input_data)  # Start with input data
    
    line_index = 0
    while line_index < len(code_lines):
        line = code_lines[line_index].strip()
        
        # Skip empty lines and comments
        if not line or (language == "python" and line.startswith("#")) or (language in ["javascript", "typescript"] and (line.startswith("//") or line.startswith("/*"))):
            line_index += 1
            continue
        
        # Create trace step
        step = {
            "line_number": line_index + 1,
            "code": line,
            "variables": dict(variables),
            "output": None,
            "error": None
        }
        
        # Simulate variable assignments
        if language == "python":
            # Python assignment
            assignment_match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)", line)
            if assignment_match:
                var_name = assignment_match.group(1)
                expression = assignment_match.group(2)
                
                # Simulate expression evaluation
                try:
                    # Handle basic arithmetic with existing variables
                    if re.search(r"[+\-*/]", expression):
                        for var in variables:
                            if var in expression:
                                expression = expression.replace(var, str(variables[var]))
                        
                        # Evaluate simple expressions
                        if re.match(r"^[\d\s+\-*/().]+$", expression):
                            try:
                                variables[var_name] = eval(expression)
                            except:
                                variables[var_name] = f"<evaluated {expression}>"
                        else:
                            variables[var_name] = f"<evaluated {expression}>"
                    
                    # Handle string operations
                    elif '"' in expression or "'" in expression:
                        variables[var_name] = f"<string: {expression}>"
                    
                    # Handle function calls
                    elif "(" in expression and ")" in expression:
                        variables[var_name] = f"<result of {expression}>"
                    
                    # Default fallback
                    else:
                        variables[var_name] = f"<value from {expression}>"
                
                except Exception as e:
                    step["error"] = f"Error evaluating expression: {str(e)}"
            
            # Python print statement
            elif line.startswith("print("):
                match = re.match(r"print\((.*)\)", line)
                if match:
                    expression = match.group(1)
                    
                    # Replace variables with their values
                    for var in variables:
                        if var in expression:
                            expression = expression.replace(var, str(variables[var]))
                    
                    step["output"] = f"Output: {expression}"
        
        elif language in ["javascript", "typescript"]:
            # JavaScript/TypeScript assignment
            assignment_match = re.match(r"(?:var|let|const)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?);?$", line)
            if assignment_match:
                var_name = assignment_match.group(1)
                expression = assignment_match.group(2)
                
                # Simulate expression evaluation
                try:
                    # Handle basic arithmetic with existing variables
                    if re.search(r"[+\-*/]", expression):
                        for var in variables:
                            if var in expression:
                                expression = expression.replace(var, str(variables[var]))
                        
                        # Evaluate simple expressions
                        if re.match(r"^[\d\s+\-*/().]+$", expression):
                            try:
                                variables[var_name] = eval(expression)
                            except:
                                variables[var_name] = f"<evaluated {expression}>"
                        else:
                            variables[var_name] = f"<evaluated {expression}>"
                    
                    # Handle string operations
                    elif '"' in expression or "'" in expression:
                        variables[var_name] = f"<string: {expression}>"
                    
                    # Handle function calls
                    elif "(" in expression and ")" in expression:
                        variables[var_name] = f"<result of {expression}>"
                    
                    # Default fallback
                    else:
                        variables[var_name] = f"<value from {expression}>"
                
                except Exception as e:
                    step["error"] = f"Error evaluating expression: {str(e)}"
            
            # JavaScript/TypeScript console.log
            elif "console.log" in line:
                match = re.match(r"console\.log\((.*)\);?", line)
                if match:
                    expression = match.group(1)
                    
                    # Replace variables with their values
                    for var in variables:
                        if var in expression:
                            expression = expression.replace(var, str(variables[var]))
                    
                    step["output"] = f"Output: {expression}"
        
        # Add the step to the trace
        trace.append(step)
        
        # Simulate control flow
        if "if " in line or "for " in line or "while " in line:
            # For simplicity, we'll just simulate entering the block
            line_index += 1
            
            # Find the indentation level of the next line
            if line_index < len(code_lines):
                next_line = code_lines[line_index]
                indent_match = re.match(r"(\s*)", next_line)
                indent = indent_match.group(1) if indent_match else ""
                
                # Add a trace step for entering the block
                trace.append({
                    "line_number": line_index + 1,
                    "code": next_line.strip(),
                    "variables": dict(variables),
                    "output": None,
                    "error": None,
                    "note": "Entered conditional/loop block"
                })
        else:
            line_index += 1
    
    # Generate summary
    summary = {
        "lines_executed": len(trace),
        "variables_final_state": variables,
        "execution_path": [step["line_number"] for step in trace],
        "outputs": [step["output"] for step in trace if step["output"]],
        "errors": [{"line": step["line_number"], "error": step["error"]} for step in trace if step["error"]]
    }
    
    return {
        "language": language,
        "input_data": input_data,
        "trace": trace,
        "summary": summary
    }


def api_build(endpoint_path: str, method: str = "GET", params: Optional[List[Dict[str, str]]] = None, response_type: str = "json") -> Dict[str, Any]:
    """
    Generate a scaffold for a REST/GraphQL API route and handler.
    
    Args:
        endpoint_path: The path for the API endpoint
        method: The HTTP method (GET, POST, PUT, DELETE)
        params: Optional list of parameters with name and type
        response_type: The response format (json, xml, etc.)
        
    Returns:
        A dictionary containing the API scaffold and metadata
    """
    # Default params if none provided
    if not params:
        if method == "GET":
            params = [
                {"name": "id", "type": "string", "required": True, "description": "Resource identifier"},
                {"name": "fields", "type": "string", "required": False, "description": "Comma-separated list of fields to include"}
            ]
        elif method == "POST":
            params = [
                {"name": "name", "type": "string", "required": True, "description": "Resource name"},
                {"name": "description", "type": "string", "required": False, "description": "Resource description"}
            ]
        elif method == "PUT":
            params = [
                {"name": "id", "type": "string", "required": True, "description": "Resource identifier"},
                {"name": "name", "type": "string", "required": False, "description": "Updated resource name"},
                {"name": "description", "type": "string", "required": False, "description": "Updated resource description"}
            ]
        elif method == "DELETE":
            params = [
                {"name": "id", "type": "string", "required": True, "description": "Resource identifier"}
            ]
    
    # Generate endpoint name
    endpoint_parts = [p for p in endpoint_path.split("/") if p]
    endpoint_name = "_".join(endpoint_parts)
    if not endpoint_name:
        endpoint_name = "root"
    
    # Generate handler name
    handler_name = f"handle_{method.lower()}_{endpoint_name}"
    
    # Generate Express.js implementation
    express_implementation = f"""// {method} {endpoint_path} - Handler
const {handler_name} = async (req, res) => {{
  try {{
    // Extract parameters
"""
    
    if method in ["GET", "DELETE"]:
        for param in params:
            if param.get("required", False):
                express_implementation += f"""    const {param["name"]} = req.query.{param["name"]};
    if (!{param["name"]}) {{
      return res.status(400).json({{ error: "{param["name"]} is required" }});
    }}
"""
            else:
                express_implementation += f"""    const {param["name"]} = req.query.{param["name"]};
"""
    else:  # POST, PUT
        for param in params:
            if param.get("required", False):
                express_implementation += f"""    const {param["name"]} = req.body.{param["name"]};
    if (!{param["name"]}) {{
      return res.status(400).json({{ error: "{param["name"]} is required" }});
    }}
"""
            else:
                express_implementation += f"""    const {param["name"]} = req.body.{param["name"]};
"""
    
    express_implementation += """
    // TODO: Implement business logic
    
    // Example response
"""
    
    if method == "GET":
        express_implementation += """    const result = {
      id: id,
      name: "Example Resource",
      description: "This is an example resource",
      created_at: new Date().toISOString()
    };
    
    return res.status(200).json(result);
"""
    elif method == "POST":
        express_implementation += """    const result = {
      id: "generated-id-123",
      name: name,
      description: description || "",
      created_at: new Date().toISOString()
    };
    
    return res.status(201).json(result);
"""
    elif method == "PUT":
        express_implementation += """    const result = {
      id: id,
      name: name || "Example Resource",
      description: description || "This is an example resource",
      updated_at: new Date().toISOString()
    };
    
    return res.status(200).json(result);
"""
    elif method == "DELETE":
        express_implementation += """    // No content in response for DELETE
    return res.status(204).send();
"""
    
    express_implementation += """  } catch (error) {
    console.error(`Error in ${handler_name}:`, error);
    return res.status(500).json({ error: "Internal server error" });
  }
};

// Register route
router.${method.toLowerCase()}('${endpoint_path}', ${handler_name});

module.exports = { ${handler_name} };
"""
    
    # Generate Flask implementation
    flask_implementation = f"""from flask import request, jsonify, Blueprint

# Create blueprint
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('{endpoint_path}', methods=['{method}'])
def {handler_name}():
    try:
        # Extract parameters
"""
    
    if method in ["GET", "DELETE"]:
        for param in params:
            if param.get("required", False):
                flask_implementation += f"""        {param["name"]} = request.args.get('{param["name"]}')
        if not {param["name"]}:
            return jsonify({{"error": "{param["name"]} is required"}}), 400
"""
            else:
                flask_implementation += f"""        {param["name"]} = request.args.get('{param["name"]}')
"""
    else:  # POST, PUT
        flask_implementation += """        data = request.get_json()
"""
        for param in params:
            if param.get("required", False):
                flask_implementation += f"""        {param["name"]} = data.get('{param["name"]}')
        if not {param["name"]}:
            return jsonify({{"error": "{param["name"]} is required"}}), 400
"""
            else:
                flask_implementation += f"""        {param["name"]} = data.get('{param["name"]}')
"""
    
    flask_implementation += """
        # TODO: Implement business logic
        
        # Example response
"""
    
    if method == "GET":
        flask_implementation += """        result = {
            "id": id,
            "name": "Example Resource",
            "description": "This is an example resource",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        return jsonify(result), 200
"""
    elif method == "POST":
        flask_implementation += """        result = {
            "id": "generated-id-123",
            "name": name,
            "description": description or "",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        return jsonify(result), 201
"""
    elif method == "PUT":
        flask_implementation += """        result = {
            "id": id,
            "name": name or "Example Resource",
            "description": description or "This is an example resource",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        return jsonify(result), 200
"""
    elif method == "DELETE":
        flask_implementation += """        # No content in response for DELETE
        return "", 204
"""
    
    flask_implementation += """    except Exception as e:
        print(f"Error in {handler_name}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Register blueprint
# app.register_blueprint(api_blueprint, url_prefix='/api')
"""
    
    # Generate FastAPI implementation
    fastapi_implementation = f"""from fastapi import APIRouter, Query, Body, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

"""
    
    # Define request/response models for FastAPI
    if method in ["POST", "PUT"]:
        fastapi_implementation += """# Request model
class RequestModel(BaseModel):
"""
        for param in params:
            required = not param.get("required", False)
            fastapi_implementation += f"""    {param["name"]}: {param["type"].capitalize() if param["type"] in ["string", "integer", "boolean"] else "str"}{"" if param.get("required", False) else " = None"}
"""
        
        fastapi_implementation += """
# Response model
class ResponseModel(BaseModel):
"""
        if method == "POST":
            fastapi_implementation += """    id: str
    name: str
    description: Optional[str] = None
    created_at: str
"""
        elif method == "PUT":
            fastapi_implementation += """    id: str
    name: str
    description: Optional[str] = None
    updated_at: str
"""
        
        fastapi_implementation += "\n"
    
    # Define endpoint
    if method == "GET":
        fastapi_implementation += f"""@router.get('{endpoint_path}')
async def {handler_name}(
"""
        for param in params:
            fastapi_implementation += f"""    {param["name"]}: {param["type"].capitalize() if param["type"] in ["string", "integer", "boolean"] else "str"} = Query({"..." if param.get("required", False) else "None"}, description="{param.get("description", "")}"),
"""
        
        fastapi_implementation += """):
    try:
        # TODO: Implement business logic
        
        # Example response
        result = {
            "id": id,
            "name": "Example Resource",
            "description": "This is an example resource",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
    
    elif method == "POST":
        fastapi_implementation += f"""@router.post('{endpoint_path}', response_model=ResponseModel, status_code=201)
async def {handler_name}(request: RequestModel):
    try:
        # TODO: Implement business logic
        
        # Example response
        result = {{
            "id": "generated-id-123",
            "name": request.name,
            "description": request.description or "",
            "created_at": "2023-01-01T00:00:00Z"
        }}
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
    
    elif method == "PUT":
        fastapi_implementation += f"""@router.put('{endpoint_path}', response_model=ResponseModel)
async def {handler_name}(id: str, request: RequestModel):
    try:
        # TODO: Implement business logic
        
        # Example response
        result = {{
            "id": id,
            "name": request.name or "Example Resource",
            "description": request.description or "This is an example resource",
            "updated_at": "2023-01-01T00:00:00Z"
        }}
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
    
    elif method == "DELETE":
        fastapi_implementation += f"""@router.delete('{endpoint_path}', status_code=204)
async def {handler_name}(id: str):
    try:
        # TODO: Implement business logic
        
        # No content in response for DELETE
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
    
    # Generate API documentation
    api_docs = f"""# API Documentation: {method} {endpoint_path}

## Overview
This endpoint allows you to {method.lower()} {'a' if method in ['GET', 'PUT', 'DELETE'] else ''} resource{' information' if method == 'GET' else ''}.

## Request

### HTTP Method
`{method}`

### URL
`{endpoint_path}`

### Parameters
"""
    
    if method in ["GET", "DELETE"]:
        api_docs += "#### Query Parameters\n\n"
    else:
        api_docs += "#### Request Body\n\n"
    
    api_docs += "| Name | Type | Required | Description |\n"
    api_docs += "|------|------|----------|-------------|\n"
    
    for param in params:
        api_docs += f"| {param['name']} | {param['type']} | {'Yes' if param.get('required', False) else 'No'} | {param.get('description', '')} |\n"
    
    api_docs += """
## Response

### Success Response

"""
    
    if method == "GET":
        api_docs += """#### Status Code: 200 OK

```json
{
  "id": "example-id",
  "name": "Example Resource",
  "description": "This is an example resource",
  "created_at": "2023-01-01T00:00:00Z"
}
```
"""
    elif method == "POST":
        api_docs += """#### Status Code: 201 Created

```json
{
  "id": "generated-id-123",
  "name": "Example Resource",
  "description": "This is an example resource",
  "created_at": "2023-01-01T00:00:00Z"
}
```
"""
    elif method == "PUT":
        api_docs += """#### Status Code: 200 OK

```json
{
  "id": "example-id",
  "name": "Updated Resource Name",
  "description": "This is an updated resource description",
  "updated_at": "2023-01-01T00:00:00Z"
}
```
"""
    elif method == "DELETE":
        api_docs += """#### Status Code: 204 No Content

No response body.
"""
    
    api_docs += """
### Error Responses

#### Status Code: 400 Bad Request

```json
{
  "error": "Parameter name is required"
}
```

#### Status Code: 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

## Examples

"""
    
    if method == "GET":
        api_docs += f"""### Example Request

```
curl -X GET "{endpoint_path}?id=example-id&fields=name,description"
```

### Example Response

```json
{{
  "id": "example-id",
  "name": "Example Resource",
  "description": "This is an example resource",
  "created_at": "2023-01-01T00:00:00Z"
}}
```
"""
    elif method == "POST":
        api_docs += f"""### Example Request

```
curl -X POST "{endpoint_path}" \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "New Resource", "description": "This is a new resource"}}'
```

### Example Response

```json
{{
  "id": "generated-id-123",
  "name": "New Resource",
  "description": "This is a new resource",
  "created_at": "2023-01-01T00:00:00Z"
}}
```
"""
    elif method == "PUT":
        api_docs += f"""### Example Request

```
curl -X PUT "{endpoint_path}" \\
  -H "Content-Type: application/json" \\
  -d '{{"id": "example-id", "name": "Updated Resource", "description": "This is an updated resource"}}'
```

### Example Response

```json
{{
  "id": "example-id",
  "name": "Updated Resource",
  "description": "This is an updated resource",
  "updated_at": "2023-01-01T00:00:00Z"
}}
```
"""
    elif method == "DELETE":
        api_docs += f"""### Example Request

```
curl -X DELETE "{endpoint_path}?id=example-id"
```

### Example Response

No response body (204 No Content)
"""
    
    return {
        "endpoint_path": endpoint_path,
        "method": method,
        "params": params,
        "response_type": response_type,
        "handler_name": handler_name,
        "implementations": {
            "express": express_implementation,
            "flask": flask_implementation,
            "fastapi": fastapi_implementation
        },
        "documentation": api_docs
    }


def db_schema_generate(table_name: str, fields: List[Dict[str, str]], db_type: str = "sql") -> Dict[str, Any]:
    """
    Generate database schema from field list.
    
    Args:
        table_name: The name of the table
        fields: List of fields with name and type
        db_type: The database type (sql, nosql)
        
    Returns:
        A dictionary containing the generated schema and metadata
    """
    # Default fields if none provided
    if not fields:
        fields = [
            {"name": "id", "type": "string", "primary": True, "nullable": False, "description": "Unique identifier"},
            {"name": "name", "type": "string", "nullable": False, "description": "Resource name"},
            {"name": "description", "type": "text", "nullable": True, "description": "Resource description"},
            {"name": "created_at", "type": "timestamp", "nullable": False, "description": "Creation timestamp"},
            {"name": "updated_at", "type": "timestamp", "nullable": True, "description": "Last update timestamp"}
        ]
    
    # Generate SQL schema
    sql_schema = f"""CREATE TABLE {table_name} (
"""
    
    # Add fields
    for i, field in enumerate(fields):
        field_name = field["name"]
        field_type = field["type"].upper()
        
        # Map common types to SQL types
        if field_type.lower() == "string":
            field_type = "VARCHAR(255)"
        elif field_type.lower() == "text":
            field_type = "TEXT"
        elif field_type.lower() == "integer":
            field_type = "INTEGER"
        elif field_type.lower() == "float":
            field_type = "FLOAT"
        elif field_type.lower() == "boolean":
            field_type = "BOOLEAN"
        elif field_type.lower() == "timestamp":
            field_type = "TIMESTAMP"
        elif field_type.lower() == "date":
            field_type = "DATE"
        
        # Add constraints
        constraints = []
        if field.get("primary", False):
            constraints.append("PRIMARY KEY")
        if not field.get("nullable", True):
            constraints.append("NOT NULL")
        if field.get("unique", False):
            constraints.append("UNIQUE")
        if "default" in field:
            default_value = field["default"]
            if isinstance(default_value, str) and not default_value.startswith("'"):
                default_value = f"'{default_value}'"
            constraints.append(f"DEFAULT {default_value}")
        
        # Add field definition
        sql_schema += f"    {field_name} {field_type}"
        if constraints:
            sql_schema += f" {' '.join(constraints)}"
        
        # Add comma if not the last field
        if i < len(fields) - 1:
            sql_schema += ","
        
        # Add comment if available
        if "description" in field:
            sql_schema += f" -- {field['description']}"
        
        sql_schema += "\n"
    
    sql_schema += ");"
    
    # Generate indexes
    indexes = []
    for field in fields:
        if field.get("index", False) and not field.get("primary", False):
            index_name = f"idx_{table_name}_{field['name']}"
            indexes.append(f"CREATE INDEX {index_name} ON {table_name} ({field['name']});")
    
    if indexes:
        sql_schema += "\n\n-- Indexes\n" + "\n".join(indexes)
    
    # Generate Sequelize ORM model
    sequelize_model = f"""const {table_name.capitalize()} = sequelize.define('{table_name}', {{
"""
    
    for field in fields:
        field_name = field["name"]
        field_type = field["type"].upper()
        
        # Map types to Sequelize types
        if field_type.lower() == "string":
            field_type = "DataTypes.STRING"
        elif field_type.lower() == "text":
            field_type = "DataTypes.TEXT"
        elif field_type.lower() == "integer":
            field_type = "DataTypes.INTEGER"
        elif field_type.lower() == "float":
            field_type = "DataTypes.FLOAT"
        elif field_type.lower() == "boolean":
            field_type = "DataTypes.BOOLEAN"
        elif field_type.lower() == "timestamp":
            field_type = "DataTypes.DATE"
        elif field_type.lower() == "date":
            field_type = "DataTypes.DATEONLY"
        
        # Add field definition
        sequelize_model += f"  {field_name}: {{\n"
        sequelize_model += f"    type: {field_type},\n"
        
        # Add constraints
        if field.get("primary", False):
            sequelize_model += "    primaryKey: true,\n"
        if field.get("unique", False):
            sequelize_model += "    unique: true,\n"
        if not field.get("nullable", True):
            sequelize_model += "    allowNull: false,\n"
        if "default" in field:
            default_value = field["default"]
            if isinstance(default_value, str):
                default_value = f"'{default_value}'"
            sequelize_model += f"    defaultValue: {default_value},\n"
        
        # Add comment if available
        if "description" in field:
            sequelize_model += f"    comment: '{field['description']}',\n"
        
        sequelize_model += "  },\n"
    
    sequelize_model += "}, {\n"
    sequelize_model += "  timestamps: true,\n"
    sequelize_model += "  underscored: true,\n"
    sequelize_model += "  tableName: '" + table_name + "'\n"
    sequelize_model += "});\n"
    
    # Generate SQLAlchemy ORM model
    sqlalchemy_model = f"""from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class {table_name.capitalize()}(Base):
    __tablename__ = '{table_name}'
    
"""
    
    for field in fields:
        field_name = field["name"]
        field_type = field["type"].lower()
        
        # Map types to SQLAlchemy types
        if field_type == "string":
            field_type = "String"
        elif field_type == "text":
            field_type = "Text"
        elif field_type == "integer":
            field_type = "Integer"
        elif field_type == "float":
            field_type = "Float"
        elif field_type == "boolean":
            field_type = "Boolean"
        elif field_type == "timestamp":
            field_type = "DateTime"
        elif field_type == "date":
            field_type = "Date"
        
        # Add constraints
        constraints = []
        if field.get("primary", False):
            constraints.append("primary_key=True")
        if not field.get("nullable", True):
            constraints.append("nullable=False")
        if field.get("unique", False):
            constraints.append("unique=True")
        if "default" in field:
            default_value = field["default"]
            if isinstance(default_value, str):
                default_value = f"'{default_value}'"
            constraints.append(f"default={default_value}")
        
        # Add field definition
        sqlalchemy_model += f"    {field_name} = Column({field_type}"
        if constraints:
            sqlalchemy_model += f", {', '.join(constraints)}"
        sqlalchemy_model += ")"
        
        # Add comment if available
        if "description" in field:
            sqlalchemy_model += f"  # {field['description']}"
        
        sqlalchemy_model += "\n"
    
    # Generate MongoDB schema
    mongodb_schema = f"""const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const {table_name.toLowerCase()}Schema = new Schema({{
"""
    
    for field in fields:
        field_name = field["name"]
        field_type = field["type"].lower()
        
        # Map types to MongoDB types
        if field_type == "string" or field_type == "text":
            field_type = "String"
        elif field_type == "integer" or field_type == "float":
            field_type = "Number"
        elif field_type == "boolean":
            field_type = "Boolean"
        elif field_type == "timestamp" or field_type == "date":
            field_type = "Date"
        elif field_type == "object":
            field_type = "Object"
        elif field_type == "array":
            field_type = "Array"
        
        # Simple field definition
        if not field.get("required", False) and not field.get("default", None) and not field.get("description", None):
            mongodb_schema += f"  {field_name}: {field_type}"
        else:
            # Complex field definition
            mongodb_schema += f"  {field_name}: {{\n"
            mongodb_schema += f"    type: {field_type},\n"
            
            # Add constraints
            if not field.get("nullable", True) or field.get("required", False):
                mongodb_schema += "    required: true,\n"
            if "default" in field:
                default_value = field["default"]
                if isinstance(default_value, str):
                    default_value = f"'{default_value}'"
                mongodb_schema += f"    default: {default_value},\n"
            
            mongodb_schema += "  }"
        
        # Add comma if not the last field
        if field != fields[-1]:
            mongodb_schema += ","
        
        # Add comment if available
        if "description" in field:
            mongodb_schema += f" // {field['description']}"
        
        mongodb_schema += "\n"
    
    mongodb_schema += "}, {\n"
    mongodb_schema += "  timestamps: true\n"
    mongodb_schema += "});\n\n"
    mongodb_schema += f"module.exports = mongoose.model('{table_name.capitalize()}', {table_name.toLowerCase()}Schema);\n"
    
    # Generate TypeORM entity
    typeorm_entity = f"""import {{ Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn }} from 'typeorm';

@Entity()
export class {table_name.charAt(0).toUpperCase() + table_name.slice(1)} {{
"""
    
    for field in fields:
        field_name = field["name"]
        field_type = field["type"].toLowerCase()
        
        # Add decorators
        if field.get("primary", False):
            typeorm_entity += "  @PrimaryGeneratedColumn()\n"
        else:
            # Map types to TypeORM types
            typeorm_type = field_type
            if field_type == "string":
                typeorm_type = "varchar"
            elif field_type == "integer":
                typeorm_type = "int"
            elif field_type == "timestamp":
                if field_name == "created_at":
                    typeorm_entity += "  @CreateDateColumn()\n"
                elif field_name == "updated_at":
                    typeorm_entity += "  @UpdateDateColumn()\n"
                else:
                    typeorm_entity += f"  @Column({{ type: 'timestamp' }})\n"
                typeorm_type = None  # Skip regular Column decorator
            
            # Add Column decorator if not a special column
            if typeorm_type:
                options = []
                if not field.get("nullable", True):
                    options.append("nullable: false")
                if "default" in field:
                    default_value = field["default"]
                    if isinstance(default_value, str):
                        default_value = f"'{default_value}'"
                    options.append(f"default: {default_value}")
                
                if options:
                    typeorm_entity += f"  @Column({{ type: '{typeorm_type}', {', '.join(options)} }})\n"
                else:
                    typeorm_entity += f"  @Column({{ type: '{typeorm_type}' }})\n"
        
        # Add field
        js_type = "string"
        if field_type in ["integer", "float", "number"]:
            js_type = "number"
        elif field_type in ["boolean"]:
            js_type = "boolean"
        elif field_type in ["timestamp", "date"]:
            js_type = "Date"
        
        typeorm_entity += f"  {field_name}: {js_type};"
        
        # Add comment if available
        if "description" in field:
            typeorm_entity += f" // {field['description']}"
        
        typeorm_entity += "\n\n"
    
    typeorm_entity += "}\n"
    
    return {
        "table_name": table_name,
        "fields": fields,
        "db_type": db_type,
        "schemas": {
            "sql": sql_schema,
            "sequelize": sequelize_model,
            "sqlalchemy": sqlalchemy_model,
            "mongodb": mongodb_schema,
            "typeorm": typeorm_entity
        }
    }


# Register all Dev + Testing tools
register_tool(
    name="code.read",
    description="Extract method summaries and comments from code",
    category="Dev + Testing",
    timeout_seconds=30,
    max_retries=2,
    requires_reflection=False,
    handler=code_read
)

register_tool(
    name="code.comment",
    description="Generate comments for a given code snippet",
    category="Dev + Testing",
    timeout_seconds=45,
    max_retries=2,
    requires_reflection=True,
    handler=code_comment
)

register_tool(
    name="unit.test.generate",
    description="Generate unit tests for a given code snippet",
    category="Dev + Testing",
    timeout_seconds=60,
    max_retries=3,
    requires_reflection=True,
    handler=unit_test_generate
)

register_tool(
    name="unit.test.run",
    description="Simulate running unit tests and return pass/fail output with logs",
    category="Dev + Testing",
    timeout_seconds=30,
    max_retries=2,
    requires_reflection=False,
    handler=unit_test_run
)

register_tool(
    name="debug.trace",
    description="Generate a simulated execution trace for debugging",
    category="Dev + Testing",
    timeout_seconds=45,
    max_retries=2,
    requires_reflection=True,
    handler=debug_trace
)

register_tool(
    name="api.build",
    description="Generate a scaffold for a REST/GraphQL API route and handler",
    category="Dev + Testing",
    timeout_seconds=60,
    max_retries=3,
    requires_reflection=True,
    handler=api_build
)

register_tool(
    name="db.schema.generate",
    description="Generate database schema from field list",
    category="Dev + Testing",
    timeout_seconds=45,
    max_retries=2,
    requires_reflection=False,
    handler=db_schema_generate
)
