# Left Panel Components Documentation

## Overview

This document provides detailed information about the left panel components in the Promethios UI. These components are designed to provide operators with critical system controls and information in a compact, accessible format.

## Components

### 1. OperatorHUDBar

**Purpose**: Displays operator information and system-wide controls in the left panel.

**Features**:
- Real-time operator status display (active, busy, away, offline)
- Alert count indicator with badge
- Quick access to settings and logout
- Connected to `/api/operator/status` endpoint

**API Integration**:
```javascript
// Fetch operator data from API
const { data: operatorData, error, loading } = useFetch('/api/operator/status', {}, {
  refreshInterval: 30000, // Refresh every 30 seconds
  initialData: {
    name: 'Operator',
    role: 'Admin',
    status: 'active',
    alerts: 0
  },
  transformResponse: (data) => ({
    name: data.name || 'Operator',
    role: data.role || 'Admin',
    status: data.status || 'active',
    alerts: data.alerts || 0
  })
});
```

**Error Handling**:
- Displays error indicator with tooltip when API fails
- Maintains last known state when connection is lost
- Shows loading spinner during data fetching

### 2. ProjectContextSwitcher

**Purpose**: Allows operators to switch between different project contexts.

**Features**:
- Project selection dropdown with dynamic options
- New project creation button
- Visual indication of current project context
- Connected to `/api/projects/list` endpoint

**API Integration**:
```javascript
// Fetch projects from API
const { 
  data: projectsData, 
  error, 
  loading, 
  refetch 
} = useFetch('/api/projects/list', {}, {
  initialData: {
    projects: [
      { id: 'promethios-core', name: 'Promethios Core' },
      { id: 'cognitive-stability', name: 'Cognitive Stability' },
      { id: 'loop-hardening', name: 'Loop Hardening' },
      { id: 'ui-integration', name: 'UI Integration' }
    ],
    activeProject: 'promethios-core'
  },
  transformResponse: (data) => ({
    projects: Array.isArray(data.projects) ? data.projects : [],
    activeProject: data.activeProject || ''
  })
});

// Update active project
const handleProjectChange = async (e) => {
  const newProjectId = e.target.value;
  setSelectedProject(newProjectId);
  
  try {
    // Call API to update active project
    const response = await fetch('/api/projects/set-active', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ projectId: newProjectId }),
    });
    
    // Handle response...
  } catch (err) {
    // Handle error...
  }
};
```

**Error Handling**:
- Displays error indicator with tooltip when API fails
- Shows toast notifications for successful/failed project changes
- Disables controls during loading states

### 3. OrchestratorModePanel

**Purpose**: Controls the orchestration mode of the Promethios system.

**Features**:
- Mode selection buttons with icons and tooltips
- Visual indication of current mode
- Mode description display
- Connected to `/api/system/orchestrator` endpoint

**Orchestrator Modes**:
1. **FAST** - Quick execution with minimal reflection and validation
2. **BALANCED** - Standard execution with normal reflection and validation
3. **THOROUGH** - Comprehensive execution with extensive reflection and validation
4. **RESEARCH** - Deep exploration mode with maximum reflection and validation

**API Integration**:
```javascript
// Fetch orchestrator mode from API
const { 
  data: orchestratorData, 
  error, 
  loading, 
  refetch 
} = useFetch('/api/system/orchestrator', {}, {
  refreshInterval: 15000, // Refresh every 15 seconds
  initialData: {
    mode: 'BALANCED',
    lastChanged: new Date().toISOString(),
    activeLoops: 0,
    stability: 0.95
  },
  transformResponse: (data) => ({
    mode: data.mode || 'BALANCED',
    lastChanged: data.lastChanged || new Date().toISOString(),
    activeLoops: data.activeLoops || 0,
    stability: data.stability || 0.95
  })
});

// Update orchestrator mode
const handleModeChange = async (mode) => {
  if (mode === activeMode) return;
  
  setIsChanging(true);
  
  try {
    // Call API to update orchestrator mode
    const response = await fetch('/api/system/orchestrator/set-mode', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mode }),
    });
    
    // Handle response...
  } catch (err) {
    // Handle error...
  } finally {
    setIsChanging(false);
  }
};
```

**Error Handling**:
- Displays error indicator with tooltip when API fails
- Shows loading state during mode changes
- Provides toast notifications for successful/failed mode changes

### 4. PermissionsManager

**Purpose**: Manages system permissions for the current project context.

**Features**:
- Expandable/collapsible permission list
- Toggle switches for enabling/disabling permissions
- Critical permission highlighting
- Connected to `/api/system/permissions` endpoint

**API Integration**:
```javascript
// Fetch permissions from API
const { 
  data: permissionsData, 
  error, 
  loading, 
  refetch 
} = useFetch('/api/system/permissions', {}, {
  refreshInterval: 30000, // Refresh every 30 seconds
  initialData: {
    permissions: [
      { id: 'memory_write', name: 'Memory Write', enabled: true, critical: true },
      { id: 'agent_execution', name: 'Agent Execution', enabled: true, critical: true },
      // Additional permissions...
    ],
    projectId: 'promethios-core',
    lastUpdated: new Date().toISOString()
  },
  transformResponse: (data) => ({
    permissions: Array.isArray(data.permissions) ? data.permissions : [],
    projectId: data.projectId || 'unknown',
    lastUpdated: data.lastUpdated || new Date().toISOString()
  })
});

// Toggle permission
const togglePermission = async (id) => {
  if (!permissionsData || !permissionsData.permissions) return;
  
  const permission = permissionsData.permissions.find(p => p.id === id);
  if (!permission) return;
  
  setUpdatingPermission(id);
  
  try {
    // Call API to update permission
    const response = await fetch('/api/system/permissions/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        permissionId: id, 
        enabled: !permission.enabled,
        projectId: permissionsData.projectId
      }),
    });
    
    // Handle response...
  } catch (err) {
    // Handle error...
  } finally {
    setUpdatingPermission(null);
  }
};
```

**Error Handling**:
- Displays error indicator with tooltip when API fails
- Shows spinner next to permission being updated
- Provides toast notifications for successful/failed permission changes

## Integration with Dashboard Layout

The left panel components are integrated into the dashboard layout using the UIZoneSchema.json configuration:

```json
{
  "zones": {
    "LEFT": [
      "OperatorHUDBar",
      "ProjectContextSwitcher",
      "OrchestratorModePanel",
      "AgentPanel",
      "PermissionsManager",
      "AgentChatConsole"
    ],
    // Other zones...
  }
}
```

The DashboardLayout.jsx component uses this schema to dynamically render components in their respective zones:

```javascript
<GridItem area="left" overflowY="auto" p={2} maxH="100vh">
  {UIZoneSchema.zones.LEFT.map((componentName) => (
    <Box key={componentName} mb={4}>
      {renderComponent(componentName)}
    </Box>
  ))}
</GridItem>
```

## Best Practices

When working with these components, follow these best practices:

1. **API Integration**:
   - Use the `useFetch` hook for all API calls
   - Provide fallback data for when API calls fail
   - Implement proper error handling and loading states

2. **UI Design**:
   - Follow Chakra UI design patterns
   - Ensure responsive behavior across different screen sizes
   - Provide visual feedback for all user actions

3. **Error Handling**:
   - Display error indicators with tooltips
   - Maintain last known state when connection is lost
   - Show loading spinners during data fetching

4. **Performance**:
   - Use appropriate refresh intervals for real-time data
   - Implement memoization to prevent unnecessary re-renders
   - Optimize component rendering for large datasets

## Future Enhancements

Planned enhancements for the left panel components:

1. **OperatorHUDBar**:
   - Add detailed alert dropdown
   - Implement operator profile modal
   - Add system health indicator

2. **ProjectContextSwitcher**:
   - Add project creation modal
   - Implement project search for large installations
   - Add project metadata display

3. **OrchestratorModePanel**:
   - Add custom mode configuration
   - Implement mode scheduling
   - Add historical mode performance metrics

4. **PermissionsManager**:
   - Add role-based permission templates
   - Implement permission audit log
   - Add permission dependency visualization

5. **AgentChatConsole** (to be implemented):
   - Direct communication with system agents
   - Command history and suggestions
   - Agent response visualization
