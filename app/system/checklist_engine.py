"""
Promethios Internal Checklist Engine (P.I.C.E.)

This module scans the system structure and generates a checklist of the system state.
It detects missing router imports, unwired route modules, agents missing endpoint bindings,
schemas not bound to any endpoint, and tools not wired to workflow.

The checklist is saved to /app/system/system_consciousness_index.json and validated against
/app/schemas/checklist_schema.json.
"""

import os
import json
import importlib
import inspect
import glob
import re
import sys
import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple

# Add the app directory to the path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schema validation
try:
    # First try to import from the local environment
    import jsonschema
except ImportError:
    # If that fails, try to use a direct validation approach without jsonschema
    jsonschema = None
    print("Warning: jsonschema module not available. Using basic validation.")


class ChecklistEngine:
    """
    Core engine to scan system structure and generate a checklist of the system state.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the checklist engine.
        
        Args:
            base_dir: Base directory of the application. If None, uses the parent directory of this file.
        """
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = base_dir
            
        self.routes_dir = os.path.join(self.base_dir, "routes")
        self.schemas_dir = os.path.join(self.base_dir, "schemas")
        self.modules_dir = os.path.join(self.base_dir, "modules")
        self.tools_dir = os.path.join(self.base_dir, "tools")
        self.main_file = os.path.join(self.base_dir, "main.py")
        self.manifest_file = os.path.join(self.base_dir, "system_manifest.json")
        self.schema_file = os.path.join(self.base_dir, "schemas", "checklist_schema.json")
        self.output_file = os.path.join(self.base_dir, "system", "system_consciousness_index.json")
        
        # Initialize data structures
        self.agents = []
        self.routes = []
        self.schemas = []
        self.modules = []
        self.tools = []
        self.execution_checklist = []
        
        # Cache for parsed data
        self._main_content = None
        self._manifest_data = None
        self._route_files = None
        self._schema_files = None
        
    def _load_main_file(self) -> str:
        """Load the content of main.py"""
        if self._main_content is None:
            try:
                with open(self.main_file, 'r') as f:
                    self._main_content = f.read()
            except Exception as e:
                print(f"Error loading main.py: {e}")
                self._main_content = ""
        return self._main_content
    
    def _load_manifest(self) -> Dict:
        """Load the system manifest JSON"""
        if self._manifest_data is None:
            try:
                with open(self.manifest_file, 'r') as f:
                    self._manifest_data = json.load(f)
            except Exception as e:
                print(f"Error loading system manifest: {e}")
                self._manifest_data = {}
        return self._manifest_data
    
    def _get_route_files(self) -> List[str]:
        """Get all route files in the routes directory"""
        if self._route_files is None:
            try:
                self._route_files = glob.glob(os.path.join(self.routes_dir, "*_routes.py"))
            except Exception as e:
                print(f"Error scanning routes directory: {e}")
                self._route_files = []
        return self._route_files
    
    def _get_schema_files(self) -> List[str]:
        """Get all schema files in the schemas directory"""
        if self._schema_files is None:
            try:
                self._schema_files = glob.glob(os.path.join(self.schemas_dir, "*.py"))
            except Exception as e:
                print(f"Error scanning schemas directory: {e}")
                self._schema_files = []
        return self._schema_files
    
    def _extract_router_imports(self) -> Set[str]:
        """Extract router imports from main.py"""
        main_content = self._load_main_file()
        router_imports = set()
        
        # Look for patterns like: from routes.agent_router import agent_router
        import_pattern = re.compile(r'from\s+routes\.(\w+)_router\s+import\s+\w+_router')
        for match in import_pattern.finditer(main_content):
            router_imports.add(f"{match.group(1)}_router")
            
        # Also look for patterns like: app.include_router(agent_router)
        include_pattern = re.compile(r'app\.include_router\((\w+)_router\)')
        for match in include_pattern.finditer(main_content):
            router_imports.add(f"{match.group(1)}_router")
            
        return router_imports
    
    def _extract_agent_registry(self) -> List[Dict]:
        """Extract agent information from agent_registry_enhanced.py"""
        agents = []
        registry_file = os.path.join(self.modules_dir, "agent_registry_enhanced.py")
        
        try:
            # Try to load the enhanced registry first
            if os.path.exists(registry_file):
                with open(registry_file, 'r') as f:
                    content = f.read()
                
                # Look for agent definitions
                agent_pattern = re.compile(r'(\w+)_agent\s*=\s*{[^}]*}')
                for match in agent_pattern.finditer(content):
                    agent_name = match.group(1)
                    agents.append({
                        "name": f"{agent_name}_agent",
                        "role": self._extract_agent_role(content, agent_name),
                        "wired": False,  # Will be updated later
                        "routes": []     # Will be updated later
                    })
            else:
                # Fall back to regular agent_registry.py
                registry_file = os.path.join(self.modules_dir, "agent_registry.py")
                if os.path.exists(registry_file):
                    with open(registry_file, 'r') as f:
                        content = f.read()
                    
                    # Look for agent definitions
                    agent_pattern = re.compile(r'(\w+)_agent\s*=\s*{[^}]*}')
                    for match in agent_pattern.finditer(content):
                        agent_name = match.group(1)
                        agents.append({
                            "name": f"{agent_name}_agent",
                            "role": self._extract_agent_role(content, agent_name),
                            "wired": False,
                            "routes": []
                        })
        except Exception as e:
            print(f"Error extracting agent registry: {e}")
        
        # Also check the manifest for agents
        manifest = self._load_manifest()
        if "agents" in manifest:
            for agent_name, agent_data in manifest.get("agents", {}).items():
                # Check if agent already exists in our list
                if not any(a["name"] == agent_name for a in agents):
                    agents.append({
                        "name": agent_name,
                        "role": agent_data.get("role", "Unknown"),
                        "wired": False,
                        "routes": []
                    })
        
        return agents
    
    def _extract_agent_role(self, content: str, agent_name: str) -> str:
        """Extract the role of an agent from the registry content"""
        role_pattern = re.compile(f'{agent_name}_agent\\s*=\\s*{{[^}}]*"role"\\s*:\\s*"([^"]*)"')
        match = role_pattern.search(content)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _scan_routes(self) -> List[Dict]:
        """Scan route files and extract route information"""
        routes = []
        router_imports = self._extract_router_imports()
        
        for route_file in self._get_route_files():
            file_name = os.path.basename(route_file)
            route_name = file_name.replace("_routes.py", "")
            router_name = f"{route_name}_router"
            
            try:
                with open(route_file, 'r') as f:
                    content = f.read()
                
                # Extract endpoints
                endpoint_pattern = re.compile(r'@\w+_router\.(\w+)\s*\(\s*"([^"]*)"')
                endpoints = []
                for match in endpoint_pattern.finditer(content):
                    http_method = match.group(1)
                    path = match.group(2)
                    endpoints.append({
                        "method": http_method,
                        "path": path
                    })
                
                # Extract schemas used in this route
                schema_pattern = re.compile(r'from\s+schemas\.(\w+)\s+import')
                schemas = []
                for match in schema_pattern.finditer(content):
                    schemas.append(match.group(1))
                
                routes.append({
                    "name": route_name,
                    "file": file_name,
                    "wired": router_name in router_imports,
                    "endpoints": endpoints,
                    "schemas": schemas
                })
            except Exception as e:
                print(f"Error scanning route file {file_name}: {e}")
                routes.append({
                    "name": route_name,
                    "file": file_name,
                    "wired": router_name in router_imports,
                    "endpoints": [],
                    "schemas": [],
                    "error": str(e)
                })
        
        return routes
    
    def _scan_schemas(self) -> List[Dict]:
        """Scan schema files and extract schema information"""
        schemas = []
        
        for schema_file in self._get_schema_files():
            file_name = os.path.basename(schema_file)
            schema_name = file_name.replace(".py", "")
            
            try:
                with open(schema_file, 'r') as f:
                    content = f.read()
                
                # Check if this schema is used in any route
                used_in_routes = []
                for route in self.routes:
                    if schema_name in route["schemas"]:
                        used_in_routes.append(route["name"])
                
                # Extract model classes
                model_pattern = re.compile(r'class\s+(\w+)\s*\(\s*\w+\s*\):')
                models = []
                for match in model_pattern.finditer(content):
                    models.append(match.group(1))
                
                schemas.append({
                    "name": schema_name,
                    "file": file_name,
                    "models": models,
                    "used_in_routes": used_in_routes,
                    "validation_status": "Valid" if models else "Empty"
                })
            except Exception as e:
                print(f"Error scanning schema file {file_name}: {e}")
                schemas.append({
                    "name": schema_name,
                    "file": file_name,
                    "models": [],
                    "used_in_routes": [],
                    "validation_status": "Error",
                    "error": str(e)
                })
        
        return schemas
    
    def _scan_modules(self) -> List[Dict]:
        """Scan modules and extract module information"""
        modules = []
        manifest = self._load_manifest()
        
        # Get modules from manifest
        for module_name, module_data in manifest.get("modules", {}).items():
            modules.append({
                "name": module_name,
                "type": module_data.get("type", "Unknown"),
                "wiring_status": "Wired" if module_data.get("enabled", False) else "Unwired"
            })
        
        # Also scan the modules directory
        try:
            module_files = glob.glob(os.path.join(self.modules_dir, "*.py"))
            for module_file in module_files:
                file_name = os.path.basename(module_file)
                module_name = file_name.replace(".py", "")
                
                # Skip if already in the list
                if any(m["name"] == module_name for m in modules):
                    continue
                
                # Check if it's imported in main.py
                main_content = self._load_main_file()
                is_imported = f"from modules.{module_name} import" in main_content
                
                modules.append({
                    "name": module_name,
                    "type": "Module",
                    "wiring_status": "Wired" if is_imported else "Unwired"
                })
        except Exception as e:
            print(f"Error scanning modules directory: {e}")
        
        return modules
    
    def _scan_tools(self) -> List[Dict]:
        """Scan tools and extract tool information"""
        tools = []
        manifest = self._load_manifest()
        
        # Get tools from manifest
        for tool_name, tool_data in manifest.get("tools", {}).items():
            tools.append({
                "name": tool_name,
                "type": tool_data.get("type", "Unknown"),
                "operational_status": "Operational" if tool_data.get("enabled", False) else "Disabled"
            })
        
        # Also scan the tools directory
        try:
            tool_files = glob.glob(os.path.join(self.tools_dir, "*.py"))
            for tool_file in tool_files:
                file_name = os.path.basename(tool_file)
                tool_name = file_name.replace(".py", "")
                
                # Skip if already in the list
                if any(t["name"] == tool_name for t in tools):
                    continue
                
                # Check if it's imported anywhere
                is_imported = False
                for route_file in self._get_route_files():
                    with open(route_file, 'r') as f:
                        content = f.read()
                        if f"from tools.{tool_name} import" in content:
                            is_imported = True
                            break
                
                tools.append({
                    "name": tool_name,
                    "type": "Tool",
                    "operational_status": "Operational" if is_imported else "Unwired"
                })
        except Exception as e:
            print(f"Error scanning tools directory: {e}")
        
        return tools
    
    def _generate_execution_checklist(self) -> List[str]:
        """Generate a human-readable execution checklist based on the scan results"""
        checklist = []
        
        # Check for unwired routes
        unwired_routes = [r["name"] for r in self.routes if not r["wired"]]
        if unwired_routes:
            checklist.append(f"Wire the following routes in main.py: {', '.join(unwired_routes)}")
        
        # Check for schemas not used in any route
        unused_schemas = [s["name"] for s in self.schemas if not s["used_in_routes"]]
        if unused_schemas:
            checklist.append(f"Bind the following schemas to routes: {', '.join(unused_schemas)}")
        
        # Check for unwired modules
        unwired_modules = [m["name"] for m in self.modules if m["wiring_status"] == "Unwired"]
        if unwired_modules:
            checklist.append(f"Wire the following modules: {', '.join(unwired_modules)}")
        
        # Check for unwired tools
        unwired_tools = [t["name"] for t in self.tools if t["operational_status"] == "Unwired"]
        if unwired_tools:
            checklist.append(f"Wire the following tools to workflow: {', '.join(unwired_tools)}")
        
        # Add general checklist items
        checklist.append("Verify all routes have appropriate error handling")
        checklist.append("Ensure all schemas have proper validation")
        checklist.append("Check that all agents have the necessary permissions")
        
        return checklist
    
    def _update_agent_routes(self):
        """Update agent routes based on the scan results"""
        # Map routes to agents
        for route in self.routes:
            route_name = route["name"]
            
            # Check if this route belongs to an agent
            for agent in self.agents:
                agent_name = agent["name"].replace("_agent", "")
                if route_name.startswith(agent_name):
                    agent["routes"].append(route["name"])
                    agent["wired"] = agent["wired"] or route["wired"]
    
    def scan(self) -> Dict:
        """
        Scan the system structure and generate a checklist.
        
        Returns:
            Dict: The generated checklist.
        """
        # Scan components
        self.agents = self._extract_agent_registry()
        self.routes = self._scan_routes()
        self.schemas = self._scan_schemas()
        self.modules = self._scan_modules()
        self.tools = self._scan_tools()
        
        # Update agent routes
        self._update_agent_routes()
        
        # Generate execution checklist
        self.execution_checklist = self._generate_execution_checklist()
        
        # Build the checklist
        checklist = {
            "agents": self.agents,
            "routes": self.routes,
            "schemas": self.schemas,
            "modules": self.modules,
            "tools": self.tools,
            "execution_checklist": self.execution_checklist,
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        return checklist
    
    def validate_checklist(self, checklist: Dict) -> Tuple[bool, str]:
        """
        Validate the checklist against the schema.
        
        Args:
            checklist: The checklist to validate.
            
        Returns:
            Tuple[bool, str]: A tuple of (is_valid, error_message).
        """
        try:
            # Load the schema
            with open(self.schema_file, 'r') as f:
                schema = json.load(f)
            
            # Validate the checklist
            if jsonschema:
                jsonschema.validate(instance=checklist, schema=schema)
            else:
                # Basic validation without jsonschema
                self._basic_validate(checklist, schema)
            
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def _basic_validate(self, instance, schema):
        """
        Basic validation without jsonschema dependency.
        
        Args:
            instance: The instance to validate.
            schema: The schema to validate against.
        
        Raises:
            Exception: If validation fails.
        """
        # Check required fields
        for field in schema.get("required", []):
            if field not in instance:
                raise Exception(f"Required field '{field}' is missing")
        
        # Check types for top-level fields
        for field, value in instance.items():
            if field in schema.get("properties", {}):
                prop_schema = schema["properties"][field]
                if prop_schema.get("type") == "array" and not isinstance(value, list):
                    raise Exception(f"Field '{field}' should be an array")
                elif prop_schema.get("type") == "object" and not isinstance(value, dict):
                    raise Exception(f"Field '{field}' should be an object")
                elif prop_schema.get("type") == "string" and not isinstance(value, str):
                    raise Exception(f"Field '{field}' should be a string")
        
        # Check array items for required fields
        for field, value in instance.items():
            if field in schema.get("properties", {}) and schema["properties"][field].get("type") == "array":
                if "items" in schema["properties"][field] and "required" in schema["properties"][field]["items"]:
                    required_item_fields = schema["properties"][field]["items"]["required"]
                    for i, item in enumerate(value):
                        for req_field in required_item_fields:
                            if req_field not in item:
                                raise Exception(f"Required field '{req_field}' is missing in item {i} of '{field}'")
    
    def save_checklist(self, checklist: Dict) -> Tuple[bool, str]:
        """
        Save the checklist to the output file.
        
        Args:
            checklist: The checklist to save.
            
        Returns:
            Tuple[bool, str]: A tuple of (success, error_message).
        """
        try:
            # Validate the checklist
            is_valid, error = self.validate_checklist(checklist)
            if not is_valid:
                return False, f"Validation failed: {error}"
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            # Save the checklist
            with open(self.output_file, 'w') as f:
                json.dump(checklist, f, indent=2)
            
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def run(self) -> Tuple[bool, str, Dict]:
        """
        Run the checklist engine.
        
        Returns:
            Tuple[bool, str, Dict]: A tuple of (success, error_message, checklist).
        """
        try:
            # Scan the system
            checklist = self.scan()
            
            # Save the checklist
            success, error = self.save_checklist(checklist)
            if not success:
                return False, error, checklist
            
            return True, "", checklist
        except Exception as e:
            return False, str(e), {}


if __name__ == "__main__":
    # This allows the module to be run directly for testing
    engine = ChecklistEngine()
    success, error, checklist = engine.run()
    
    if success:
        print(f"Checklist generated successfully and saved to {engine.output_file}")
    else:
        print(f"Error generating checklist: {error}")
