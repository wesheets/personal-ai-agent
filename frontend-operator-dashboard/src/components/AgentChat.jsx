import React from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  HStack,
  Avatar,
  useColorModeValue,
  Badge,
  Divider
} from '@chakra-ui/react';

const AgentChat = ({ agentId = 'hal' }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Mock messages - would be replaced with actual data from API
  const messages = [
    {
      id: '1',
      sender: 'system',
      content: 'HAL is running: tool.search.web',
      timestamp: new Date(Date.now() - 1000 * 60 * 5)
    },
    {
      id: '2',
      sender: 'agent',
      content: 'I found several relevant articles about React state management. Would you like me to summarize the key points?',
      timestamp: new Date(Date.now() - 1000 * 60 * 4),
      agentName: 'HAL'
    },
    {
      id: '3',
      sender: 'operator',
      content: 'Yes, please focus on the differences between Context API and Redux.',
      timestamp: new Date(Date.now() - 1000 * 60 * 3)
    },
    {
      id: '4',
      sender: 'system',
      content: 'HAL is running: tool.copy.generate',
      timestamp: new Date(Date.now() - 1000 * 60 * 2)
    },
    {
      id: '5',
      sender: 'agent',
      content: 'Here\'s a comparison of Context API and Redux:\n\n**Context API**:\n- Built into React\n- Simpler setup\n- Good for low-frequency updates\n- Less boilerplate\n- No middleware support\n\n**Redux**:\n- External library\n- More structured approach\n- Better for complex state logic\n- Developer tools\n- Middleware support\n\nContext API is generally better for smaller applications or when you need to share state between a few components. Redux shines in larger applications with complex state management needs.',
      timestamp: new Date(Date.now() - 1000 * 60),
      agentName: 'HAL'
    }
  ];
  
  // Format timestamp
  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Get agent color based on name
  const getAgentColor = (name) => {
    if (!name) return 'gray';
    
    switch(name.toLowerCase()) {
      case 'hal': return 'blue';
      case 'ash': return 'purple';
      case 'nova': return 'green';
      default: return 'gray';
    }
  };

  return (
    <Box
      h="100%"
      bg={bgColor}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      display="flex"
      flexDirection="column"
    >
      <Box p={4} borderBottomWidth="1px" borderColor={borderColor}>
        <Text fontWeight="bold">Agent Chat Thread</Text>
      </Box>
      
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
        {messages.map((message) => (
          <Box key={message.id}>
            {message.sender === 'system' ? (
              // System message (centered, faded)
              <Flex justify="center" my={2}>
                <Badge colorScheme="gray" px={2} py={1} borderRadius="full">
                  {message.content}
                </Badge>
              </Flex>
            ) : message.sender === 'operator' ? (
              // Operator message (right-aligned)
              <Flex justify="flex-end">
                <Box
                  maxW="80%"
                  bg={useColorModeValue('blue.100', 'blue.700')}
                  color={useColorModeValue('gray.800', 'white')}
                  p={3}
                  borderRadius="lg"
                  borderTopRightRadius="0"
                >
                  <Text>{message.content}</Text>
                  <Text fontSize="xs" color={useColorModeValue('gray.600', 'gray.300')} textAlign="right" mt={1}>
                    {formatTime(message.timestamp)}
                  </Text>
                </Box>
              </Flex>
            ) : (
              // Agent message (left-aligned)
              <Flex>
                <Avatar 
                  size="sm" 
                  name={message.agentName} 
                  bg={`${getAgentColor(message.agentName)}.500`}
                  color="white"
                  mr={2}
                />
                <Box
                  maxW="80%"
                  bg={useColorModeValue(`${getAgentColor(message.agentName)}.50`, `${getAgentColor(message.agentName)}.900`)}
                  p={3}
                  borderRadius="lg"
                  borderTopLeftRadius="0"
                >
                  <HStack mb={1}>
                    <Text fontWeight="bold" fontSize="sm">{message.agentName}</Text>
                  </HStack>
                  <Text whiteSpace="pre-wrap">{message.content}</Text>
                  <Text fontSize="xs" color={useColorModeValue('gray.600', 'gray.300')} textAlign="right" mt={1}>
                    {formatTime(message.timestamp)}
                  </Text>
                </Box>
              </Flex>
            )}
          </Box>
        ))}
      </VStack>
    </Box>
  );
};

export default AgentChat;
