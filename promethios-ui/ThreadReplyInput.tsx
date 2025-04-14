import React, { useState } from 'react';
import { Box, Flex, Input, Button, HStack, Avatar, Text, useColorModeValue } from '@chakra-ui/react';
import { UIMessage } from '../../models/Message';

interface ThreadReplyInputProps {
  onSendReply: (content: string) => void;
  onCancel: () => void;
  parentMessage: UIMessage;
}

const ThreadReplyInput: React.FC<ThreadReplyInputProps> = ({
  onSendReply,
  onCancel,
  parentMessage
}) => {
  const [replyContent, setReplyContent] = useState('');
  
  // Get agent color based on name
  const getAgentColor = (agentId: string) => {
    if (!agentId) return 'gray';
    
    switch(agentId.toLowerCase()) {
      case 'hal': return 'blue';
      case 'ash': return 'teal';
      case 'nova': return 'orange';
      case 'orchestrator': return 'purple';
      default: return 'gray';
    }
  };
  
  const handleSendReply = () => {
    if (replyContent.trim()) {
      onSendReply(replyContent);
      setReplyContent('');
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendReply();
    }
  };
  
  return (
    <Box 
      borderWidth="1px" 
      borderRadius="md" 
      p={3} 
      bg={useColorModeValue('gray.50', 'gray.700')}
      borderColor={useColorModeValue('gray.200', 'gray.600')}
      borderLeftWidth="3px"
      borderLeftColor={`${getAgentColor(parentMessage.agent_id)}.500`}
    >
      <Flex mb={2} alignItems="center">
        <Avatar 
          size="xs" 
          name={parentMessage.agent_id} 
          bg={`${getAgentColor(parentMessage.agent_id)}.500`}
          color="white"
          mr={2}
        />
        <Text fontSize="sm" fontWeight="medium">
          Replying to {parentMessage.agent_id}
        </Text>
      </Flex>
      
      <Input
        placeholder="Type your reply..."
        value={replyContent}
        onChange={(e) => setReplyContent(e.target.value)}
        onKeyPress={handleKeyPress}
        bg={useColorModeValue('white', 'gray.800')}
        mb={2}
        autoFocus
      />
      
      <HStack justifyContent="flex-end" spacing={2}>
        <Button size="sm" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button 
          size="sm" 
          colorScheme="blue" 
          onClick={handleSendReply}
          isDisabled={!replyContent.trim()}
        >
          Reply
        </Button>
      </HStack>
    </Box>
  );
};

export default ThreadReplyInput;
