# UI Integration of Continuous Goal Loop with Interrupt & Feedback Control

This document provides an overview of the UI integration for the continuous goal loop with interrupt and feedback control features implemented in Day 4.3.

## Overview

The UI integration provides a visual interface for monitoring and controlling the AI agent system's goal execution loop. It consists of four main components:

1. **Goal Loop Visualization**: Displays active goals, subtasks, agent assignments, and task statuses in real-time
2. **Memory Viewer**: Allows filtering and viewing memory entries by goal ID, agent type, or timestamp
3. **Interrupt Control**: Provides controls for pausing execution, killing/restarting tasks, redirecting tasks, and editing prompts
4. **Status Feedback**: Shows live status indicators for each active agent

## Components

### Goal Loop Visualization

The Goal Loop Visualization component displays:
- Active goals with their descriptions and status
- Subtasks for each goal with assigned agents and status
- Timeline view showing progression from main goal → subtasks → completions

The component automatically refreshes every 5 seconds to show the latest state of goals and tasks.

### Memory Viewer

The Memory Viewer component allows:
- Filtering memory entries by goal ID, agent type, and timestamp range
- Viewing memory content with metadata (agent type, goal ID, tags)
- Scrollable panel for browsing through memory entries

### Interrupt Control

The Interrupt Control component provides:
- System execution mode controls (Auto, Manual, Pause All)
- Task-level controls for killing, restarting, or redirecting tasks
- Prompt editing capability in Manual Mode
- Real-time updates of task status

### Status Feedback

The Status Feedback component displays:
- Live status indicators for each active agent
- Current task information
- Error details and retry counts
- Performance metrics (tasks completed, average response time, success rate)

## API Endpoints

The UI components interact with the following API endpoints:

### Goals API
- `GET /api/goals`: Get all active goals with their subtasks
- `GET /api/task-state`: Get the current state of all tasks
- `POST /api/task-state/{task_id}/kill`: Kill a running task
- `POST /api/task-state/{task_id}/restart`: Restart a task

### Memory API
- `GET /api/memory`: Get memory entries with optional filtering by goal ID, agent type, and timestamp

### Control API
- `GET /api/system/control-mode`: Get the current system control mode and active agents
- `POST /api/system/control-mode`: Set the system control mode
- `GET /api/agent/status`: Get status of all active agents
- `POST /api/agent/delegate`: Delegate a task to a different agent
- `POST /api/agent/goal/{task_id}/edit-prompt`: Edit the prompt for a task (Manual Mode only)

## Usage Guide

### Monitoring Goals and Tasks

1. The Goal Loop Visualization panel shows all active goals and their subtasks
2. Each goal and task displays its current status with color indicators:
   - Green: In progress
   - Orange: Pending/Paused
   - Red: Failed/Error
   - Gray: Completed
3. The timeline view shows the progression of tasks over time

### Viewing Memory

1. Use the filters at the top of the Memory Viewer to narrow down memory entries:
   - Enter a Goal ID to see memories related to a specific goal
   - Select an Agent Type to see memories from a specific agent
   - Set date/time ranges to filter by timestamp
2. Click "Reset Filters" to clear all filters
3. Scroll through the memory entries to view content and metadata

### Controlling Execution

1. Use the execution mode buttons to control the overall system:
   - Auto Mode: System runs tasks automatically
   - Manual Mode: Enables prompt editing and manual control
   - Pause All: Pauses all execution
2. For individual tasks, use the task-level controls:
   - Kill/Restart: Stop or restart a specific task
   - Redirect: Change which agent handles a task
   - Edit Prompt (Manual Mode only): Modify the task prompt

### Monitoring Agent Status

1. The Status Feedback panel shows all active agents with their current status
2. For each agent, you can see:
   - Current task (if any)
   - Completion state
   - Error count and details (expandable)
   - Performance metrics (expandable)

## Implementation Notes

- The UI automatically refreshes at different intervals for different components:
  - Goal Loop Visualization: Every 5 seconds
  - Interrupt Control: Every 3 seconds
  - Status Feedback: Every 2 seconds
- The Memory Viewer refreshes when filters are changed
- All components handle loading states, error states, and empty states appropriately
