# app/agents/__init__.py
import os
import importlib
import logging

logger = logging.getLogger(__name__)

# Automatically import all agent modules in this directory
# This ensures that the @register decorator in each agent file is executed.

AGENT_DIR = os.path.dirname(__file__)

for filename in os.listdir(AGENT_DIR):
    if filename.endswith(".py") and filename != "__init__.py" and not filename.startswith("base"):
        module_name = filename[:-3] # Remove .py extension
        try:
            # Construct the full module path relative to the 'app' package
            full_module_path = f"app.agents.{module_name}"
            # Import the module
            importlib.import_module(full_module_path)
            logger.debug(f"Successfully imported agent module: {full_module_path}")
        except ImportError as e:
            logger.error(f"Failed to import agent module {module_name}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while importing {module_name}: {e}")

# --- Explicit import for Belief Manager (Batch 21.5 Remediation) ---
# Ensure belief_manager_agent is loaded, as auto-import might have issues
try:
    importlib.import_module("app.agents.belief_manager_agent")
    logger.info("Explicitly imported belief_manager_agent.")
except ImportError as e:
    logger.error(f"Failed to explicitly import belief_manager_agent: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred during explicit import of belief_manager_agent: {e}")
# --- End Remediation ---

logger.info("Agent module auto-import process completed.")

