# Nested Comments API Documentation

This document provides comprehensive documentation for the Nested Comments + Thread Logic system implemented in Phase 11.3.1. The system enables structured discussions with thread management, summarization, plan integration, and deviation tracking.

## Table of Contents

1. [Schema](#schema)
2. [Core Modules](#core-modules)
3. [Memory Integration](#memory-integration)
4. [Thread Lifecycle](#thread-lifecycle)
5. [Plan Integration](#plan-integration)
6. [Deviation Tracking](#deviation-tracking)
7. [Frontend Components](#frontend-components)
8. [Usage Examples](#usage-examples)

## Schema

The nested comments system is built on the `nested_message.schema.json` schema, which defines the structure for all thread messages.

### Key Fields

- `message_id`: Unique identifier for each message
- `thread_id`: Identifier grouping related messages into a thread
- `parent_id`: Reference to parent message (null for root messages)
- `depth`: Nesting level (0 for root messages, increments for replies)
- `loop_id`: Associated orchestrator loop
- `agent`: Agent that created the message
- `role`: Role of the agent (agent, orchestrator, operator)
- `message`: Content of the message
- `timestamp`: Creation time
- `status`: Thread status (open, closed, integrated, discarded)
- `summary`: Thread summary (only on root messages)
- `actionable`: Flag indicating thread contains actionable insights
- `plan_integration`: Details about how thread was integrated into a plan
- `thread_metadata`: Additional thread metadata

## Core Modules

### nested_comments.py

Core module for creating and managing nested comment threads.

#### Key Functions

```python
# Create a new thread
thread_id = create_thread(
    memory,
    loop_id=1,
    agent="hal",
    role="agent",
    message="This is a root message",
    timestamp="2025-04-20T12:00:00Z"
)

# Reply to an existing thread
reply_id = reply_to_thread(
    memory,
    thread_id="thread-123",
    parent_id="msg-456",
    agent="nova",
    role="agent",
    message="This is a reply",
    timestamp="2025-04-20T12:05:00Z"
)

# Get all messages in a thread
messages = get_thread_messages(memory, thread_id="thread-123")

# Get all threads for a specific loop
threads = get_threads_for_loop(memory, loop_id=1)

# Update thread status
update_thread_status(
    memory,
    thread_id="thread-123",
    status="closed",
    summary="Thread closed for testing",
    agent="orchestrator"
)

# Mark thread for plan revision
mark_thread_for_plan_revision(
    memory,
    thread_id="thread-123",
    agent="orchestrator"
)

# Find similar threads
similar_threads = find_similar_threads(
    memory,
    thread_id="thread-123",
    max_results=5
)

# Integrate thread with plan
integrate_thread_with_plan(
    memory,
    thread_id="thread-123",
    plan_step=1,
    integration_type="addition",
    integration_summary="Added thread insights to step 2",
    agent="orchestrator"
)
```

### thread_summarizer.py

Module for generating and managing thread summaries.

#### Key Functions

```python
# Generate a summary for a thread
summary = generate_thread_summary(
    memory,
    thread_id="thread-123",
    max_length=200
)

# Close a thread with auto-generated summary
close_thread_with_summary(
    memory,
    thread_id="thread-123",
    agent="orchestrator",
    max_summary_length=200
)

# Get summaries for all threads in a loop
summaries = get_thread_summaries_for_loop(
    memory,
    loop_id=1,
    status="closed"  # Optional filter
)

# Get actionable threads
actionable_threads = get_actionable_threads(memory, loop_id=1)

# Batch summarize multiple threads
result = batch_summarize_threads(
    memory,
    loop_id=1,
    agent="orchestrator",
    max_threads=5,
    max_summary_length=200
)
```

## Memory Integration

### memory_integration.py

Module for integrating nested comments with the memory system.

#### Key Functions

```python
# Initialize thread memory structures
initialize_thread_memory(memory)

# Store a thread in memory
store_thread_in_memory(
    memory,
    thread_id="thread-123",
    thread_data={...}
)

# Store a reply in memory
store_reply_in_memory(
    memory,
    thread_id="thread-123",
    reply_data={...}
)

# Store a thread summary
store_thread_summary_in_memory(
    memory,
    thread_id="thread-123",
    summary="This is a summary",
    agent="orchestrator"
)

# Retrieve threads from memory
threads = retrieve_threads_from_memory(
    memory,
    loop_id=1,  # Optional filter
    agent="hal"  # Optional filter
)

# Retrieve thread messages
messages = retrieve_thread_messages_from_memory(
    memory,
    thread_id="thread-123"
)

# Retrieve thread summaries
summaries = retrieve_thread_summaries_from_memory(
    memory,
    loop_id=1  # Optional filter
)

# Export threads to chat messages
export_threads_to_chat_messages(
    memory,
    loop_id=1
)

# Import chat messages to threads
import_chat_messages_to_threads(
    memory,
    loop_id=1
)
```

## Thread Lifecycle

### thread_lifecycle.py

Module for managing thread lifecycle states.

#### Key Functions

```python
# Close a thread
close_thread(
    memory,
    thread_id="thread-123",
    agent="orchestrator",
    auto_summarize=True,
    summary="Thread closed for testing"
)

# Integrate a thread into a plan
integrate_thread(
    memory,
    thread_id="thread-123",
    agent="orchestrator",
    plan_step=1,
    integration_type="addition",
    integration_summary="Added thread insights to step 2"
)

# Discard a thread
discard_thread(
    memory,
    thread_id="thread-123",
    agent="orchestrator",
    reason="Thread is no longer relevant"
)

# Reopen a thread
reopen_thread(
    memory,
    thread_id="thread-123",
    agent="orchestrator",
    reason="Further discussion needed"
)

# Batch close inactive threads
result = batch_close_inactive_threads(
    memory,
    loop_id=1,
    agent="orchestrator",
    inactivity_threshold_minutes=30,
    max_threads=10
)

# Get thread lifecycle history
history = get_thread_lifecycle_history(
    memory,
    thread_id="thread-123"
)
```

## Plan Integration

### thread_plan_integration.py

Module for integrating thread insights into plans.

#### Key Functions

```python
# Mark a thread as actionable
mark_thread_actionable(
    memory,
    thread_id="thread-123",
    agent="orchestrator",
    reason="Contains valuable insights for error handling"
)

# Get plan for a loop
plan = get_plan_for_loop(
    memory,
    loop_id=1
)

# Update plan with thread insight
update_plan_with_thread_insight(
    memory,
    thread_id="thread-123",
    plan_step=2,
    agent="orchestrator",
    modification_type="addition",
    modification_content="Ensure consistent use of try-except blocks."
)

# Process actionable threads
result = process_actionable_threads(
    memory,
    loop_id=1,
    agent="orchestrator",
    max_threads=5
)

# Suggest plan modifications from threads
suggestions = suggest_plan_modifications_from_threads(
    memory,
    loop_id=1,
    max_suggestions=3
)

# Get plan integration history
history = get_plan_integration_history(
    memory,
    loop_id=1
)
```

## Deviation Tracking

### thread_deviation.py

Module for tracking historical deviations in threads and analyzing patterns.

#### Key Functions

```python
# Initialize deviation memory
initialize_deviation_memory(memory)

# Record a thread deviation
record_thread_deviation(
    memory,
    thread_id="thread-123",
    deviation_type="scope_expansion",
    agent="orchestrator",
    description="Thread proposes changing authentication mechanism which is out of scope",
    severity="high",
    related_plan_step=2
)

# Resolve a thread deviation
resolve_thread_deviation(
    memory,
    thread_id="thread-123",
    deviation_index=0,
    agent="orchestrator",
    resolution_description="Decided to keep current authentication mechanism and document reasons"
)

# Update deviation patterns
update_deviation_patterns(
    memory,
    deviation_type="scope_expansion",
    thread_messages=[...]
)

# Get thread deviations
deviations = get_thread_deviations(
    memory,
    thread_id="thread-123",  # Optional filter
    loop_id=1,               # Optional filter
    deviation_type="scope_expansion",  # Optional filter
    resolved=False,          # Optional filter
    limit=100
)

# Get deviation patterns
patterns = get_deviation_patterns(
    memory,
    deviation_type="scope_expansion",  # Optional filter
    min_count=1
)

# Detect potential deviations
potential_deviations = detect_potential_deviations(
    memory,
    loop_id=1,
    threshold=0.7
)

# Generate deviation report
report = generate_deviation_report(
    memory,
    loop_id=1,
    include_patterns=True,
    include_unresolved=True,
    include_resolved=False
)
```

## Frontend Components

### ChatMessageFeed.jsx

Main component for displaying the chat message feed with nested comments.

#### Props

- `userMessages`: Array of message objects
- `isThinking`: Boolean indicating if the orchestrator is thinking

#### Features

- Thread expansion/collapse
- Status badges
- Thread summaries
- Message filtering
- Auto-scrolling
- Accessibility support

### NestedReply.jsx

Component for rendering nested replies with proper indentation.

#### Props

- `reply`: Reply message object
- `agentColors`: Color mapping for agents
- `formatTime`: Function to format timestamps
- `parentMessage`: Parent message object
- `allMessages`: All messages in the thread
- `expandedThreads`: Object tracking expanded state
- `toggleThreadExpansion`: Function to toggle expansion

#### Features

- Depth-based indentation
- Collapsible deep replies
- Nested reply chains
- Agent badges
- Accessibility support

### ThreadSummaryTooltip.jsx

Component for displaying thread summaries in a tooltip.

#### Props

- `summary`: Thread summary text
- `status`: Thread status (open, closed, integrated, discarded)

#### Features

- Pinnable tooltips
- Status indicators
- Click-outside detection
- Accessibility support

## Usage Examples

### Creating a Thread and Replies

```python
from orchestrator.modules.nested_comments import create_thread, reply_to_thread

# Initialize memory if needed
if "thread_history" not in memory:
    memory["thread_history"] = {}
if "thread_messages" not in memory:
    memory["thread_messages"] = {}

# Create a new thread
thread_id = create_thread(
    memory=memory,
    loop_id=current_loop_id,
    agent="hal",
    role="agent",
    message="I think we should consider a different approach to authentication",
    timestamp=datetime.datetime.now().isoformat()
)

# Add a reply
reply_id = reply_to_thread(
    memory=memory,
    thread_id=thread_id,
    parent_id=memory["thread_messages"][thread_id][0]["message_id"],
    agent="nova",
    role="agent",
    message="I agree, OAuth would be better than JWT for this use case",
    timestamp=datetime.datetime.now().isoformat()
)
```

### Thread Lifecycle Management

```python
from orchestrator.modules.thread_lifecycle import close_thread, reopen_thread

# Close a thread with summary
close_thread(
    memory=memory,
    thread_id=thread_id,
    agent="orchestrator",
    auto_summarize=True,
    summary="Decided to switch from JWT to OAuth for authentication"
)

# Later, reopen the thread if needed
reopen_thread(
    memory=memory,
    thread_id=thread_id,
    agent="orchestrator",
    reason="Need to reconsider OAuth implementation details"
)
```

### Integrating Thread Insights into Plans

```python
from orchestrator.modules.thread_plan_integration import mark_thread_actionable, update_plan_with_thread_insight

# Mark thread as containing actionable insights
mark_thread_actionable(
    memory=memory,
    thread_id=thread_id,
    agent="orchestrator",
    reason="Contains valuable insights for authentication mechanism"
)

# Update plan with thread insights
update_plan_with_thread_insight(
    memory=memory,
    thread_id=thread_id,
    plan_step=2,  # Step related to authentication
    agent="orchestrator",
    modification_type="modification",
    modification_content="Replace JWT authentication with OAuth 2.0 flow"
)
```

### Tracking Thread Deviations

```python
from orchestrator.modules.thread_deviation import record_thread_deviation, resolve_thread_deviation

# Record a deviation when thread goes off-topic
record_thread_deviation(
    memory=memory,
    thread_id=thread_id,
    deviation_type="scope_expansion",
    agent="orchestrator",
    description="Thread proposes changing entire authentication system which exceeds current sprint scope",
    severity="medium"
)

# Later, resolve the deviation
resolve_thread_deviation(
    memory=memory,
    thread_id=thread_id,
    deviation_index=0,  # First deviation for this thread
    agent="orchestrator",
    resolution_description="Limited scope to JWT improvements only, OAuth will be considered in next sprint"
)
```

### Rendering in React Frontend

```jsx
import ChatMessageFeed from './components/ChatMessageFeed';

function App() {
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  
  // Fetch messages from API or state
  
  return (
    <div className="app-container">
      <ChatMessageFeed 
        userMessages={messages}
        isThinking={isThinking}
      />
    </div>
  );
}
```

This documentation covers the core functionality of the Nested Comments + Thread Logic system. For more detailed information, refer to the source code and unit tests for each module.
