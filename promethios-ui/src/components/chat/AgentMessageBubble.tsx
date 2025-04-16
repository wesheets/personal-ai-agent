import React from 'react';
import { Box, HStack, Text, useColorModeValue } from '@chakra-ui/react';
import { UIMessage } from '../../models/Message';

interface AgentMessageBubbleProps {
  message: UIMessage;
  messages: UIMessage[];
  onReply: (messageId: string) => void;
  onToggleThread: (messageId: string) => void;
  onMarkResolved: (messageId: string) => void;
  onSummarizeThread: (messageId: string) => void;
  onExportMarkdown: (messageId: string) => void;
  onExportPDF: (messageId: string) => void;
  onUpdatePermissions: (threadId: string, permissions: any) => void;
  isThreaded?: boolean;
  indentLevel?: number;
}

const AgentMessageBubble: React.FC<AgentMessageBubbleProps> = ({
  message,
  onReply,
  onToggleThread,
  onMarkResolved,
  onSummarizeThread,
  onExportMarkdown,
  onExportPDF,
  isThreaded = false,
  indentLevel = 0
}) => {
  const isOperator = message.sender === 'operator';
  const isSystem = message.sender === 'system';

  // Calculate indentation based on level
  const indentSize = 20; // 20px as specified in the visual spec
  const indentPx = indentLevel * indentSize;

  // Get background color based on sender and resolved status
  const getBgColor = () => {
    if (message.isResolved) {
      return useColorModeValue('gray.100', 'gray.700');
    }

    if (isSystem) {
      return useColorModeValue('purple.50', 'purple.900');
    }

    if (isOperator) {
      return useColorModeValue('blue.50', 'blue.900');
    }

    return useColorModeValue('gray.50', 'gray.800');
  };

  // Get text color based on sender and resolved status
  const getTextColor = () => {
    if (message.isResolved) {
      return useColorModeValue('gray.500', 'gray.400');
    }

    return useColorModeValue('gray.800', 'white');
  };

  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Handle reply click
  const handleReply = () => {
    onReply(message.message_id);
  };

  // Handle thread toggle
  const handleToggleThread = () => {
    if (message.threadCount && message.threadCount > 0) {
      onToggleThread(message.message_id);
    }
  };

  return (
    <Box
      ml={`${indentPx}px`}
      mb={2}
      maxW="80%"
      alignSelf={isOperator ? 'flex-end' : 'flex-start'}
      opacity={message.isResolved ? 0.7 : 1}
    >
      <Box
        p={3}
        borderRadius="lg"
        bg={getBgColor()}
        color={getTextColor()}
        borderWidth="1px"
        borderColor={useColorModeValue('gray.200', 'gray.600')}
      >
        <HStack mb={1} justify="space-between">
          <Text fontSize="sm" fontWeight="bold">
            {isOperator ? 'Operator' : message.agent_id}
          </Text>
          <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
            {formatTime(message.timestamp)}
          </Text>
        </HStack>

        <Text whiteSpace="pre-wrap">{message.content}</Text>

        {/* Thread controls */}
        {!isThreaded && message.threadCount && message.threadCount > 0 && (
          <Box as="button" mt={2} onClick={handleToggleThread} fontSize="sm" color="blue.500">
            {message.isExpanded ? 'Hide' : 'Show'} {message.threadCount}{' '}
            {message.threadCount === 1 ? 'reply' : 'replies'}
          </Box>
        )}

        {/* Reply button */}
        {!message.isResolved && (
          <Box as="button" mt={2} onClick={handleReply} fontSize="sm" color="blue.500" ml={2}>
            Reply
          </Box>
        )}

        {/* Thread actions for parent messages */}
        {!isThreaded && !message.thread_parent_id && (
          <HStack mt={2} spacing={2}>
            <Box
              as="button"
              onClick={() => onMarkResolved(message.message_id)}
              fontSize="xs"
              color="gray.500"
              p={1}
              borderRadius="md"
              _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
            >
              {message.isResolved ? 'Resolved' : 'Mark Resolved'}
            </Box>

            <Box
              as="button"
              onClick={() => onSummarizeThread(message.message_id)}
              fontSize="xs"
              color="gray.500"
              p={1}
              borderRadius="md"
              _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
            >
              Summarize
            </Box>

            <Box
              as="button"
              onClick={() => onExportMarkdown(message.message_id)}
              fontSize="xs"
              color="gray.500"
              p={1}
              borderRadius="md"
              _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
            >
              Export MD
            </Box>

            <Box
              as="button"
              onClick={() => onExportPDF(message.message_id)}
              fontSize="xs"
              color="gray.500"
              p={1}
              borderRadius="md"
              _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
            >
              Export PDF
            </Box>
          </HStack>
        )}
      </Box>
    </Box>
  );
};

export default AgentMessageBubble;
