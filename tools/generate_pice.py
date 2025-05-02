# tools/generate_pice.py
import json
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_pice(permissions_path: str, output_path: str):
    """Generates the Platform Integration Component Encyclopedia (PICE) JSON file.
    
    Currently, it uses the tool_permissions.json as a source for known tools.
    This should be expanded later to include more sources (e.g., API specs, library scans).
    """
    pice_data = {"tools": {}}
    logger.info(f"Scanning for tools, starting with {permissions_path}...")

    try:
        with open(permissions_path, "r") as f:
            permissions_data = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Tool permissions file not found at {permissions_path}. PICE will be empty.")
        permissions_data = {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {permissions_path}. PICE generation might be incomplete.")
        permissions_data = {}

    # Extract unique tool names from permissions
    known_tools = set()
    if isinstance(permissions_data, dict) and "agent_permissions" in permissions_data:
        agent_perms_dict = permissions_data["agent_permissions"]
        if isinstance(agent_perms_dict, dict):
            for agent_permissions in agent_perms_dict.values():
                if isinstance(agent_permissions, list):
                    for tool_name in agent_permissions:
                        if isinstance(tool_name, str):
                            known_tools.add(tool_name)

    logger.info(f"Found {len(known_tools)} unique tool names from permissions file.")

    # Create basic entries for each known tool
    for tool_name in known_tools:
        pice_data["tools"][tool_name] = {
            "name": tool_name,
            "description": "Placeholder description - needs manual update or discovery.",
            "type": "ExternalTool", # Placeholder type
            "source": permissions_path, # Indicate where it was found
            "version": "N/A",
            "dependencies": [],
            "schemas": {
                "input": "N/A",
                "output": "N/A"
            }
            # Add more details later: endpoint, authentication, rate limits, etc.
        }
        logger.info(f"Added tool {tool_name} to PICE data.")

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write the PICE data to the specified JSON file
    try:
        with open(output_path, "w") as f:
            json.dump(pice_data, f, indent=4)
        logger.info(f"✅ PICE data successfully written to {output_path}")
    except IOError as e:
        logger.error(f"Failed to write PICE data to {output_path}: {e}")
    except TypeError as e:
        logger.error(f"Failed to serialize PICE data to JSON: {e}")

if __name__ == "__main__":
    # Determine the project root directory (assuming tools/ is one level down)
    project_root = Path(__file__).parent.parent
    default_permissions_path = project_root / "config" / "tool_permissions.json"
    default_output_path = project_root / "memory" / "platform_integration_component_encyclopedia.json"
    
    permissions_file = default_permissions_path
    output_file = default_output_path
    # Allow overriding paths via command-line arguments if needed later

    logger.info(f"Starting PICE generation. Permissions source: {permissions_file}, Output file: {output_file}")
    generate_pice(str(permissions_file), str(output_file))
    logger.info("PICE generation process finished.")
