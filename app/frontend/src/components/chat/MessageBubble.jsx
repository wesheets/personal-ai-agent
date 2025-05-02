import React from 'react';
import { Box, Flex, Text, Avatar, Badge, useColorModeValue } from '@chakra-ui/react';
import ReactMarkdown from 'react-markdown';
import ChakraUIRenderer from 'chakra-ui-markdown-renderer';

/**
 * MessageBubble Component
 * 
 * Displays a single message in the chat interface with agent information,
 * timestamp, and formatted message content.
 * 
 * @param {Object} props
 * @param {string} props.agent - Agent name/identifier
 * @param {string} props.role - Message role (operator or agent)
 * @param {string} props.message - Message content (supports markdown)
 * @param {string} props.timestamp - ISO timestamp string
 * @param {string} props.loop_id - Associated loop ID
 * @param {Array} props.tags - Optional memory tags
 */
const MessageBubble = ({ 
  agent, 
  role, 
  message, 
  timestamp, 
  loop_id,
  tags = []
}) => {
  // Color scheme based on role
  const isOperator = role === 'operator';
  const bgColor = useColorModeValue(
    isOperator ? 'blue.50' : 'gray.50',
    isOperator ? 'blue.900' : 'gray.700'
  );
  const textColor = useColorModeValue('gray.800', 'white');
  const borderColor = useColorModeValue(
    isOperator ? 'blue.200' : 'gray.200',
    isOperator ? 'blue.700' : 'gray.600'
  );
  
  // Format timestamp
  const formattedTime = new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
  
  // Get agent avatar and color
  const getAgentInfo = (agentId) => {
    const agentMap = {
      operator: { 
        name: 'Operator', 
        color: 'blue',
        avatar: '👤'
      },
      orchestrator: { 
        name: 'Orchestrator', 
        color: 'purple',
        avatar: '🧠'
      },
      ash: { 
        name: 'ASH', 
        color: 'orange',
        avatar: '🔥'
      },
      sage: { 
        name: 'SAGE', 
        color: 'green',
        avatar: '🧙'
      },
      skeptic: { 
        name: 'Skeptic', 
        color: 'red',
        avatar: '🤔'
      },
      default: { 
        name: agentId, 
        color: 'gray',
        avatar: '🤖'
      }
    };
    
    return agentMap[agentId] || agentMap.default;
  };
  
  const agentInfo = getAgentInfo(agent);
  
  // Custom markdown theme
  const markdownTheme = {
    p: (props) => {
      const { children } = props;
      return (
        <Text mb={2}>{children}</Text>
      );
    },
    code: (props) => {
      const { children } = props;
      return (
        <Box
          as="code"
          bg={useColorModeValue('gray.100', 'gray.700')}
          p={1}
          borderRadius="md"
          fontSize="sm"
          fontFamily="monospace"
        >
          {children}
        </Box>
      );
    },
    // Add more custom renderers as needed
  };
  
  // Handle typing indicator
  if (role === 'typing') {
    return (
      <Flex 
        direction="row"
        alignSelf={isOperator ? 'flex-end' : 'flex-start'}
        maxW="80%"
        mb={2}
      >
        <Avatar 
          size="sm" 
          name={agentInfo.name}
          bg={`${agentInfo.color}.500`}
          color="white"
          mr={2}
          fontSize="sm"
        >
          {agentInfo.avatar}
        </Avatar>
        <Box
          p={3}
          borderRadius="lg"
          bg={bgColor}
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Text fontSize="sm" color={textColor}>
            <span className="typing-indicator">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </Text>
        </Box>
      </Flex>
    );
  }
  
  return (
    <Flex 
      direction="row"
      alignSelf={isOperator ? 'flex-end' : 'flex-start'}
      maxW="80%"
      mb={4}
    >
      {!isOperator && (
        <Avatar 
          size="sm" 
          name={agentInfo.name}
          bg={`${agentInfo.color}.500`}
          color="white"
          mr={2}
          fontSize="sm"
        >
          {agentInfo.avatar}
        </Avatar>
      )}
      
      <Box
        p={3}
        borderRadius="lg"
        bg={bgColor}
        borderWidth="1px"
        borderColor={borderColor}
        shadow="sm"
      >
        <Flex justify="space-between" mb={1}>
          <Text fontWeight="bold" fontSize="sm" color={`${agentInfo.color}.500`}>
            {agentInfo.name}
          </Text>
          <Text fontSize="xs" color="gray.500">
            {formattedTime}
          </Text>
        </Flex>
        
        <Box color={textColor}>
          <ReactMarkdown components={ChakraUIRenderer(markdownTheme)}>
            {message}
          </ReactMarkdown>
        </Box>
        
        <Flex mt={2} wrap="wrap" gap={1}>
          {loop_id && (
            <Badge size="sm" colorScheme="purple" variant="subtle">
              Loop: {loop_id.substring(0, 8)}
            </Badge>
          )}
          
          {tags.map((tag, index) => (
            <Badge key={index} size="sm" colorScheme="gray" variant="subtle">
              {tag}
            </Badge>
          ))}
        </Flex>
      </Box>
      
      {isOperator && (
        <Avatar 
          size="sm" 
          name="Operator"
          bg="blue.500"
          color="white"
          ml={2}
          fontSize="sm"
        >
          👤
        </Avatar>
      )}
    </Flex>
  );
};

export default MessageBubble;
