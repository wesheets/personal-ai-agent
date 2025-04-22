import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useToast } from '@chakra-ui/react';

// Create context
const ChatMemoryContext = createContext();

/**
 * ChatMemoryProvider Component
 * 
 * Provides context for chat message history and project scoping.
 * Handles local storage of messages and syncing with memory via /memory/write.
 */
export const ChatMemoryProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [projectId, setProjectId] = useState('promethios-core');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const toast = useToast();

  // Load messages from local storage on mount
  useEffect(() => {
    const loadMessages = () => {
      try {
        const storedMessages = localStorage.getItem(`chat_messages_${projectId}`);
        if (storedMessages) {
          setMessages(JSON.parse(storedMessages));
        }
      } catch (err) {
        console.error('Error loading messages from local storage:', err);
        setError('Failed to load message history');
      }
    };

    loadMessages();
  }, [projectId]);

  // Save messages to local storage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(`chat_messages_${projectId}`, JSON.stringify(messages));
    } catch (err) {
      console.error('Error saving messages to local storage:', err);
    }
  }, [messages, projectId]);

  // Function to add a new message
  const addMessage = useCallback(async (message) => {
    // Ensure message has all required fields
    const completeMessage = {
      id: `msg_${Date.now()}`,
      timestamp: new Date().toISOString(),
      schema_compliant: true,
      project_id: projectId,
      ...message
    };

    // Update local state
    setMessages(prevMessages => [...prevMessages, completeMessage]);

    // Sync with memory API
    if (message.role !== 'typing') {
      try {
        setIsLoading(true);
        const response = await fetch('/memory/write', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content: completeMessage,
            tags: [`loop:${completeMessage.loop_id}`, `agent:${completeMessage.agent}`, 'thread:chat'],
            project_id: projectId,
            schema_compliant: true
          }),
        });

        if (!response.ok) {
          throw new Error(`Memory API error: ${response.status}`);
        }

        setError(null);
      } catch (err) {
        console.error('Error writing message to memory:', err);
        setError('Failed to save message to memory');
        toast({
          title: 'Memory Sync Error',
          description: 'Message saved locally but failed to sync with memory',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    }
  }, [projectId, toast]);

  // Function to clear messages for current project
  const clearMessages = useCallback(() => {
    setMessages([]);
    try {
      localStorage.removeItem(`chat_messages_${projectId}`);
    } catch (err) {
      console.error('Error clearing messages from local storage:', err);
    }
  }, [projectId]);

  // Function to change project context
  const changeProject = useCallback((newProjectId) => {
    setProjectId(newProjectId);
  }, []);

  // Context value
  const value = {
    messages,
    addMessage,
    clearMessages,
    projectId,
    changeProject,
    isLoading,
    error
  };

  return (
    <ChatMemoryContext.Provider value={value}>
      {children}
    </ChatMemoryContext.Provider>
  );
};

// Custom hook to use the chat memory context
export const useChatMemory = () => {
  const context = useContext(ChatMemoryContext);
  if (!context) {
    throw new Error('useChatMemory must be used within a ChatMemoryProvider');
  }
  return context;
};

export default ChatMemoryContext;
