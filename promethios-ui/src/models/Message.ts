/**
 * Message model for the threaded conversation architecture
 * Implements the data model changes for Phase 9.0
 */

export interface Message {
  message_id: string;        // UUID
  thread_parent_id: string | null; // Parent message ID for threaded replies
  goal_id: string;           // Associated goal/task ID
  agent_id: string;          // ID of the agent involved
  sender: 'operator' | 'agent' | 'system'; // Who sent the message
  content: string;           // Message content
  timestamp: Date;           // When the message was sent
}

// Extended message interface with UI-specific properties
export interface UIMessage extends Message {
  isExpanded?: boolean;      // Whether thread is expanded or collapsed
  threadCount?: number;      // Number of replies in thread
  isResolved?: boolean;      // Whether thread is marked as resolved
  isThreaded?: boolean;      // Whether message is part of a thread (for UI indentation)
  threadPermissions?: ThreadPermissions; // Thread-based permissions
  attachments?: Attachment[]; // Attached files or tool results
}

// Attachment interface for thread attachments (Phase 9.1)
export interface Attachment {
  id: string;
  type: 'tool_result' | 'memory_block' | 'file' | 'image';
  content: any;
  name: string;
  timestamp: Date;
}

// Thread summary interface (Phase 9.1)
export interface ThreadSummary {
  thread_id: string;
  summary: string;
  generated_at: Date;
}

// Thread permissions interface (Phase 9.1)
export interface ThreadPermissions {
  thread_id: string;
  can_execute: boolean;
  can_reflect: boolean;
  agent_ids: string[];
}
