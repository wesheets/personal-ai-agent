import React from 'react';
import {
  Box,
  Flex,
  Text,
  Badge,
  useColorModeValue,
  HStack,
  VStack,
  Progress,
  Icon,
  Divider
} from '@chakra-ui/react';
import { FiCpu, FiActivity, FiTool, FiBookOpen, FiThumbsUp } from 'react-icons/fi';

const AgentSandboxCard = ({ agent }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Get status color
  const getStatusColor = (status) => {
    switch(status.toLowerCase()) {
      case 'executing':
      case 'active':
        return 'green';
      case 'paused':
        return 'orange';
      case 'idle':
        return 'blue';
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Get agent color
  const getAgentColor = (id) => {
    switch(id.toLowerCase()) {
      case 'hal':
        return 'blue';
      case 'ash':
        return 'purple';
      case 'nova':
        return 'orange';
      default:
        return 'gray';
    }
  };

  return (
    <Box
      mb={4}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      overflow="hidden"
      boxShadow="sm"
      borderLeftWidth="4px"
      borderLeftColor={`${getAgentColor(agent.id)}.500`}
    >
      {/* Agent header */}
      <Flex 
        justify="space-between" 
        align="center" 
        p={3} 
        borderBottomWidth="1px" 
        borderColor={borderColor}
        bg={useColorModeValue(`${getAgentColor(agent.id)}.50`, `${getAgentColor(agent.id)}.900`)}
      >
        <Flex align="center">
          <Box
            bg={`${getAgentColor(agent.id)}.500`}
            color="white"
            borderRadius="full"
            boxSize="30px"
            fontSize="sm"
            fontWeight="bold"
            display="flex"
            alignItems="center"
            justifyContent="center"
            mr={2}
          >
            <Icon as={FiCpu} />
          </Box>
          <Box>
            <Text fontWeight="bold">{agent.name}</Text>
            <Badge colorScheme={getStatusColor(agent.status)}>
              {agent.status.toUpperCase()}
            </Badge>
          </Box>
        </Flex>
      </Flex>
      
      {/* Agent content */}
      <Box p={3}>
        <VStack align="stretch" spacing={3}>
          {/* Active Task */}
          <Box>
            <HStack mb={1}>
              <Icon as={FiActivity} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                ACTIVE TASK
              </Text>
            </HStack>
            <Text fontSize="sm">{agent.activeTask}</Text>
          </Box>
          
          {/* Last Memory Entry */}
          <Box>
            <HStack mb={1}>
              <Icon as={FiBookOpen} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                LAST MEMORY
              </Text>
            </HStack>
            <Text fontSize="sm">{agent.lastMemoryEntry}</Text>
          </Box>
          
          {/* Active Tools */}
          <Box>
            <HStack mb={1}>
              <Icon as={FiTool} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                TOOLKIT
              </Text>
            </HStack>
            <Flex flexWrap="wrap" gap={1}>
              {agent.tools.map((tool, index) => (
                <Badge key={index} colorScheme={getAgentColor(agent.id)} variant="subtle">
                  {tool}
                </Badge>
              ))}
            </Flex>
          </Box>
          
          <Divider />
          
          {/* Reflection */}
          <Box>
            <HStack mb={1}>
              <Icon as={FiThumbsUp} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                REFLECTION
              </Text>
            </HStack>
            <Text fontSize="sm" fontStyle="italic">
              "{agent.reflection}"
            </Text>
          </Box>
        </VStack>
      </Box>
    </Box>
  );
};

export default AgentSandboxCard;
