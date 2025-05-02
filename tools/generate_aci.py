# tools/generate_aci.py
import json
import logging
import os
import sys
import re # Import re for parsing error messages
from pathlib import Path

# Ensure the app directory is in the Python path
sys.path.append(str(Path(__file__).parent.parent))

# --- Import Agent Modules to Trigger Registration --- 
# This ensures the @register decorators run and populate the registry
# before the script accesses it.
print("Importing agent modules for registration...")
missing_capabilities = set()
agent_import_errors = {}

agent_modules = [
    "app.agents.forge_agent",
    "app.agents.orchestrator_agent",
    "app.agents.hal_agent",
    "app.agents.nova_agent",
    "app.agents.critic_agent",
    "app.agents.sage_agent"
]

for module_name in agent_modules:
    agent_key = module_name.split('.')[-1]
    try:
        __import__(module_name)
        print(f"✅ Imported {agent_key}")
    except ImportError as e:
        err_msg = f"Failed to import {agent_key} (ImportError): {e}"
        print(f"⚠️ {err_msg}")
        agent_import_errors[agent_key] = err_msg
    except AttributeError as e:
        # Check if it's the expected enum error
        error_str = str(e)
        # Use regex to find potential missing capability (assuming format like "AttributeError: FOO")
        match = re.search(r"AttributeError: ([A-Z_]+)$", error_str)
        if match:
            missing_name = match.group(1)
            missing_capabilities.add(missing_name)
            err_msg = f"Failed to import {agent_key} due to missing capability: {missing_name}"
            print(f"⚠️ {err_msg}")
            # Store specific capability error, but allow script to continue
            if agent_key not in agent_import_errors:
                 agent_import_errors[agent_key] = []
            if isinstance(agent_import_errors[agent_key], list):
                 agent_import_errors[agent_key].append(err_msg)
        else:
            err_msg = f"Failed to import {agent_key} (AttributeError): {e}"
            print(f"⚠️ {err_msg}")
            agent_import_errors[agent_key] = err_msg # Overwrite if a non-capability error occurs
    except Exception as e:
        err_msg = f"Failed to import {agent_key} (Other Exception): {type(e).__name__}: {e}"
        print(f"⚠️ {err_msg}")
        agent_import_errors[agent_key] = err_msg

print("Finished importing agent modules.")

# Print summary of missing capabilities found during imports
if missing_capabilities:
    print("\n--- Discovered Missing Agent Capabilities During Import --- ")
    for cap in sorted(list(missing_capabilities)):
        print(f"- {cap}")
    print("--------------------------------------------------------\n")
# --- End Agent Module Imports --- 

# Import necessary components after attempting agent imports
try:
    from app.core.agent_registry import AGENT_REGISTRY
    from app.core.agent_types import AgentCapability
except Exception as e:
    print(f"FATAL: Could not import core components (AGENT_REGISTRY, AgentCapability): {e}")
    sys.exit(1) # Cannot proceed without these

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_schema_path(schema_obj):
    """Helper function to safely get the full path of a schema object."""
    if schema_obj and hasattr(schema_obj, '__module__') and hasattr(schema_obj, '__name__'):
        module_parts = schema_obj.__module__.split('.')
        if module_parts[0] == 'app':
             return f"{schema_obj.__module__}.{schema_obj.__name__}"
        else:
            logger.warning(f"Schema module '{schema_obj.__module__}' not directly under 'app'. Path might be incorrect.")
            return f"{schema_obj.__module__}.{schema_obj.__name__}"
    return "N/A"

def generate_aci(output_path: str):
    """Generates the Agent Cognitive Infrastructure (ACI) JSON file."""
    aci_data = {"agents": {}}
    logger.info(f"Scanning AGENT_REGISTRY for agents...")

    if not AGENT_REGISTRY:
        logger.warning("AGENT_REGISTRY is empty. No agents to add to ACI. Check import errors above.")
    else:
        logger.info(f"Found {len(AGENT_REGISTRY)} potential agent registrations.")
        for agent_key, agent_info in AGENT_REGISTRY.items():
            logger.info(f"Processing agent registration: {agent_key}")
            try:
                if not isinstance(agent_info, dict):
                    logger.warning(f"Skipping agent {agent_key}: Registration data is not a dictionary.")
                    continue
                
                if 'class' not in agent_info or not agent_info['class']:
                    logger.warning(f"Skipping agent {agent_key}: Missing or invalid 'class' in registration data.")
                    continue

                agent_class = agent_info['class']
                agent_name = agent_info.get('name', 'Unknown Name')
                agent_description = agent_info.get('description', 'No description provided.')
                
                input_schema = getattr(agent_class, 'input_schema', None)
                output_schema = getattr(agent_class, 'output_schema', None)

                input_schema_path = get_schema_path(input_schema)
                output_schema_path = get_schema_path(output_schema)

                capabilities_raw = agent_info.get('capabilities', [])
                capabilities = []
                if isinstance(capabilities_raw, list):
                    for cap in capabilities_raw:
                        if isinstance(cap, AgentCapability):
                            capabilities.append(cap.name)
                        elif isinstance(cap, str):
                             capabilities.append(cap) 
                        # Check if it's a missing capability identified earlier
                        elif isinstance(cap, str) and cap in missing_capabilities:
                             capabilities.append(f"MISSING_ENUM: {cap}") # Mark as missing
                             logger.warning(f"Agent {agent_key} references missing capability '{cap}' in its registration.")
                        else:
                            logger.warning(f"Invalid capability type for agent {agent_key}: {type(cap)}")
                else:
                     logger.warning(f"Capabilities for agent {agent_key} is not a list.")

                class_path = f"{agent_class.__module__}.{agent_class.__name__}"

                aci_data["agents"][agent_key] = {
                    "key": agent_key,
                    "name": agent_name,
                    "class_path": class_path,
                    "description": agent_description,
                    "capabilities": capabilities,
                    "input_schema_path": input_schema_path,
                    "output_schema_path": output_schema_path,
                }
                logger.info(f"Successfully added {agent_name} ({agent_key}) to ACI data.")

            except Exception as e:
                logger.error(f"Error processing agent {agent_key}: {e}", exc_info=True)

    # Add import errors to the ACI data for visibility
    if agent_import_errors:
        aci_data['import_errors'] = agent_import_errors

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, 'w') as f:
            json.dump(aci_data, f, indent=4)
        logger.info(f"✅ ACI data successfully written to {output_path}")
    except IOError as e:
        logger.error(f"Failed to write ACI data to {output_path}: {e}")
    except TypeError as e:
        logger.error(f"Failed to serialize ACI data to JSON: {e}")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    default_output = project_root / "memory" / "agent_cognitive_infrastructure.json"
    
    output_file_path = default_output
    logger.info(f"Starting ACI generation (Discovery Mode). Output file: {output_file_path}")
    generate_aci(str(output_file_path))
    logger.info("ACI generation process finished.")

