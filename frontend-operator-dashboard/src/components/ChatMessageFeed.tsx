import React from 'react';
import {
  Box,
  VStack,
  useColorModeValue,
  Divider,
  Text
} from '@chakra-ui/react';
import { UIMessage } from '../models/Message';
import AgentMessageBubble from './chat/AgentMessageBubble';
import ReflectionPanel from './ReflectionPanel';

interface ChatMessageFeedProps {
  messages: UIMessage[];
  onReply: (messageId: string) => void;
  onToggleThread: (messageId: string) => void;
  onMarkResolved: (messageId: string) => void;
  onSummarizeThread: (messageId: string) => void;
  onExportMarkdown: (messageId: string) => void;
  onExportPDF: (messageId: string) => void;
  onUpdatePermissions: (threadId: string, permissions: any) => void;
  onRevise: (beliefKey: string) => void;
  onReinforce: (beliefKey: string) => void;
  onChallenge: (beliefKey: string) => void;
}

const ChatMessageFeed: React.FC<ChatMessageFeedProps> = ({
  messages,
  onReply,
  onToggleThread,
  onMarkResolved,
  onSummarizeThread,
  onExportMarkdown,
  onExportPDF,
  onUpdatePermissions,
  onRevise,
  onReinforce,
  onChallenge
}) => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  
  // Function to render message or reflection panel based on message type
  const renderMessage = (message: UIMessage) => {
    // Check if this is a reflection response
    if (message.attachments && message.attachments.some(att => att.type === 'memory_block' && att.content?.status === 'self-reflection')) {
      const reflectionData = message.attachments.find(
        att => att.type === 'memory_block' && att.content?.status === 'self-reflection'
      )?.content;
      
      if (reflectionData) {
        return (
          <ReflectionPanel
            beliefs={reflectionData.beliefs}
            belief_stability={reflectionData.belief_stability}
            reinforced_beliefs={reflectionData.reinforced_beliefs}
            revision_log={reflectionData.revision_log}
            volatility_flags={reflectionData.volatility_flags}
            onRevise={onRevise}
            onReinforce={onReinforce}
            onChallenge={onChallenge}
          />
        );
      }
    }
    
    // Check if this is a reinforcement response
    if (message.attachments && message.attachments.some(att => att.type === 'memory_block' && att.content?.status === 'reinforced')) {
      return (
        <Box
          p={3}
          borderRadius="lg"
          bg={useColorModeValue('green.50', 'green.900')}
          borderWidth="1px"
          borderColor={useColorModeValue('green.200', 'green.700')}
          mb={3}
          maxW="80%"
          alignSelf="flex-start"
        >
          <Text fontWeight="bold">Belief Reinforced</Text>
          <Text>The belief has been locked and will not be modified.</Text>
        </Box>
      );
    }
    
    // Check if this is a challenge response
    if (message.attachments && message.attachments.some(att => att.type === 'memory_block' && att.content?.status === 'challenged')) {
      return (
        <Box
          p={3}
          borderRadius="lg"
          bg={useColorModeValue('yellow.50', 'yellow.900')}
          borderWidth="1px"
          borderColor={useColorModeValue('yellow.200', 'yellow.700')}
          mb={3}
          maxW="80%"
          alignSelf="flex-start"
        >
          <Text fontWeight="bold">Belief Challenged</Text>
          <Text>The belief is under review but has not been modified.</Text>
        </Box>
      );
    }
    
    // Regular message
    return (
      <AgentMessageBubble
        message={message}
        onReply={onReply}
        onToggleThread={onToggleThread}
        onMarkResolved={onMarkResolved}
        onSummarizeThread={onSummarizeThread}
        onExportMarkdown={onExportMarkdown}
        onExportPDF={onExportPDF}
        onUpdatePermissions={onUpdatePermissions}
        isThreaded={!!message.thread_parent_id}
        indentLevel={message.thread_parent_id ? 1 : 0}
      />
    );
  };
  
  // Group messages by date for better organization
  const groupMessagesByDate = () => {
    const groups: { [key: string]: UIMessage[] } = {};
    
    messages.forEach(message => {
      const date = new Date(message.timestamp);
      const dateKey = date.toDateString();
      
      if (!groups[dateKey]) {
        groups[dateKey] = [];
      }
      
      groups[dateKey].push(message);
    });
    
    return groups;
  };
  
  const messageGroups = groupMessagesByDate();
  
  return (
    <Box
      bg={bgColor}
      p={4}
      borderRadius="md"
      height="100%"
      overflowY="auto"
    >
      <VStack spacing={4} align="stretch">
        {Object.entries(messageGroups).map(([dateKey, messagesGroup]) => (
          <Box key={dateKey}>
            <Divider mb={2} />
            <Text fontSize="xs" color="gray.500" textAlign="center" mb={2}>
              {dateKey}
            </Text>
            
            <VStack spacing={2} align="stretch">
              {messagesGroup.map(message => (
                <Box key={message.message_id}>
                  {renderMessage(message)}
                </Box>
              ))}
            </VStack>
          </Box>
        ))}
      </VStack>
    </Box>
  );
};

export default ChatMessageFeed;
