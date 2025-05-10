"""
Legacy compatibility shim: redirects to /app/loop_controller.py.
Used for phases prior to 29 that import from controllers.loop_controller.
"""

from ..loop_controller import *
