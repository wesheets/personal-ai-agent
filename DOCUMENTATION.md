# Ground Control Integration Documentation

## Overview

The Ground Control integration adds real-time system status monitoring and summary capabilities to the Promethios Playground UI. This enhancement provides users with immediate visibility into the current state of their projects, including agent activities, progress status, and a narrative summary of the project state.

## Components

### 1. SystemStatusPanel

The SystemStatusPanel component displays the current status of the system, including:

- Current project status (in progress, completed, error, blocked)
- List of agents involved in the project
- Latest agent action
- Next planned step
- Count of files created
- Blocking information (when applicable)

The panel automatically refreshes every 10 seconds to ensure the displayed information is current.

### 2. SystemSummaryPanel

The SystemSummaryPanel component displays a narrative summary of the project state, including:

- SAGE-generated summary of the current project state
- Timestamp of when the summary was last generated
- A manual refresh button to trigger summary regeneration

The panel automatically refreshes every 15 seconds to ensure the summary remains current.

## Implementation Details

### API Integration

Both panels communicate with backend API endpoints:

- `/api/system/status?project_id={projectId}` - Retrieves system status information
- `/api/system/summary?project_id={projectId}` - Retrieves the narrative summary
- `/api/system/summary` (POST) - Triggers generation of a new summary

### Styling

The components use a custom CSS file (`SystemPanels.css`) that defines styles for:

- Panel containers and headers
- Status indicators with appropriate colors
- Content layout and spacing
- Interactive elements like buttons
- Loading and error states

The styling follows the existing Promethios UI design language while providing clear visual hierarchy for the information displayed.

### Auto-Refresh Mechanism

Both panels implement auto-refresh using React's `useEffect` hook with `setInterval`:

```jsx
useEffect(() => {
  const fetchData = async () => {
    // Fetch data from API
  };

  fetchData();
  
  // Set up polling interval
  const intervalId = setInterval(fetchData, 10000); // Poll every 10 seconds
  
  // Clean up interval on component unmount
  return () => clearInterval(intervalId);
}, [projectId]);
```

This ensures that the displayed information stays current without requiring manual refreshes.

## Integration with Playground UI

The panels are integrated into the `ControlRoom` component, positioned between the header and the agent output cards:

```jsx
<main className="flex-1 flex flex-col overflow-y-auto p-6 space-y-6">
  <header>...</header>
  
  {/* Ground Control Integration - System Status and Summary Panels */}
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <SystemStatusPanel projectId={data.project_id} />
    <SystemSummaryPanel projectId={data.project_id} />
  </div>
  
  <section>
    {/* Agent output cards */}
  </section>
  
  <section>
    {/* Chat panel */}
  </section>
</main>
```

The responsive grid layout ensures that the panels display properly on different screen sizes.

## Error Handling

Both components implement comprehensive error handling:

1. API request failures are caught and displayed to the user
2. Loading states are shown during initial data fetching
3. Existing data is preserved during refresh operations
4. Components gracefully handle missing or incomplete data

## Testing

The implementation includes comprehensive tests:

1. Unit tests for individual panel components (`test_system_panels.js`)
2. Integration tests for the ControlRoom component (`test_control_room_integration.js`)

Tests cover loading states, successful data fetching, error handling, and refresh functionality.

## Usage

The Ground Control panels are automatically included in the Playground UI and require no additional configuration. They will display information for the current project as specified by the `projectId` prop.

To manually refresh the summary, users can click the "Refresh Summary" button in the System Summary panel.

## Future Enhancements

Potential future enhancements could include:

1. Detailed view of files created with links to view/edit
2. Historical view of agent actions with timeline
3. Filtering options for specific agent activities
4. Customizable refresh intervals
5. Export functionality for status reports

## Maintenance Considerations

When maintaining this code, consider:

1. API endpoint changes may require updates to the fetch calls
2. CSS changes should maintain consistency with the overall UI design
3. Performance optimizations may be needed if the amount of status data grows significantly
4. Additional error handling may be needed for specific edge cases
