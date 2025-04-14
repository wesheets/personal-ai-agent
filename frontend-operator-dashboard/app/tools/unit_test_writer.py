"""
Unit Test Writer Tool for Autonomous Coding Agents.

This module provides functionality to auto-generate unit tests for submitted functions.
"""

import os
import sys
import ast
import inspect
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnitTestWriter:
    """
    Tool for auto-generating unit tests for submitted functions.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the UnitTestWriter.
        
        Args:
            memory_manager: Optional memory manager for storing generated tests
        """
        self.memory_manager = memory_manager
    
    async def run(
        self,
        code_path: str,
        output_path: Optional[str] = None,
        test_framework: str = "pytest",
        include_edge_cases: bool = True,
        include_doctest_examples: bool = True,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate unit tests for submitted functions.
        
        Args:
            code_path: Path to the code file to generate tests for
            output_path: Optional path to write the generated tests to
            test_framework: Test framework to use (pytest or unittest)
            include_edge_cases: Whether to include edge cases in the tests
            include_doctest_examples: Whether to extract examples from docstrings
            store_memory: Whether to store generated tests in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing generated tests
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
            
            # Extract functions and classes
            functions, classes = self._extract_functions_and_classes(tree)
            
            if not functions and not classes:
                return {
                    "status": "error",
                    "error": "No functions or classes found in the code file"
                }
            
            # Generate tests
            if test_framework.lower() == "pytest":
                tests = self._generate_pytest_tests(
                    code_path,
                    functions,
                    classes,
                    include_edge_cases,
                    include_doctest_examples
                )
            elif test_framework.lower() == "unittest":
                tests = self._generate_unittest_tests(
                    code_path,
                    functions,
                    classes,
                    include_edge_cases,
                    include_doctest_examples
                )
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported test framework: {test_framework}"
                }
            
            # Write tests to file if output path is provided
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(tests)
            
            # Prepare result
            result = {
                "status": "success",
                "code_path": code_path,
                "output_path": output_path,
                "test_framework": test_framework,
                "functions_tested": len(functions),
                "classes_tested": len(classes),
                "tests": tests
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager:
                memory_content = {
                    "type": "unit_tests",
                    "code_path": code_path,
                    "test_framework": test_framework,
                    "functions_tested": [f["name"] for f in functions],
                    "classes_tested": [c["name"] for c in classes],
                    "tests": tests
                }
                
                tags = memory_tags or ["test", "unit_test", test_framework]
                
                # Add module name to tags
                module_name = os.path.basename(code_path).replace(".py", "")
                if module_name not in tags:
                    tags.append(module_name)
                
                await self.memory_manager.store(
                    input_text=f"Generate unit tests for {os.path.basename(code_path)}",
                    output_text=f"Generated {result['functions_tested']} function tests and {result['classes_tested']} class tests using {test_framework}.",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating unit tests: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _extract_functions_and_classes(self, tree: ast.AST) -> tuple:
        """
        Extract functions and classes from AST.
        
        Args:
            tree: AST of the code
            
        Returns:
            Tuple of (functions, classes)
        """
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            # Extract functions
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Skip if it's a method in a class
                if isinstance(node.parent, ast.ClassDef) if hasattr(node, "parent") else False:
                    continue
                
                function_info = {
                    "name": node.name,
                    "args": self._extract_args(node),
                    "returns": self._extract_returns(node),
                    "docstring": ast.get_docstring(node),
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "lineno": node.lineno
                }
                functions.append(function_info)
            
            # Extract classes
            elif isinstance(node, ast.ClassDef):
                methods = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        method_info = {
                            "name": item.name,
                            "args": self._extract_args(item),
                            "returns": self._extract_returns(item),
                            "docstring": ast.get_docstring(item),
                            "is_async": isinstance(item, ast.AsyncFunctionDef),
                            "lineno": item.lineno
                        }
                        methods.append(method_info)
                
                class_info = {
                    "name": node.name,
                    "bases": [self._get_name(base) for base in node.bases],
                    "docstring": ast.get_docstring(node),
                    "methods": methods,
                    "lineno": node.lineno
                }
                classes.append(class_info)
        
        return functions, classes
    
    def _extract_args(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> List[Dict[str, Any]]:
        """
        Extract arguments from function definition.
        
        Args:
            node: Function definition node
            
        Returns:
            List of argument information
        """
        args = []
        
        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation) if arg.annotation else None
            }
            args.append(arg_info)
        
        # Add *args if present
        if node.args.vararg:
            args.append({
                "name": f"*{node.args.vararg.arg}",
                "annotation": self._get_annotation(node.args.vararg.annotation) if node.args.vararg.annotation else None
            })
        
        # Add **kwargs if present
        if node.args.kwarg:
            args.append({
                "name": f"**{node.args.kwarg.arg}",
                "annotation": self._get_annotation(node.args.kwarg.annotation) if node.args.kwarg.annotation else None
            })
        
        return args
    
    def _extract_returns(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Optional[str]:
        """
        Extract return annotation from function definition.
        
        Args:
            node: Function definition node
            
        Returns:
            Return annotation or None
        """
        if node.returns:
            return self._get_annotation(node.returns)
        return None
    
    def _get_annotation(self, node: ast.AST) -> str:
        """
        Get string representation of annotation.
        
        Args:
            node: Annotation node
            
        Returns:
            String representation of annotation
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Index):
            return self._get_annotation(node.value)
        elif isinstance(node, ast.Tuple):
            return ", ".join(self._get_annotation(elt) for elt in node.elts)
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Str):
            return node.s
        else:
            return "Any"
    
    def _get_name(self, node: ast.AST) -> str:
        """
        Get string representation of name.
        
        Args:
            node: Name node
            
        Returns:
            String representation of name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return "object"
    
    def _generate_pytest_tests(
        self,
        code_path: str,
        functions: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        include_edge_cases: bool,
        include_doctest_examples: bool
    ) -> str:
        """
        Generate pytest tests for functions and classes.
        
        Args:
            code_path: Path to the code file
            functions: List of function information
            classes: List of class information
            include_edge_cases: Whether to include edge cases
            include_doctest_examples: Whether to extract examples from docstrings
            
        Returns:
            Generated tests as string
        """
        module_name = os.path.basename(code_path).replace(".py", "")
        
        # Generate imports
        imports = [
            "import pytest",
            f"import {module_name}",
            "from unittest.mock import patch, MagicMock",
            ""
        ]
        
        # Generate function tests
        function_tests = []
        for func in functions:
            function_tests.extend(self._generate_pytest_function_test(module_name, func, include_edge_cases, include_doctest_examples))
        
        # Generate class tests
        class_tests = []
        for cls in classes:
            class_tests.extend(self._generate_pytest_class_test(module_name, cls, include_edge_cases, include_doctest_examples))
        
        # Combine all tests
        all_tests = imports + function_tests + class_tests
        
        return "\n".join(all_tests)
    
    def _generate_pytest_function_test(
        self,
        module_name: str,
        func: Dict[str, Any],
        include_edge_cases: bool,
        include_doctest_examples: bool
    ) -> List[str]:
        """
        Generate pytest tests for a function.
        
        Args:
            module_name: Name of the module
            func: Function information
            include_edge_cases: Whether to include edge cases
            include_doctest_examples: Whether to extract examples from docstrings
            
        Returns:
            List of test lines
        """
        func_name = func["name"]
        is_async = func["is_async"]
        
        # Skip test functions
        if func_name.startswith("test_"):
            return []
        
        test_lines = [
            f"# Tests for {func_name}",
            f"def test_{func_name}_basic():",
            f"    # Test basic functionality of {func_name}",
        ]
        
        # Generate test for basic functionality
        if is_async:
            test_lines.append(f"    import asyncio")
            test_lines.append(f"    result = asyncio.run({module_name}.{func_name}())")
        else:
            test_lines.append(f"    result = {module_name}.{func_name}()")
        
        test_lines.append(f"    assert result is not None  # Replace with actual assertion")
        test_lines.append("")
        
        # Generate test for edge cases if requested
        if include_edge_cases:
            test_lines.extend([
                f"def test_{func_name}_edge_cases():",
                f"    # Test edge cases for {func_name}",
                f"    # Example: empty input, None input, large input, etc.",
                f"    pass  # Replace with actual test",
                ""
            ])
        
        # Extract examples from docstring if requested
        if include_doctest_examples and func["docstring"]:
            examples = self._extract_doctest_examples(func["docstring"])
            if examples:
                test_lines.extend([
                    f"def test_{func_name}_doctest_examples():",
                    f"    # Test examples from docstring",
                ])
                
                for i, example in enumerate(examples):
                    test_lines.extend([
                        f"    # Example {i+1}:",
                        f"    {example['input']}",
                        f"    assert {example['output']}",
                        ""
                    ])
                
                test_lines.append("")
        
        return test_lines
    
    def _generate_pytest_class_test(
        self,
        module_name: str,
        cls: Dict[str, Any],
        include_edge_cases: bool,
        include_doctest_examples: bool
    ) -> List[str]:
        """
        Generate pytest tests for a class.
        
        Args:
            module_name: Name of the module
            cls: Class information
            include_edge_cases: Whether to include edge cases
            include_doctest_examples: Whether to extract examples from docstrings
            
        Returns:
            List of test lines
        """
        cls_name = cls["name"]
        
        # Skip test classes
        if cls_name.startswith("Test"):
            return []
        
        test_lines = [
            f"# Tests for {cls_name}",
            f"class Test{cls_name}:",
            f"    # Fixture for creating an instance of {cls_name}",
            f"    @pytest.fixture",
            f"    def {cls_name.lower()}_instance(self):",
            f"        return {module_name}.{cls_name}()",
            ""
        ]
        
        # Generate tests for methods
        for method in cls["methods"]:
            # Skip private methods and special methods
            if method["name"].startswith("_"):
                continue
            
            method_name = method["name"]
            is_async = method["is_async"]
            
            test_lines.extend([
                f"    def test_{method_name}_basic(self, {cls_name.lower()}_instance):",
                f"        # Test basic functionality of {method_name}",
            ])
            
            # Generate test for basic functionality
            if is_async:
                test_lines.append(f"        import asyncio")
                test_lines.append(f"        result = asyncio.run({cls_name.lower()}_instance.{method_name}())")
            else:
                test_lines.append(f"        result = {cls_name.lower()}_instance.{method_name}()")
            
            test_lines.append(f"        assert result is not None  # Replace with actual assertion")
            test_lines.append("")
            
            # Generate test for edge cases if requested
            if include_edge_cases:
                test_lines.extend([
                    f"    def test_{method_name}_edge_cases(self, {cls_name.lower()}_instance):",
                    f"        # Test edge cases for {method_name}",
                    f"        # Example: empty input, None input, large input, etc.",
                    f"        pass  # Replace with actual test",
                    ""
                ])
        
        return test_lines
    
    def _generate_unittest_tests(
        self,
        code_path: str,
        functions: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        include_edge_cases: bool,
        include_doctest_examples: bool
    ) -> str:
        """
        Generate unittest tests for functions and classes.
        
        Args:
            code_path: Path to the code file
            functions: List of function information
            classes: List of class information
            include_edge_cases: Whether to include edge cases
            include_doctest_examples: Whether to extract examples from docstrings
            
        Returns:
            Generated tests as string
        """
        module_name = os.path.basename(code_path).replace(".py", "")
        
        # Generate imports
        imports = [
            "import unittest",
            "import asyncio",
            f"import {module_name}",
            "from unittest.mock import patch, MagicMock",
            ""
        ]
        
        # Generate function tests
        function_tests = []
        if functions:
            function_tests.extend([
                f"class Test{module_name.capitalize()}Functions(unittest.TestCase):",
                ""
            ])
            
            for func in functions:
                function_tests.extend(self._generate_unittest_function_test(module_name, func, include_edge_cases, include_doctest_examples))
        
        # Generate class tests
        class_tests = []
        for cls in classes:
            class_tests.extend(self._generate_unittest_class_test(module_name, cls, include_edge_cases, include_doctest_examples))
        
        # Add main block
        main_block = [
            "",
            "if __name__ == '__main__':",
            "    unittest.main()",
            ""
        ]
        
        # Combine all tests
        all_tests = imports + function_tests + class_tests + main_block
        
        return "\n".join(all_tests)
    
    def _generate_unittest_function_test(
        self,
        module_name: str,
        func: Dict[str, Any],
        include_edge_cases: bool,
        include_doctest_examples: bool
    ) -> List[str]:
        """
        Generate unittest tests for a function.
        
        Args:
            module_name: Name of the module
            func: Function information
            include_edge_cases: Whether to include edge cases
            include_doctest_examples: Whether to extract examples from docstrings
            
        Returns:
            List of test lines
        """
        func_name = func["name"]
        is_async = func["is_async"]
        
        # Skip test functions
        if func_name.startswith("test_"):
            return []
        
        test_lines = [
            f"    def test_{func_name}_basic(self):",
            f"        # Test basic functionality of {func_name}",
        ]
        
        # Generate test for basic functionality
        if is_async:
            test_lines.append(f"        result = asyncio.run({module_name}.{func_name}())")
        else:
            test_lines.append(f"        result = {module_name}.{func_name}()")
        
        test_lines.append(f"        self.assertIsNotNone(result)  # Replace with actual assertion")
        test_lines.append("")
        
        # Generate test for edge cases if requested
        if include_edge_cases:
            test_lines.extend([
                f"    def test_{func_name}_edge_cases(self):",
                f"        # Test edge cases for {func_name}",
                f"        # Example: empty input, None input, large input, etc.",
                f"        pass  # Replace with actual test",
                ""
            ])
        
        # Extract examples from docstring if requested
        if include_doctest_examples and func["docstring"]:
            examples = self._extract_doctest_examples(func["docstring"])
            if examples:
                test_lines.extend([
                    f"    def test_{func_name}_doctest_examples(self):",
                    f"        # Test examples from docstring",
                ])
                
                for i, example in enumerate(examples):
                    test_lines.extend([
                        f"        # Example {i+1}:",
                        f"        {example['input']}",
                        f"        self.assertTrue({example['output']})",
                        ""
                    ])
                
                test_lines.append("")
        
        return test_lines
    
    def _generate_unittest_class_test(
        self,
        module_name: str,
        cls: Dict[str, Any],
        include_edge_cases: bool,
        include_doctest_examples: bool
    ) -> List[str]:
        """
        Generate unittest tests for a class.
        
        Args:
            module_name: Name of the module
            cls: Class information
            include_edge_cases: Whether to include edge cases
            include_doctest_examples: Whether to extract examples from docstrings
            
        Returns:
            List of test lines
        """
        cls_name = cls["name"]
        
        # Skip test classes
        if cls_name.startswith("Test"):
            return []
        
        test_lines = [
            f"class Test{cls_name}(unittest.TestCase):",
            f"    def setUp(self):",
            f"        # Create an instance of {cls_name} for testing",
            f"        self.{cls_name.lower()} = {module_name}.{cls_name}()",
            ""
        ]
        
        # Generate tests for methods
        for method in cls["methods"]:
            # Skip private methods and special methods
            if method["name"].startswith("_"):
                continue
            
            method_name = method["name"]
            is_async = method["is_async"]
            
            test_lines.extend([
                f"    def test_{method_name}_basic(self):",
                f"        # Test basic functionality of {method_name}",
            ])
            
            # Generate test for basic functionality
            if is_async:
                test_lines.append(f"        result = asyncio.run(self.{cls_name.lower()}.{method_name}())")
            else:
                test_lines.append(f"        result = self.{cls_name.lower()}.{method_name}()")
            
            test_lines.append(f"        self.assertIsNotNone(result)  # Replace with actual assertion")
            test_lines.append("")
            
            # Generate test for edge cases if requested
            if include_edge_cases:
                test_lines.extend([
                    f"    def test_{method_name}_edge_cases(self):",
                    f"        # Test edge cases for {method_name}",
                    f"        # Example: empty input, None input, large input, etc.",
                    f"        pass  # Replace with actual test",
                    ""
                ])
        
        return test_lines
    
    def _extract_doctest_examples(self, docstring: str) -> List[Dict[str, str]]:
        """
        Extract examples from docstring.
        
        Args:
            docstring: Function or method docstring
            
        Returns:
            List of examples
        """
        examples = []
        lines = docstring.splitlines()
        
        in_example = False
        current_input = []
        current_output = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith(">>> "):
                # Start of a new example
                if in_example and current_input and current_output:
                    examples.append({
                        "input": "\n".join(current_input),
                        "output": "\n".join(current_output)
                    })
                
                in_example = True
                current_input = [line.replace(">>> ", "")]
                current_output = []
            elif in_example and line.startswith("... "):
                # Continuation of input
                current_input.append(line.replace("... ", ""))
            elif in_example and current_input:
                # Output
                current_output.append(line)
        
        # Add the last example
        if in_example and current_input and current_output:
            examples.append({
                "input": "\n".join(current_input),
                "output": "\n".join(current_output)
            })
        
        return examples
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_unit_test_writer(memory_manager=None):
    """
    Get a UnitTestWriter instance.
    
    Args:
        memory_manager: Optional memory manager for storing generated tests
        
    Returns:
        UnitTestWriter instance
    """
    return UnitTestWriter(memory_manager=memory_manager)
