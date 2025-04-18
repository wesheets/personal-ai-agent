"""
AGENT_RUNNERS Restoration Documentation

This document explains the restoration of the AGENT_RUNNERS mapping in agent_runner.py.

## Problem

The app/modules/agent_runner.py file was missing the AGENT_RUNNERS object or had a broken export,
which is essential for direct agent execution through the agent registry system.

## Solution

We implemented the following changes:

1. **Added Missing Imports**: Added imports for all agent runner functions from app.agents:
   - run_hal_agent (imported as hal_agent_import to avoid conflicts)
   - run_nova_agent
   - run_ash_agent
   - run_critic_agent
   - run_orchestrator_agent
   - run_sage_agent

2. **Restored AGENT_RUNNERS Mapping**: Added the AGENT_RUNNERS dictionary at the bottom of the file
   with mappings for all six agents:
   ```python
   AGENT_RUNNERS = {
       "hal": run_hal_agent,
       "nova": run_nova_agent,
       "ash": run_ash_agent,
       "critic": run_critic_agent,
       "orchestrator": run_orchestrator_agent,
       "sage": run_sage_agent,
   }
   ```

## Implementation Details

The implementation ensures that:
- The locally defined run_hal_agent function is used in the AGENT_RUNNERS mapping
- All other agent functions are imported from their respective modules
- The AGENT_RUNNERS mapping is placed at the bottom of the file for easy access
- The format matches the required specification exactly

## Testing

The changes have been tested to ensure:
- The file syntax is valid Python
- All required imports are present
- The AGENT_RUNNERS mapping includes all six required agents
- The mapping uses the correct function references

## Future Improvements

For future improvements, consider:
1. Adding type hints to the AGENT_RUNNERS mapping
2. Adding docstrings to explain the purpose of the AGENT_RUNNERS object
3. Implementing a more robust import system with fallbacks
4. Adding unit tests for the agent runner functions
"""
