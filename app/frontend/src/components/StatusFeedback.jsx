import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  Badge, 
  useColorModeValue
} from '@chakra-ui/react';
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
    // Function to fetch agent status data
    const fetchAgentStatus = async () => {
      try {
        // Only show loading on initial fetch, not during polling updates
        if (agents.length === 0) {
          setLoading(true);
        }
        
        // TEMPORARILY DISABLED: Fetch call to agentsService.getAgentStatus()
        // const data = await agentsService.getAgentStatus();
        
        // Use mock data instead
        const mockData = [
          {
            agent_id: 'builder-1',
            name: 'Builder Agent',
            status: 'online',
            type: 'builder',
            description: 'Handles building and deployment tasks',
            last_active: new Date().toISOString(),
            tasks_completed: 12
          },
          {
            agent_id: 'research-1',
            name: 'Research Agent',
            status: 'idle',
            type: 'research',
            description: 'Performs research and data gathering',
            last_active: new Date().toISOString(),
            tasks_completed: 8
          }
        ];
        
        // Compare data before updating state to avoid unnecessary re-renders
        const dataChanged = !isEqual(prevAgentsRef.current, mockData);
        if (dataChanged) {
          if (process.env.NODE_ENV === "development") {
            console.log('Agent status data changed, updating state');
          }
          // Create a deep copy to avoid reference issues
          prevAgentsRef.current = JSON.parse(JSON.stringify(mockData));
          setAgents(mockData);
        } else if (process.env.NODE_ENV === "development") {
          console.log('Agent status data unchanged, skipping update');
        }
        
        if (loading) {
          setLoading(false);
        }
      } catch (err) {
        setError('Agent status service temporarily unavailable');
        setLoading(false);
        if (process.env.NODE_ENV === "development") {
          console.error('Error in mock agent status:', err);
        }
      }
    };

    // Initial fetch
    fetchAgentStatus();

    // Set up polling for real-time updates (every 5 seconds)
    const intervalId = setInterval(fetchAgentStatus, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color
  const getStatusColor = (status) => {
    // Ensure status is a string before attempting to use toLowerCase
    if (!status || typeof status !== 'string') {
      return 'gray';
    }
    
    switch (status.toLowerCase()) {
      case 'online':
      case 'active':
      case 'running':
        return 'green';
      case 'idle':
        return 'blue';
      case 'busy':
        return 'yellow';
      case 'offline':
      case 'error':
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  // Memoize the agents list to prevent unnecessary re-renders
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
      <VStack spacing={4} align="stretch">
        {Array.isArray(memoizedAgents) && memoizedAgents.filter(agent => agent).map((agent) => (
          <Box 
            key={agent?.agent_id || `agent-${Math.random()}`} 
            borderWidth="1px" 
            borderRadius="lg" 
            p={4} 
            shadow="sm" 
            bg={bgColor} 
            borderColor={borderColor}
          >
            <Flex justifyContent="space-between" alignItems="center" mb={3}>
              <Flex alignItems="center">
                <Badge colorScheme={getStatusColor(agent?.status)} mr={2}>
                  {agent?.status || 'Unknown'}
                </Badge>
                <Text fontWeight="bold">{agent?.name || 'Unnamed Agent'}</Text>
              </Flex>
              <Text fontSize="sm" color="gray.500">
                Type: {agent?.type || 'Unknown'}
              </Text>
            </Flex>
            
            <Text mb={3}>{agent?.description || 'No description available'}</Text>
            
            <Flex justifyContent="space-between" fontSize="sm" color="gray.500">
              <Text>Last active: {agent?.last_active ? new Date(agent.last_active).toLocaleString() : 'Unknown'}</Text>
              <Text>Tasks completed: {agent?.tasks_completed || 0}</Text>
            </Flex>
            
            {/* Display errors if any */}
            {agent.errors && Array.isArray(agent.errors) && agent.errors.length > 0 && (
              <Box mt={3} p={3} borderRadius="md" bg="red.50" borderWidth="1px" borderColor="red.200">
                <Text fontWeight="bold" color="red.500" mb={2}>Errors:</Text>
                <VStack spacing={2} align="stretch">
                  {Array.isArray(agent.errors) && agent.errors.map((error, index) => (
                    <Text key={index} fontSize="sm" color="red.600">{error}</Text>
                  ))}
                </VStack>
              </Box>
            )}
          </Box>
        ))}
      </VStack>
    );
  };

  // Consistent container with fixed height and no spinner
  return (
    <Box position="relative" minH="360px">
      {loading && <Box />} {/* noop */}
      <Box>
        {renderContent()}
      </Box>
    </Box>
  );
};

export default StatusFeedback;
