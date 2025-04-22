# Loop Repair and Agent Auto-Rerouting Components

This documentation covers the Loop Repair and Agent Auto-Rerouting system for Promethios, a set of components that enable self-healing cognition through detection, repair, and logging of problematic loops.

## Table of Contents

1. [Overview](#overview)
2. [Component Architecture](#component-architecture)
3. [LoopRepairSuggestionPanel](#looprepairsuggestionpanel)
4. [AutoRerouter](#autorerouter)
5. [LoopRepairLog](#looprepairlog)
6. [API Endpoints](#api-endpoints)
7. [Integration Guide](#integration-guide)
8. [Usage Examples](#usage-examples)
9. [Performance Considerations](#performance-considerations)
10. [Accessibility Features](#accessibility-features)
11. [Troubleshooting](#troubleshooting)

## Overview

The Loop Repair and Agent Auto-Rerouting system provides Promethios with self-healing cognitive capabilities. It automatically detects problematic loops based on metrics like realism scores, drift scores, and failure states, then provides repair suggestions or automatically reroutes to alternative agents. The system maintains a comprehensive log of all repair activities for analysis and improvement.

### Key Features

- **Real-time Detection**: Monitors loop health metrics to identify issues as they occur
- **Repair Suggestions**: Provides actionable repair options for loops with issues
- **Automatic Rerouting**: Redirects tasks to alternative agents when thresholds are exceeded
- **Comprehensive Logging**: Maintains a detailed history of repairs and outcomes
- **Visual Analytics**: Offers timeline and table views of repair history with filtering

## Component Architecture

The system consists of three primary components:

1. **LoopRepairSuggestionPanel**: A UI component that renders when loops have issues, suggesting repair actions
2. **AutoRerouter**: A logic component that monitors metrics and automatically triggers agent re-delegation
3. **LoopRepairLog**: A UI component that displays the history of repairs and outcomes

These components are designed to work together but can also function independently. The LoopRepairSuggestionPanel and LoopRepairLog are React components, while the AutoRerouter is a JavaScript service with a React context provider wrapper for UI integration.

## LoopRepairSuggestionPanel

The LoopRepairSuggestionPanel is a React component that renders conditionally for loops with issues, providing repair suggestions and action buttons.

### When It Renders

The panel renders for any loop that meets one or more of these conditions:
- Low realism_score (< 0.5)
- High drift_score (> 0.7)
- Failed status
- Unresolved contradictions

### Features

- **Severity Indicators**: Color coding and badges indicate the severity of issues
- **Detailed Metrics**: Displays realism, drift, and trust scores with visual indicators
- **Failure Information**: Shows failure reasons and contradictions
- **Suggested Repairs**: Lists recommended repair actions with confidence scores
- **Action Buttons**: Provides one-click access to repair actions:
  - Replan: Triggers a replan of the loop with clearer requirements
  - Try with SAGE: Switches to the SAGE agent for better schema adherence
  - Reflect Again: Initiates additional reflection on requirements
  - Flag for Review: Marks the loop for operator review

### Props

| Prop | Type | Description |
|------|------|-------------|
| loopId | string | ID of the loop to analyze and potentially repair |
| onRepair | function | Callback function triggered when a repair action is taken |

### Example Usage

```jsx
import LoopRepairSuggestionPanel from './components/repair/LoopRepairSuggestionPanel';

// In your component
const handleRepair = (repairType, result) => {
  console.log(`Repair of type ${repairType} initiated for loop ${result.loop_id}`);
  // Handle the repair action
};

// In your render method
<LoopRepairSuggestionPanel 
  loopId="loop-123" 
  onRepair={handleRepair} 
/>
```

## AutoRerouter

The AutoRerouter is a JavaScript service that monitors loop scorecard values and automatically triggers re-delegation to secondary agents when certain conditions are met.

### Monitoring Conditions

The AutoRerouter monitors these metrics:
- trust_delta: When it falls below -0.5
- drift_score: When it exceeds 0.7
- agent failure count: When an agent has 3 or more recent failures

### Features

- **Continuous Monitoring**: Polls for recent loop scorecards at regular intervals
- **Agent Fallback Mapping**: Maintains a mapping of primary agents to their fallbacks
- **Automatic Rerouting**: Triggers rerouting when thresholds are exceeded
- **Manual Rerouting**: Provides an API for operator-initiated rerouting
- **Failure Tracking**: Tracks failure counts per agent
- **Notification System**: Alerts operators when rerouting occurs
- **Memory Integration**: Logs all rerouting decisions for future reference

### Agent Fallback Mapping

```javascript
const AGENT_FALLBACKS = {
  'ASH': 'SAGE',
  'NOVA': 'SAGE',
  'SKEPTIC': 'PHILOSOPHER',
  'HISTORIAN': 'LIBRARIAN',
  'DEFAULT': 'SAGE' // Default fallback
};
```

### React Integration

The AutoRerouter provides a React context provider for easy integration with the UI:

```jsx
import { AutoRouterProvider, useAutoRouter } from '../logic/AutoRerouter';

// Wrap your app with the provider
<AutoRouterProvider>
  <YourApp />
</AutoRouterProvider>

// Use the context in components
const MyComponent = () => {
  const autoRouter = useAutoRouter();
  
  // Access properties and methods
  const { reroutes, isMonitoring, agentFailureCounts } = autoRouter;
  
  // Trigger manual reroute
  const handleReroute = () => {
    autoRouter.manualReroute('loop-123', 'ASH', 'SAGE', 'Manual operator reroute');
  };
  
  // ...
};
```

### Standalone Usage

The AutoRerouter also provides standalone functions for use outside of React:

```javascript
import { checkNeedsReroute, getFallbackAgent } from '../logic/AutoRerouter';

// Check if a loop needs rerouting
const needsReroute = checkNeedsReroute(loopScorecard, agentFailureCounts);

// Get fallback agent for a given agent
const fallbackAgent = getFallbackAgent('ASH'); // Returns 'SAGE'
```

## LoopRepairLog

The LoopRepairLog is a React component that displays the history of failed loops, chosen repair paths, and outcomes of rerouted plans.

### Features

- **Dual Visualization**: Supports both timeline and table views
- **Advanced Filtering**: Filter by time period, agent, repair type, and outcome
- **Search Functionality**: Search across all repair records
- **Detailed Metrics**: Shows before/after metrics for repaired loops
- **Modal Details**: Click on any repair to see full details
- **Statistics Summary**: Displays counts of success, partial, failure, and pending repairs
- **Auto-Refresh**: Automatically refreshes data every 30 seconds

### Visualization Modes

1. **Timeline View**: Chronological display with color-coded nodes and expandable details
2. **Table View**: Tabular display with sortable columns and compact information

### Filtering Options

- **Time Range**: All time, past hour, past day, past week
- **Agent**: Filter by original or fallback agent
- **Repair Type**: Replan, agent switch, reflect, flag
- **Outcome**: Success, partial, failure, pending

### Example Usage

```jsx
import LoopRepairLog from './components/repair/LoopRepairLog';

// In your render method
<LoopRepairLog />
```

## API Endpoints

The Loop Repair and Auto-Rerouting system interacts with these API endpoints:

### Loop Details

```
GET /api/loop/details/:loopId
```

Returns details about a specific loop, including:
- Loop ID and title
- Status (completed, failed, etc.)
- Metrics (realism_score, drift_score, trust_score)
- Agent ID
- Failure reason (if applicable)
- Contradictions (if any)
- Suggested repairs

### Loop Repair

```
POST /api/loop/repair
```

Initiates a repair action for a loop.

**Request Body:**
```json
{
  "loop_id": "loop-123",
  "repair_type": "replan|agent_switch|reflect|flag",
  "agent_id": "SAGE" // Only for agent_switch
}
```

**Response:**
```json
{
  "success": true,
  "repair_id": "repair-456",
  "message": "Repair initiated successfully"
}
```

### Loop Reroute

```
POST /api/loop/reroute
```

Reroutes a loop to a different agent.

**Request Body:**
```json
{
  "loop_id": "loop-123",
  "original_agent": "ASH",
  "fallback_agent": "SAGE",
  "reason": "Agent has 3 recent failures",
  "manual": false
}
```

**Response:**
```json
{
  "success": true,
  "reroute_id": "reroute-789",
  "message": "Loop rerouted successfully"
}
```

### Recent Reroutes

```
GET /api/loop/reroutes
```

Returns a list of recent reroutes.

### Recent Scorecards

```
GET /api/loop/scorecards/recent
```

Returns recent loop scorecards for monitoring.

### Repair History

```
GET /api/loop/repairs
```

Returns the repair history with optional filters:
- time_range: hour, day, week, all
- agent: Filter by agent ID
- repair_type: replan, agent_switch, reflect, flag
- outcome: success, partial, failure, pending
- query: Search term

## Integration Guide

### Dashboard Integration

The Loop Repair components are integrated into the dashboard layout as follows:

1. **LoopRepairSuggestionPanel**: Added to the CENTER zone in UIZoneSchema.json
2. **LoopRepairLog**: Added to the MODAL zone in UIZoneSchema.json
3. **AutoRerouter**: Wrapped around the entire application in DashboardLayout.jsx

The LoopRepairLog is accessible via a "Repair Log" button in the bottom-right corner of the dashboard.

### Adding to a New Project

1. Copy the components from the `components/repair` directory
2. Copy the AutoRerouter.js file from the `logic` directory
3. Update your UI schema to include the components
4. Wrap your application with the AutoRouterProvider
5. Add a button to access the LoopRepairLog modal

## Usage Examples

### Basic Integration

```jsx
import React from 'react';
import { AutoRouterProvider } from './logic/AutoRerouter';
import LoopRepairSuggestionPanel from './components/repair/LoopRepairSuggestionPanel';
import LoopRepairLog from './components/repair/LoopRepairLog';

const App = () => {
  const [activeModal, setActiveModal] = useState(null);
  const [currentLoopId, setCurrentLoopId] = useState('loop-123');
  
  const handleRepair = (repairType, result) => {
    console.log(`Repair of type ${repairType} initiated for loop ${result.loop_id}`);
    // Handle the repair action
  };
  
  return (
    <AutoRouterProvider>
      <div>
        {/* Main content */}
        <LoopRepairSuggestionPanel 
          loopId={currentLoopId} 
          onRepair={handleRepair} 
        />
        
        {/* Button to open repair log */}
        <button onClick={() => setActiveModal('repairLog')}>
          View Repair Log
        </button>
        
        {/* Modal for repair log */}
        {activeModal === 'repairLog' && (
          <div className="modal">
            <LoopRepairLog />
            <button onClick={() => setActiveModal(null)}>Close</button>
          </div>
        )}
      </div>
    </AutoRouterProvider>
  );
};
```

### Advanced Usage: Custom Thresholds

```jsx
import React from 'react';
import { AutoRouterProvider } from './logic/AutoRerouter';

// Create a custom version with different thresholds
const CustomAutoRouterProvider = ({ children }) => {
  // Override default thresholds
  const customThresholds = {
    trustDelta: -0.3,      // More sensitive than default -0.5
    driftScore: 0.6,       // More sensitive than default 0.7
    failureCount: 2        // More sensitive than default 3
  };
  
  return (
    <AutoRouterProvider 
      overrideThresholds={customThresholds}
    >
      {children}
    </AutoRouterProvider>
  );
};

const App = () => {
  return (
    <CustomAutoRouterProvider>
      {/* Your app content */}
    </CustomAutoRouterProvider>
  );
};
```

## Performance Considerations

### LoopRepairSuggestionPanel

- Only renders when needed, minimizing performance impact
- Uses collapsible sections to reduce DOM elements when not expanded
- Implements conditional rendering for detailed sections

### AutoRerouter

- Uses a 10-second polling interval by default (configurable)
- Implements debouncing for failure count updates
- Avoids duplicate notifications within a 5-second window
- Can be disabled via the `toggleMonitoring` method when not needed

### LoopRepairLog

- Implements pagination for large datasets
- Uses virtualized lists for timeline view to handle thousands of entries
- Implements memoization for filtered data to avoid unnecessary re-renders
- Auto-refreshes every 30 seconds by default (configurable)

## Accessibility Features

All components follow WCAG 2.1 AA guidelines:

- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Reader Support**: Proper ARIA labels and roles for all components
- **Color Contrast**: Meets minimum contrast requirements
- **Focus Management**: Visible focus indicators and proper focus trapping in modals
- **Responsive Design**: Works across different screen sizes and zoom levels

## Troubleshooting

### Common Issues

#### LoopRepairSuggestionPanel Not Showing

If the panel isn't showing for a loop with issues:

1. Verify the loop metrics meet the threshold criteria
2. Check the console for API errors when fetching loop details
3. Ensure the component is properly registered in UIZoneSchema.json
4. Verify the loopId prop is being passed correctly

#### AutoRerouter Not Triggering

If automatic rerouting isn't happening:

1. Verify monitoring is enabled (`isMonitoring` should be true)
2. Check the console for API errors when fetching scorecards
3. Verify agent failure counts are being tracked correctly
4. Ensure the thresholds are appropriate for your use case

#### LoopRepairLog Empty or Not Updating

If the repair log is empty or not updating:

1. Check the console for API errors when fetching repair history
2. Verify filters aren't too restrictive
3. Try manually refreshing the data
4. Check that repairs are being logged to the API

### Support

For additional support, contact the Promethios development team or file an issue in the repository.
