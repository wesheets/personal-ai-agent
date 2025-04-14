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
import { FiCpu, FiActivity, FiTool, FiBookOpen, FiThumbsUp, FiGrid, FiTarget } from 'react-icons/fi';
import orchestratorAgent from '../data/orchestratorAgent';

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
        return 'teal';
      case 'nova':
        return 'orange';
      case 'orchestrator':
        return 'purple';
      default:
        return 'gray';
    }
  };

  // Check if agent is system agent (Orchestrator)
  const isSystemAgent = agent.id.toLowerCase() === 'orchestrator';

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
            <Icon as={isSystemAgent ? FiGrid : FiCpu} />
          </Box>
          <Box>
            <Flex align="center">
              <Text fontWeight="bold">{agent.name}</Text>
              {isSystemAgent && (
                <Badge ml={2} colorScheme="purple" variant="subtle">System</Badge>
              )}
            </Flex>
            <Badge colorScheme={getStatusColor(agent.status)}>
              {agent.status.toUpperCase()}
            </Badge>
          </Box>
        </Flex>
      </Flex>
      
      {/* Agent content */}
      <Box p={3}>
        <VStack align="stretch" spacing={3}>
          {/* Active Task or Goal Processing for Orchestrator */}
          <Box>
            <HStack mb={1}>
              <Icon as={isSystemAgent ? FiTarget : FiActivity} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                {isSystemAgent ? "GOAL PROCESSING" : "ACTIVE TASK"}
              </Text>
            </HStack>
            <Text fontSize="sm">{agent.activeTask}</Text>
          </Box>
          
          {/* Last Memory Entry */}
          <Box>
            <HStack mb={1}>
              <Icon as={FiBookOpen} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                {isSystemAgent ? "LATEST ACTIVITY" : "LAST MEMORY"}
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
          
          {/* Reflection or Thinking State for Orchestrator */}
          <Box>
            <HStack mb={1}>
              <Icon as={FiThumbsUp} color="gray.500" />
              <Text fontSize="sm" fontWeight="medium" color="gray.500">
                {isSystemAgent ? "THINKING STATE" : "REFLECTION"}
              </Text>
            </HStack>
            <Text fontSize="sm" fontStyle="italic" color={isSystemAgent ? "purple.500" : "inherit"}>
              "{agent.reflection}"
            </Text>
          </Box>
        </VStack>
      </Box>
    </Box>
  );
};

// Component to display both regular agents and the Orchestrator
const AgentSandboxPanel = () => {
  // Mock agents - would be replaced with actual data from API
  const agents = [
    orchestratorAgent,
    {
      id: 'hal',
      name: 'HAL',
      status: 'active',
      activeTask: 'Researching React state management',
      lastMemoryEntry: 'User requested comparison of Context API and Redux',
      tools: ['search.web', 'copy.generate', 'code.analyze'],
      reflection: 'The user seems to be building a React application and needs guidance on state management approaches.'
    },
    {
      id: 'ash',
      name: 'ASH',
      status: 'idle',
      activeTask: 'None',
      lastMemoryEntry: 'Completed data analysis task',
      tools: ['data.analyze', 'chart.create', 'file.read'],
      reflection: 'Ready for new data processing tasks.'
    }
  ];

  return (
    <Box>
      {agents.map((agent) => (
        <AgentSandboxCard key={agent.id} agent={agent} />
      ))}
    </Box>
  );
};

export default AgentSandboxPanel;
