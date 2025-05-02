#!/usr/bin/env python3
"""
SchemaTraceTool v1 - Diagnostic Utility for Promethios

This tool scans the Promethios codebase to locate and report:
- Routes that depend on missing or undefined schema classes
- Improper or stale schema imports in route modules
- Breaks between `main.py` route loading and actual files
- Missing schema file paths that prevent application boot

Usage:
  python schema_trace.py [--output FILE] [--memory-tag] [--verbose]

Options:
  --output FILE     Write results to a specific JSON file (default: logs/schema_trace_report.json)
  --memory-tag      Store results in memory with tag schema_trace_report_<timestamp>
  --verbose         Show detailed information during scanning
"""

import os
import sys
import re
import json
import ast
import importlib
import inspect
import logging
import argparse
import datetime
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("schema_trace")

# Constants
ROUTES_DIR = os.path.join("app", "routes")
SCHEMAS_DIR = os.path.join("app", "schemas")
MAIN_PY_PATH = os.path.join("app", "main.py")
LOGS_DIR = "logs"
DEFAULT_OUTPUT_PATH = os.path.join(LOGS_DIR, "schema_trace_report.json")

class SchemaReference:
    """Class to store information about a schema reference."""
    def __init__(self, name: str, file_path: str, line_number: int, import_path: Optional[str] = None):
        self.name = name
        self.file_path = file_path
        self.line_number = line_number
        self.import_path = import_path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "import_path": self.import_path
        }

class SchemaDefinition:
    """Class to store information about a schema definition."""
    def __init__(self, name: str, file_path: str, class_def: ast.ClassDef):
        self.name = name
        self.file_path = file_path
        self.class_def = class_def
        self.parent_classes = []
        
        # Extract parent classes
        for base in class_def.bases:
            if isinstance(base, ast.Name):
                self.parent_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                self.parent_classes.append(f"{base.value.id}.{base.attr}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "parent_classes": self.parent_classes
        }

class RouteDefinition:
    """Class to store information about a route definition."""
    def __init__(self, path: str, method: str, file_path: str, line_number: int, 
                 response_model: Optional[str] = None, request_model: Optional[str] = None):
        self.path = path
        self.method = method
        self.file_path = file_path
        self.line_number = line_number
        self.response_model = response_model
        self.request_model = request_model
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "method": self.method,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "response_model": self.response_model,
            "request_model": self.request_model
        }

class MainPyRouteRegistration:
    """Class to store information about a route registration in main.py."""
    def __init__(self, router_var: str, import_path: str, line_number: int, prefix: Optional[str] = None):
        self.router_var = router_var
        self.import_path = import_path
        self.line_number = line_number
        self.prefix = prefix
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "router_var": self.router_var,
            "import_path": self.import_path,
            "line_number": self.line_number,
            "prefix": self.prefix
        }

class SchemaTracer:
    """Main class for tracing schema references and validating them."""
    
    def __init__(self, project_root: str, verbose: bool = False):
        """Initialize the schema tracer with project paths."""
        self.project_root = project_root
        self.verbose = verbose
        self.routes_dir = os.path.join(project_root, ROUTES_DIR)
        self.schemas_dir = os.path.join(project_root, SCHEMAS_DIR)
        self.main_py_path = os.path.join(project_root, MAIN_PY_PATH)
        
        # Initialize collections
        self.schema_references: List[SchemaReference] = []
        self.schema_definitions: Dict[str, SchemaDefinition] = {}
        self.route_definitions: List[RouteDefinition] = []
        self.main_py_registrations: List[MainPyRouteRegistration] = []
        
        # Results
        self.missing_schemas: List[Dict[str, Any]] = []
        self.routes_with_missing_imports: List[Dict[str, Any]] = []
        self.suggested_schema_locations: List[Dict[str, Any]] = []
        self.main_py_issues: List[Dict[str, Any]] = []
    
    def scan_all(self) -> None:
        """Run all scanning operations."""
        logger.info("Starting schema trace scan...")
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(self.project_root, LOGS_DIR), exist_ok=True)
        
        # Scan schema definitions first
        self._scan_schema_definitions()
        
        # Scan route files for schema references
        self._scan_route_files()
        
        # Scan main.py for route registrations
        self._scan_main_py()
        
        # Analyze results
        self._analyze_results()
        
        logger.info("Schema trace scan completed.")
    
    def _scan_schema_definitions(self) -> None:
        """Scan schema files to build a registry of available schema classes."""
        logger.info(f"Scanning schema definitions in {self.schemas_dir}...")
        
        for root, _, files in os.walk(self.schemas_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._parse_schema_file(file_path)
        
        if self.verbose:
            logger.info(f"Found {len(self.schema_definitions)} schema definitions")
    
    def _parse_schema_file(self, file_path: str) -> None:
        """Parse a schema file to extract class definitions."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
            
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's likely a schema class (inherits from BaseModel or another schema)
                    is_schema = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in ["BaseModel", "Schema"]:
                            is_schema = True
                            break
                        elif isinstance(base, ast.Attribute) and base.attr in ["BaseModel", "Schema"]:
                            is_schema = True
                            break
                    
                    if is_schema or "Schema" in node.name:
                        schema_def = SchemaDefinition(node.name, rel_path, node)
                        self.schema_definitions[node.name] = schema_def
                        if self.verbose:
                            logger.info(f"Found schema definition: {node.name} in {rel_path}")
        
        except Exception as e:
            logger.error(f"Error parsing schema file {rel_path}: {str(e)}")
    
    def _scan_route_files(self) -> None:
        """Scan route files for schema references and route definitions."""
        logger.info(f"Scanning route files in {self.routes_dir}...")
        
        for root, _, files in os.walk(self.routes_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._parse_route_file(file_path)
        
        if self.verbose:
            logger.info(f"Found {len(self.schema_references)} schema references")
            logger.info(f"Found {len(self.route_definitions)} route definitions")
    
    def _parse_route_file(self, file_path: str) -> None:
        """Parse a route file to extract schema references and route definitions."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
                file_lines = file_content.split('\n')
            
            # Use regex to find import statements for schemas
            import_matches = re.finditer(r'from\s+([\w.]+)\s+import\s+([^#\n]+)', file_content)
            for match in import_matches:
                import_path = match.group(1)
                imported_names = match.group(2).strip()
                
                # Skip if not importing from schemas
                if 'schema' not in import_path.lower():
                    continue
                
                # Extract line number
                line_number = file_content[:match.start()].count('\n') + 1
                
                # Process imported names
                for name_match in re.finditer(r'(\w+)(?:\s+as\s+(\w+))?', imported_names):
                    original_name = name_match.group(1)
                    alias = name_match.group(2)
                    
                    # Record both original name and alias if present
                    schema_name = original_name
                    self.schema_references.append(
                        SchemaReference(schema_name, rel_path, line_number, import_path)
                    )
                    
                    if alias:
                        self.schema_references.append(
                            SchemaReference(alias, rel_path, line_number, import_path)
                        )
            
            # Use AST to find route definitions and response_model references
            tree = ast.parse(file_content)
            
            # Find router variable name
            router_var = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                            if hasattr(node.value.func, 'id') and node.value.func.id == 'APIRouter':
                                router_var = target.id
                                break
            
            if not router_var:
                return
            
            # Find route decorators
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                            if decorator.func.value.id == router_var and decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                method = decorator.func.attr.upper()
                                
                                # Extract path
                                path = None
                                if decorator.args:
                                    path = ast.literal_eval(decorator.args[0])
                                
                                # Extract response_model
                                response_model = None
                                request_model = None
                                for keyword in decorator.keywords:
                                    if keyword.arg == 'response_model' and isinstance(keyword.value, ast.Name):
                                        response_model = keyword.value.id
                                        # Add to schema references
                                        self.schema_references.append(
                                            SchemaReference(response_model, rel_path, node.lineno, None)
                                        )
                                
                                # Check function parameters for request models
                                for arg in node.args.args:
                                    if hasattr(arg, 'annotation') and isinstance(arg.annotation, ast.Name):
                                        request_model = arg.annotation.id
                                        # Add to schema references
                                        self.schema_references.append(
                                            SchemaReference(request_model, rel_path, node.lineno, None)
                                        )
                                
                                # Add route definition
                                if path:
                                    self.route_definitions.append(
                                        RouteDefinition(path, method, rel_path, node.lineno, response_model, request_model)
                                    )
        
        except Exception as e:
            logger.error(f"Error parsing route file {rel_path}: {str(e)}")
    
    def _scan_main_py(self) -> None:
        """Scan main.py for route registrations."""
        logger.info(f"Scanning {self.main_py_path} for route registrations...")
        
        try:
            with open(self.main_py_path, 'r') as f:
                file_content = f.read()
                file_lines = file_content.split('\n')
            
            # Use regex to find import statements for routes
            import_matches = re.finditer(r'from\s+([\w.]+)\s+import\s+router\s+as\s+(\w+)', file_content)
            router_imports = {}
            for match in import_matches:
                import_path = match.group(1)
                router_var = match.group(2)
                router_imports[router_var] = import_path
            
            # Use regex to find try-except blocks for route imports
            try_import_matches = re.finditer(r'try:\s+from\s+([\w.]+)\s+import\s+router\s+as\s+(\w+)[^#\n]+(\w+)_routes_loaded\s+=\s+True', file_content)
            for match in try_import_matches:
                import_path = match.group(1)
                router_var = match.group(2)
                flag_var = match.group(3)
                router_imports[router_var] = import_path
            
            # Use AST to find include_router calls
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    call = node.value
                    if isinstance(call.func, ast.Attribute) and call.func.attr == 'include_router':
                        # Extract router variable
                        router_arg = call.args[0] if call.args else None
                        if router_arg and isinstance(router_arg, ast.Attribute):
                            router_var = f"{router_arg.value.id}.{router_arg.attr}"
                        elif router_arg and isinstance(router_arg, ast.Name):
                            router_var = router_arg.id
                        else:
                            continue
                        
                        # Extract prefix if present
                        prefix = None
                        for keyword in call.keywords:
                            if keyword.arg == 'prefix' and isinstance(keyword.value, ast.Constant):
                                prefix = keyword.value.value
                        
                        # Find import path for this router
                        import_path = None
                        for key, value in router_imports.items():
                            if key in router_var:
                                import_path = value
                                break
                        
                        # Add registration
                        self.main_py_registrations.append(
                            MainPyRouteRegistration(router_var, import_path, node.lineno, prefix)
                        )
            
            if self.verbose:
                logger.info(f"Found {len(self.main_py_registrations)} route registrations in main.py")
        
        except Exception as e:
            logger.error(f"Error parsing main.py: {str(e)}")
    
    def _analyze_results(self) -> None:
        """Analyze scan results to identify issues."""
        logger.info("Analyzing scan results...")
        
        # Find missing schemas
        referenced_schemas = set(ref.name for ref in self.schema_references)
        defined_schemas = set(self.schema_definitions.keys())
        missing_schema_names = referenced_schemas - defined_schemas
        
        for schema_name in missing_schema_names:
            references = [ref for ref in self.schema_references if ref.name == schema_name]
            for ref in references:
                self.missing_schemas.append({
                    "schema_name": schema_name,
                    "referenced_in": ref.file_path,
                    "line_number": ref.line_number,
                    "import_path": ref.import_path
                })
        
        # Find routes with missing imports
        route_files = set(os.path.relpath(os.path.join(root, f), self.project_root) 
                         for root, _, files in os.walk(self.routes_dir) 
                         for f in files if f.endswith('.py'))
        
        registered_routes = set()
        for reg in self.main_py_registrations:
            if reg.import_path:
                if reg.import_path.startswith('app.'):
                    # Convert import path to file path
                    file_path = reg.import_path.replace('.', '/') + '.py'
                    registered_routes.add(file_path)
                elif reg.import_path.startswith('routes.'):
                    # Handle routes outside app directory
                    file_path = reg.import_path.replace('.', '/') + '.py'
                    registered_routes.add(file_path)
        
        # Find routes not registered in main.py
        unregistered_routes = route_files - registered_routes
        for route in unregistered_routes:
            self.routes_with_missing_imports.append({
                "route_file": route,
                "issue": "Route file exists but is not imported in main.py",
                "suggestion": f"Add import and registration for {route} in main.py"
            })
        
        # Find registrations for non-existent routes
        nonexistent_routes = registered_routes - route_files
        for route in nonexistent_routes:
            reg = next((r for r in self.main_py_registrations if r.import_path and r.import_path.replace('.', '/') + '.py' == route), None)
            if reg:
                self.main_py_issues.append({
                    "issue_type": "missing_route_file",
                    "import_path": reg.import_path,
                    "router_var": reg.router_var,
                    "line_number": reg.line_number,
                    "suggestion": f"Create missing route file or remove registration from main.py"
                })
        
        # Generate suggested schema locations
        for schema in self.missing_schemas:
            schema_name = schema["schema_name"]
            
            # Suggest schema file based on naming convention
            suggested_file = None
            if "Request" in schema_name or "Result" in schema_name or "Response" in schema_name:
                base_name = schema_name.replace("Request", "").replace("Result", "").replace("Response", "").replace("Schema", "").lower()
                suggested_file = f"app/schemas/{base_name}_schema.py"
            else:
                suggested_file = f"app/schemas/{schema_name.lower()}.py"
            
            # Generate stub template
            stub_template = f"""from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class {schema_name}(BaseModel):
    \"\"\"
    Schema for {schema_name}.
    \"\"\"
    # TODO: Add fields
    
    class Config:
        schema_extra = {{
            "example": {{
                # TODO: Add example
            }}
        }}
"""
            
            self.suggested_schema_locations.append({
                "schema_name": schema_name,
                "suggested_file": suggested_file,
                "stub_template": stub_template
            })
        
        logger.info(f"Analysis complete. Found {len(self.missing_schemas)} missing schemas, "
                   f"{len(self.routes_with_missing_imports)} routes with missing imports, "
                   f"{len(self.main_py_issues)} issues in main.py")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a report of the scan results."""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "missing_schemas": self.missing_schemas,
            "routes_with_missing_imports": self.routes_with_missing_imports,
            "suggested_schema_locations": self.suggested_schema_locations,
            "main_py_issues": self.main_py_issues,
            "stats": {
                "total_schema_references": len(self.schema_references),
                "total_schema_definitions": len(self.schema_definitions),
                "total_route_definitions": len(self.route_definitions),
                "total_main_py_registrations": len(self.main_py_registrations),
                "total_missing_schemas": len(self.missing_schemas),
                "total_routes_with_missing_imports": len(self.routes_with_missing_imports),
                "total_main_py_issues": len(self.main_py_issues)
            }
        }
    
    def save_report(self, output_path: str) -> str:
        """Save the report to a file."""
        report = self.generate_report()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {output_path}")
        return output_path
    
    def store_in_memory(self, tag_prefix: str = "schema_trace_report") -> str:
        """Store the report in memory with a timestamp tag."""
        try:
            # Import memory writer
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from app.modules.memory_writer import write_memory
            
            # Generate report
            report = self.generate_report()
            
            # Create tag with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            tag = f"{tag_prefix}_{timestamp}"
            
            # Store in memory
            import asyncio
            asyncio.run(write_memory(project_id="system", tag=tag, value=report))
            
            logger.info(f"Report stored in memory with tag {tag}")
            return tag
        
        except Exception as e:
            logger.error(f"Error storing report in memory: {str(e)}")
            return None
    
    def print_summary(self) -> None:
        """Print a summary of the scan results."""
        print("\n" + "=" * 80)
        print("SCHEMA TRACE SUMMARY")
        print("=" * 80)
        
        print(f"\nMissing Schemas: {len(self.missing_schemas)}")
        for i, schema in enumerate(self.missing_schemas[:10], 1):
            print(f"  {i}. {schema['schema_name']} (referenced in {schema['referenced_in']}:{schema['line_number']})")
        if len(self.missing_schemas) > 10:
            print(f"  ... and {len(self.missing_schemas) - 10} more")
        
        print(f"\nRoutes with Missing Imports: {len(self.routes_with_missing_imports)}")
        for i, route in enumerate(self.routes_with_missing_imports[:10], 1):
            print(f"  {i}. {route['route_file']}: {route['issue']}")
        if len(self.routes_with_missing_imports) > 10:
            print(f"  ... and {len(self.routes_with_missing_imports) - 10} more")
        
        print(f"\nMain.py Issues: {len(self.main_py_issues)}")
        for i, issue in enumerate(self.main_py_issues[:10], 1):
            print(f"  {i}. {issue['issue_type']}: {issue['import_path']} (line {issue['line_number']})")
        if len(self.main_py_issues) > 10:
            print(f"  ... and {len(self.main_py_issues) - 10} more")
        
        print("\nSuggested Schema Locations:")
        for i, suggestion in enumerate(self.suggested_schema_locations[:5], 1):
            print(f"  {i}. {suggestion['schema_name']} -> {suggestion['suggested_file']}")
        if len(self.suggested_schema_locations) > 5:
            print(f"  ... and {len(self.suggested_schema_locations) - 5} more")
        
        print("\nSuggested Import Patches:")
        for i, schema in enumerate(self.missing_schemas[:5], 1):
            schema_name = schema['schema_name']
            suggestion = next((s for s in self.suggested_schema_locations if s['schema_name'] == schema_name), None)
            if suggestion:
                import_path = suggestion['suggested_file'].replace('/', '.').replace('.py', '')
                print(f"  {i}. from {import_path} import {schema_name}")
        if len(self.missing_schemas) > 5:
            print(f"  ... and {len(self.missing_schemas) - 5} more")
        
        print("\n" + "=" * 80)

def main():
    """Main function to parse arguments and run the schema tracer."""
    parser = argparse.ArgumentParser(description="Schema Trace Tool for Promethios")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH,
                        help=f"Output file path (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("--memory-tag", action="store_true",
                        help="Store results in memory with tag schema_trace_report_<timestamp>")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed information during scanning")
    args = parser.parse_args()
    
    # Get project root (assuming script is in tools/ directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"Starting Schema Trace Tool v1 at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {project_root}")
    
    # Create and run schema tracer
    tracer = SchemaTracer(project_root, args.verbose)
    tracer.scan_all()
    
    # Save report
    output_path = os.path.join(project_root, args.output)
    tracer.save_report(output_path)
    
    # Store in memory if requested
    if args.memory_tag:
        memory_tag = tracer.store_in_memory()
        if memory_tag:
            print(f"Report stored in memory with tag: {memory_tag}")
    
    # Print summary
    tracer.print_summary()
    
    # Update manifest if possible
    try:
        from app.utils.manifest_manager import update_hardening_layer
        update_hardening_layer("schema_trace_tool_enabled", True)
        print("✅ Updated system manifest: schema_trace_tool_enabled = True")
    except Exception as e:
        print(f"⚠️ Could not update system manifest: {str(e)}")
    
    print(f"\nSchema Trace Tool completed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Report saved to: {output_path}")

if __name__ == "__main__":
    main()
