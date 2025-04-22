# RIGHT Zone Components Documentation

This document provides an overview of the RIGHT zone components for the Promethios UI, including the RightPanelContainer and all individual components that are mounted inside it.

## RightPanelContainer

The RightPanelContainer is the main container component that houses all diagnostic tools in a tabbed interface. It allows operators to switch between different views: Files, System, Trust, Logs, and Metrics.

### Features
- Tabbed interface with icon and text labels
- Project-aware via projectId state
- Responsive design for both desktop and mobile
- Error handling and loading states
- Tooltips for tab descriptions

### API Integration
The RightPanelContainer fetches the current project context from:
```
/api/projects/active
```

## Individual Components

### FileTreePanel
Displays a hierarchical file tree for the current project with expandable folders and file size information.

**API Endpoint:**
```
/api/files/tree?projectId={projectId}
```

**Features:**
- Expandable folder structure
- File size formatting
- Folder/file icons
- Hover effects for better UX

### SystemHealthPanel
Displays system health metrics including CPU, memory, network, and service status.

**API Endpoint:**
```
/api/system/health?projectId={projectId}
```

**Features:**
- Resource usage visualization (CPU, memory, disk, network)
- Service status with uptime information
- System alerts with severity indicators
- Color-coded status indicators

### RebuildStatusDisplay
Displays the status of system rebuilds and cognitive restructuring processes.

**API Endpoint:**
```
/api/rebuild/status?projectId={projectId}
```

**Features:**
- Active rebuild progress tracking
- Recent rebuilds history
- Rebuild schedule information
- Manual rebuild trigger

### TrustScoreDisplay
Displays trust scores and reliability metrics for the cognitive system.

**API Endpoint:**
```
/api/trust/scores?projectId={projectId}
```

**Features:**
- Overall trust score visualization
- Trust categories breakdown
- Recent trust-related events
- Trend indicators for each metric

### LoopDriftIndex
Displays cognitive loop drift metrics and anomalies.

**API Endpoint:**
```
/api/loop/drift?projectId={projectId}
```

**Features:**
- Overall drift index visualization
- Drift metrics table with thresholds
- Detected anomalies with severity indicators
- Historical drift visualization

### AuditLogViewer
Displays system audit logs with filtering and search capabilities.

**API Endpoint:**
```
/api/audit/logs?projectId={projectId}
```

**Features:**
- Log search functionality
- Filtering by log type and severity
- Color-coded severity indicators
- Log export functionality
- Pagination information

### MetricsVisualization
Displays system performance metrics and visualizations.

**API Endpoint:**
```
/api/metrics?projectId={projectId}&timeRange={timeRange}&type={metricType}
```

**Features:**
- Performance, cognitive, and operational metrics
- Time range selection
- Bar chart visualizations for trends
- Metrics export functionality
- Trend indicators for each metric

## Integration

The RIGHT zone components are integrated into the Promethios UI through the UIZoneSchema.json configuration. The RightPanelContainer is the only component directly referenced in the schema, and it dynamically loads the individual components based on the selected tab.

### Schema Configuration
```json
{
  "zones": {
    "RIGHT": [
      "RightPanelContainer"
    ]
  }
}
```

### Component Dependencies
All components depend on the following shared utilities:
- useFetch hook for API integration
- Chakra UI for styling and components
- React Icons for iconography

## Best Practices
- All components should use the useFetch hook for API integration
- Include proper error handling and loading states
- Make components project-aware via projectId parameter
- Follow schema compliance as specified in the requirements
- Use Chakra UI components for consistent styling
- Implement responsive design for both desktop and mobile
