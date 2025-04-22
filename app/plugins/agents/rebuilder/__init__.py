"""Plugin module for rebuilder agent.

This module provides the Rebuilder Agent functionality for Promethios,
which automatically detects degradation or drift and coordinates scoped rebuilds.
"""

from app.plugins.agents.rebuilder.rebuilder import run_agent

__all__ = ["run_agent"]
