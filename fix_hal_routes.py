"""
Helper script to modify main.py to add HAL routes loader fallback
"""
import re

def add_hal_routes_loader_fallback(main_py_path):
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    # Pattern to match the HAL routes section
    pattern = r'(# Include HAL routes with priority \(first\)\nif hal_routes_loaded:.*?loaded_routes\.append\("hal_routes"\))'
    
    # Replacement with fallback mechanism
    replacement = r'\1\n# Use HAL routes loader if available (fallback mechanism)\nelif hal_routes_loader_available:\n    loaded_routes = register_hal_routes(app, loaded_routes)\n    print("✅ Included HAL routes via loader")'
    
    # Replace all occurrences
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(main_py_path, 'w') as f:
        f.write(modified_content)
    
    print("✅ Added HAL routes loader fallback to main.py")

if __name__ == "__main__":
    add_hal_routes_loader_fallback("/home/ubuntu/personal-ai-agent/app/main.py")
