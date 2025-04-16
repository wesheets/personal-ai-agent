# Agent Interaction UI - Implementation Documentation

## Overview

The Agent Interaction UI component provides a user interface for testing HAL and Ash personas via the streaming route. It allows users to select an agent, submit a task, and view the streaming response in real-time.

## Component Structure

The implementation consists of two main files:

1. **AgentTestPanel.jsx**: The core component that handles agent selection, task input, and streaming response display
2. **AgentListPage.jsx**: The page component that integrates the AgentTestPanel into the main application

## Features

### Agent Selection

- Fetches available agents from the `/api/agents` endpoint
- Displays agents in a dropdown with their icons and names
- Handles loading and error states gracefully
- Falls back to default agents if API fails

### Task Input Form

- Provides fields for:
  - Agent ID (dropdown selection)
  - Task Input (textarea)
  - Task ID (auto-generated with option to customize)
- Validates form inputs before submission
- Disables form during request processing

### Streaming Response Handling

- Connects to `/api/agent/delegate-stream` endpoint
- Processes streaming response using the Fetch API and ReadableStream
- Displays progress updates in real-time
- Parses and handles different response types (progress, success, error)

### Response Display

- Shows the agent's:
  - Name with icon
  - Tone (with color-coded badge)
  - Message (in a styled container)
  - Raw response (in a code block, expandable)
- Auto-scrolls to show latest content
- Provides visual feedback during loading

### Error Handling

- Validates form inputs
- Handles network errors
- Processes and displays server-side errors
- Shows user-friendly toast notifications

## Technical Implementation

### API Integration

The component interacts with two API endpoints:

1. **GET /api/agents**

   - Fetches the list of available agents on component mount
   - Used to populate the agent selection dropdown
   - Includes fallback for API failures

2. **POST /api/agent/delegate-stream**
   - Streaming endpoint that processes agent requests
   - Request format:
     ```json
     {
       "agent_id": "hal9000",
       "task": {
         "task_id": "demo-001",
         "task_type": "text",
         "input": "Say hello"
       }
     }
     ```
   - Handles streaming response with progress updates

### Streaming Implementation

The component uses the Fetch API's streaming capabilities:

```javascript
const response = await fetch('/api/agent/delegate-stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(requestBody)
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

let done = false;
while (!done) {
  const { value, done: readerDone } = await reader.read();
  done = readerDone;

  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n').filter((line) => line.trim());

  for (const line of lines) {
    const data = JSON.parse(line);
    // Process different response types
  }
}
```

### UI Framework

The component is built using:

- React for component structure and state management
- Chakra UI for styling and UI components
- React hooks for state and side effects

## Usage

Users can access the Agent Interaction UI by navigating to the `/agents` route in the application. The interface allows them to:

1. Select an agent from the dropdown
2. Enter a task prompt
3. Submit the request
4. View the streaming response in real-time
5. See the final response with agent details

## Future Enhancements

Potential improvements for future iterations:

1. **History**: Add a history of previous interactions
2. **Comparison View**: Allow side-by-side comparison of different agents
3. **Custom Parameters**: Support for additional task parameters
4. **Response Visualization**: Enhanced visualization of streaming progress
5. **Export/Share**: Ability to export or share interaction results

## Conclusion

The Agent Interaction UI component provides a user-friendly interface for testing and comparing HAL and Ash personas. It leverages the streaming endpoint to provide real-time feedback and a comprehensive view of agent responses.
