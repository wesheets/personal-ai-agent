"""
Promethios Registry Package
This package contains registries for modules, endpoints, and schemas in the Promethios system.
"""
from .module_registry import MODULE_REGISTRY, MODULE_LIST
from .endpoint_registry import ENDPOINT_REGISTRY, ENDPOINT_LIST
from .schema_registry import SCHEMA_REGISTRY, SCHEMA_LIST

from .registry_utils import find_module, find_modules_by_category, find_endpoint, find_endpoints_by_module, find_schema, find_schemas_by_module, get_system_stats

__all__ = [
    "MODULE_REGISTRY", "MODULE_LIST",
    "ENDPOINT_REGISTRY", "ENDPOINT_LIST",
    "SCHEMA_REGISTRY", "SCHEMA_LIST"

    "find_module", "find_modules_by_category", "find_endpoint", "find_endpoints_by_module", "find_schema", "find_schemas_by_module", "get_system_stats",]
