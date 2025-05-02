# app/registries/toolkit_registry.py

TOOLKIT_REGISTRY = {
    "trace_reader": {
        "path": "app/modules/trace_reader.py",
        "enabled": True,
        "schema": "trace_reader.schema.json"
    },
    "trace_summarizer": {
        "path": "app/modules/trace_summarizer.py",
        "enabled": True,
        "schema": None
    },
    "loop_controller": {
        "path": "app/core/loop_controller.py",
        "enabled": True
    }
}
