import React, { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Badge,
  Flex,
  Divider,
  Button,
  Collapse,
  useColorModeValue,
  Icon,
  VStack,
  HStack
} from '@chakra-ui/react';
import { FiChevronDown, FiChevronUp, FiCpu, FiTool, FiMessageSquare } from 'react-icons/fi';

interface AgentSandboxCardProps {
  agent: {
    id: string;
    name: string;
    status: 'idle' | 'executing' | 'paused';
    activeTask?: string;
    lastMemoryEntry?: string;
    tools?: string[];
    reflection?: string;
  };
}

const AgentSandboxCard: React.FC<AgentSandboxCardProps> = ({ agent }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Status color mapping
  const getStatusColor = (status: string) => {
    switch(status) {
      case 'executing': return 'green';
      case 'paused': return 'orange';
      case 'idle': return 'gray';
      default: return 'gray';
    }
  };

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      borderColor={borderColor}
      bg={bgColor}
      p={4}
      mb={4}
      boxShadow="sm"
      transition="all 0.2s"
      _hover={{ boxShadow: 'md' }}
    >
      <Flex justify="space-between" align="center" mb={2}>
        <HStack>
          <Icon as={FiCpu} color={`${getStatusColor(agent.status)}.500`} />
          <Heading size="sm">{agent.name}</Heading>
        </HStack>
        <Badge colorScheme={getStatusColor(agent.status)}>
          {agent.status}
        </Badge>
      </Flex>
      
      {agent.activeTask && (
        <Box mb={2}>
          <Text fontSize="xs" color="gray.500">ACTIVE TASK</Text>
          <Text fontSize="sm" fontWeight="medium">{agent.activeTask}</Text>
        </Box>
      )}
      
      {agent.lastMemoryEntry && (
        <Box mb={2}>
          <Text fontSize="xs" color="gray.500">LAST MEMORY</Text>
          <Text fontSize="sm" noOfLines={2}>{agent.lastMemoryEntry}</Text>
        </Box>
      )}
      
      <Divider my={2} />
      
      <Button 
        size="sm" 
        variant="ghost" 
        width="full" 
        onClick={() => setIsExpanded(!isExpanded)}
        rightIcon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
      >
        {isExpanded ? 'Show Less' : 'Show More'}
      </Button>
      
      <Collapse in={isExpanded} animateOpacity>
        <VStack align="stretch" mt={3} spacing={3}>
          {agent.tools && agent.tools.length > 0 && (
            <Box>
              <Flex align="center" mb={1}>
                <Icon as={FiTool} mr={1} />
                <Text fontSize="xs" fontWeight="bold" color="gray.500">TOOLKIT</Text>
              </Flex>
              <Flex wrap="wrap" gap={2}>
                {agent.tools.map((tool, index) => (
                  <Badge key={index} colorScheme="blue" variant="outline">
                    {tool}
                  </Badge>
                ))}
              </Flex>
            </Box>
          )}
          
          {agent.reflection && (
            <Box>
              <Flex align="center" mb={1}>
                <Icon as={FiMessageSquare} mr={1} />
                <Text fontSize="xs" fontWeight="bold" color="gray.500">REFLECTION</Text>
              </Flex>
              <Text fontSize="sm">{agent.reflection}</Text>
            </Box>
          )}
        </VStack>
      </Collapse>
    </Box>
  );
};

export default AgentSandboxCard;
