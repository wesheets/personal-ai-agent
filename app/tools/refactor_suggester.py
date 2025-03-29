"""
Refactor Suggester Tool for Autonomous Coding Agents.

This module provides functionality to suggest code improvements, cleaner structure,
and performance gains for submitted code.
"""

import os
import sys
import ast
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RefactorSuggester:
    """
    Tool for suggesting code improvements, cleaner structure, and performance gains.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the RefactorSuggester.
        
        Args:
            memory_manager: Optional memory manager for storing refactoring suggestions
        """
        self.memory_manager = memory_manager
    
    async def run(
        self,
        code_path: str,
        output_path: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        include_code_examples: bool = True,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Suggest code improvements for submitted code.
        
        Args:
            code_path: Path to the code file to analyze
            output_path: Optional path to write the suggestions to
            focus_areas: Optional list of areas to focus on (performance, readability, structure, etc.)
            include_code_examples: Whether to include code examples in suggestions
            store_memory: Whether to store suggestions in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing refactoring suggestions
        """
        try:
            # Validate inputs
            if not os.path.exists(code_path):
                return {
                    "status": "error",
                    "error": f"Code path does not exist: {code_path}"
                }
            
            if not os.path.isfile(code_path):
                return {
                    "status": "error",
                    "error": f"Code path is not a file: {code_path}"
                }
            
            # Set default focus areas if not provided
            if not focus_areas:
                focus_areas = ["performance", "readability", "structure", "maintainability"]
            
            # Read the code file
            with open(code_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse the code
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return {
                    "status": "error",
                    "error": f"Syntax error in code file: {str(e)}"
                }
            
            # Analyze code and generate suggestions
            suggestions = self._analyze_code(tree, code, focus_areas, include_code_examples)
            
            if not suggestions:
                return {
                    "status": "success",
                    "message": "No refactoring suggestions found. The code appears to follow best practices.",
                    "suggestions": []
                }
            
            # Format suggestions
            formatted_suggestions = self._format_suggestions(suggestions, include_code_examples)
            
            # Write suggestions to file if output path is provided
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_suggestions)
            
            # Prepare result
            result = {
                "status": "success",
                "code_path": code_path,
                "output_path": output_path,
                "focus_areas": focus_areas,
                "suggestion_count": len(suggestions),
                "suggestions": suggestions,
                "formatted_suggestions": formatted_suggestions
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager:
                memory_content = {
                    "type": "refactor_suggestions",
                    "code_path": code_path,
                    "focus_areas": focus_areas,
                    "suggestions": suggestions
                }
                
                tags = memory_tags or ["refactor", "code_quality"]
                
                # Add focus areas to tags
                for area in focus_areas:
                    if area not in tags:
                        tags.append(area)
                
                # Add module name to tags
                module_name = os.path.basename(code_path).replace(".py", "")
                if module_name not in tags:
                    tags.append(module_name)
                
                await self.memory_manager.store(
                    input_text=f"Generate refactoring suggestions for {os.path.basename(code_path)}",
                    output_text=f"Generated {result['suggestion_count']} refactoring suggestions focusing on {', '.join(focus_areas)}.",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating refactoring suggestions: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _analyze_code(
        self,
        tree: ast.AST,
        code: str,
        focus_areas: List[str],
        include_code_examples: bool
    ) -> List[Dict[str, Any]]:
        """
        Analyze code and generate suggestions.
        
        Args:
            tree: AST of the code
            code: Original code string
            focus_areas: Areas to focus on
            include_code_examples: Whether to include code examples
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Add analyzers based on focus areas
        if "performance" in focus_areas:
            suggestions.extend(self._analyze_performance(tree, code))
        
        if "readability" in focus_areas:
            suggestions.extend(self._analyze_readability(tree, code))
        
        if "structure" in focus_areas:
            suggestions.extend(self._analyze_structure(tree, code))
        
        if "maintainability" in focus_areas:
            suggestions.extend(self._analyze_maintainability(tree, code))
        
        return suggestions
    
    def _analyze_performance(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code for performance improvements.
        
        Args:
            tree: AST of the code
            code: Original code string
            
        Returns:
            List of performance-related suggestions
        """
        suggestions = []
        
        # Check for inefficient list comprehensions vs. generator expressions
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                # Check if the list comprehension is used in a context where a generator would be more efficient
                parent = self._get_parent(tree, node)
                if isinstance(parent, (ast.Call, ast.BoolOp, ast.Compare)):
                    suggestions.append({
                        "type": "performance",
                        "line": node.lineno,
                        "title": "Consider using a generator expression instead of a list comprehension",
                        "description": "Generator expressions are more memory-efficient than list comprehensions when the result is consumed immediately.",
                        "original_code": self._get_node_source(node, code),
                        "suggested_code": self._get_node_source(node, code).replace("[", "(").replace("]", ")"),
                        "priority": "medium"
                    })
        
        # Check for repeated function calls that could be cached
        function_calls = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_str = self._get_node_source(node, code)
                if call_str not in function_calls:
                    function_calls[call_str] = []
                function_calls[call_str].append(node.lineno)
        
        for call_str, lines in function_calls.items():
            if len(lines) > 2 and "(" in call_str and ")" in call_str:
                suggestions.append({
                    "type": "performance",
                    "line": lines[0],
                    "title": f"Consider caching the result of '{call_str}'",
                    "description": f"The function '{call_str}' is called multiple times (lines {', '.join(map(str, lines))}). Consider caching the result in a variable if the function is pure and expensive.",
                    "original_code": f"result1 = {call_str}\nresult2 = {call_str}",
                    "suggested_code": f"cached_result = {call_str}\nresult1 = cached_result\nresult2 = cached_result",
                    "priority": "medium"
                })
        
        return suggestions
    
    def _analyze_readability(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code for readability improvements.
        
        Args:
            tree: AST of the code
            code: Original code string
            
        Returns:
            List of readability-related suggestions
        """
        suggestions = []
        
        # Check for overly complex expressions
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp) and len(node.values) > 3:
                suggestions.append({
                    "type": "readability",
                    "line": node.lineno,
                    "title": "Consider breaking down complex boolean expression",
                    "description": "Complex boolean expressions with many conditions are hard to read. Consider breaking them down into multiple variables with descriptive names.",
                    "original_code": self._get_node_source(node, code),
                    "suggested_code": "# Break down into multiple variables with descriptive names\n" + 
                                     "condition1 = ...\ncondition2 = ...\nresult = condition1 and condition2",
                    "priority": "medium"
                })
            
            # Check for deeply nested expressions
            elif isinstance(node, (ast.If, ast.For, ast.While)) and self._get_nesting_level(tree, node) > 3:
                suggestions.append({
                    "type": "readability",
                    "line": node.lineno,
                    "title": "Consider reducing nesting level",
                    "description": "Deeply nested code blocks are hard to read and maintain. Consider extracting inner blocks into separate functions or using early returns to reduce nesting.",
                    "original_code": self._get_node_source(node, code),
                    "suggested_code": "# Extract inner blocks into separate functions\ndef handle_inner_logic():\n    ...\n\n# Or use early returns\nif not condition:\n    return\n# Rest of the code without nesting",
                    "priority": "high"
                })
        
        # Check for functions that are too long
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.body) > 30:
                    suggestions.append({
                        "type": "readability",
                        "line": node.lineno,
                        "title": f"Function '{node.name}' is too long",
                        "description": f"The function '{node.name}' has {len(node.body)} statements. Long functions are hard to understand and maintain. Consider breaking it down into smaller, more focused functions.",
                        "original_code": f"def {node.name}(...):\n    # {len(node.body)} statements...",
                        "suggested_code": f"def {node.name}(...):\n    result = helper_function1(...)\n    return helper_function2(result)\n\ndef helper_function1(...):\n    # Extracted logic...\n\ndef helper_function2(...):\n    # Extracted logic...",
                        "priority": "high"
                    })
        
        return suggestions
    
    def _analyze_structure(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code for structural improvements.
        
        Args:
            tree: AST of the code
            code: Original code string
            
        Returns:
            List of structure-related suggestions
        """
        suggestions = []
        
        # Check for classes that could use dataclasses
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                init_method = None
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        init_method = item
                        break
                
                if init_method:
                    # Check if __init__ mostly assigns parameters to attributes
                    assignments = 0
                    total_statements = 0
                    
                    for stmt in init_method.body:
                        total_statements += 1
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                    assignments += 1
                    
                    if assignments > 3 and assignments / total_statements > 0.7:
                        suggestions.append({
                            "type": "structure",
                            "line": node.lineno,
                            "title": f"Consider using @dataclass for '{node.name}'",
                            "description": f"The class '{node.name}' primarily stores data with {assignments} attribute assignments in __init__. Consider using @dataclass to reduce boilerplate code.",
                            "original_code": f"class {node.name}:\n    def __init__(self, ...):\n        self.attr1 = attr1\n        self.attr2 = attr2\n        ...",
                            "suggested_code": f"from dataclasses import dataclass\n\n@dataclass\nclass {node.name}:\n    attr1: type\n    attr2: type\n    ...",
                            "priority": "medium"
                        })
        
        # Check for repeated code patterns that could be refactored
        code_patterns = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Expr, ast.Assign, ast.AugAssign)) and hasattr(node, 'lineno'):
                code_str = self._get_node_source(node, code)
                if len(code_str) > 20:  # Only consider substantial code blocks
                    if code_str not in code_patterns:
                        code_patterns[code_str] = []
                    code_patterns[code_str].append(node.lineno)
        
        for pattern, lines in code_patterns.items():
            if len(lines) > 1:
                suggestions.append({
                    "type": "structure",
                    "line": lines[0],
                    "title": "Repeated code pattern detected",
                    "description": f"The same code pattern appears multiple times (lines {', '.join(map(str, lines))}). Consider extracting it into a function to avoid duplication.",
                    "original_code": pattern,
                    "suggested_code": f"def extracted_function(...):\n    {pattern.replace(chr(10), chr(10) + '    ')}\n\n# Usage:\nextracted_function(...)",
                    "priority": "high"
                })
        
        return suggestions
    
    def _analyze_maintainability(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code for maintainability improvements.
        
        Args:
            tree: AST of the code
            code: Original code string
            
        Returns:
            List of maintainability-related suggestions
        """
        suggestions = []
        
        # Check for magic numbers
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                # Exclude common values like 0, 1, -1
                if node.value not in (0, 1, -1, 2, 10, 100) and abs(node.value) > 1:
                    parent = self._get_parent(tree, node)
                    # Exclude numbers in simple assignments (might be constants already)
                    if not (isinstance(parent, ast.Assign) and len(parent.targets) == 1 and isinstance(parent.targets[0], ast.Name)):
                        suggestions.append({
                            "type": "maintainability",
                            "line": node.lineno,
                            "title": f"Consider replacing magic number '{node.value}'",
                            "description": f"The number {node.value} appears in the code without explanation. Consider defining it as a named constant to improve maintainability.",
                            "original_code": f"result = calculation * {node.value}",
                            "suggested_code": f"MEANINGFUL_CONSTANT_NAME = {node.value}  # Add explanation here\nresult = calculation * MEANINGFUL_CONSTANT_NAME",
                            "priority": "medium"
                        })
        
        # Check for commented-out code
        lines = code.splitlines()
        commented_blocks = []
        current_block = []
        in_block = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") and len(stripped) > 2:
                # Check if it looks like code (has common programming constructs)
                code_indicators = ["def ", "class ", "import ", "from ", "if ", "for ", "while ", "return ", "=", "+=", "-=", "==", "!="]
                is_code = any(indicator in stripped[1:] for indicator in code_indicators)
                
                if is_code:
                    if not in_block:
                        in_block = True
                        current_block = []
                    current_block.append((i + 1, stripped))
            else:
                if in_block and len(current_block) > 1:  # Only consider blocks with multiple lines
                    commented_blocks.append(current_block)
                in_block = False
        
        # Add the last block if there is one
        if in_block and len(current_block) > 1:
            commented_blocks.append(current_block)
        
        for block in commented_blocks:
            start_line = block[0][0]
            suggestions.append({
                "type": "maintainability",
                "line": start_line,
                "title": "Commented-out code block detected",
                "description": f"There is a block of commented-out code starting at line {start_line}. Commented-out code reduces maintainability. Consider removing it or documenting why it's kept.",
                "original_code": "\n".join(line[1] for line in block),
                "suggested_code": "# Either remove the commented code entirely or add a clear explanation:\n# NOTE: This code is kept for reference because...",
                "priority": "low"
            })
        
        # Check for TODO comments without assignee or ticket reference
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line:
                has_assignee = "@" in line
                has_ticket = any(ref in line for ref in ["#", "JIRA-", "TICKET-", "ISSUE-"])
                
                if not (has_assignee or has_ticket):
                    suggestions.append({
                        "type": "maintainability",
                        "line": i + 1,
                        "title": "TODO comment without assignee or ticket reference",
                        "description": f"The TODO comment on line {i + 1} doesn't have an assignee or ticket reference. This makes it hard to track and follow up.",
                        "original_code": line.strip(),
                        "suggested_code": f"{line.strip()} (@username, #issue-number)",
                        "priority": "low"
                    })
        
        return suggestions
    
    def _format_suggestions(self, suggestions: List[Dict[str, Any]], include_code_examples: bool) -> str:
        """
        Format suggestions into a readable string.
        
        Args:
            suggestions: List of suggestions
            include_code_examples: Whether to include code examples
            
        Returns:
            Formatted suggestions as string
        """
        if not suggestions:
            return "No refactoring suggestions found. The code appears to follow best practices."
        
        # Group suggestions by type
        grouped = {}
        for suggestion in suggestions:
            suggestion_type = suggestion["type"]
            if suggestion_type not in grouped:
                grouped[suggestion_type] = []
            grouped[suggestion_type].append(suggestion)
        
        # Format each group
        formatted = ["# Refactoring Suggestions", ""]
        
        for suggestion_type, group in grouped.items():
            formatted.append(f"## {suggestion_type.capitalize()} ({len(group)} suggestions)")
            formatted.append("")
            
            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_group = sorted(group, key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
            
            for i, suggestion in enumerate(sorted_group):
                formatted.append(f"### {i+1}. {suggestion['title']} (line {suggestion['line']})")
                formatted.append("")
                formatted.append(suggestion["description"])
                formatted.append("")
                
                if include_code_examples and "original_code" in suggestion and "suggested_code" in suggestion:
                    formatted.append("Original code:")
                    formatted.append("```python")
                    formatted.append(suggestion["original_code"])
                    formatted.append("```")
                    formatted.append("")
                    formatted.append("Suggested improvement:")
                    formatted.append("```python")
                    formatted.append(suggestion["suggested_code"])
                    formatted.append("```")
                    formatted.append("")
            
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _get_parent(self, tree: ast.AST, node: ast.AST) -> Optional[ast.AST]:
        """
        Get the parent node of a given node.
        
        Args:
            tree: AST of the code
            node: Node to find parent for
            
        Returns:
            Parent node or None
        """
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None
    
    def _get_nesting_level(self, tree: ast.AST, node: ast.AST) -> int:
        """
        Get the nesting level of a node.
        
        Args:
            tree: AST of the code
            node: Node to find nesting level for
            
        Returns:
            Nesting level
        """
        level = 0
        current = node
        
        while True:
            parent = self._get_parent(tree, current)
            if parent is None:
                break
            
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Stop at function or class definitions
                break
            
            if isinstance(parent, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                level += 1
            
            current = parent
        
        return level
    
    def _get_node_source(self, node: ast.AST, code: str) -> str:
        """
        Get the source code for a node.
        
        Args:
            node: AST node
            code: Original code string
            
        Returns:
            Source code for the node
        """
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return "<unknown>"
        
        lines = code.splitlines()
        
        # Handle single-line nodes
        if node.lineno == getattr(node, 'end_lineno', node.lineno):
            line = lines[node.lineno - 1]
            start_col = getattr(node, 'col_offset', 0)
            end_col = getattr(node, 'end_col_offset', len(line))
            return line[start_col:end_col]
        
        # Handle multi-line nodes
        start_line = node.lineno - 1
        end_line = getattr(node, 'end_lineno', start_line + 1) - 1
        
        if start_line >= len(lines) or end_line >= len(lines):
            return "<unknown>"
        
        result = []
        for i in range(start_line, end_line + 1):
            if i == start_line:
                result.append(lines[i][getattr(node, 'col_offset', 0):])
            elif i == end_line:
                result.append(lines[i][:getattr(node, 'end_col_offset', len(lines[i]))])
            else:
                result.append(lines[i])
        
        return "\n".join(result)
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_refactor_suggester(memory_manager=None):
    """
    Get a RefactorSuggester instance.
    
    Args:
        memory_manager: Optional memory manager for storing refactoring suggestions
        
    Returns:
        RefactorSuggester instance
    """
    return RefactorSuggester(memory_manager=memory_manager)
