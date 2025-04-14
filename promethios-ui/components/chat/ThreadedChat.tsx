import React, { useState, useEffect } from 'react';
import { Box, VStack, useColorModeValue, Text } from '@chakra-ui/react';
import AgentMessageBubble from './AgentMessageBubble';
import ThreadReplyInput from './ThreadReplyInput';
import { UIMessage, ThreadPermissions } from '../../models/Message';

interface ThreadedChatProps {
  messages: UIMessage[];
  onSendMessage: (content: string, threadParentId?: string) => void;
  onMarkResolved: (messageId: string) => void;
  onSummarizeThread: (messageId: string) => void;
  onExportMarkdown: (messageId: string) => void;
  onExportPDF: (messageId: string) => void;
}

const ThreadedChat: React.FC<ThreadedChatProps> = ({
  messages,
  onSendMessage,
  onMarkResolved,
  onSummarizeThread,
  onExportMarkdown,
  onExportPDF
}) => {
  const [threadedMessages, setThreadedMessages] = useState<UIMessage[]>([]);
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  
  // Process messages into threaded structure
  useEffect(() => {
    // Create a map of parent messages to their children
    const threadMap = new Map<string, UIMessage[]>();
    
    // First pass: identify all thread parents and their direct children
    messages.forEach(message => {
      if (message.thread_parent_id) {
        // This is a child message in a thread
        if (!threadMap.has(message.thread_parent_id)) {
          threadMap.set(message.thread_parent_id, []);
        }
        threadMap.get(message.thread_parent_id)?.push(message);
      }
    });
    
    // Second pass: update thread counts and build the final array
    const result: UIMessage[] = [];
    
    messages.forEach(message => {
      if (!message.thread_parent_id) {
        // This is a top-level message
        const threadChildren = threadMap.get(message.message_id) || [];
        const updatedMessage = {
          ...message,
          threadCount: threadChildren.length,
          isExpanded: message.isExpanded || false
        };
        
        result.push(updatedMessage);
        
        // If thread is expanded, add all children with proper indentation
        if (updatedMessage.isExpanded && threadChildren.length > 0) {
          threadChildren.forEach(child => {
            result.push({
              ...child,
              isThreaded: true
            });
          });
        }
      }
    });
    
    setThreadedMessages(result);
  }, [messages]);
  
  // Handle toggling thread expansion
  const handleToggleThread = (messageId: string) => {
    setThreadedMessages(prev => 
      prev.map(msg => 
        msg.message_id === messageId 
          ? { ...msg, isExpanded: !msg.isExpanded } 
          : msg
      )
    );
  };
  
  // Handle reply to message
  const handleReply = (parentId: string) => {
    setReplyingTo(parentId);
  };
  
  // Handle send reply
  const handleSendReply = (content: string) => {
    if (replyingTo) {
      onSendMessage(content, replyingTo);
      setReplyingTo(null);
    }
  };
  
  // Handle cancel reply
  const handleCancelReply = () => {
    setReplyingTo(null);
  };
  
  // Handle updating thread permissions
  const handleUpdatePermissions = (threadId: string, permissions: ThreadPermissions) => {
    // In a real implementation, this would update permissions in the backend
    console.log(`Updating permissions for thread ${threadId}:`, permissions);
  };
  
  return (
    <Box
      h="100%"
      bg={useColorModeValue('white', 'gray.800')}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={useColorModeValue('gray.200', 'gray.700')}
      overflow="hidden"
      display="flex"
      flexDirection="column"
      maxW="880px" // As specified in the visual spec
      mx="auto" // Center the chat area
    >
      <VStack
        flex="1"
        spacing={4}
        align="stretch"
        p={4}
        overflowY="auto"
        css={{
          '&::-webkit-scrollbar': {
            width: '4px',
          },
          '&::-webkit-scrollbar-track': {
            width: '6px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: useColorModeValue('gray.300', 'gray.600'),
            borderRadius: '24px',
          },
        }}
      >
        {threadedMessages.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text color={useColorModeValue('gray.500', 'gray.400')}>
              No messages yet. Start a conversation!
            </Text>
          </Box>
        ) : (
          threadedMessages.map((message) => (
            <React.Fragment key={message.message_id}>
              <AgentMessageBubble
                message={message}
                messages={messages}
                onReply={handleReply}
                onToggleThread={handleToggleThread}
                onMarkResolved={onMarkResolved}
                onSummarizeThread={onSummarizeThread}
                onExportMarkdown={onExportMarkdown}
                onExportPDF={onExportPDF}
                onUpdatePermissions={handleUpdatePermissions}
                isThreaded={message.isThreaded}
                indentLevel={message.isThreaded ? 1 : 0}
              />
              {replyingTo === message.message_id && (
                <Box ml={message.isThreaded ? '40px' : '20px'}>
                  <ThreadReplyInput
                    onSendReply={handleSendReply}
                    onCancel={handleCancelReply}
                    parentMessage={message}
                  />
                </Box>
              )}
            </React.Fragment>
          ))
        )}
      </VStack>
    </Box>
  );
};

export default ThreadedChat;
