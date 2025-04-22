# Project Timeline + Loop Fork Viewer Documentation

This documentation provides comprehensive information about the Project Timeline and Loop Fork Viewer components implemented for Promethios. These components give the Operator a narrative understanding of project cognition, complete with belief changes, loop forks, and drift detection.

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
   - [ProjectTimelineViewer](#projecttimelineviewer)
   - [LoopForkMap](#loopforkmap)
   - [BeliefChangeLog](#beliefchangelog)
3. [Integration](#integration)
4. [API Endpoints](#api-endpoints)
5. [Schema Contracts](#schema-contracts)
6. [Usage Examples](#usage-examples)
7. [Performance Considerations](#performance-considerations)
8. [Accessibility Features](#accessibility-features)
9. [Troubleshooting](#troubleshooting)

## Overview

The Project Timeline + Loop Fork Viewer components provide a comprehensive visualization of cognitive evolution within Promethios. These components allow Operators to:

- View the progression of loops over time with a clear timeline
- Visualize where loops diverged and which forks were explored
- Track belief changes and their evolution throughout a project
- Understand trust scores and drift indices at each stage
- Navigate between related components for deeper exploration

Together, these components transform the understanding of cognition from isolated moments to a continuous narrative, enabling Operators to see how projects evolve and where key decision points occurred.

## Components

### ProjectTimelineViewer

The ProjectTimelineViewer displays a chronological view of loops within a project, showing their progression, agents involved, and key metrics.

#### Features

- **Dual-orientation Timeline**: Supports both vertical and horizontal timeline views
- **Loop Node Details**: Each node displays:
  - Loop ID
  - Agent(s) involved
  - Summary titles (first 10-15 words)
  - Trust score (color-coded)
  - Drift index (color-coded)
- **Fork Visualization**: Visual indicators for loop forks and branches
- **Filtering Capabilities**: Filter by time range, agent, and fork visibility
- **Interactive Navigation**: Click to open LoopTraceViewer or ReflectionHistoryPanel
- **Export Functionality**: Export timeline data as JSON

#### Props

| Prop | Type | Description |
|------|------|-------------|
| projectId | string | ID of the project to display timeline for |
| onLoopSelect | function | Callback function when a loop is selected |

#### Example

```jsx
<ProjectTimelineViewer 
  projectId="project-123" 
  onLoopSelect={(loopId) => console.log(`Selected loop: ${loopId}`)} 
/>
```

### LoopForkMap

The LoopForkMap provides a recursive tree/graph visualization showing where loops diverged, which forks were explored, skipped, or merged, and tracks drift scores over branches.

#### Features

- **Interactive Graph Visualization**: Using ReactFlow for an interactive graph experience
- **Fork Type Indicators**: Visual distinction between:
  - Active forks
  - Merged forks
  - Skipped forks
- **Layout Options**: Toggle between vertical (top-down) and horizontal (left-right) layouts
- **Filtering Capabilities**: Show/hide skipped and merged loops
- **Node Details**: Each node displays:
  - Loop ID
  - Agent
  - Summary
  - Trust score
  - Drift index
- **Interactive Navigation**: Click to open LoopTraceViewer
- **Export Functionality**: Export fork map data as JSON

#### Props

| Prop | Type | Description |
|------|------|-------------|
| projectId | string | ID of the project to display fork map for |
| onLoopSelect | function | Callback function when a loop is selected |

#### Example

```jsx
<LoopForkMap 
  projectId="project-123" 
  onLoopSelect={(loopId) => console.log(`Selected loop: ${loopId}`)} 
/>
```

### BeliefChangeLog

The BeliefChangeLog shows belief version diffs over time, tracking how beliefs evolve with information about authoring agents and change types.

#### Features

- **Belief Grouping**: Accordion view groups beliefs by ID for easy navigation
- **Change Type Indicators**: Visual distinction between:
  - Added beliefs (new)
  - Modified beliefs (updated)
  - Deprecated beliefs (removed)
- **Version History**: Complete history of each belief with timestamps and authoring agents
- **Diff Visualization**: Side-by-side or inline diff view showing specific changes between versions
- **Rollback Functionality**: Option to revert to previous versions of beliefs
- **Filtering Capabilities**: Filter by time range, agent, and change type
- **Export Functionality**: Export belief change data as JSON

#### Props

| Prop | Type | Description |
|------|------|-------------|
| projectId | string | ID of the project to display belief changes for |

#### Example

```jsx
<BeliefChangeLog projectId="project-123" />
```

## Integration

The components are integrated into the Promethios UI in the following zones:

- **ProjectTimelineViewer**: CENTER zone
- **LoopForkMap**: CENTER zone
- **BeliefChangeLog**: MODAL zone (accessible via a dedicated button)

The components are registered in the UIZoneSchema.json file and imported in the DashboardLayout.jsx file. The BeliefChangeLog is accessible through a dedicated "Belief Changes" button in the bottom-right corner of the dashboard.

## API Endpoints

The components interact with the following API endpoints:

### Project Timeline API

```
GET /api/project/timeline
```

**Parameters:**
- `project_id` (required): ID of the project
- `time_range` (optional): Filter by time range ('all', 'day', 'week', 'month')
- `agent` (optional): Filter by agent

**Response Schema:**
```json
{
  "project_id": "string",
  "loops": [
    {
      "loop_id": "string",
      "timestamp": "ISO8601",
      "agent": "string",
      "summary": "string",
      "trust_score": "float",
      "drift_index": "float",
      "fork_parent": "string | null"
    }
  ]
}
```

### Loop Fork API

```
GET /api/project/loop-forks
```

**Parameters:**
- `project_id` (required): ID of the project

**Response Schema:**
```json
{
  "project_id": "string",
  "loops": [
    {
      "loop_id": "string",
      "timestamp": "ISO8601",
      "agent": "string",
      "summary": "string",
      "trust_score": "float",
      "drift_index": "float",
      "fork_parent": "string | null",
      "is_skipped": "boolean",
      "is_merged": "boolean"
    }
  ]
}
```

### Belief Changes API

```
GET /api/project/belief-changes
```

**Parameters:**
- `project_id` (required): ID of the project
- `time_range` (optional): Filter by time range ('all', 'day', 'week', 'month')
- `agent` (optional): Filter by agent
- `change_type` (optional): Filter by change type ('all', 'added', 'modified', 'deprecated')

**Response Schema:**
```json
{
  "project_id": "string",
  "beliefs": [
    {
      "belief_id": "string",
      "timestamp": "ISO8601",
      "agent": "string",
      "change_type": "string",
      "content": "string",
      "version": "integer"
    }
  ]
}
```

## Schema Contracts

### Timeline Object Schema

```json
{
  "loop_id": "string",
  "timestamp": "ISO8601",
  "agent": "string",
  "summary": "string",
  "trust_score": "float",
  "drift_index": "float",
  "fork_parent": "string | null"
}
```

### Loop Fork Object Schema

```json
{
  "loop_id": "string",
  "timestamp": "ISO8601",
  "agent": "string",
  "summary": "string",
  "trust_score": "float",
  "drift_index": "float",
  "fork_parent": "string | null",
  "is_skipped": "boolean",
  "is_merged": "boolean"
}
```

### Belief Change Object Schema

```json
{
  "belief_id": "string",
  "timestamp": "ISO8601",
  "agent": "string",
  "change_type": "string",
  "content": "string",
  "version": "integer"
}
```

## Usage Examples

### Tracking Project Evolution

1. Open the ProjectTimelineViewer to see the chronological progression of loops
2. Identify key decision points where trust scores or drift indices change significantly
3. Click on specific loops to view their detailed trace
4. Use the time range filter to focus on recent developments

### Analyzing Loop Forks

1. Open the LoopForkMap to visualize the branching structure of loops
2. Identify where loops diverged into multiple paths
3. See which forks were explored, which were merged, and which were skipped
4. Toggle between vertical and horizontal layouts for different perspectives
5. Click on specific nodes to view their detailed trace

### Tracking Belief Changes

1. Click the "Belief Changes" button to open the BeliefChangeLog
2. Browse through beliefs grouped by ID
3. Expand a belief to see its version history
4. View diffs between versions to understand specific changes
5. Filter by agent or change type to focus on specific aspects
6. Use the rollback functionality to revert to previous versions if needed

## Performance Considerations

### ProjectTimelineViewer

- Implements virtualization for large timelines to maintain performance
- Uses pagination when fetching large datasets
- Optimizes rendering by only showing visible nodes
- Implements memoization to prevent unnecessary re-renders

### LoopForkMap

- Uses ReactFlow's built-in optimization for large graphs
- Implements node virtualization for complex fork structures
- Provides filtering options to reduce the number of displayed nodes
- Uses web workers for layout calculations with large datasets

### BeliefChangeLog

- Implements lazy loading for belief content
- Uses pagination for version histories
- Optimizes diff calculation to only run when needed
- Implements memoization for filtered results

## Accessibility Features

All components implement the following accessibility features:

- **Keyboard Navigation**: Full keyboard support for navigating timelines, graphs, and logs
- **Screen Reader Support**: ARIA labels and roles for all interactive elements
- **Focus Management**: Clear focus indicators and logical tab order
- **Color Contrast**: All color-coded elements meet WCAG AA standards
- **Responsive Design**: Components adapt to different screen sizes and orientations
- **Reduced Motion**: Respects user preferences for reduced motion
- **Text Scaling**: Supports browser text scaling without breaking layouts

## Troubleshooting

### Common Issues

#### Timeline Not Loading

- Check if the project ID is correct
- Verify API endpoint is accessible
- Check browser console for errors
- Try refreshing the timeline using the refresh button

#### Fork Map Layout Issues

- Try toggling between vertical and horizontal layouts
- Adjust zoom level using zoom controls
- Reset the view using the fit view button
- Check if there are too many nodes (try filtering)

#### Belief Changes Not Showing

- Verify project ID is correct
- Check if filters are too restrictive
- Try clearing all filters
- Verify API endpoint is accessible

### Error Handling

All components implement comprehensive error handling:

- Informative error messages with suggested actions
- Automatic retry mechanisms for transient failures
- Fallback UI states when data cannot be loaded
- Detailed logging to help with debugging

### Support

For additional support or to report issues:

- Check the Promethios documentation portal
- Contact the development team through the support channel
- File issues in the project repository with detailed reproduction steps
