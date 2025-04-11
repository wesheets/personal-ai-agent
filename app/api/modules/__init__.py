"""
Initialize the API modules package.

This file ensures that the API modules package is properly initialized
and can be imported from other parts of the application.
"""

# Explicitly import modules to ensure they are loaded
try:
    from . import memory
    from . import delegate
    from . import stream
    from . import train
    from . import system
    from . import observer
    from . import agent_context
    from . import plan
    print("✅ All API modules pre-loaded in __init__.py")
except Exception as e:
    import traceback
    print(f"⚠️ Error pre-loading modules in __init__.py: {str(e)}")
    traceback.print_exc()
