# tools/generate_aci.py
import json
import logging
import os
import sys
from pathlib import Path

# Ensure the app directory is in the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.agent_registry import AGENT_REGISTRY
from app.core.agent_types import AgentCapability

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_schema_path(schema_obj):
    """Helper function to safely get the full path of a schema object."""
    if schema_obj and hasattr(schema_obj, '__module__') and hasattr(schema_obj, '__name__'):
        # Attempt to construct path relative to 'app' assuming standard structure
        module_parts = schema_obj.__module__.split('.')
        if module_parts[0] == 'app':
             return f"{schema_obj.__module__}.{schema_obj.__name__}"
        else:
            # Fallback if module is not directly under 'app' (might need adjustment)
            logger.warning(f"Schema module '{schema_obj.__module__}' not directly under 'app'. Path might be incorrect.")
            return f"{schema_obj.__module__}.{schema_obj.__name__}"
    return "N/A"

def generate_aci(output_path: str):
    """Generates the Agent Cognitive Infrastructure (ACI) JSON file."""
    aci_data = {"agents": {}}
    logger.info(f"Scanning AGENT_REGISTRY for agents...")

    if not AGENT_REGISTRY:
        logger.warning("AGENT_REGISTRY is empty. No agents to add to ACI.")
    else:
        logger.info(f"Found {len(AGENT_REGISTRY)} potential agent registrations.")
        for agent_key, agent_info in AGENT_REGISTRY.items():
            logger.info(f"Processing agent registration: {agent_key}")
            try:
                # Validate the structure of agent_info
                if not isinstance(agent_info, dict):
                    logger.warning(f"Skipping agent {agent_key}: Registration data is not a dictionary.")
                    continue
                
                if 'class' not in agent_info or not agent_info['class']:
                    logger.warning(f"Skipping agent {agent_key}: Missing or invalid 'class' in registration data.")
                    continue

                agent_class = agent_info['class']
                agent_name = agent_info.get('name', 'Unknown Name')
                agent_description = agent_info.get('description', 'No description provided.')
                
                # Safely get schema objects from agent_info
                input_schema = agent_info.get('input_schema')
                output_schema = agent_info.get('output_schema')

                # Get schema paths using the helper function
                input_schema_path = get_schema_path(input_schema)
                output_schema_path = get_schema_path(output_schema)

                # Extract capabilities (assuming they are AgentCapability enums)
                capabilities_raw = agent_info.get('capabilities', [])
                capabilities = []
                if isinstance(capabilities_raw, list):
                    for cap in capabilities_raw:
                        if isinstance(cap, AgentCapability):
                            capabilities.append(cap.name)
                        elif isinstance(cap, str):
                             capabilities.append(cap) # Allow strings if needed
                        else:
                            logger.warning(f"Invalid capability type for agent {agent_key}: {type(cap)}")
                else:
                     logger.warning(f"Capabilities for agent {agent_key} is not a list.")

                # Construct class path
                class_path = f"{agent_class.__module__}.{agent_class.__name__}"

                aci_data["agents"][agent_key] = {
                    "key": agent_key,
                    "name": agent_name,
                    "class_path": class_path,
                    "description": agent_description,
                    "capabilities": capabilities,
                    "input_schema_path": input_schema_path,
                    "output_schema_path": output_schema_path,
                    # Add other relevant details later (e.g., version, dependencies)
                }
                logger.info(f"Successfully added {agent_name} ({agent_key}) to ACI data.")

            except Exception as e:
                # Log specific errors during processing of an agent
                logger.error(f"Error processing agent {agent_key}: {e}", exc_info=True)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write the ACI data to the specified JSON file
    try:
        with open(output_path, 'w') as f:
            json.dump(aci_data, f, indent=4)
        logger.info(f"✅ ACI data successfully written to {output_path}")
    except IOError as e:
        logger.error(f"Failed to write ACI data to {output_path}: {e}")
    except TypeError as e:
        logger.error(f"Failed to serialize ACI data to JSON: {e}")

if __name__ == "__main__":
    # Determine the project root directory (assuming tools/ is one level down)
    project_root = Path(__file__).parent.parent
    default_output = project_root / "memory" / "agent_cognitive_infrastructure.json"
    
    output_file_path = default_output
    # Allow overriding output path via command-line argument if needed later
    # if len(sys.argv) > 1:
    #     output_file_path = sys.argv[1]

    logger.info(f"Starting ACI generation. Output file: {output_file_path}")
    generate_aci(str(output_file_path))
    logger.info("ACI generation process finished.")
