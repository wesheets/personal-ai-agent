"""
Code Explainer Tool for the Personal AI Agent System.

This module provides functionality to analyze, explain, and suggest improvements
for code in various programming languages.
"""

import os
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("code_explainer")

def run(
    code: str,
    language: str = "python",
    explanation_level: str = "detailed",
    include_suggestions: bool = True,
    include_refactoring: bool = False,
    include_security_analysis: bool = False,
    include_performance_tips: bool = False,
    focus_areas: Optional[List[str]] = None,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["code_explanation", "development"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Analyze and explain code, providing insights and improvement suggestions.
    
    Args:
        code: The code to analyze and explain
        language: Programming language of the code
        explanation_level: Level of detail for explanation ("brief", "detailed", "comprehensive")
        include_suggestions: Whether to include improvement suggestions
        include_refactoring: Whether to include refactoring examples
        include_security_analysis: Whether to include security analysis
        include_performance_tips: Whether to include performance optimization tips
        focus_areas: Optional list of specific areas to focus on in the analysis
        store_memory: Whether to store the analysis in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing code analysis and explanation
    """
    logger.info(f"Analyzing {language} code")
    
    try:
        # Validate language
        if language.lower() not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}")
            
        # In a real implementation, this would use advanced code analysis
        # For now, we'll simulate the code analysis and explanation
        
        # Analyze code structure
        structure_analysis = _analyze_code_structure(code, language)
        
        # Generate explanation based on requested level
        explanation = _generate_explanation(code, language, explanation_level, structure_analysis)
        
        # Prepare result
        result = {
            "success": True,
            "language": language,
            "code_length": len(code),
            "structure_analysis": structure_analysis,
            "explanation": explanation
        }
        
        # Add additional analyses if requested
        if include_suggestions:
            result["improvement_suggestions"] = _generate_suggestions(code, language, structure_analysis)
            
        if include_refactoring:
            result["refactoring_examples"] = _generate_refactoring(code, language, structure_analysis)
            
        if include_security_analysis:
            result["security_analysis"] = _analyze_security(code, language)
            
        if include_performance_tips:
            result["performance_tips"] = _analyze_performance(code, language)
            
        if focus_areas:
            result["focused_analysis"] = _generate_focused_analysis(code, language, focus_areas)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the analysis for memory storage
                code_snippet = code[:100] + "..." if len(code) > 100 else code
                explanation_summary = explanation[:300] + "..." if len(explanation) > 300 else explanation
                
                memory_entry = {
                    "type": "code_explanation",
                    "language": language,
                    "code_snippet": code_snippet,
                    "explanation_summary": explanation_summary,
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored code explanation in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store code explanation in memory: {str(e)}")
        
        return result
    except Exception as e:
        error_msg = f"Error analyzing code: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "language": language
        }

def _analyze_code_structure(code: str, language: str) -> Dict[str, Any]:
    """
    Analyze the structure of the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        
    Returns:
        Dictionary with code structure analysis
    """
    # In a real implementation, this would use language-specific parsers
    # For now, we'll simulate the structure analysis
    
    # Count lines of code
    lines = code.split("\n")
    line_count = len(lines)
    
    # Estimate complexity based on line count and nesting
    complexity = "Low" if line_count < 50 else "Medium" if line_count < 200 else "High"
    
    # Basic structure analysis
    structure = {
        "line_count": line_count,
        "estimated_complexity": complexity,
        "blank_lines": sum(1 for line in lines if not line.strip()),
        "comment_lines": sum(1 for line in lines if line.strip().startswith(("#", "//", "/*", "*", "'")))
    }
    
    # Language-specific analysis
    if language.lower() == "python":
        structure["imports"] = [line.strip() for line in lines if line.strip().startswith(("import ", "from "))]
        structure["functions"] = sum(1 for line in lines if line.strip().startswith("def "))
        structure["classes"] = sum(1 for line in lines if line.strip().startswith("class "))
        
    elif language.lower() in ["javascript", "typescript"]:
        structure["imports"] = [line.strip() for line in lines if "import " in line or "require(" in line]
        structure["functions"] = sum(1 for line in lines if "function " in line or "=> {" in line)
        structure["classes"] = sum(1 for line in lines if line.strip().startswith("class "))
        
    elif language.lower() in ["java", "c#"]:
        structure["imports"] = [line.strip() for line in lines if line.strip().startswith("import ")]
        structure["methods"] = sum(1 for line in lines if "public " in line or "private " in line or "protected " in line)
        structure["classes"] = sum(1 for line in lines if "class " in line or "interface " in line)
    
    return structure

def _generate_explanation(code: str, language: str, level: str, structure: Dict[str, Any]) -> str:
    """
    Generate an explanation of the code.
    
    Args:
        code: The code to explain
        language: Programming language of the code
        level: Level of detail for explanation
        structure: Code structure analysis
        
    Returns:
        Explanation text
    """
    # In a real implementation, this would generate actual explanations
    # For now, we'll simulate explanations of different detail levels
    
    # Extract key information for the explanation
    line_count = structure["line_count"]
    complexity = structure["estimated_complexity"]
    
    # Generate explanation based on level
    if level == "brief":
        explanation = f"""
        This is a {complexity.lower()} complexity {language} program consisting of {line_count} lines of code.
        
        The code appears to {_infer_code_purpose(code, language)}.
        
        Key components include {_identify_key_components(code, language)}.
        """
    
    elif level == "comprehensive":
        explanation = f"""
        This is a {complexity.lower()} complexity {language} program consisting of {line_count} lines of code.
        
        Purpose:
        The code is designed to {_infer_code_purpose(code, language)}.
        
        Structure:
        {_explain_structure(code, language, structure)}
        
        Key Components:
        {_identify_key_components(code, language, detailed=True)}
        
        Control Flow:
        {_explain_control_flow(code, language)}
        
        Data Handling:
        {_explain_data_handling(code, language)}
        
        External Dependencies:
        {_identify_dependencies(code, language, structure)}
        
        Overall Assessment:
        {_provide_overall_assessment(code, language, structure)}
        """
    
    else:  # detailed (default)
        explanation = f"""
        This is a {complexity.lower()} complexity {language} program consisting of {line_count} lines of code.
        
        Purpose:
        The code is designed to {_infer_code_purpose(code, language)}.
        
        Structure:
        {_explain_structure(code, language, structure)}
        
        Key Components:
        {_identify_key_components(code, language)}
        
        Control Flow:
        {_explain_control_flow(code, language)}
        
        External Dependencies:
        {_identify_dependencies(code, language, structure)}
        """
    
    return explanation.strip()

def _infer_code_purpose(code: str, language: str) -> str:
    """
    Infer the purpose of the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        
    Returns:
        Inferred purpose
    """
    # This is a simplified simulation
    
    if "def main" in code or "function main" in code:
        return "serve as a standalone program with a main entry point"
    
    if "class" in code and ("__init__" in code or "constructor" in code):
        return "define a class with initialization logic"
    
    if "import" in code and "def " in code:
        return "provide utility functions that can be imported by other modules"
    
    if "fetch" in code or "request" in code or "http" in code.lower():
        return "make HTTP requests to external services"
    
    if "read" in code and ("file" in code or "csv" in code or "json" in code):
        return "read and process data from files"
    
    if "write" in code and ("file" in code or "save" in code or "output" in code):
        return "generate and save output to files"
    
    if "plot" in code or "chart" in code or "graph" in code:
        return "visualize data through charts or graphs"
    
    if "model" in code or "predict" in code or "train" in code:
        return "implement machine learning or data analysis functionality"
    
    # Default
    return "perform various operations based on the provided logic"

def _explain_structure(code: str, language: str, structure: Dict[str, Any]) -> str:
    """
    Explain the structure of the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        structure: Code structure analysis
        
    Returns:
        Structure explanation
    """
    # This is a simplified simulation
    
    parts = []
    
    if language.lower() == "python":
        if "imports" in structure and structure["imports"]:
            parts.append(f"The code imports {len(structure['imports'])} modules or packages.")
        
        if "functions" in structure:
            parts.append(f"It defines {structure['functions']} functions.")
        
        if "classes" in structure:
            parts.append(f"It contains {structure['classes']} classes.")
    
    elif language.lower() in ["javascript", "typescript"]:
        if "imports" in structure and structure["imports"]:
            parts.append(f"The code imports {len(structure['imports'])} modules or packages.")
        
        if "functions" in structure:
            parts.append(f"It defines {structure['functions']} functions.")
        
        if "classes" in structure:
            parts.append(f"It contains {structure['classes']} classes.")
    
    elif language.lower() in ["java", "c#"]:
        if "imports" in structure and structure["imports"]:
            parts.append(f"The code imports {len(structure['imports'])} packages or namespaces.")
        
        if "classes" in structure:
            parts.append(f"It defines {structure['classes']} classes or interfaces.")
        
        if "methods" in structure:
            parts.append(f"It contains {structure['methods']} methods.")
    
    # Add general structure information
    parts.append(f"The code has {structure['blank_lines']} blank lines and approximately {structure['comment_lines']} comment lines.")
    
    return " ".join(parts)

def _identify_key_components(code: str, language: str, detailed: bool = False) -> str:
    """
    Identify key components in the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        detailed: Whether to provide detailed component descriptions
        
    Returns:
        Key components description
    """
    # This is a simplified simulation
    
    components = []
    
    if "class" in code:
        components.append("class definitions")
    
    if "def " in code or "function " in code:
        components.append("function definitions")
    
    if "import" in code or "require" in code:
        components.append("module imports")
    
    if "for " in code:
        components.append("loop structures")
    
    if "if " in code:
        components.append("conditional logic")
    
    if "try" in code and "except" in code or "try" in code and "catch" in code:
        components.append("error handling")
    
    if "return" in code:
        components.append("return statements")
    
    if "async" in code or "await" in code or "Promise" in code:
        components.append("asynchronous operations")
    
    if "print" in code or "console.log" in code or "System.out" in code:
        components.append("output statements")
    
    if "input" in code or "readline" in code or "Scanner" in code:
        components.append("input handling")
    
    if not components:
        return "basic operations and assignments"
    
    if detailed:
        return ", ".join(components) + ". " + _elaborate_on_components(code, language, components)
    else:
        return ", ".join(components)

def _elaborate_on_components(code: str, language: str, components: List[str]) -> str:
    """
    Provide more detailed explanations of identified components.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        components: List of identified components
        
    Returns:
        Elaborated explanation
    """
    # This is a simplified simulation
    
    elaborations = []
    
    if "class definitions" in components:
        elaborations.append("The classes appear to implement object-oriented patterns for data encapsulation and behavior.")
    
    if "function definitions" in components:
        elaborations.append("The functions break down the logic into modular, reusable pieces.")
    
    if "loop structures" in components:
        elaborations.append("Loops are used for iterative processing of data or repeated operations.")
    
    if "conditional logic" in components:
        elaborations.append("Conditional statements control the flow of execution based on various criteria.")
    
    if "error handling" in components:
        elaborations.append("Error handling mechanisms are in place to gracefully manage exceptions.")
    
    if "asynchronous operations" in components:
        elaborations.append("Asynchronous code patterns are used to handle non-blocking operations.")
    
    return " ".join(elaborations)

def _explain_control_flow(code: str, language: str) -> str:
    """
    Explain the control flow of the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        
    Returns:
        Control flow explanation
    """
    # This is a simplified simulation
    
    flow_patterns = []
    
    if "if " in code:
        flow_patterns.append("conditional branching")
    
    if "for " in code:
        flow_patterns.append("iterative processing")
    
    if "while " in code:
        flow_patterns.append("conditional looping")
    
    if "switch" in code or "match" in code:
        flow_patterns.append("multi-way branching")
    
    if "return" in code:
        flow_patterns.append("early returns")
    
    if "break" in code:
        flow_patterns.append("loop termination")
    
    if "continue" in code:
        flow_patterns.append("loop iteration skipping")
    
    if "try" in code:
        flow_patterns.append("exception handling")
    
    if "yield" in code or "generator" in code:
        flow_patterns.append("generator-based iteration")
    
    if "async" in code or "await" in code or "Promise" in code or ".then" in code:
        flow_patterns.append("asynchronous execution")
    
    if "callback" in code:
        flow_patterns.append("callback-based flow")
    
    if not flow_patterns:
        return "The code follows a straightforward, sequential execution path."
    
    return f"The code utilizes {', '.join(flow_patterns)} to control its execution flow."

def _explain_data_handling(code: str, language: str) -> str:
    """
    Explain how data is handled in the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        
    Returns:
        Data handling explanation
    """
    # This is a simplified simulation
    
    data_patterns = []
    
    if "list" in code or "array" in code or "[" in code:
        data_patterns.append("lists/arrays")
    
    if "dict" in code or "map" in code or "{" in code:
        data_patterns.append("dictionaries/maps")
    
    if "set" in code or "Set" in code:
        data_patterns.append("sets")
    
    if "class" in code and ("self" in code or "this" in code):
        data_patterns.append("object properties")
    
    if "json" in code.lower():
        data_patterns.append("JSON data")
    
    if "xml" in code.lower():
        data_patterns.append("XML data")
    
    if "csv" in code.lower():
        data_patterns.append("CSV data")
    
    if "database" in code.lower() or "sql" in code.lower() or "query" in code.lower():
        data_patterns.append("database operations")
    
    if "file" in code.lower() or "open(" in code or "read" in code or "write" in code:
        data_patterns.append("file I/O")
    
    if not data_patterns:
        return "The code primarily works with simple variables and basic data types."
    
    return f"The code works with {', '.join(data_patterns)} for data storage and manipulation."

def _identify_dependencies(code: str, language: str, structure: Dict[str, Any]) -> str:
    """
    Identify external dependencies in the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        structure: Code structure analysis
        
    Returns:
        Dependencies explanation
    """
    # This is a simplified simulation
    
    if "imports" not in structure or not structure["imports"]:
        return "The code does not appear to have external dependencies."
    
    num_imports = len(structure["imports"])
    
    if num_imports <= 3:
        return f"The code has {num_imports} external dependencies: {', '.join(structure['imports'])}."
    else:
        return f"The code has {num_imports} external dependencies, including {', '.join(structure['imports'][:3])} and others."

def _provide_overall_assessment(code: str, language: str, structure: Dict[str, Any]) -> str:
    """
    Provide an overall assessment of the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        structure: Code structure analysis
        
    Returns:
        Overall assessment
    """
    # This is a simplified simulation
    
    complexity = structure["estimated_complexity"]
    line_count = structure["line_count"]
    
    if complexity == "Low":
        return f"This is a relatively simple {language} program with straightforward logic and minimal complexity."
    
    elif complexity == "Medium":
        return f"This is a moderately complex {language} program with a reasonable structure and organization."
    
    else:  # High
        return f"This is a complex {language} program that would benefit from careful review and potentially refactoring for maintainability."

def _generate_suggestions(code: str, language: str, structure: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate improvement suggestions for the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        structure: Code structure analysis
        
    Returns:
        List of improvement suggestions
    """
    # This is a simplified simulation
    
    suggestions = []
    
    # Suggestion based on comment ratio
    comment_ratio = structure["comment_lines"] / structure["line_count"] if structure["line_count"] > 0 else 0
    if comment_ratio < 0.1:
        suggestions.append({
            "type": "documentation",
            "suggestion": "Consider adding more comments to explain complex logic and improve code readability.",
            "importance": "medium"
        })
    
    # Suggestion based on function/method count
    function_count = structure.get("functions", 0) or structure.get("methods", 0)
    if function_count > 10:
        suggestions.append({
            "type": "organization",
            "suggestion": "Consider breaking down the code into multiple modules or files for better organization.",
            "importance": "medium"
        })
    
    # Suggestion based on line count
    if structure["line_count"] > 300:
        suggestions.append({
            "type": "complexity",
            "suggestion": "The code is quite long. Consider refactoring to improve maintainability.",
            "importance": "high"
        })
    
    # Language-specific suggestions
    if language.lower() == "python":
        if "import *" in code:
            suggestions.append({
                "type": "best_practice",
                "suggestion": "Avoid using 'import *' as it can lead to namespace pollution. Import only what you need.",
                "importance": "medium"
            })
    
    elif language.lower() in ["javascript", "typescript"]:
        if "var " in code:
            suggestions.append({
                "type": "modernization",
                "suggestion": "Consider using 'let' and 'const' instead of 'var' for better scoping and immutability.",
                "importance": "medium"
            })
    
    # Generic suggestions
    suggestions.append({
        "type": "testing",
        "suggestion": "Consider adding unit tests to verify the code's functionality and prevent regressions.",
        "importance": "high"
    })
    
    return suggestions

def _generate_refactoring(code: str, language: str, structure: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate refactoring examples for the code.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        structure: Code structure analysis
        
    Returns:
        List of refactoring examples
    """
    # This is a simplified simulation
    
    refactoring_examples = []
    
    # Extract a small code snippet for demonstration
    lines = code.split("\n")
    snippet = "\n".join(lines[:min(5, len(lines))])
    
    # Generic refactoring examples
    refactoring_examples.append({
        "name": "Extract Function",
        "description": "Break down complex logic into smaller, reusable functions.",
        "before": snippet,
        "after": _simulate_extract_function(snippet, language)
    })
    
    refactoring_examples.append({
        "name": "Improve Variable Names",
        "description": "Use more descriptive variable names to enhance readability.",
        "before": snippet,
        "after": _simulate_improve_names(snippet, language)
    })
    
    # Language-specific refactoring
    if language.lower() == "python":
        refactoring_examples.append({
            "name": "Use List Comprehension",
            "description": "Replace for loops with more concise list comprehensions where appropriate.",
            "before": "results = []\nfor x in data:\n    if x > 0:\n        results.append(x * 2)",
            "after": "results = [x * 2 for x in data if x > 0]"
        })
    
    elif language.lower() in ["javascript", "typescript"]:
        refactoring_examples.append({
            "name": "Use Modern Array Methods",
            "description": "Replace imperative loops with declarative array methods.",
            "before": "const results = [];\nfor (let i = 0; i < data.length; i++) {\n    if (data[i] > 0) {\n        results.push(data[i] * 2);\n    }\n}",
            "after": "const results = data.filter(x => x > 0).map(x => x * 2);"
        })
    
    return refactoring_examples

def _simulate_extract_function(snippet: str, language: str) -> str:
    """
    Simulate extracting a function from a code snippet.
    
    Args:
        snippet: Code snippet
        language: Programming language
        
    Returns:
        Refactored code
    """
    # This is a simplified simulation
    
    if language.lower() == "python":
        return f"def process_data(data):\n    # Extracted function to handle data processing\n{snippet.replace('    ', '    ')}\n\n# Call the extracted function\nresult = process_data(input_data)"
    
    elif language.lower() in ["javascript", "typescript"]:
        return f"function processData(data) {{\n    // Extracted function to handle data processing\n{snippet.replace('    ', '    ')}\n}}\n\n// Call the extracted function\nconst result = processData(inputData);"
    
    else:
        return f"// Extracted function\nprocessData(data) {{\n    // Logic to handle data processing\n{snippet}\n}}\n\n// Call the extracted function\nresult = processData(inputData);"

def _simulate_improve_names(snippet: str, language: str) -> str:
    """
    Simulate improving variable names in a code snippet.
    
    Args:
        snippet: Code snippet
        language: Programming language
        
    Returns:
        Refactored code
    """
    # This is a very simplified simulation
    # In a real implementation, this would analyze the code and suggest meaningful names
    
    improved = snippet.replace("x", "item")
    improved = improved.replace("i", "index")
    improved = improved.replace("arr", "dataArray")
    improved = improved.replace("fn", "processFunction")
    improved = improved.replace("tmp", "temporaryValue")
    improved = improved.replace("res", "result")
    
    return improved

def _analyze_security(code: str, language: str) -> List[Dict[str, str]]:
    """
    Analyze code for security issues.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        
    Returns:
        List of security issues
    """
    # This is a simplified simulation
    
    security_issues = []
    
    # Check for common security issues
    if "password" in code.lower() and ("hardcoded" in code.lower() or "=" in code):
        security_issues.append({
            "severity": "high",
            "issue": "Potential hardcoded password or credentials",
            "recommendation": "Store sensitive information in environment variables or secure credential stores."
        })
    
    if "sql" in code.lower() and "'" in code:
        security_issues.append({
            "severity": "high",
            "issue": "Potential SQL injection vulnerability",
            "recommendation": "Use parameterized queries or an ORM instead of string concatenation for SQL queries."
        })
    
    if "exec(" in code or "eval(" in code:
        security_issues.append({
            "severity": "high",
            "issue": "Use of potentially dangerous functions (exec/eval)",
            "recommendation": "Avoid using exec() or eval() as they can execute arbitrary code."
        })
    
    # Language-specific security checks
    if language.lower() == "python":
        if "pickle.load" in code:
            security_issues.append({
                "severity": "medium",
                "issue": "Use of pickle module which can lead to code execution vulnerabilities",
                "recommendation": "Consider using safer serialization formats like JSON."
            })
    
    elif language.lower() in ["javascript", "typescript"]:
        if "innerHTML" in code:
            security_issues.append({
                "severity": "medium",
                "issue": "Use of innerHTML which can lead to XSS vulnerabilities",
                "recommendation": "Use textContent or DOM manipulation methods instead."
            })
    
    # If no issues found
    if not security_issues:
        security_issues.append({
            "severity": "info",
            "issue": "No obvious security issues detected",
            "recommendation": "Continue following security best practices and consider a comprehensive security review."
        })
    
    return security_issues

def _analyze_performance(code: str, language: str) -> List[Dict[str, str]]:
    """
    Analyze code for performance issues.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        
    Returns:
        List of performance tips
    """
    # This is a simplified simulation
    
    performance_tips = []
    
    # Check for common performance issues
    if "for" in code and "for" in code[code.find("for")+3:]:
        performance_tips.append({
            "impact": "medium",
            "issue": "Nested loops detected",
            "recommendation": "Nested loops can lead to O(n²) complexity. Consider if the algorithm can be optimized."
        })
    
    # Language-specific performance tips
    if language.lower() == "python":
        if "+=" in code and "[" in code and "]" in code:
            performance_tips.append({
                "impact": "low",
                "issue": "Potential inefficient list concatenation",
                "recommendation": "Consider using list.append() for single items or list.extend() for multiple items instead of += for better performance."
            })
    
    elif language.lower() in ["javascript", "typescript"]:
        if "document.getElementsBy" in code and "for" in code:
            performance_tips.append({
                "impact": "medium",
                "issue": "Potential DOM collection iteration inefficiency",
                "recommendation": "Consider caching the length of DOM collections when iterating to avoid recalculating it on each iteration."
            })
    
    # Generic performance tips
    performance_tips.append({
        "impact": "info",
        "issue": "General optimization",
        "recommendation": "Profile the code to identify actual bottlenecks before optimizing. Premature optimization can lead to more complex, harder to maintain code."
    })
    
    return performance_tips

def _generate_focused_analysis(code: str, language: str, focus_areas: List[str]) -> Dict[str, Any]:
    """
    Generate analysis focused on specific areas.
    
    Args:
        code: The code to analyze
        language: Programming language of the code
        focus_areas: Areas to focus on
        
    Returns:
        Focused analysis
    """
    # This is a simplified simulation
    
    focused_results = {}
    
    for area in focus_areas:
        area_lower = area.lower()
        
        if "readability" in area_lower:
            focused_results["readability"] = {
                "assessment": "The code's readability is " + ("good" if len(code.split("\n")) < 100 else "moderate" if len(code.split("\n")) < 300 else "potentially challenging"),
                "suggestions": [
                    "Consider adding more comments to explain complex logic",
                    "Break down long functions into smaller, more focused ones",
                    "Use consistent indentation and formatting"
                ]
            }
        
        elif "maintainability" in area_lower:
            focused_results["maintainability"] = {
                "assessment": "The code's maintainability is " + ("good" if len(code.split("\n")) < 100 else "moderate" if len(code.split("\n")) < 300 else "potentially challenging"),
                "suggestions": [
                    "Ensure proper error handling is in place",
                    "Consider adding unit tests",
                    "Document public APIs and complex logic",
                    "Follow the Single Responsibility Principle for functions and classes"
                ]
            }
        
        elif "scalability" in area_lower:
            focused_results["scalability"] = {
                "assessment": "Based on the code structure, scalability considerations include:",
                "considerations": [
                    "Consider how the code will handle increased data volume",
                    "Evaluate if the current algorithms have appropriate time complexity",
                    "Consider potential bottlenecks in resource usage",
                    "Evaluate if the architecture allows for horizontal scaling if needed"
                ]
            }
        
        elif "testing" in area_lower:
            focused_results["testing"] = {
                "assessment": "Testing considerations for this code:",
                "suggestions": [
                    "Identify key functions that would benefit from unit tests",
                    "Consider edge cases and boundary conditions",
                    "Ensure error paths are tested, not just happy paths",
                    "Consider mocking external dependencies for isolated testing"
                ]
            }
    
    return focused_results

# Define supported languages
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "java",
    "c#",
    "c++",
    "go",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "rust",
    "bash",
    "sql",
    "r",
    "scala",
    "perl",
    "html",
    "css"
]
