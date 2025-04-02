import React, { useState, useEffect, useMemo, useRef } from 'react';
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
import isEqual from 'lodash.isequal';

const StatusFeedback = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Add ref for tracking render count
  const renderCountRef = useRef(0);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const overlayBg = useColorModeValue('whiteAlpha.800', 'blackAlpha.700');
  
  // Add ref to store previous agents for comparison
  const prevAgentsRef = useRef(null);

  // Diagnostic DOM logging to detect component redraws
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("StatusFeedback component rendered/redrawn");
    }
  });

  // Track render count for debugging
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
        // Only show loading on initial fetch, not during polling updates
        if (agents.length === 0) {
          setLoading(true);
        }
        const data = await controlService.getAgentStatus();
        
        // Compare data before updating state to avoid unnecessary re-renders
        const dataChanged = !isEqual(prevAgentsRef.current, data);
        if (dataChanged) {
          if (process.env.NODE_ENV === "development") {
            console.log('Agent status changed, updating state');
          }
          // Store the new data in ref for future comparisons
          prevAgentsRef.current = JSON.parse(JSON.stringify(data));
          // Use functional update to avoid dependency on previous state
          setAgents(data);
        } else if (process.env.NODE_ENV === "development") {
          console.log('Agent status unchanged, skipping update');
        }
        
        if (loading) {
          setLoading(false);
        }
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

    // Set up polling for real-time updates (every 5 seconds as requested)
    // Increased interval to reduce re-renders while maintaining responsiveness
    const intervalId = setInterval(fetchAgentStatus, 5000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color with defensive coding
  const getStatusColor = (status) => {
    // Ensure status is a string before attempting to use toLowerCase
    if (!status || typeof status !== 'string') {
      return 'gray';
    }
    
    switch (status.toLowerCase()) {
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

  // Memoize the agent list to prevent unnecessary re-renders
  const memoizedAgents = useMemo(() => agents, [agents]);

  // Render content based on state
  const renderContent = () => {
    if (error) {
      return (
        <Box display="flex" alignItems="center" justifyContent="center" h="100%">
          <Text fontSize="lg" color="red.500">{error}</Text>
        </Box>
      );
    }

    // Add safety check for memoizedAgents
    if (!Array.isArray(memoizedAgents) || memoizedAgents.length === 0) {
      return (
        <Box 
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderWidth="1px" 
          borderRadius="md" 
          borderStyle="dashed"
          borderColor={borderColor}
          h="100%"
        >
          <Text color="gray.500">No active agents found</Text>
        </Box>
      );
    }

    return (
      <VStack spacing={4} align="stretch" h="100%">
        {/* Add Array.isArray check before filter and map */}
        {Array.isArray(memoizedAgents) && memoizedAgents.filter(agent => agent).map((agent) => (
          <Box 
            key={agent?.id || `agent-${Math.random()}`} 
            borderWidth="1px" 
            borderRadius="lg" 
            overflow="hidden"
            bg={bgColor}
            borderColor={borderColor}
            minH="120px"
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
              
              <Heading size="md" flex="1">{agent?.name || 'Unknown Agent'}</Heading>
              
              <Badge colorScheme="purple" fontSize="0.8em">
                {agent?.type || 'Unknown Type'}
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
                {/* Error details (expandable) - Add Array.isArray check */}
                {agent.errors && Array.isArray(agent.errors) && agent.errors.length > 0 && (
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
                        {/* Add Array.isArray check before map */}
                        {Array.isArray(agent.errors) && agent.errors.map((error, index) => (
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
    );
  };

  // Consistent container with fixed height and absolute loading overlay
  return (
    <Box position="relative" minH="360px" overflow="hidden" w="full">
      {loading && (
        <Box 
          position="absolute" 
          inset="0" 
          display="flex" 
          alignItems="center" 
          justifyContent="center" 
          bg={overlayBg} 
          zIndex="10"
        >
          <Text fontWeight="medium" fontSize="lg">Loading...</Text>
        </Box>
      )}
      <Box h="100%" w="full">
        {renderContent()}
      </Box>
    </Box>
  );
};

export default StatusFeedback;
