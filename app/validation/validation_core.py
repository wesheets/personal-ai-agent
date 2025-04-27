"""
Unified Validation Core for Promethios.

This module provides core validation functions for validating various components
of the Promethios system, including agents, modules, schemas, endpoints, and components.
It also provides utilities for calculating system health and generating drift reports.

This is an isolated sketch as per Operator directive and should not be wired into
startup or post-merge validators until Operator approval.
"""

import os
import json
import logging
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationResult:
    """
    Class representing the result of a validation operation.
    
    This class provides a standardized structure for validation results
    across different validation functions in the system.
    """
    
    def __init__(
        self,
        validation_name: str,
        success: bool,
        details: Dict[str, Any] = None,
        messages: List[str] = None,
        recommendations: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a ValidationResult instance.
        
        Args:
            validation_name: Name of the validation operation
            success: Whether the validation was successful
            details: Detailed information about the validation
            messages: List of informational messages
            recommendations: List of recommendations if validation failed
            metadata: Additional metadata about the validation
        """
        self.validation_name = validation_name
        self.success = success
        self.details = details or {}
        self.messages = messages or []
        self.recommendations = recommendations or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ValidationResult to a dictionary.
        
        Returns:
            Dictionary representation of the ValidationResult
        """
        result = {
            "validation_name": self.validation_name,
            "success": self.success,
            "timestamp": self.timestamp
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.messages:
            result["messages"] = self.messages
        
        if not self.success and self.recommendations:
            result["recommendations"] = self.recommendations
        
        if self.metadata:
            result["metadata"] = self.metadata
        
        return result
    
    def __str__(self) -> str:
        """
        String representation of the ValidationResult.
        
        Returns:
            String representation of the ValidationResult
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """
        Create a ValidationResult instance from a dictionary.
        
        Args:
            data: Dictionary containing validation result data
            
        Returns:
            ValidationResult instance
        """
        result = cls(
            validation_name=data.get("validation_name", "Unknown Validation"),
            success=data.get("success", False),
            details=data.get("details"),
            messages=data.get("messages"),
            recommendations=data.get("recommendations"),
            metadata=data.get("metadata")
        )
        
        if "timestamp" in data:
            result.timestamp = data["timestamp"]
            
        return result

def validate_agents(base_path: str) -> ValidationResult:
    """
    Validate all agent configurations and implementations in the system.
    
    This function checks for the presence and correctness of agent configurations,
    verifies that all required agent files exist, and validates their structure.
    
    Args:
        base_path: Base path to the project directory
        
    Returns:
        ValidationResult containing the validation results
    """
    logger.info("Validating agents...")
    
    # Expected agent directories and files
    expected_agent_dirs = ["plugins/agents", "agents"]
    expected_agent_files = ["__init__.py", "config.json", "agent.py"]
    
    # Initialize validation details
    details = {
        "agent_count": 0,
        "valid_agents": [],
        "invalid_agents": [],
        "missing_files": {},
        "configuration_issues": {}
    }
    
    messages = []
    recommendations = []
    all_agents_valid = True
    
    # Check each potential agent directory
    for agent_dir in expected_agent_dirs:
        full_agent_dir = os.path.join(base_path, agent_dir)
        
        if not os.path.exists(full_agent_dir):
            messages.append(f"Agent directory {agent_dir} does not exist")
            continue
            
        # Find all agent subdirectories
        agent_subdirs = [d for d in os.listdir(full_agent_dir) 
                        if os.path.isdir(os.path.join(full_agent_dir, d)) and not d.startswith('__')]
        
        if not agent_subdirs:
            messages.append(f"No agent subdirectories found in {agent_dir}")
            continue
            
        details["agent_count"] += len(agent_subdirs)
        
        # Validate each agent
        for agent_name in agent_subdirs:
            agent_path = os.path.join(full_agent_dir, agent_name)
            agent_valid = True
            missing_files = []
            
            # Check for required files
            for required_file in expected_agent_files:
                file_path = os.path.join(agent_path, required_file)
                if not os.path.exists(file_path):
                    agent_valid = False
                    missing_files.append(required_file)
            
            # Check configuration if config.json exists
            config_issues = []
            config_path = os.path.join(agent_path, "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Validate required config fields
                    required_fields = ["name", "version", "description", "capabilities"]
                    for field in required_fields:
                        if field not in config:
                            agent_valid = False
                            config_issues.append(f"Missing required field: {field}")
                            
                except json.JSONDecodeError:
                    agent_valid = False
                    config_issues.append("Invalid JSON format in config.json")
                except Exception as e:
                    agent_valid = False
                    config_issues.append(f"Error reading config.json: {str(e)}")
            
            # Record validation results for this agent
            if agent_valid:
                details["valid_agents"].append(f"{agent_dir}/{agent_name}")
            else:
                all_agents_valid = False
                details["invalid_agents"].append(f"{agent_dir}/{agent_name}")
                
                if missing_files:
                    details["missing_files"][f"{agent_dir}/{agent_name}"] = missing_files
                    recommendations.append(f"Add missing files for {agent_name}: {', '.join(missing_files)}")
                
                if config_issues:
                    details["configuration_issues"][f"{agent_dir}/{agent_name}"] = config_issues
                    recommendations.append(f"Fix configuration issues for {agent_name}: {', '.join(config_issues)}")
    
    # Generate overall validation result
    if details["agent_count"] == 0:
        messages.append("No agents found in the system")
        recommendations.append("Create agent implementations in plugins/agents or agents directory")
        all_agents_valid = False
    
    return ValidationResult(
        validation_name="Agent Validation",
        success=all_agents_valid,
        details=details,
        messages=messages,
        recommendations=recommendations
    )

def validate_modules(base_path: str) -> ValidationResult:
    """
    Validate all modules in the system.
    
    This function checks for the presence and correctness of module implementations,
    verifies that all required module files exist, and validates their structure.
    
    Args:
        base_path: Base path to the project directory
        
    Returns:
        ValidationResult containing the validation results
    """
    logger.info("Validating modules...")
    
    # Expected module directories and files
    module_dir = "modules"
    expected_module_files = ["__init__.py", "module.py"]
    
    # Initialize validation details
    details = {
        "module_count": 0,
        "valid_modules": [],
        "invalid_modules": [],
        "missing_files": {},
        "import_issues": {}
    }
    
    messages = []
    recommendations = []
    all_modules_valid = True
    
    # Check if modules directory exists
    full_module_dir = os.path.join(base_path, module_dir)
    if not os.path.exists(full_module_dir):
        messages.append(f"Module directory {module_dir} does not exist")
        recommendations.append(f"Create the {module_dir} directory")
        return ValidationResult(
            validation_name="Module Validation",
            success=False,
            details=details,
            messages=messages,
            recommendations=recommendations
        )
    
    # Find all module subdirectories
    module_subdirs = [d for d in os.listdir(full_module_dir) 
                     if os.path.isdir(os.path.join(full_module_dir, d)) and not d.startswith('__')]
    
    if not module_subdirs:
        messages.append(f"No module subdirectories found in {module_dir}")
        recommendations.append(f"Create module implementations in the {module_dir} directory")
        return ValidationResult(
            validation_name="Module Validation",
            success=False,
            details=details,
            messages=messages,
            recommendations=recommendations
        )
    
    details["module_count"] = len(module_subdirs)
    
    # Validate each module
    for module_name in module_subdirs:
        module_path = os.path.join(full_module_dir, module_name)
        module_valid = True
        missing_files = []
        
        # Check for required files
        for required_file in expected_module_files:
            file_path = os.path.join(module_path, required_file)
            if not os.path.exists(file_path):
                module_valid = False
                missing_files.append(required_file)
        
        # Check for import issues in module.py if it exists
        import_issues = []
        module_file_path = os.path.join(module_path, "module.py")
        if os.path.exists(module_file_path):
            try:
                with open(module_file_path, 'r') as f:
                    module_code = f.read()
                
                # Check for common import patterns
                required_imports = ["import os", "import json", "from typing import"]
                for required_import in required_imports:
                    if required_import not in module_code:
                        import_issues.append(f"Missing expected import: {required_import}")
                
                # Check for class definition
                if "class " not in module_code:
                    import_issues.append("No class definition found in module.py")
                
                # Check for function definitions
                if "def " not in module_code:
                    import_issues.append("No function definitions found in module.py")
                
            except Exception as e:
                import_issues.append(f"Error reading module.py: {str(e)}")
        
        # Record validation results for this module
        if module_valid and not import_issues:
            details["valid_modules"].append(module_name)
        else:
            all_modules_valid = False
            details["invalid_modules"].append(module_name)
            
            if missing_files:
                details["missing_files"][module_name] = missing_files
                recommendations.append(f"Add missing files for {module_name}: {', '.join(missing_files)}")
            
            if import_issues:
                details["import_issues"][module_name] = import_issues
                recommendations.append(f"Fix import issues for {module_name}: {', '.join(import_issues)}")
    
    # Check for module interdependencies
    dependency_issues = []
    for module_name in module_subdirs:
        module_file_path = os.path.join(full_module_dir, module_name, "module.py")
        if os.path.exists(module_file_path):
            try:
                with open(module_file_path, 'r') as f:
                    module_code = f.read()
                
                # Check for imports from other modules
                for other_module in module_subdirs:
                    if other_module != module_name and f"from app.modules.{other_module}" in module_code:
                        dependency_issues.append(f"{module_name} depends on {other_module}")
            except Exception:
                pass
    
    if dependency_issues:
        details["dependency_issues"] = dependency_issues
        messages.append("Module interdependencies detected")
    
    return ValidationResult(
        validation_name="Module Validation",
        success=all_modules_valid,
        details=details,
        messages=messages,
        recommendations=recommendations
    )

def validate_schemas(base_path: str) -> ValidationResult:
    """
    Validate all schema definitions in the system.
    
    This function checks for the presence and correctness of schema files,
    verifies their JSON structure, and validates against expected schema patterns.
    
    Args:
        base_path: Base path to the project directory
        
    Returns:
        ValidationResult containing the validation results
    """
    logger.info("Validating schemas...")
    
    # Expected schema directories and required schema fields
    schema_dirs = ["schemas", "schemas/schemas"]
    required_schema_fields = ["type", "properties"]
    
    # Initialize validation details
    details = {
        "schema_count": 0,
        "valid_schemas": [],
        "invalid_schemas": [],
        "parse_errors": {},
        "validation_errors": {}
    }
    
    messages = []
    recommendations = []
    all_schemas_valid = True
    
    # Check each potential schema directory
    for schema_dir in schema_dirs:
        full_schema_dir = os.path.join(base_path, schema_dir)
        
        if not os.path.exists(full_schema_dir):
            messages.append(f"Schema directory {schema_dir} does not exist")
            continue
        
        # Find all schema files (JSON files)
        schema_files = glob.glob(os.path.join(full_schema_dir, "*.json"))
        
        if not schema_files:
            messages.append(f"No schema files found in {schema_dir}")
            continue
            
        details["schema_count"] += len(schema_files)
        
        # Validate each schema file
        for schema_file in schema_files:
            schema_name = os.path.basename(schema_file)
            schema_valid = True
            
            try:
                # Attempt to parse the schema file
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                
                # Validate required schema fields
                validation_errors = []
                
                # Check if it's a JSON Schema
                if not isinstance(schema, dict):
                    schema_valid = False
                    validation_errors.append("Schema is not a JSON object")
                else:
                    # Check for required fields
                    for field in required_schema_fields:
                        if field not in schema:
                            schema_valid = False
                            validation_errors.append(f"Missing required field: {field}")
                    
                    # Check if properties is a dictionary
                    if "properties" in schema and not isinstance(schema["properties"], dict):
                        schema_valid = False
                        validation_errors.append("'properties' field is not a JSON object")
                    
                    # Check if type is valid
                    if "type" in schema and schema["type"] not in ["object", "array", "string", "number", "boolean", "null"]:
                        schema_valid = False
                        validation_errors.append(f"Invalid 'type' value: {schema['type']}")
                
                # Record validation errors
                if validation_errors:
                    details["validation_errors"][schema_name] = validation_errors
                
            except json.JSONDecodeError as e:
                schema_valid = False
                details["parse_errors"][schema_name] = f"JSON parse error: {str(e)}"
                recommendations.append(f"Fix JSON syntax in {schema_name}")
            except Exception as e:
                schema_valid = False
                details["parse_errors"][schema_name] = f"Error reading schema: {str(e)}"
            
            # Record validation results for this schema
            if schema_valid:
                details["valid_schemas"].append(f"{schema_dir}/{schema_name}")
            else:
                all_schemas_valid = False
                details["invalid_schemas"].append(f"{schema_dir}/{schema_name}")
                
                if schema_name in details["validation_errors"]:
                    error_list = details["validation_errors"][schema_name]
                    recommendations.append(f"Fix schema issues in {schema_name}: {', '.join(error_list)}")
    
    # Generate overall validation result
    if details["schema_count"] == 0:
        messages.append("No schema files found in the system")
        recommendations.append("Create schema definitions in the schemas directory")
        all_schemas_valid = False
    
    # Check for schema references and consistency
    if details["schema_count"] > 0:
        # Check for schema references
        reference_issues = []
        for schema_dir in schema_dirs:
            full_schema_dir = os.path.join(base_path, schema_dir)
            if not os.path.exists(full_schema_dir):
                continue
                
            schema_files = glob.glob(os.path.join(full_schema_dir, "*.json"))
            for schema_file in schema_files:
                try:
                    with open(schema_file, 'r') as f:
                        schema_content = f.read()
                        
                    # Look for $ref references
                    if '"$ref"' in schema_content:
                        import re
                        refs = re.findall(r'"\\$ref"\s*:\s*"([^"]+)"', schema_content)
                        for ref in refs:
                            # Check if the referenced schema exists
                            if ref.startswith("#"):
                                # Internal reference, skip
                                continue
                                
                            ref_parts = ref.split("/")
                            if len(ref_parts) > 1:
                                ref_file = ref_parts[-1]
                                if not ref_file.endswith(".json"):
                                    ref_file += ".json"
                                    
                                ref_exists = False
                                for check_dir in schema_dirs:
                                    check_path = os.path.join(base_path, check_dir, ref_file)
                                    if os.path.exists(check_path):
                                        ref_exists = True
                                        break
                                        
                                if not ref_exists:
                                    reference_issues.append(f"Schema {os.path.basename(schema_file)} references non-existent schema: {ref}")
                except Exception:
                    pass
        
        if reference_issues:
            details["reference_issues"] = reference_issues
            messages.append("Schema reference issues detected")
            recommendations.append("Fix schema references to ensure all referenced schemas exist")
    
    return ValidationResult(
        validation_name="Schema Validation",
        success=all_schemas_valid,
        details=details,
        messages=messages,
        recommendations=recommendations
    )

def validate_endpoints(base_path: str) -> ValidationResult:
    """
    Validate all API endpoints in the system.
    
    This function checks for the presence and correctness of API endpoint implementations,
    verifies their route definitions, and validates their handler functions.
    
    Args:
        base_path: Base path to the project directory
        
    Returns:
        ValidationResult containing the validation results
    """
    logger.info("Validating endpoints...")
    
    # Expected endpoint directories and files
    routes_dir = "routes"
    
    # Initialize validation details
    details = {
        "endpoint_count": 0,
        "valid_endpoints": [],
        "invalid_endpoints": [],
        "missing_handlers": {},
        "route_issues": {}
    }
    
    messages = []
    recommendations = []
    all_endpoints_valid = True
    
    # Check if routes directory exists
    full_routes_dir = os.path.join(base_path, routes_dir)
    if not os.path.exists(full_routes_dir):
        messages.append(f"Routes directory {routes_dir} does not exist")
        recommendations.append(f"Create the {routes_dir} directory")
        return ValidationResult(
            validation_name="Endpoint Validation",
            success=False,
            details=details,
            messages=messages,
            recommendations=recommendations
        )
    
    # Find all Python files in routes directory
    route_files = glob.glob(os.path.join(full_routes_dir, "*.py"))
    
    if not route_files:
        messages.append(f"No route files found in {routes_dir}")
        recommendations.append(f"Create route implementations in the {routes_dir} directory")
        return ValidationResult(
            validation_name="Endpoint Validation",
            success=False,
            details=details,
            messages=messages,
            recommendations=recommendations
        )
    
    # Validate each route file
    for route_file in route_files:
        route_name = os.path.basename(route_file)
        
        if route_name == "__init__.py":
            continue
            
        try:
            # Read the route file
            with open(route_file, 'r') as f:
                route_code = f.read()
            
            # Extract endpoints from route file
            import re
            
            # Look for FastAPI route decorators
            route_patterns = [
                r'@\w+\.(?:get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
                r'@router\.(?:get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']'
            ]
            
            endpoints = []
            for pattern in route_patterns:
                endpoints.extend(re.findall(pattern, route_code))
            
            if not endpoints:
                messages.append(f"No endpoints found in {route_name}")
                continue
                
            details["endpoint_count"] += len(endpoints)
            
            # Validate each endpoint
            for endpoint in endpoints:
                endpoint_valid = True
                route_issues = []
                
                # Check if endpoint has a handler function
                handler_pattern = rf'@\w+\.(?:get|post|put|delete|patch|options|head)\s*\(\s*["\'{endpoint}["\'].*?\)\s*\n\s*(?:async\s+)?def\s+(\w+)'
                handlers = re.findall(handler_pattern, route_code, re.DOTALL)
                
                if not handlers:
                    endpoint_valid = False
                    details["missing_handlers"][f"{route_name}:{endpoint}"] = "No handler function found"
                    recommendations.append(f"Add handler function for endpoint {endpoint} in {route_name}")
                
                # Check for common route issues
                if "{" in endpoint and "}" not in endpoint:
                    endpoint_valid = False
                    route_issues.append("Unclosed path parameter")
                
                if endpoint.count("{") != endpoint.count("}"):
                    endpoint_valid = False
                    route_issues.append("Mismatched path parameter braces")
                
                # Check for duplicate path parameters
                path_params = re.findall(r'{([^}]+)}', endpoint)
                if len(path_params) != len(set(path_params)):
                    endpoint_valid = False
                    route_issues.append("Duplicate path parameters")
                
                # Record route issues
                if route_issues:
                    details["route_issues"][f"{route_name}:{endpoint}"] = route_issues
                    recommendations.append(f"Fix route issues for {endpoint} in {route_name}: {', '.join(route_issues)}")
                
                # Record validation results for this endpoint
                if endpoint_valid:
                    details["valid_endpoints"].append(f"{route_name}:{endpoint}")
                else:
                    all_endpoints_valid = False
                    details["invalid_endpoints"].append(f"{route_name}:{endpoint}")
                
        except Exception as e:
            all_endpoints_valid = False
            messages.append(f"Error validating {route_name}: {str(e)}")
    
    # Generate overall validation result
    if details["endpoint_count"] == 0:
        messages.append("No endpoints found in the system")
        recommendations.append("Create API endpoints in the routes directory")
        all_endpoints_valid = False
    
    return ValidationResult(
        validation_name="Endpoint Validation",
        success=all_endpoints_valid,
        details=details,
        messages=messages,
        recommendations=recommendations
    )

def validate_components(base_path: str) -> ValidationResult:
    """
    Validate all UI and system components in the system.
    
    This function checks for the presence and correctness of component implementations,
    verifies their structure, and validates their dependencies.
    
    Args:
        base_path: Base path to the project directory
        
    Returns:
        ValidationResult containing the validation results
    """
    logger.info("Validating components...")
    
    # Expected component directories
    component_dirs = ["frontend/src/components", "components"]
    
    # Initialize validation details
    details = {
        "component_count": 0,
        "valid_components": [],
        "invalid_components": [],
        "missing_files": {},
        "structure_issues": {}
    }
    
    messages = []
    recommendations = []
    all_components_valid = True
    
    # Check each potential component directory
    component_found = False
    for component_dir in component_dirs:
        full_component_dir = os.path.join(base_path, component_dir)
        
        if not os.path.exists(full_component_dir):
            messages.append(f"Component directory {component_dir} does not exist")
            continue
            
        component_found = True
        
        # Find all component files (JS, JSX, TS, TSX files)
        component_files = []
        for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
            component_files.extend(glob.glob(os.path.join(full_component_dir, "**", ext), recursive=True))
        
        if not component_files:
            messages.append(f"No component files found in {component_dir}")
            continue
            
        details["component_count"] += len(component_files)
        
        # Validate each component file
        for component_file in component_files:
            rel_path = os.path.relpath(component_file, base_path)
            component_name = os.path.basename(component_file)
            
            # Skip index files and non-component files
            if component_name.startswith("index.") or component_name.startswith("_"):
                continue
                
            component_valid = True
            structure_issues = []
            
            try:
                # Read the component file
                with open(component_file, 'r') as f:
                    component_code = f.read()
                
                # Check for React component patterns
                if any(ext in component_file for ext in [".js", ".jsx", ".ts", ".tsx"]):
                    # Check for component definition
                    if not any(pattern in component_code for pattern in ["function ", "class ", "const ", "export default"]):
                        component_valid = False
                        structure_issues.append("No component definition found")
                    
                    # Check for export statement
                    if "export" not in component_code:
                        component_valid = False
                        structure_issues.append("No export statement found")
                    
                    # Check for React import
                    if "import React" not in component_code and "import { " not in component_code:
                        component_valid = False
                        structure_issues.append("No React import found")
                    
                    # Check for return statement in functional components
                    if "function " in component_code and "return " not in component_code:
                        component_valid = False
                        structure_issues.append("No return statement found in functional component")
                    
                    # Check for render method in class components
                    if "class " in component_code and "extends " in component_code and "render() {" not in component_code:
                        component_valid = False
                        structure_issues.append("No render method found in class component")
                
                # Record structure issues
                if structure_issues:
                    details["structure_issues"][rel_path] = structure_issues
                    recommendations.append(f"Fix structure issues in {rel_path}: {', '.join(structure_issues)}")
                
            except Exception as e:
                component_valid = False
                details["structure_issues"][rel_path] = [f"Error reading component: {str(e)}"]
                recommendations.append(f"Fix error in {rel_path}: {str(e)}")
            
            # Record validation results for this component
            if component_valid:
                details["valid_components"].append(rel_path)
            else:
                all_components_valid = False
                details["invalid_components"].append(rel_path)
    
    # Check for Python component files
    python_component_dirs = ["components", "toolkit/components"]
    for py_component_dir in python_component_dirs:
        full_py_component_dir = os.path.join(base_path, py_component_dir)
        
        if not os.path.exists(full_py_component_dir):
            continue
            
        component_found = True
        
        # Find all Python component files
        py_component_files = glob.glob(os.path.join(full_py_component_dir, "**", "*.py"), recursive=True)
        
        if not py_component_files:
            continue
            
        details["component_count"] += len(py_component_files)
        
        # Validate each Python component file
        for py_component_file in py_component_files:
            rel_path = os.path.relpath(py_component_file, base_path)
            py_component_name = os.path.basename(py_component_file)
            
            # Skip __init__.py and non-component files
            if py_component_name == "__init__.py" or py_component_name.startswith("_"):
                continue
                
            py_component_valid = True
            py_structure_issues = []
            
            try:
                # Read the component file
                with open(py_component_file, 'r') as f:
                    py_component_code = f.read()
                
                # Check for class definition
                if "class " not in py_component_code:
                    py_component_valid = False
                    py_structure_issues.append("No class definition found")
                
                # Check for init method
                if "__init__" not in py_component_code:
                    py_component_valid = False
                    py_structure_issues.append("No __init__ method found")
                
                # Record structure issues
                if py_structure_issues:
                    details["structure_issues"][rel_path] = py_structure_issues
                    recommendations.append(f"Fix structure issues in {rel_path}: {', '.join(py_structure_issues)}")
                
            except Exception as e:
                py_component_valid = False
                details["structure_issues"][rel_path] = [f"Error reading component: {str(e)}"]
                recommendations.append(f"Fix error in {rel_path}: {str(e)}")
            
            # Record validation results for this component
            if py_component_valid:
                details["valid_components"].append(rel_path)
            else:
                all_components_valid = False
                details["invalid_components"].append(rel_path)
    
    # Generate overall validation result
    if not component_found:
        messages.append("No component directories found in the system")
        recommendations.append("Create component implementations in frontend/src/components or components directory")
        all_components_valid = False
    elif details["component_count"] == 0:
        messages.append("No component files found in the system")
        recommendations.append("Create component implementations in the component directories")
        all_components_valid = False
    
    return ValidationResult(
        validation_name="Component Validation",
        success=all_components_valid,
        details=details,
        messages=messages,
        recommendations=recommendations
    )

def calculate_surface_health(validations: dict) -> float:
    """
    Calculate the overall system health based on validation results.
    
    This function aggregates the results from all validation functions and
    calculates a health score between 0.0 and 1.0, where 1.0 represents
    a perfectly healthy system.
    
    Args:
        validations: Dictionary containing validation results from all validation functions
        
    Returns:
        Float representing the overall system health (0.0 to 1.0)
    """
    logger.info("Calculating surface health...")
    
    if not validations:
        logger.warning("No validation results provided")
        return 0.0
    
    # Define weights for different validation categories
    weights = {
        "Agent Validation": 0.25,
        "Module Validation": 0.20,
        "Schema Validation": 0.15,
        "Endpoint Validation": 0.20,
        "Component Validation": 0.20
    }
    
    # Adjust weights if some validation categories are missing
    total_weight = sum(weights.get(validation_name, 0.0) for validation_name in validations.keys())
    if total_weight == 0:
        logger.warning("No recognized validation categories found")
        return 0.0
    
    # Normalize weights to ensure they sum to 1.0
    normalized_weights = {k: v / total_weight for k, v in weights.items() if k in validations}
    
    # Calculate weighted health score
    health_score = 0.0
    for validation_name, validation_result in validations.items():
        if validation_name not in normalized_weights:
            continue
            
        # Extract success flag and calculate category score
        category_success = validation_result.success
        
        # If validation was successful, use 1.0 as the score
        if category_success:
            category_score = 1.0
        else:
            # For failed validations, calculate a partial score based on valid vs. total items
            valid_count = 0
            total_count = 0
            
            # Extract counts from different validation types
            details = validation_result.details
            if "agent_count" in details:
                total_count = details.get("agent_count", 0)
                valid_count = len(details.get("valid_agents", []))
            elif "module_count" in details:
                total_count = details.get("module_count", 0)
                valid_count = len(details.get("valid_modules", []))
            elif "schema_count" in details:
                total_count = details.get("schema_count", 0)
                valid_count = len(details.get("valid_schemas", []))
            elif "endpoint_count" in details:
                total_count = details.get("endpoint_count", 0)
                valid_count = len(details.get("valid_endpoints", []))
            elif "component_count" in details:
                total_count = details.get("component_count", 0)
                valid_count = len(details.get("valid_components", []))
            
            # Calculate category score (minimum 0.1 to avoid complete failure)
            category_score = valid_count / total_count if total_count > 0 else 0.1
            category_score = max(0.1, category_score)  # Ensure minimum score of 0.1
        
        # Add weighted category score to total health score
        health_score += normalized_weights[validation_name] * category_score
    
    # Ensure health score is between 0.0 and 1.0
    health_score = max(0.0, min(1.0, health_score))
    
    logger.info(f"Calculated surface health: {health_score:.2f}")
    return health_score

def generate_drift_report(validations: dict) -> dict:
    """
    Generate a drift report based on validation results.
    
    This function analyzes validation results to identify potential drift
    in system components, highlighting areas that may need attention or
    have changed significantly since the last validation.
    
    Args:
        validations: Dictionary containing validation results from all validation functions
        
    Returns:
        Dictionary containing drift report information
    """
    logger.info("Generating drift report...")
    
    if not validations:
        logger.warning("No validation results provided for drift report")
        return {
            "timestamp": datetime.now().isoformat(),
            "drift_detected": False,
            "message": "No validation results provided",
            "details": {}
        }
    
    # Initialize drift report
    drift_report = {
        "timestamp": datetime.now().isoformat(),
        "drift_detected": False,
        "surface_health": calculate_surface_health(validations),
        "category_health": {},
        "critical_issues": [],
        "warnings": [],
        "recommendations": [],
        "details": {}
    }
    
    # Define severity thresholds
    critical_threshold = 0.6  # Below this is critical
    warning_threshold = 0.8   # Below this is a warning
    
    # Analyze each validation category
    for validation_name, validation_result in validations.items():
        # Calculate category health
        category_health = 1.0
        if not validation_result.success:
            details = validation_result.details
            valid_count = 0
            total_count = 0
            
            # Extract counts from different validation types
            if "agent_count" in details:
                total_count = details.get("agent_count", 0)
                valid_count = len(details.get("valid_agents", []))
            elif "module_count" in details:
                total_count = details.get("module_count", 0)
                valid_count = len(details.get("valid_modules", []))
            elif "schema_count" in details:
                total_count = details.get("schema_count", 0)
                valid_count = len(details.get("valid_schemas", []))
            elif "endpoint_count" in details:
                total_count = details.get("endpoint_count", 0)
                valid_count = len(details.get("valid_endpoints", []))
            elif "component_count" in details:
                total_count = details.get("component_count", 0)
                valid_count = len(details.get("valid_components", []))
            
            # Calculate category health
            if total_count > 0:
                category_health = valid_count / total_count
            else:
                category_health = 0.1
        
        drift_report["category_health"][validation_name] = category_health
        
        # Check for critical issues and warnings
        if category_health < critical_threshold:
            drift_report["drift_detected"] = True
            drift_report["critical_issues"].append({
                "category": validation_name,
                "health": category_health,
                "message": f"Critical health issues in {validation_name}"
            })
            
            # Add specific recommendations
            if validation_result.recommendations:
                for recommendation in validation_result.recommendations:
                    drift_report["recommendations"].append({
                        "category": validation_name,
                        "recommendation": recommendation,
                        "severity": "critical"
                    })
        elif category_health < warning_threshold:
            drift_report["drift_detected"] = True
            drift_report["warnings"].append({
                "category": validation_name,
                "health": category_health,
                "message": f"Health issues detected in {validation_name}"
            })
            
            # Add specific recommendations
            if validation_result.recommendations:
                for recommendation in validation_result.recommendations:
                    drift_report["recommendations"].append({
                        "category": validation_name,
                        "recommendation": recommendation,
                        "severity": "warning"
                    })
        
        # Add detailed validation results
        drift_report["details"][validation_name] = {
            "success": validation_result.success,
            "health": category_health,
            "messages": validation_result.messages,
            "details": validation_result.details
        }
    
    # Add overall system health assessment
    overall_health = drift_report["surface_health"]
    if overall_health < critical_threshold:
        drift_report["system_status"] = "critical"
        drift_report["system_message"] = "System has critical health issues that require immediate attention"
    elif overall_health < warning_threshold:
        drift_report["system_status"] = "warning"
        drift_report["system_message"] = "System has health issues that should be addressed"
    else:
        drift_report["system_status"] = "healthy"
        drift_report["system_message"] = "System is healthy"
    
    # Add drift detection summary
    if drift_report["drift_detected"]:
        drift_report["drift_summary"] = f"System drift detected with overall health at {overall_health:.2f}"
        
        # Count critical and warning issues
        critical_count = len(drift_report["critical_issues"])
        warning_count = len(drift_report["warnings"])
        
        if critical_count > 0:
            drift_report["drift_summary"] += f". {critical_count} critical issue(s) detected"
        if warning_count > 0:
            drift_report["drift_summary"] += f". {warning_count} warning(s) detected"
    else:
        drift_report["drift_summary"] = "No significant system drift detected"
    
    logger.info(f"Drift report generated: {drift_report['drift_summary']}")
    return drift_report
