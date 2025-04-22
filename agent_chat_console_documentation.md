# AgentChatConsole Documentation

## Overview

The AgentChatConsole is a fully conversational chat interface for Operator ↔ Agent interactions in the Promethios UI. It provides a project-scoped, memory-threaded chat experience powered by various agent endpoints.

## Components

### 1. AgentChatConsole.jsx

The main container component that displays the conversational message thread and manages the overall chat interface.

**Features:**
- Project-scoped conversations
- Auto-scrolling message thread
- Expandable/collapsible chat window
- Chat history export
- Empty state with suggested prompts
- Integration with ChatMemoryContext for state management

**Props:**
- `projectId` (string, optional): Project identifier, defaults to 'promethios-core'

### 2. MessageBubble.jsx

Displays individual messages in the chat interface with agent information, timestamps, and formatted content.

**Features:**
- Role-based styling (operator vs agent)
- Markdown support for message formatting
- Agent avatar and color coding
- Timestamp display
- Loop ID and tag badges
- Typing indicator support

**Props:**
- `agent` (string): Agent identifier
- `role` (string): Message role ('operator', 'agent', or 'typing')
- `message` (string): Message content (supports markdown)
- `timestamp` (string): ISO timestamp
- `loop_id` (string): Associated loop ID
- `tags` (array, optional): Memory tags

### 3. ChatInputBar.jsx

Input field for sending messages with agent selection capabilities.

**Features:**
- Agent selection dropdown
- Text input with auto-resize
- @ mention syntax for quick agent switching
- Keyboard shortcuts (Ctrl+Enter to send)
- Loading state during message submission
- Clear input button
- Typing hints

### 4. ChatMemoryContext.jsx

Context provider for managing message history and project scoping.

**Features:**
- Local storage persistence
- API integration with /memory/write
- Project context switching
- Message addition and clearing
- Error handling and loading states

**Context API:**
- `messages` (array): Current message history
- `addMessage` (function): Add a new message
- `clearMessages` (function): Clear message history
- `projectId` (string): Current project ID
- `changeProject` (function): Change project context
- `isLoading` (boolean): Loading state
- `error` (string): Error state

### 5. AgentRouter.js

Utility for routing messages to appropriate endpoints based on agent type.

**Functions:**
- `routeMessage(message)`: Routes a message to the appropriate endpoint
- `writeToMemory(message, tags)`: Writes a message to memory

**Routing Logic:**
- 'orchestrator' → /loop/plan
- 'sage' → /reflect
- All others → /agent/run

## Schema Requirements

All messages follow this schema:

```json
{
  "agent": "string",
  "role": "operator" | "agent",
  "loop_id": "string",
  "project_id": "string",
  "message": "string",
  "schema_compliant": true,
  "timestamp": "ISO8601"
}
```

## Integration

The AgentChatConsole is integrated into the LEFT zone of the Promethios UI through:

1. A bridge file in `/components/left/AgentChatConsole.jsx` that re-exports the main component
2. The UIZoneSchema.json configuration that includes "AgentChatConsole" in the LEFT zone
3. The DashboardLayout.jsx that imports and renders components based on the zone schema

## API Endpoints

The component interacts with these endpoints:

- `/agent/run`: For standard agent interactions
- `/loop/plan`: For orchestrator interactions
- `/reflect`: For sage agent interactions
- `/memory/write`: For persisting messages

## Dependencies

- Chakra UI for styling and components
- React Icons for iconography
- React Markdown for message formatting
- Local Storage for message persistence

## Usage Example

```jsx
import AgentChatConsole from '../components/chat/AgentChatConsole';

const MyComponent = () => {
  return (
    <div>
      <h1>Agent Chat</h1>
      <AgentChatConsole projectId="my-project" />
    </div>
  );
};
```

## Future Enhancements

Potential enhancements that could be added in the future:

1. "View Full Loop" button to see the complete plan → reflect → output trace
2. "Summarize This Thread" feature to generate a summary of the current conversation
3. Ability to rerun prompts with different agents
4. Message search functionality
5. Rich media attachments in messages
