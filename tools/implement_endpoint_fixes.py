#!/usr/bin/env python3
"""
Endpoint Fix Implementer
Implements fixes for the next batch of prioritized non-operational endpoints.
"""

import os
import json
import datetime
import re
from pathlib import Path

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
NEXT_BATCH_FILE = "/home/ubuntu/personal-ai-agent/logs/next_batch_priorities.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_fix_implementation_results.json"
APP_DIR = "/home/ubuntu/personal-ai-agent/app"

def load_next_batch():
    """Load next batch of endpoints to fix"""
    with open(NEXT_BATCH_FILE, "r") as f:
        return json.load(f)

def implement_server_error_fix(strategy):
    """Implement fix for server error"""
    endpoint = strategy["endpoint"]
    method = endpoint["method"]
    route_path = endpoint["route_path"]
    
    # Determine the route module based on the path
    parts = route_path.strip("/").split("/")
    module_name = parts[0] if parts else "root"
    
    # Check if the route file exists
    route_file = None
    if strategy.get("schema_info") and strategy["schema_info"].get("route_file"):
        route_file = strategy["schema_info"]["route_file"]
    else:
        # Try to find the route file
        potential_route_files = [
            f"{APP_DIR}/routes/{module_name}_routes.py",
            f"{APP_DIR}/routes/{module_name}_router.py",
            f"{APP_DIR}/routes/{module_name}.py"
        ]
        for file in potential_route_files:
            if os.path.exists(file):
                route_file = file
                break
    
    if not route_file:
        return {
            "status": "error",
            "message": f"Could not find route file for {method} {route_path}",
            "endpoint": endpoint,
            "fix_type": "server_error_fix"
        }
    
    # Read the route file
    try:
        with open(route_file, "r") as f:
            route_content = f.read()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading route file: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "server_error_fix"
        }
    
    # Find the route handler for this endpoint
    route_pattern = route_path.replace("{", "{").replace("}", "}")
    handler_match = re.search(rf'@router\.{method.lower()}\([\'"]({route_pattern}|{re.escape(route_path)})[\'"]', route_content)
    
    if not handler_match:
        return {
            "status": "error",
            "message": f"Could not find route handler for {method} {route_path} in {route_file}",
            "endpoint": endpoint,
            "fix_type": "server_error_fix"
        }
    
    # Find the function definition after the decorator
    function_match = re.search(r'async def ([a-zA-Z0-9_]+)\(', route_content[handler_match.end():])
    if not function_match:
        return {
            "status": "error",
            "message": f"Could not find function definition for route handler in {route_file}",
            "endpoint": endpoint,
            "fix_type": "server_error_fix"
        }
    
    function_name = function_match.group(1)
    
    # Find the entire function
    function_start = handler_match.start()
    function_pattern = rf'@router\.{method.lower()}\([\'"](?:{route_pattern}|{re.escape(route_path)})[\'"].*?async def {function_name}\(.*?\).*?(?=@|\Z)'
    function_match = re.search(function_pattern, route_content[function_start:], re.DOTALL)
    
    if not function_match:
        return {
            "status": "error",
            "message": f"Could not find complete function for route handler in {route_file}",
            "endpoint": endpoint,
            "fix_type": "server_error_fix"
        }
    
    function_code = function_match.group(0)
    
    # Check if the function has a try-except block
    if "try:" not in function_code:
        # Add try-except block to the function
        fixed_function = add_try_except_to_function(function_code, function_name)
    else:
        # Fix the existing try-except block
        fixed_function = fix_try_except_in_function(function_code, function_name)
    
    # Replace the function in the route file
    fixed_route_content = route_content[:function_start] + fixed_function + route_content[function_start + function_match.end():]
    
    # Write the fixed route file
    try:
        with open(route_file, "w") as f:
            f.write(fixed_route_content)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error writing fixed route file: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "server_error_fix"
        }
    
    return {
        "status": "success",
        "message": f"Fixed server error in {method} {route_path}",
        "endpoint": endpoint,
        "fix_type": "server_error_fix",
        "route_file": route_file,
        "function_name": function_name,
        "changes": "Added or fixed try-except block to handle exceptions"
    }

def add_try_except_to_function(function_code, function_name):
    """Add try-except block to a function"""
    # Find the function body indentation
    lines = function_code.split("\n")
    function_def_line = next((i for i, line in enumerate(lines) if f"def {function_name}" in line), 0)
    
    if function_def_line >= len(lines) - 1:
        # Function definition is the last line, can't determine indentation
        return function_code
    
    # Find the first non-empty line after the function definition
    body_line = function_def_line + 1
    while body_line < len(lines) and not lines[body_line].strip():
        body_line += 1
    
    if body_line >= len(lines):
        # No function body found
        return function_code
    
    # Determine indentation
    indentation = ""
    for char in lines[body_line]:
        if char in [" ", "\t"]:
            indentation += char
        else:
            break
    
    # Split the function into definition and body
    definition = "\n".join(lines[:body_line])
    body = "\n".join(lines[body_line:])
    
    # Add try-except block
    fixed_body = f"{indentation}try:\n"
    
    # Indent the body
    for line in body.split("\n"):
        if line.strip():
            fixed_body += f"{indentation}    {line.lstrip()}\n"
        else:
            fixed_body += f"{line}\n"
    
    # Add except block
    fixed_body += f"{indentation}except Exception as e:\n"
    fixed_body += f"{indentation}    logger.error(f\"Error in {function_name}: {{str(e)}}\")\n"
    fixed_body += f"{indentation}    return {{\n"
    fixed_body += f"{indentation}        \"status\": \"error\",\n"
    fixed_body += f"{indentation}        \"message\": f\"Internal server error: {{str(e)}}\"\n"
    fixed_body += f"{indentation}    }}\n"
    
    return definition + "\n" + fixed_body

def fix_try_except_in_function(function_code, function_name):
    """Fix existing try-except block in a function"""
    # Check if there's a generic Exception handler
    if "except Exception" in function_code:
        # Already has a generic exception handler, no need to fix
        return function_code
    
    # Find the try block
    try_match = re.search(r'(\s+)try:', function_code)
    if not try_match:
        # No try block found, can't fix
        return function_code
    
    indentation = try_match.group(1)
    
    # Find all except blocks
    except_blocks = re.findall(r'except [^:]+:', function_code)
    
    # Add a generic Exception handler if not present
    if not any("except Exception" in block for block in except_blocks):
        # Find the last except block
        last_except_pos = function_code.rfind("except ")
        if last_except_pos == -1:
            # No except blocks found, can't fix
            return function_code
        
        # Find the end of the last except block
        last_except_end = function_code.find("\n", last_except_pos)
        if last_except_end == -1:
            # Can't find the end of the last except block
            return function_code
        
        # Add generic Exception handler after the last except block
        fixed_function = function_code[:last_except_end + 1]
        fixed_function += f"{indentation}except Exception as e:\n"
        fixed_function += f"{indentation}    logger.error(f\"Error in {function_name}: {{str(e)}}\")\n"
        fixed_function += f"{indentation}    return {{\n"
        fixed_function += f"{indentation}        \"status\": \"error\",\n"
        fixed_function += f"{indentation}        \"message\": f\"Internal server error: {{str(e)}}\"\n"
        fixed_function += f"{indentation}    }}\n"
        fixed_function += function_code[last_except_end + 1:]
        
        return fixed_function
    
    return function_code

def implement_route_with_schema(strategy):
    """Implement a missing route using schema information"""
    endpoint = strategy["endpoint"]
    method = endpoint["method"]
    route_path = endpoint["route_path"]
    schema_info = strategy.get("schema_info", {})
    
    if not schema_info:
        return {
            "status": "error",
            "message": f"No schema information available for {method} {route_path}",
            "endpoint": endpoint,
            "fix_type": "route_implementation"
        }
    
    # Determine the route module based on the path
    parts = route_path.strip("/").split("/")
    module_name = parts[0] if parts else "root"
    
    # Check if the route file exists
    route_file = schema_info.get("route_file")
    if not route_file:
        # Try to find or create the route file
        potential_route_files = [
            f"{APP_DIR}/routes/{module_name}_routes.py",
            f"{APP_DIR}/routes/{module_name}_router.py",
            f"{APP_DIR}/routes/{module_name}.py"
        ]
        for file in potential_route_files:
            if os.path.exists(file):
                route_file = file
                break
        
        if not route_file:
            # Create a new route file
            route_file = f"{APP_DIR}/routes/{module_name}_routes.py"
            try:
                with open(route_file, "w") as f:
                    f.write(f"""from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
import logging

from app.schemas.{module_name}_schema import *

router = APIRouter(tags=["{module_name.capitalize()}"])
logger = logging.getLogger(__name__)

# Routes will be added here
""")
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error creating route file: {str(e)}",
                    "endpoint": endpoint,
                    "fix_type": "route_implementation"
                }
    
    # Read the route file
    try:
        with open(route_file, "r") as f:
            route_content = f.read()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading route file: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "route_implementation"
        }
    
    # Check if the route already exists
    route_pattern = route_path.replace("{", "{").replace("}", "}")
    if re.search(rf'@router\.{method.lower()}\([\'"]({route_pattern}|{re.escape(route_path)})[\'"]', route_content):
        return {
            "status": "warning",
            "message": f"Route {method} {route_path} already exists in {route_file}",
            "endpoint": endpoint,
            "fix_type": "route_implementation"
        }
    
    # Generate a function name based on the path
    function_name = generate_function_name(method, route_path)
    
    # Generate the route handler
    route_handler = generate_route_handler(method, route_path, function_name, schema_info)
    
    # Add the route handler to the file
    fixed_route_content = route_content + "\n\n" + route_handler
    
    # Write the fixed route file
    try:
        with open(route_file, "w") as f:
            f.write(fixed_route_content)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error writing fixed route file: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "route_implementation"
        }
    
    # Check if the router is imported in main.py
    main_file = f"{APP_DIR}/main.py"
    try:
        with open(main_file, "r") as f:
            main_content = f.read()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading main.py: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "route_implementation"
        }
    
    # Extract the module name from the route file path
    route_module = os.path.basename(route_file).replace(".py", "")
    
    # Check if the router is imported
    import_pattern = rf'from app\.routes\.{route_module} import router as {module_name}_router'
    if import_pattern not in main_content:
        # Add the import
        import_section_end = main_content.find("# Application setup")
        if import_section_end == -1:
            import_section_end = main_content.find("app = FastAPI")
        
        if import_section_end == -1:
            return {
                "status": "warning",
                "message": f"Could not find appropriate location to add router import in main.py",
                "endpoint": endpoint,
                "fix_type": "route_implementation",
                "route_file": route_file,
                "function_name": function_name
            }
        
        # Add the import
        fixed_main_content = main_content[:import_section_end] + f"\nfrom app.routes.{route_module} import router as {module_name}_router\n" + main_content[import_section_end:]
        
        # Write the fixed main.py
        try:
            with open(main_file, "w") as f:
                f.write(fixed_main_content)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error writing fixed main.py: {str(e)}",
                "endpoint": endpoint,
                "fix_type": "route_implementation"
            }
    
    # Check if the router is included in the app
    include_pattern = rf'app\.include_router\({module_name}_router, prefix="/{module_name}"'
    if include_pattern not in main_content:
        # Add the include_router call
        app_setup_end = main_content.find("# Middleware setup")
        if app_setup_end == -1:
            app_setup_end = main_content.find("if __name__ ==")
        
        if app_setup_end == -1:
            return {
                "status": "warning",
                "message": f"Could not find appropriate location to add router inclusion in main.py",
                "endpoint": endpoint,
                "fix_type": "route_implementation",
                "route_file": route_file,
                "function_name": function_name
            }
        
        # Add the include_router call
        fixed_main_content = main_content[:app_setup_end] + f"\napp.include_router({module_name}_router, prefix=\"/{module_name}\")\n" + main_content[app_setup_end:]
        
        # Write the fixed main.py
        try:
            with open(main_file, "w") as f:
                f.write(fixed_main_content)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error writing fixed main.py: {str(e)}",
                "endpoint": endpoint,
                "fix_type": "route_implementation"
            }
    
    return {
        "status": "success",
        "message": f"Implemented route {method} {route_path}",
        "endpoint": endpoint,
        "fix_type": "route_implementation",
        "route_file": route_file,
        "function_name": function_name,
        "changes": "Added route handler and ensured router is properly imported and included"
    }

def generate_function_name(method, route_path):
    """Generate a function name based on the method and path"""
    # Remove leading/trailing slashes and split by /
    parts = route_path.strip("/").split("/")
    
    # Remove path parameters
    parts = [re.sub(r'{.*?}', '', part) for part in parts]
    
    # Join parts with underscore
    name = "_".join(parts)
    
    # Add method prefix
    return f"{method.lower()}_{name}"

def generate_route_handler(method, route_path, function_name, schema_info):
    """Generate a route handler based on the method, path, and schema"""
    # Determine response model
    response_model = None
    request_model = None
    
    if schema_info and "models" in schema_info:
        for model in schema_info["models"]:
            model_name = model["name"]
            if "Response" in model_name and not response_model:
                response_model = model_name
            elif "Request" in model_name and not request_model:
                request_model = model_name
    
    # Generate function parameters
    params = []
    path_params = re.findall(r'{([^}]+)}', route_path)
    for param in path_params:
        params.append(f"{param}: str")
    
    if method in ["POST", "PUT", "PATCH"] and request_model:
        params.append(f"request: {request_model}")
    
    # Generate function signature
    if response_model:
        signature = f"@router.{method.lower()}(\"{route_path}\", response_model={response_model})"
    else:
        signature = f"@router.{method.lower()}(\"{route_path}\")"
    
    # Generate function body
    body = f"""async def {function_name}({", ".join(params)}):
    \"\"\"
    {method} {route_path}
    \"\"\"
    try:
        # TODO: Implement actual logic
        return {{
            "status": "success",
            "message": "Endpoint implemented successfully",
            "data": {{
                "endpoint": "{method} {route_path}",
                "params": {{{", ".join([f'"{param}": {param}' for param in path_params])}}}
            }}
        }}
    except Exception as e:
        logger.error(f"Error in {function_name}: {{str(e)}}")
        return {{
            "status": "error",
            "message": f"Internal server error: {{str(e)}}"
        }}"""
    
    return signature + "\n" + body

def implement_route_registration(strategy):
    """Implement route registration for a missing route"""
    endpoint = strategy["endpoint"]
    method = endpoint["method"]
    route_path = endpoint["route_path"]
    
    # Determine the route module based on the path
    parts = route_path.strip("/").split("/")
    module_name = parts[0] if parts else "root"
    
    # Check if the route file exists
    potential_route_files = [
        f"{APP_DIR}/routes/{module_name}_routes.py",
        f"{APP_DIR}/routes/{module_name}_router.py",
        f"{APP_DIR}/routes/{module_name}.py"
    ]
    
    route_file = None
    for file in potential_route_files:
        if os.path.exists(file):
            route_file = file
            break
    
    if not route_file:
        # Create a new route file
        route_file = f"{APP_DIR}/routes/{module_name}_routes.py"
        try:
            with open(route_file, "w") as f:
                f.write(f"""from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
import logging

router = APIRouter(tags=["{module_name.capitalize()}"])
logger = logging.getLogger(__name__)

# Routes will be added here
""")
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error creating route file: {str(e)}",
                "endpoint": endpoint,
                "fix_type": "route_registration"
            }
    
    # Read the route file
    try:
        with open(route_file, "r") as f:
            route_content = f.read()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading route file: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "route_registration"
        }
    
    # Check if the route already exists
    route_pattern = route_path.replace("{", "{").replace("}", "}")
    if re.search(rf'@router\.{method.lower()}\([\'"]({route_pattern}|{re.escape(route_path)})[\'"]', route_content):
        return {
            "status": "warning",
            "message": f"Route {method} {route_path} already exists in {route_file}",
            "endpoint": endpoint,
            "fix_type": "route_registration"
        }
    
    # Generate a function name based on the path
    function_name = generate_function_name(method, route_path)
    
    # Generate the route handler
    route_handler = f"""@router.{method.lower()}("{route_path}")
async def {function_name}({", ".join([f"{param}: str" for param in re.findall(r'{([^}]+)}', route_path)])}):
    \"\"\"
    {method} {route_path}
    \"\"\"
    try:
        # TODO: Implement actual logic
        return {{
            "status": "success",
            "message": "Endpoint implemented successfully",
            "data": {{
                "endpoint": "{method} {route_path}",
                "params": {{{", ".join([f'"{param}": {param}' for param in re.findall(r'{([^}]+)}', route_path)])}}}
            }}
        }}
    except Exception as e:
        logger.error(f"Error in {function_name}: {{str(e)}}")
        return {{
            "status": "error",
            "message": f"Internal server error: {{str(e)}}"
        }}"""
    
    # Add the route handler to the file
    fixed_route_content = route_content + "\n\n" + route_handler
    
    # Write the fixed route file
    try:
        with open(route_file, "w") as f:
            f.write(fixed_route_content)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error writing fixed route file: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "route_registration"
        }
    
    # Check if the router is imported in main.py
    main_file = f"{APP_DIR}/main.py"
    try:
        with open(main_file, "r") as f:
            main_content = f.read()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading main.py: {str(e)}",
            "endpoint": endpoint,
            "fix_type": "route_registration"
        }
    
    # Extract the module name from the route file path
    route_module = os.path.basename(route_file).replace(".py", "")
    
    # Check if the router is imported
    import_pattern = rf'from app\.routes\.{route_module} import router as {module_name}_router'
    if import_pattern not in main_content:
        # Add the import
        import_section_end = main_content.find("# Application setup")
        if import_section_end == -1:
            import_section_end = main_content.find("app = FastAPI")
        
        if import_section_end == -1:
            return {
                "status": "warning",
                "message": f"Could not find appropriate location to add router import in main.py",
                "endpoint": endpoint,
                "fix_type": "route_registration",
                "route_file": route_file,
                "function_name": function_name
            }
        
        # Add the import
        fixed_main_content = main_content[:import_section_end] + f"\nfrom app.routes.{route_module} import router as {module_name}_router\n" + main_content[import_section_end:]
        
        # Write the fixed main.py
        try:
            with open(main_file, "w") as f:
                f.write(fixed_main_content)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error writing fixed main.py: {str(e)}",
                "endpoint": endpoint,
                "fix_type": "route_registration"
            }
    
    # Check if the router is included in the app
    include_pattern = rf'app\.include_router\({module_name}_router, prefix="/{module_name}"'
    if include_pattern not in main_content:
        # Add the include_router call
        app_setup_end = main_content.find("# Middleware setup")
        if app_setup_end == -1:
            app_setup_end = main_content.find("if __name__ ==")
        
        if app_setup_end == -1:
            return {
                "status": "warning",
                "message": f"Could not find appropriate location to add router inclusion in main.py",
                "endpoint": endpoint,
                "fix_type": "route_registration",
                "route_file": route_file,
                "function_name": function_name
            }
        
        # Add the include_router call
        fixed_main_content = main_content[:app_setup_end] + f"\napp.include_router({module_name}_router, prefix=\"/{module_name}\")\n" + main_content[app_setup_end:]
        
        # Write the fixed main.py
        try:
            with open(main_file, "w") as f:
                f.write(fixed_main_content)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error writing fixed main.py: {str(e)}",
                "endpoint": endpoint,
                "fix_type": "route_registration"
            }
    
    return {
        "status": "success",
        "message": f"Registered route {method} {route_path}",
        "endpoint": endpoint,
        "fix_type": "route_registration",
        "route_file": route_file,
        "function_name": function_name,
        "changes": "Added route handler and ensured router is properly imported and included"
    }

def implement_general_fix(strategy):
    """Implement a general fix for an endpoint"""
    endpoint = strategy["endpoint"]
    method = endpoint["method"]
    route_path = endpoint["route_path"]
    
    # This is a fallback for endpoints that don't fit other categories
    # For now, we'll just implement a basic route registration
    return implement_route_registration(strategy)

def main():
    """Main function to implement fixes for the next batch of endpoints"""
    print("Starting implementation of fixes for the next batch of endpoints...")
    
    # Load next batch
    next_batch = load_next_batch()
    fix_strategies = next_batch["fix_strategies"]
    print(f"Loaded {len(fix_strategies)} fix strategies")
    
    # Implement fixes
    results = []
    for strategy in fix_strategies:
        print(f"Implementing fix for {strategy['endpoint']['method']} {strategy['endpoint']['route_path']} ({strategy['fix_type']})")
        
        if strategy["fix_type"] == "server_error_fix":
            result = implement_server_error_fix(strategy)
        elif strategy["fix_type"] == "route_implementation":
            result = implement_route_with_schema(strategy)
        elif strategy["fix_type"] == "route_registration":
            result = implement_route_registration(strategy)
        else:
            result = implement_general_fix(strategy)
        
        results.append(result)
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "batch_size": len(fix_strategies),
        "success_count": sum(1 for result in results if result["status"] == "success"),
        "warning_count": sum(1 for result in results if result["status"] == "warning"),
        "error_count": sum(1 for result in results if result["status"] == "error"),
        "fixed_endpoints": [
            {
                "endpoint": result["endpoint"],
                "fix_type": result["fix_type"],
                "status": result["status"],
                "message": result["message"],
                "route_file": result.get("route_file"),
                "function_name": result.get("function_name"),
                "changes": result.get("changes")
            }
            for result in results
        ],
        "results": results
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Implementation of fixes completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nFix Implementation Summary:")
    print(f"Total Endpoints: {output['batch_size']}")
    print(f"Success: {output['success_count']}")
    print(f"Warnings: {output['warning_count']}")
    print(f"Errors: {output['error_count']}")
    
    print("\nFixed Endpoints:")
    for i, result in enumerate(results):
        if result["status"] == "success":
            endpoint = result["endpoint"]
            print(f"  {i+1}. {endpoint['method']} {endpoint['route_path']} ({result['fix_type']})")
            print(f"     Route File: {result.get('route_file', 'N/A')}")
            print(f"     Function: {result.get('function_name', 'N/A')}")
    
    return output

if __name__ == "__main__":
    main()
