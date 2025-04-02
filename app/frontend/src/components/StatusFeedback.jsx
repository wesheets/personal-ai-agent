import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  Spinner, 
  Badge, 
  Divider, 
  useColorModeValue,
  Heading,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Grid,
  GridItem
} from '@chakra-ui/react';
import { controlService } from '../services/api';
import isEqual from 'lodash/isEqual';

const StatusFeedback = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Add refs for tracking previous state and render count
  const lastAgentStateRef = useRef(null);
  const renderCountRef = useRef(0);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    // Increment render counter for diagnostic purposes
    renderCountRef.current += 1;
    
    if (process.env.NODE_ENV === "development") {
      console.log(`StatusFeedback render count: ${renderCountRef.current}`);
    }
  });

  useEffect(() => {
    // Function to fetch agent status
    const fetchAgentStatus = async () => {
      try {
        setLoading(true);
        const fetchedAgentStatus = await controlService.getAgentStatus();
        
        // Only update state if data has actually changed (deep comparison)
        if (!isEqual(fetchedAgentStatus, lastAgentStateRef.current)) {
          if (process.env.NODE_ENV === "development") {
            console.log('Agent status changed, updating state');
          }
          lastAgentStateRef.current = JSON.parse(JSON.stringify(fetchedAgentStatus));
          setAgents(fetchedAgentStatus);
        } else if (process.env.NODE_ENV === "development") {
          console.log('Agent status unchanged, skipping update');
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch agent status');
        setLoading(false);
        if (process.env.NODE_ENV === "development") {
          console.error('Error fetching agent status:', err);
        }
      }
    };

    // Initial fetch
    fetchAgentStatus();

    // Set up polling for real-time updates (every 2 seconds)
    const intervalId = setInterval(fetchAgentStatus, 2000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'running':
      case 'in_progress':
        return 'blue';
      case 'idle':
      case 'waiting':
      case 'pending':
        return 'yellow';
      case 'error':
      case 'failed':
        return 'red';
      case 'completed':
      case 'success':
        return 'green';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} minH="inherit">
          <Spinner size="xl" />
          <Text mt={4}>Loading agent status...</Text>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} color="red.500" minH="inherit">
          <Text fontSize="lg">{error}</Text>
        </Box>
      </Box>
    );
  }

  return (
    <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
      {agents.length > 0 ? (
        <VStack spacing={4} align="stretch">
          {agents.map((agent) => (
            <Box 
              key={agent.id} 
              borderWidth="1px" 
              borderRadius="lg" 
              overflow="hidden"
              bg={bgColor}
              borderColor={borderColor}
            >
              <Flex 
                p={4} 
                alignItems="center" 
                bg={`${getStatusColor(agent.status)}.50`}
                _dark={{ bg: `${getStatusColor(agent.status)}.900` }}
                borderBottomWidth="1px"
              >
                <Badge 
                  colorScheme={getStatusColor(agent.status)} 
                  fontSize="0.8em" 
                  p={1} 
                  borderRadius="full"
                  mr={3}
                >
                  {agent.status}
                </Badge>
                
                <Heading size="md" flex="1">{agent.name}</Heading>
                
                <Badge colorScheme="purple" fontSize="0.8em">
                  {agent.type}
                </Badge>
              </Flex>
              
              <Box p={4}>
                {agent.current_task && (
                  <Box mb={3}>
                    <Text fontWeight="bold" fontSize="sm" color="gray.500">
                      Current Task:
                    </Text>
                    <Text>{agent.current_task.title}</Text>
                  </Box>
                )}
                
                {agent.completion_state && (
                  <Box mb={3}>
                    <Text fontWeight="bold" fontSize="sm" color="gray.500">
                      Completion:
                    </Text>
                    <Text>{agent.completion_state}</Text>
                  </Box>
                )}
                
                <Accordion allowToggle mt={3}>
                  {/* Error details (expandable) */}
                  {agent.errors && agent.errors.length > 0 && (
                    <AccordionItem>
                      <h2>
                        <AccordionButton>
                          <Box flex="1" textAlign="left">
                            <Flex alignItems="center">
                              <Badge colorScheme="red" mr={2}>
                                {agent.errors.length}
                              </Badge>
                              Error Details
                            </Flex>
                          </Box>
                          <AccordionIcon />
                        </AccordionButton>
                      </h2>
                      <AccordionPanel pb={4}>
                        <VStack spacing={2} align="stretch">
                          {agent.errors.map((error, index) => (
                            <Box 
                              key={index} 
                              p={2} 
                              borderWidth="1px" 
                              borderRadius="md" 
                              borderColor="red.200"
                              bg="red.50"
                              _dark={{ bg: "red.900", borderColor: "red.700" }}
                            >
                              <Text fontSize="xs" color="gray.500">
                                {new Date(error.timestamp).toLocaleString()}
                              </Text>
                              <Text>{error.message}</Text>
                            </Box>
                          ))}
                        </VStack>
                      </AccordionPanel>
                    </AccordionItem>
                  )}
                  
                  {/* Performance metrics */}
                  {agent.metrics && (
                    <AccordionItem>
                      <h2>
                        <AccordionButton>
                          <Box flex="1" textAlign="left">
                            Performance Metrics
                          </Box>
                          <AccordionIcon />
                        </AccordionButton>
                      </h2>
                      <AccordionPanel pb={4}>
                        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                          <Stat>
                            <StatLabel>Tasks Completed</StatLabel>
                            <StatNumber>{agent.metrics.tasks_completed || 0}</StatNumber>
                          </Stat>
                          
                          <Stat>
                            <StatLabel>Avg. Response Time</StatLabel>
                            <StatNumber>{agent.metrics.avg_response_time || 'N/A'}</StatNumber>
                            <StatHelpText>seconds</StatHelpText>
                          </Stat>
                          
                          <Stat>
                            <StatLabel>Success Rate</StatLabel>
                            <StatNumber>{agent.metrics.success_rate || 'N/A'}</StatNumber>
                            <StatHelpText>percent</StatHelpText>
                          </Stat>
                        </Grid>
                      </AccordionPanel>
                    </AccordionItem>
                  )}
                </Accordion>
              </Box>
            </Box>
          ))}
        </VStack>
      ) : (
        <Box 
          textAlign="center" 
          py={10} 
          borderWidth="1px" 
          borderRadius="md" 
          borderStyle="dashed"
          borderColor={borderColor}
          minH="inherit"
        >
          <Text color="gray.500">No active agents found</Text>
        </Box>
      )}
    </Box>
  );
};

export default StatusFeedback;
