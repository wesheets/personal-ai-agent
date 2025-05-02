import React from 'react';
import { Box, Text, Badge, Flex, useColorModeValue } from '@chakra-ui/react';

/**
 * AgentCard Component
 * 
 * Displays information about an agent with dynamic properties
 * 
 * @param {Object} props
 * @param {string} props.name - The name of the agent
 * @param {string} props.status - The current status of the agent (active, idle, error)
 * @param {string} props.description - A brief description of the agent's purpose
 * @param {boolean} props.active - Whether the agent is currently active
 * @param {string} [props.color] - Optional color scheme for the agent card
 */
const AgentCard = ({ name, status, description, active, color = 'blue' }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const activeBorderColor = useColorModeValue(`${color}.300`, `${color}.500`);
  
  // Determine status color
  const getStatusColor = (status) => {
    if (!status || typeof status !== 'string') {
      return 'gray';
    }
    
    switch (status.toLowerCase()) {
      case 'active':
        return 'green';
      case 'idle':
        return 'blue';
      case 'error':
        return 'red';
      case 'busy':
        return 'orange';
      default:
        return 'gray';
    }
  };
  
  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      p={4} 
      shadow="sm" 
      bg={bgColor} 
      borderColor={active ? activeBorderColor : borderColor}
      borderLeftWidth={active ? "4px" : "1px"}
      transition="all 0.2s"
      _hover={{ 
        shadow: "md",
        transform: "translateY(-2px)"
      }}
    >
      <Flex justifyContent="space-between" alignItems="center" mb={2}>
        <Text fontWeight="bold" fontSize="md">{name}</Text>
        <Badge colorScheme={getStatusColor(status)}>
          {status || 'Unknown'}
        </Badge>
      </Flex>
      
      <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }}>
        {description || 'No description available'}
      </Text>
    </Box>
  );
};

export default AgentCard;
