# Memory Query Console & Reflection Trace Viewer Documentation

## Overview

The Memory Query Console and Reflection Trace Viewer feature provides operators with deep introspection into Promethios' cognitive processes. This suite of components allows operators to query memory across time, agents, and projects, visualize the progression of loops, and examine reflections tied to specific loops.

## Components

### 1. MemoryQueryConsole

A searchable input panel that accepts natural language or schema filters to query memory.

**Features:**
- Natural language query support
- Schema-based filtering options
- Project-scoped queries
- Agent-specific filtering
- Time range selection
- Advanced query builder
- Query history tracking
- Export results functionality

**Usage:**
```jsx
<MemoryQueryConsole 
  projectId="project-123"
  initialQuery="Show all reflections from SAGE in the last week"
  onResultsChange={(results) => console.log('Results changed:', results)}
  onLoopSelect={(loopId) => console.log('Loop selected:', loopId)}
/>
```

**API Endpoints:**
- `/api/memory/query` - For executing memory queries
- `/api/memory/schema` - For retrieving memory schema information

### 2. LoopTraceViewer

A visual tree or timeline showing the progression of loops, including agent delegations, summaries, and reflections.

**Features:**
- Tree view of loop execution
- Timeline view alternative
- Expandable/collapsible nodes
- Node details in side drawer
- Agent color coding
- Node type indicators
- Zoom in/out functionality
- Export trace as JSON

**Usage:**
```jsx
<LoopTraceViewer 
  loopId="loop-123"
  projectId="project-456"
  onNodeSelect={(nodeId) => console.log('Node selected:', nodeId)}
/>
```

**API Endpoints:**
- `/api/loop/trace` - For retrieving loop trace data

### 3. ReflectionHistoryPanel

A side drawer or modal that displays all reflections tied to a given loop, with diff views between original plans and final reflections.

**Features:**
- Reflection list with filtering
- Reflection details view
- Diff view between original plans and reflections
- Summary tab with key metrics
- Timeline visualization of reflections
- Export functionality

**Usage:**
```jsx
<ReflectionHistoryPanel 
  loopId="loop-123"
  nodeId="node-456" // Optional, to filter reflections for a specific node
  inDrawer={true} // Optional, for when used inside a drawer
/>
```

**API Endpoints:**
- `/api/loop/reflections` - For retrieving reflection history data

## Integration

These components are integrated into the Promethios UI in the following zones:

- `MemoryQueryConsole` - MODAL zone, accessible via the "Memory Query" button in the bottom left corner
- `LoopTraceViewer` - CENTER zone, displayed in the main content area
- `ReflectionHistoryPanel` - MODAL zone, displayed when viewing reflection details

## Schema Contract

All memory objects adhere to the following schema:

```typescript
interface MemoryObject {
  project_id: string;
  loop_id: string;
  agent: string;
  timestamp: string;
  type: string;
  content: string;
  tags?: string[];
}
```

## Data Flow

1. User enters a query in the `MemoryQueryConsole`
2. Results are displayed in the console
3. User selects a loop from the results
4. `LoopTraceViewer` loads and displays the selected loop's trace
5. User selects a node in the trace
6. `ReflectionHistoryPanel` loads and displays reflections for the selected node

## Error Handling

All components include comprehensive error handling:

- API connection failures
- Invalid query syntax
- Missing data
- Schema validation errors
- Timeout handling

## Performance Considerations

- Pagination is implemented for large result sets
- Lazy loading of trace nodes
- Optimized rendering for complex visualizations
- Caching of frequently accessed data

## Accessibility

- All components are keyboard navigable
- Screen reader support
- High contrast mode compatibility
- Responsive design for all screen sizes

## Future Enhancements

- Vector-based semantic search capabilities
- Real-time updates for active loops
- Advanced filtering options
- Custom visualization layouts
- Integration with external analysis tools

## Troubleshooting

### Common Issues

1. **Query returns no results**
   - Check project_id is correct
   - Verify time range is appropriate
   - Ensure query syntax is valid

2. **Loop trace not loading**
   - Verify loop_id exists
   - Check network connection
   - Confirm API endpoints are accessible

3. **Reflection history empty**
   - Verify loop has reflections
   - Check permissions for accessing reflections
   - Ensure correct loop_id is provided

### Support

For additional support, contact the Promethios development team or refer to the internal documentation portal.
