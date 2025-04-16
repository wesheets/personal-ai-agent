"""
Architecture Validator Tool for Autonomous Coding Agents.

This module provides functionality to review code for DRY violations, modularity,
and naming conventions to ensure high-quality architecture.
"""

import os
import sys
import ast
import re
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from collections import defaultdict, Counter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArchitectureValidator:
    """
    Tool for reviewing code for DRY violations, modularity, and naming conventions.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the ArchitectureValidator.
        
        Args:
            memory_manager: Optional memory manager for storing validation results
        """
        self.memory_manager = memory_manager
    
    async def run(
        self,
        target_path: str,
        rules: Optional[List[str]] = None,
        ignore_dirs: Optional[List[str]] = None,
        ignore_files: Optional[List[str]] = None,
        output_path: Optional[str] = None,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate code architecture.
        
        Args:
            target_path: Path to the file or directory to validate
            rules: Optional list of rules to check (default: all)
                Available rules: 'dry', 'modularity', 'naming', 'complexity', 'imports', 'documentation'
            ignore_dirs: Optional list of directories to ignore
            ignore_files: Optional list of files to ignore
            output_path: Optional path to write the validation report to
            store_memory: Whether to store validation results in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Validate inputs
            if not os.path.exists(target_path):
                return {
                    "status": "error",
                    "error": f"Target path does not exist: {target_path}"
                }
            
            # Set default rules if not provided
            if not rules:
                rules = ['dry', 'modularity', 'naming', 'complexity', 'imports', 'documentation']
            
            # Set default ignore dirs if not provided
            if not ignore_dirs:
                ignore_dirs = ['venv', '.venv', 'env', '.env', '__pycache__', '.git', 'node_modules', 'dist', 'build']
            
            # Set default ignore files if not provided
            if not ignore_files:
                ignore_files = ['__init__.py', 'setup.py', 'conftest.py']
            
            # Collect Python files
            python_files = []
            
            if os.path.isfile(target_path) and target_path.endswith('.py'):
                python_files.append(target_path)
            elif os.path.isdir(target_path):
                for root, dirs, files in os.walk(target_path):
                    # Skip ignored directories
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    
                    for file in files:
                        if file.endswith('.py') and file not in ignore_files:
                            file_path = os.path.join(root, file)
                            python_files.append(file_path)
            else:
                return {
                    "status": "error",
                    "error": f"Target path is not a Python file or directory: {target_path}"
                }
            
            if not python_files:
                return {
                    "status": "error",
                    "error": f"No Python files found in target path: {target_path}"
                }
            
            # Analyze files
            issues = []
            file_stats = {}
            
            for file_path in python_files:
                file_issues, stats = self._analyze_file(file_path, rules)
                issues.extend(file_issues)
                file_stats[file_path] = stats
            
            # Check for cross-file issues
            if len(python_files) > 1 and 'dry' in rules:
                cross_file_issues = self._check_cross_file_duplication(file_stats)
                issues.extend(cross_file_issues)
            
            # Generate report
            report = self._generate_report(issues, file_stats, rules, target_path)
            
            # Write report to file if output path is provided
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
            
            # Prepare result
            result = {
                "status": "success",
                "target_path": target_path,
                "rules_checked": rules,
                "files_analyzed": len(python_files),
                "issue_count": len(issues),
                "issues": issues,
                "file_stats": file_stats,
                "report": report
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager:
                memory_content = {
                    "type": "architecture_validation",
                    "target_path": target_path,
                    "rules_checked": rules,
                    "files_analyzed": len(python_files),
                    "issue_count": len(issues),
                    "issues": issues
                }
                
                tags = memory_tags or ["architecture", "validation"]
                
                # Add rules to tags
                for rule in rules:
                    if rule not in tags:
                        tags.append(rule)
                
                # Add issue types to tags
                issue_types = set(issue["type"] for issue in issues)
                for issue_type in issue_types:
                    if issue_type not in tags:
                        tags.append(issue_type)
                
                await self.memory_manager.store(
                    input_text=f"Validate architecture for {os.path.basename(target_path)}",
                    output_text=f"Found {len(issues)} architecture issues across {len(python_files)} files.",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating architecture: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _analyze_file(self, file_path: str, rules: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file
            rules: List of rules to check
            
        Returns:
            Tuple of (issues, file_stats)
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse the code
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                issues.append({
                    "file": file_path,
                    "type": "syntax_error",
                    "line": e.lineno,
                    "message": f"Syntax error: {str(e)}",
                    "severity": "high"
                })
                return issues, {}
            
            # Collect file statistics
            stats = self._collect_file_stats(tree, code, file_path)
            
            # Check rules
            if 'dry' in rules:
                issues.extend(self._check_dry_violations(tree, code, file_path, stats))
            
            if 'modularity' in rules:
                issues.extend(self._check_modularity(tree, code, file_path, stats))
            
            if 'naming' in rules:
                issues.extend(self._check_naming_conventions(tree, code, file_path, stats))
            
            if 'complexity' in rules:
                issues.extend(self._check_complexity(tree, code, file_path, stats))
            
            if 'imports' in rules:
                issues.extend(self._check_imports(tree, code, file_path, stats))
            
            if 'documentation' in rules:
                issues.extend(self._check_documentation(tree, code, file_path, stats))
            
            return issues, stats
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            issues.append({
                "file": file_path,
                "type": "analysis_error",
                "line": 0,
                "message": f"Error analyzing file: {str(e)}",
                "severity": "high"
            })
            return issues, {}
    
    def _collect_file_stats(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """
        Collect statistics about a Python file.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            
        Returns:
            Dictionary containing file statistics
        """
        stats = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "loc": len(code.splitlines()),
            "functions": [],
            "classes": [],
            "imports": [],
            "code_blocks": [],
            "has_docstring": bool(ast.get_docstring(tree)),
            "complexity": {
                "max_function_complexity": 0,
                "avg_function_complexity": 0,
                "max_class_complexity": 0,
                "avg_class_complexity": 0
            }
        }
        
        # Collect functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip if it's a method in a class
                if isinstance(node.parent, ast.ClassDef) if hasattr(node, "parent") else False:
                    continue
                
                function_code = self._get_node_source(node, code)
                complexity = self._calculate_cyclomatic_complexity(node)
                
                function_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "args": [arg.arg for arg in node.args.args],
                    "loc": len(function_code.splitlines()),
                    "complexity": complexity,
                    "has_docstring": bool(ast.get_docstring(node)),
                    "code": function_code
                }
                
                stats["functions"].append(function_info)
                stats["code_blocks"].append({
                    "type": "function",
                    "name": node.name,
                    "code": function_code,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno)
                })
                
                if complexity > stats["complexity"]["max_function_complexity"]:
                    stats["complexity"]["max_function_complexity"] = complexity
        
        # Calculate average function complexity
        if stats["functions"]:
            stats["complexity"]["avg_function_complexity"] = sum(f["complexity"] for f in stats["functions"]) / len(stats["functions"])
        
        # Collect classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_code = self._get_node_source(node, code)
                methods = []
                class_complexity = 0
                
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_code = self._get_node_source(item, code)
                        method_complexity = self._calculate_cyclomatic_complexity(item)
                        class_complexity += method_complexity
                        
                        method_info = {
                            "name": item.name,
                            "line": item.lineno,
                            "end_line": getattr(item, "end_lineno", item.lineno),
                            "args": [arg.arg for arg in item.args.args],
                            "loc": len(method_code.splitlines()),
                            "complexity": method_complexity,
                            "has_docstring": bool(ast.get_docstring(item)),
                            "code": method_code
                        }
                        
                        methods.append(method_info)
                        stats["code_blocks"].append({
                            "type": "method",
                            "class_name": node.name,
                            "name": item.name,
                            "code": method_code,
                            "line": item.lineno,
                            "end_line": getattr(item, "end_lineno", item.lineno)
                        })
                
                class_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "loc": len(class_code.splitlines()),
                    "methods": methods,
                    "complexity": class_complexity,
                    "has_docstring": bool(ast.get_docstring(node)),
                    "code": class_code
                }
                
                stats["classes"].append(class_info)
                stats["code_blocks"].append({
                    "type": "class",
                    "name": node.name,
                    "code": class_code,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno)
                })
                
                if class_complexity > stats["complexity"]["max_class_complexity"]:
                    stats["complexity"]["max_class_complexity"] = class_complexity
        
        # Calculate average class complexity
        if stats["classes"]:
            stats["complexity"]["avg_class_complexity"] = sum(c["complexity"] for c in stats["classes"]) / len(stats["classes"])
        
        # Collect imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    stats["imports"].append({
                        "type": "import",
                        "name": name.name,
                        "asname": name.asname,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    stats["imports"].append({
                        "type": "importfrom",
                        "module": module,
                        "name": name.name,
                        "asname": name.asname,
                        "line": node.lineno
                    })
        
        return stats
    
    def _check_dry_violations(self, tree: ast.AST, code: str, file_path: str, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for DRY (Don't Repeat Yourself) violations.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            stats: File statistics
            
        Returns:
            List of DRY violation issues
        """
        issues = []
        
        # Check for duplicate code blocks within functions and methods
        code_blocks = {}
        
        for block in stats["code_blocks"]:
            if block["type"] in ("function", "method"):
                # Normalize code by removing comments, docstrings, and whitespace
                normalized_code = self._normalize_code(block["code"])
                
                # Skip small code blocks (less than 5 lines)
                if len(normalized_code.splitlines()) < 5:
                    continue
                
                if normalized_code in code_blocks:
                    issues.append({
                        "file": file_path,
                        "type": "dry_violation",
                        "line": block["line"],
                        "message": f"Duplicate code block found: {block['name']} (line {block['line']}) is similar to {code_blocks[normalized_code]['name']} (line {code_blocks[normalized_code]['line']})",
                        "severity": "medium",
                        "suggestion": "Extract the duplicate code into a shared function or method"
                    })
                else:
                    code_blocks[normalized_code] = block
        
        # Check for repeated expressions
        expressions = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and hasattr(node, 'value'):
                expr_code = self._get_node_source(node, code)
                
                # Skip simple expressions
                if len(expr_code) < 20:
                    continue
                
                expressions[expr_code].append(node.lineno)
        
        for expr, lines in expressions.items():
            if len(lines) > 1:
                issues.append({
                    "file": file_path,
                    "type": "dry_violation",
                    "line": lines[0],
                    "message": f"Repeated expression found at lines {', '.join(map(str, lines))}",
                    "severity": "low",
                    "suggestion": "Extract the repeated expression into a variable or function"
                })
        
        return issues
    
    def _check_modularity(self, tree: ast.AST, code: str, file_path: str, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for modularity issues.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            stats: File statistics
            
        Returns:
            List of modularity issues
        """
        issues = []
        
        # Check file size
        if stats["loc"] > 500:
            issues.append({
                "file": file_path,
                "type": "modularity",
                "line": 1,
                "message": f"File is too large ({stats['loc']} lines). Consider splitting it into multiple modules.",
                "severity": "medium",
                "suggestion": "Split the file into multiple modules based on functionality"
            })
        
        # Check function size
        for func in stats["functions"]:
            if func["loc"] > 50:
                issues.append({
                    "file": file_path,
                    "type": "modularity",
                    "line": func["line"],
                    "message": f"Function '{func['name']}' is too large ({func['loc']} lines). Consider breaking it down.",
                    "severity": "medium",
                    "suggestion": "Break down the function into smaller, more focused functions"
                })
        
        # Check class size
        for cls in stats["classes"]:
            if cls["loc"] > 300:
                issues.append({
                    "file": file_path,
                    "type": "modularity",
                    "line": cls["line"],
                    "message": f"Class '{cls['name']}' is too large ({cls['loc']} lines). Consider splitting it.",
                    "severity": "medium",
                    "suggestion": "Split the class into multiple classes with more focused responsibilities"
                })
            
            # Check method size
            for method in cls["methods"]:
                if method["loc"] > 50:
                    issues.append({
                        "file": file_path,
                        "type": "modularity",
                        "line": method["line"],
                        "message": f"Method '{cls['name']}.{method['name']}' is too large ({method['loc']} lines). Consider breaking it down.",
                        "severity": "medium",
                        "suggestion": "Break down the method into smaller, more focused methods"
                    })
        
        # Check for too many imports
        if len(stats["imports"]) > 20:
            issues.append({
                "file": file_path,
                "type": "modularity",
                "line": 1,
                "message": f"Too many imports ({len(stats['imports'])}). This may indicate poor modularity.",
                "severity": "low",
                "suggestion": "Consider reorganizing the code to reduce dependencies"
            })
        
        # Check for too many classes
        if len(stats["classes"]) > 10:
            issues.append({
                "file": file_path,
                "type": "modularity",
                "line": 1,
                "message": f"Too many classes ({len(stats['classes'])}) in one file. Consider splitting into multiple files.",
                "severity": "medium",
                "suggestion": "Split classes into separate files based on functionality"
            })
        
        # Check for too many functions
        if len(stats["functions"]) > 20:
            issues.append({
                "file": file_path,
                "type": "modularity",
                "line": 1,
                "message": f"Too many functions ({len(stats['functions'])}) in one file. Consider splitting into multiple files.",
                "severity": "medium",
                "suggestion": "Split functions into separate files based on functionality"
            })
        
        return issues
    
    def _check_naming_conventions(self, tree: ast.AST, code: str, file_path: str, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for naming convention issues.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            stats: File statistics
            
        Returns:
            List of naming convention issues
        """
        issues = []
        
        # Check module name (file name)
        module_name = os.path.basename(file_path).replace('.py', '')
        if not re.match(r'^[a-z][a-z0-9_]*$', module_name):
            issues.append({
                "file": file_path,
                "type": "naming",
                "line": 1,
                "message": f"Module name '{module_name}' does not follow snake_case convention",
                "severity": "low",
                "suggestion": f"Rename the file to follow snake_case (e.g., '{self._to_snake_case(module_name)}.py')"
            })
        
        # Check class names
        for cls in stats["classes"]:
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls["name"]):
                issues.append({
                    "file": file_path,
                    "type": "naming",
                    "line": cls["line"],
                    "message": f"Class name '{cls['name']}' does not follow PascalCase convention",
                    "severity": "low",
                    "suggestion": f"Rename the class to follow PascalCase (e.g., '{self._to_pascal_case(cls['name'])}')"
                })
        
        # Check function and method names
        for func in stats["functions"]:
            if not re.match(r'^[a-z][a-z0-9_]*$', func["name"]) and not func["name"].startswith('_'):
                issues.append({
                    "file": file_path,
                    "type": "naming",
                    "line": func["line"],
                    "message": f"Function name '{func['name']}' does not follow snake_case convention",
                    "severity": "low",
                    "suggestion": f"Rename the function to follow snake_case (e.g., '{self._to_snake_case(func['name'])}')"
                })
        
        for cls in stats["classes"]:
            for method in cls["methods"]:
                if not re.match(r'^[a-z][a-z0-9_]*$', method["name"]) and not method["name"].startswith('_'):
                    issues.append({
                        "file": file_path,
                        "type": "naming",
                        "line": method["line"],
                        "message": f"Method name '{method['name']}' in class '{cls['name']}' does not follow snake_case convention",
                        "severity": "low",
                        "suggestion": f"Rename the method to follow snake_case (e.g., '{self._to_snake_case(method['name'])}')"
                    })
        
        # Check variable names
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # Skip constants (all uppercase)
                        if re.match(r'^[A-Z][A-Z0-9_]*$', var_name):
                            continue
                        
                        if not re.match(r'^[a-z][a-z0-9_]*$', var_name) and not var_name.startswith('_'):
                            issues.append({
                                "file": file_path,
                                "type": "naming",
                                "line": node.lineno,
                                "message": f"Variable name '{var_name}' does not follow snake_case convention",
                                "severity": "low",
                                "suggestion": f"Rename the variable to follow snake_case (e.g., '{self._to_snake_case(var_name)}')"
                            })
        
        return issues
    
    def _check_complexity(self, tree: ast.AST, code: str, file_path: str, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for complexity issues.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            stats: File statistics
            
        Returns:
            List of complexity issues
        """
        issues = []
        
        # Check function complexity
        for func in stats["functions"]:
            if func["complexity"] > 10:
                issues.append({
                    "file": file_path,
                    "type": "complexity",
                    "line": func["line"],
                    "message": f"Function '{func['name']}' has high cyclomatic complexity ({func['complexity']})",
                    "severity": "high" if func["complexity"] > 15 else "medium",
                    "suggestion": "Refactor the function to reduce complexity by extracting logic into smaller functions"
                })
        
        # Check class complexity
        for cls in stats["classes"]:
            if cls["complexity"] > 30:
                issues.append({
                    "file": file_path,
                    "type": "complexity",
                    "line": cls["line"],
                    "message": f"Class '{cls['name']}' has high total complexity ({cls['complexity']})",
                    "severity": "high" if cls["complexity"] > 50 else "medium",
                    "suggestion": "Refactor the class to reduce complexity by splitting it into multiple classes"
                })
            
            # Check method complexity
            for method in cls["methods"]:
                if method["complexity"] > 10:
                    issues.append({
                        "file": file_path,
                        "type": "complexity",
                        "line": method["line"],
                        "message": f"Method '{cls['name']}.{method['name']}' has high cyclomatic complexity ({method['complexity']})",
                        "severity": "high" if method["complexity"] > 15 else "medium",
                        "suggestion": "Refactor the method to reduce complexity by extracting logic into smaller methods"
                    })
        
        # Check nesting depth
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                nesting_depth = self._calculate_nesting_depth(node)
                if nesting_depth > 3:
                    issues.append({
                        "file": file_path,
                        "type": "complexity",
                        "line": node.lineno,
                        "message": f"Deep nesting detected (depth: {nesting_depth})",
                        "severity": "high" if nesting_depth > 4 else "medium",
                        "suggestion": "Refactor the code to reduce nesting by extracting logic into separate functions"
                    })
        
        return issues
    
    def _check_imports(self, tree: ast.AST, code: str, file_path: str, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for import issues.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            stats: File statistics
            
        Returns:
            List of import issues
        """
        issues = []
        
        # Check for unused imports
        imported_names = set()
        used_names = set()
        
        # Collect imported names
        for imp in stats["imports"]:
            if imp["type"] == "import":
                name = imp["asname"] or imp["name"]
                imported_names.add(name.split('.')[0])  # Handle cases like 'import os.path'
            elif imp["type"] == "importfrom":
                name = imp["asname"] or imp["name"]
                imported_names.add(name)
        
        # Collect used names
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
        
        # Find unused imports
        for imp in stats["imports"]:
            if imp["type"] == "import":
                name = imp["asname"] or imp["name"]
                base_name = name.split('.')[0]
                
                if base_name not in used_names and base_name != "__future__":
                    issues.append({
                        "file": file_path,
                        "type": "unused_import",
                        "line": imp["line"],
                        "message": f"Unused import: '{imp['name']}'",
                        "severity": "low",
                        "suggestion": f"Remove the unused import"
                    })
            elif imp["type"] == "importfrom":
                name = imp["asname"] or imp["name"]
                
                if name not in used_names and name != "*" and imp["module"] != "__future__":
                    issues.append({
                        "file": file_path,
                        "type": "unused_import",
                        "line": imp["line"],
                        "message": f"Unused import: '{name}' from '{imp['module']}'",
                        "severity": "low",
                        "suggestion": f"Remove the unused import"
                    })
        
        # Check for wildcard imports
        for imp in stats["imports"]:
            if imp["type"] == "importfrom" and imp["name"] == "*":
                issues.append({
                    "file": file_path,
                    "type": "wildcard_import",
                    "line": imp["line"],
                    "message": f"Wildcard import: 'from {imp['module']} import *'",
                    "severity": "medium",
                    "suggestion": "Explicitly import only what you need instead of using wildcard imports"
                })
        
        # Check for duplicate imports
        import_counts = Counter((imp["type"], imp["name"], imp.get("module", "")) for imp in stats["imports"])
        
        for (imp_type, name, module), count in import_counts.items():
            if count > 1:
                if imp_type == "import":
                    issues.append({
                        "file": file_path,
                        "type": "duplicate_import",
                        "line": next(imp["line"] for imp in stats["imports"] if imp["type"] == imp_type and imp["name"] == name),
                        "message": f"Duplicate import: '{name}' imported {count} times",
                        "severity": "low",
                        "suggestion": "Remove duplicate imports"
                    })
                else:
                    issues.append({
                        "file": file_path,
                        "type": "duplicate_import",
                        "line": next(imp["line"] for imp in stats["imports"] if imp["type"] == imp_type and imp["name"] == name and imp.get("module", "") == module),
                        "message": f"Duplicate import: '{name}' from '{module}' imported {count} times",
                        "severity": "low",
                        "suggestion": "Remove duplicate imports"
                    })
        
        return issues
    
    def _check_documentation(self, tree: ast.AST, code: str, file_path: str, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for documentation issues.
        
        Args:
            tree: AST of the code
            code: Original code string
            file_path: Path to the file
            stats: File statistics
            
        Returns:
            List of documentation issues
        """
        issues = []
        
        # Check for missing module docstring
        if not stats["has_docstring"]:
            issues.append({
                "file": file_path,
                "type": "missing_docstring",
                "line": 1,
                "message": "Missing module docstring",
                "severity": "low",
                "suggestion": "Add a docstring at the beginning of the file to describe its purpose"
            })
        
        # Check for missing class docstrings
        for cls in stats["classes"]:
            if not cls["has_docstring"]:
                issues.append({
                    "file": file_path,
                    "type": "missing_docstring",
                    "line": cls["line"],
                    "message": f"Missing docstring for class '{cls['name']}'",
                    "severity": "low",
                    "suggestion": "Add a docstring to describe the class purpose and usage"
                })
        
        # Check for missing function docstrings
        for func in stats["functions"]:
            # Skip simple functions (less than 5 lines)
            if func["loc"] < 5:
                continue
            
            if not func["has_docstring"]:
                issues.append({
                    "file": file_path,
                    "type": "missing_docstring",
                    "line": func["line"],
                    "message": f"Missing docstring for function '{func['name']}'",
                    "severity": "low",
                    "suggestion": "Add a docstring to describe the function purpose, parameters, and return value"
                })
        
        # Check for missing method docstrings
        for cls in stats["classes"]:
            for method in cls["methods"]:
                # Skip simple methods (less than 5 lines) and special methods
                if method["loc"] < 5 or method["name"].startswith('__'):
                    continue
                
                if not method["has_docstring"]:
                    issues.append({
                        "file": file_path,
                        "type": "missing_docstring",
                        "line": method["line"],
                        "message": f"Missing docstring for method '{cls['name']}.{method['name']}'",
                        "severity": "low",
                        "suggestion": "Add a docstring to describe the method purpose, parameters, and return value"
                    })
        
        return issues
    
    def _check_cross_file_duplication(self, file_stats: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for code duplication across multiple files.
        
        Args:
            file_stats: Dictionary of file statistics
            
        Returns:
            List of cross-file duplication issues
        """
        issues = []
        
        # Collect all code blocks from all files
        all_blocks = []
        
        for file_path, stats in file_stats.items():
            for block in stats.get("code_blocks", []):
                if block["type"] in ("function", "method"):
                    # Normalize code by removing comments, docstrings, and whitespace
                    normalized_code = self._normalize_code(block["code"])
                    
                    # Skip small code blocks (less than 5 lines)
                    if len(normalized_code.splitlines()) < 5:
                        continue
                    
                    all_blocks.append({
                        "file": file_path,
                        "type": block["type"],
                        "name": block["name"],
                        "line": block["line"],
                        "code": normalized_code
                    })
        
        # Check for duplicates
        for i, block1 in enumerate(all_blocks):
            for j, block2 in enumerate(all_blocks[i+1:], i+1):
                if block1["code"] == block2["code"]:
                    # Only report cross-file duplications
                    if block1["file"] != block2["file"]:
                        issues.append({
                            "file": block1["file"],
                            "type": "cross_file_duplication",
                            "line": block1["line"],
                            "message": f"Duplicate code found across files: {block1['type']} '{block1['name']}' in {os.path.basename(block1['file'])} (line {block1['line']}) is similar to {block2['type']} '{block2['name']}' in {os.path.basename(block2['file'])} (line {block2['line']})",
                            "severity": "high",
                            "suggestion": "Extract the duplicate code into a shared module or utility function"
                        })
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a function or method.
        
        Args:
            node: AST node of the function or method
            
        Returns:
            Cyclomatic complexity
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Increment complexity for control flow statements
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, (ast.And, ast.Or)):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 1) -> int:
        """
        Calculate the nesting depth of a node.
        
        Args:
            node: AST node
            current_depth: Current nesting depth
            
        Returns:
            Maximum nesting depth
        """
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _normalize_code(self, code: str) -> str:
        """
        Normalize code by removing comments, docstrings, and normalizing whitespace.
        
        Args:
            code: Original code string
            
        Returns:
            Normalized code
        """
        # Parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If parsing fails, return the original code
            return code
        
        # Remove docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    node.body = node.body[1:]
        
        # Convert back to code
        normalized = ast.unparse(tree)
        
        # Remove comments and normalize whitespace
        lines = []
        for line in normalized.splitlines():
            # Remove comments
            line = line.split('#')[0].rstrip()
            
            # Skip empty lines
            if line.strip():
                lines.append(line)
        
        return '\n'.join(lines)
    
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
    
    def _to_snake_case(self, name: str) -> str:
        """
        Convert a name to snake_case.
        
        Args:
            name: Original name
            
        Returns:
            Name in snake_case
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """
        Convert a name to PascalCase.
        
        Args:
            name: Original name
            
        Returns:
            Name in PascalCase
        """
        components = name.split('_')
        return ''.join(x.title() for x in components)
    
    def _generate_report(self, issues: List[Dict[str, Any]], file_stats: Dict[str, Dict[str, Any]], rules: List[str], target_path: str) -> str:
        """
        Generate a validation report.
        
        Args:
            issues: List of issues
            file_stats: Dictionary of file statistics
            rules: List of rules that were checked
            target_path: Path to the target file or directory
            
        Returns:
            Validation report as string
        """
        # Group issues by file and type
        issues_by_file = defaultdict(list)
        issues_by_type = defaultdict(list)
        
        for issue in issues:
            issues_by_file[issue["file"]].append(issue)
            issues_by_type[issue["type"]].append(issue)
        
        # Count issues by severity
        severity_counts = Counter(issue["severity"] for issue in issues)
        
        # Generate report
        report = [
            "# Architecture Validation Report",
            "",
            f"## Summary",
            "",
            f"Target: `{target_path}`",
            f"Rules checked: {', '.join(rules)}",
            f"Files analyzed: {len(file_stats)}",
            f"Total issues: {len(issues)}",
            f"- High severity: {severity_counts.get('high', 0)}",
            f"- Medium severity: {severity_counts.get('medium', 0)}",
            f"- Low severity: {severity_counts.get('low', 0)}",
            ""
        ]
        
        # Add issues by type
        report.append("## Issues by Type")
        report.append("")
        
        for issue_type, type_issues in sorted(issues_by_type.items()):
            report.append(f"### {issue_type.replace('_', ' ').title()} ({len(type_issues)})")
            report.append("")
            
            for issue in sorted(type_issues, key=lambda x: (x["file"], x["line"])):
                report.append(f"- [{os.path.basename(issue['file'])}:{issue['line']}] {issue['message']} ({issue['severity']})")
                if "suggestion" in issue:
                    report.append(f"  - Suggestion: {issue['suggestion']}")
            
            report.append("")
        
        # Add issues by file
        report.append("## Issues by File")
        report.append("")
        
        for file_path, file_issues in sorted(issues_by_file.items()):
            report.append(f"### {os.path.basename(file_path)} ({len(file_issues)})")
            report.append("")
            
            for issue in sorted(file_issues, key=lambda x: (x["line"], x["type"])):
                report.append(f"- Line {issue['line']}: {issue['message']} ({issue['severity']})")
                if "suggestion" in issue:
                    report.append(f"  - Suggestion: {issue['suggestion']}")
            
            report.append("")
        
        # Add file statistics
        report.append("## File Statistics")
        report.append("")
        
        for file_path, stats in sorted(file_stats.items()):
            report.append(f"### {os.path.basename(file_path)}")
            report.append("")
            report.append(f"- Lines of code: {stats.get('loc', 0)}")
            report.append(f"- Functions: {len(stats.get('functions', []))}")
            report.append(f"- Classes: {len(stats.get('classes', []))}")
            report.append(f"- Imports: {len(stats.get('imports', []))}")
            
            complexity = stats.get('complexity', {})
            report.append(f"- Max function complexity: {complexity.get('max_function_complexity', 0)}")
            report.append(f"- Avg function complexity: {complexity.get('avg_function_complexity', 0):.2f}")
            report.append(f"- Max class complexity: {complexity.get('max_class_complexity', 0)}")
            report.append(f"- Avg class complexity: {complexity.get('avg_class_complexity', 0):.2f}")
            
            report.append("")
        
        return "\n".join(report)
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_architecture_validator(memory_manager=None):
    """
    Get an ArchitectureValidator instance.
    
    Args:
        memory_manager: Optional memory manager for storing validation results
        
    Returns:
        ArchitectureValidator instance
    """
    return ArchitectureValidator(memory_manager=memory_manager)
