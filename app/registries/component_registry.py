"""
Promethios Smart UI Component Registry

This module provides a centralized registry of UI components used by Promethios,
categorized by their cognitive system participation.

Components are verified based on actual usage and cognitive system participation,
not just file presence.
"""

# Component Registry with verified UI components
COMPONENT_REGISTRY = [
    {
        "name": "MemoryViewer",
        "path": "src/components/MemoryViewer.jsx",
        "type": "Cognitive",
        "status": "active",
        "linked_to": ["/api/memory"]
    },
    {
        "name": "MemoryBrowser",
        "path": "src/components/MemoryBrowser.jsx",
        "type": "Cognitive",
        "status": "active",
        "linked_to": ["/api/memory"]
    },
    {
        "name": "MemoryIndexService",
        "path": "src/components/MemoryIndexService.jsx",
        "type": "Cognitive",
        "status": "active",
        "linked_to": ["/api/memory"]
    },
    {
        "name": "MemoryUserScoping",
        "path": "src/components/MemoryUserScoping.jsx",
        "type": "Cognitive",
        "status": "active",
        "linked_to": ["/api/memory"]
    },
    {
        "name": "LoopStatusPanel",
        "path": "src/components/LoopStatusPanel.jsx",
        "type": "Cognitive",
        "status": "active",
        "linked_to": ["/api/project/state"]
    },
    {
        "name": "SystemIntegrityPanel",
        "path": "src/components/SystemIntegrityPanel.jsx",
        "type": "System",
        "status": "active",
        "linked_to": ["/api/system/health"]
    },
    {
        "name": "AgentManifestViewer",
        "path": "src/components/AgentManifestViewer.jsx",
        "type": "System",
        "status": "active",
        "linked_to": ["/api/system"]
    },
    {
        "name": "DashboardView",
        "path": "src/components/DashboardView.jsx",
        "type": "System",
        "status": "active",
        "linked_to": ["/api/system"]
    },
    {
        "name": "MainConsolePanel",
        "path": "src/components/MainConsolePanel.jsx",
        "type": "System",
        "status": "active",
        "linked_to": []
    },
    {
        "name": "FileTreePanel",
        "path": "src/components/FileTreePanel.jsx",
        "type": "System",
        "status": "active",
        "linked_to": []
    },
    {
        "name": "OverrideControls",
        "path": "src/components/OverrideControls.jsx",
        "type": "Cognitive",
        "status": "active",
        "linked_to": []
    },
    {
        "name": "AgentChatPanel",
        "path": "src/components/AgentChatPanel.jsx",
        "type": "Visual",
        "status": "active",
        "linked_to": []
    },
    {
        "name": "AgentActivityMap",
        "path": "src/components/AgentActivityMap.jsx",
        "type": "Visual",
        "status": "active",
        "linked_to": []
    },
    {
        "name": "AgentActivityPings",
        "path": "src/components/AgentActivityPings.jsx",
        "type": "Visual",
        "status": "active",
        "linked_to": []
    },
    {
        "name": "AgentDebugFeedback",
        "path": "src/components/AgentDebugFeedback.jsx",
        "type": "System",
        "status": "active",
        "linked_to": []
    }
]

# Component type counts
COMPONENT_TYPE_COUNTS = {
    "Cognitive": len([c for c in COMPONENT_REGISTRY if c["type"] == "Cognitive"]),
    "System": len([c for c in COMPONENT_REGISTRY if c["type"] == "System"]),
    "Visual": len([c for c in COMPONENT_REGISTRY if c["type"] == "Visual"])
}

# Helper function to get components by type
def get_components_by_type(component_type):
    """
    Get all components of a specific type.
    
    Args:
        component_type (str): Type of component to filter by ("Cognitive", "System", or "Visual")
        
    Returns:
        list: List of components matching the specified type
    """
    return [c for c in COMPONENT_REGISTRY if c["type"] == component_type]

# Helper function to get components by linked API
def get_components_by_api(api_path):
    """
    Get all components linked to a specific API path.
    
    Args:
        api_path (str): API path to filter by (e.g., "/api/memory")
        
    Returns:
        list: List of components linked to the specified API path
    """
    return [c for c in COMPONENT_REGISTRY if api_path in c.get("linked_to", [])]

# Registry metadata
REGISTRY_METADATA = {
    "total_components": len(COMPONENT_REGISTRY),
    "type_counts": COMPONENT_TYPE_COUNTS,
    "last_updated": "2025-04-26",
    "memory_tag": "component_registry_surface_verified_20250426"
}
