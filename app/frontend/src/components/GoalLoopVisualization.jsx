import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  Badge, 
  Divider, 
  useColorModeValue,
  Heading
} from '@chakra-ui/react';
import { goalsService } from '../services/api';
import isEqual from 'lodash.isequal';

// Component for visualizing the goal loop with subtasks and agent assignments
const GoalLoopVisualization = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Add ref for tracking render count
  const renderCountRef = useRef(0);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const overlayBg = useColorModeValue('whiteAlpha.800', 'blackAlpha.700');
  
  // Add ref to store previous goals for comparison
  const prevGoalsRef = useRef(null);

  // Diagnostic DOM logging to detect component redraws
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("GoalLoopVisualization component rendered/redrawn");
    }
  });

  // Track render count for debugging
  useEffect(() => {
    // Increment render counter for diagnostic purposes
    renderCountRef.current += 1;
    
    if (process.env.NODE_ENV === "development") {
      console.log(`GoalLoopVisualization render count: ${renderCountRef.current}`);
    }
  });

  useEffect(() => {
    // Function to fetch goals data from the API
    const fetchGoals = async () => {
      try {
        // Only show loading on initial fetch, not during polling updates
        if (goals.length === 0) {
          setLoading(true);
        }
        const data = await goalsService.getGoals();
        
        // Compare data before updating state to avoid unnecessary re-renders
        const dataChanged = !isEqual(prevGoalsRef.current, data);
        if (dataChanged) {
          if (process.env.NODE_ENV === "development") {
            console.log('Goals data changed, updating state');
          }
          // Create a deep copy to avoid reference issues
          prevGoalsRef.current = JSON.parse(JSON.stringify(data));
          setGoals(data);
        } else if (process.env.NODE_ENV === "development") {
          console.log('Goals data unchanged, skipping update');
        }
        
        if (loading) {
          setLoading(false);
        }
      } catch (err) {
        setError('Failed to fetch goals data');
        setLoading(false);
        if (process.env.NODE_ENV === "development") {
          console.error('Error fetching goals:', err);
        }
      }
    };

    // Initial fetch
    fetchGoals();

    // Set up polling for real-time updates (every 5 seconds as requested)
    const intervalId = setInterval(fetchGoals, 5000);

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
      case 'completed':
        return 'green';
      case 'in_progress':
        return 'blue';
      case 'failed':
        return 'red';
      case 'pending':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  // Memoize the goals list to prevent unnecessary re-renders
  const memoizedGoals = useMemo(() => goals, [goals]);

  // Render content based on state
  const renderContent = () => {
    if (error) {
      return (
        <Box display="flex" alignItems="center" justifyContent="center" h="100%">
          <Text fontSize="lg" color="red.500">{error}</Text>
        </Box>
      );
    }

    if (memoizedGoals.length === 0) {
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
          <Text color="gray.500">No active goals found</Text>
        </Box>
      );
    }

    return (
      <VStack spacing={6} align="stretch" h="100%">
        {memoizedGoals.filter(goal => goal).map((goal) => (
          <Box 
            key={goal?.goal_id || `goal-${Math.random()}`} 
            borderWidth="1px" 
            borderRadius="lg" 
            p={4} 
            shadow="sm" 
            bg={bgColor} 
            borderColor={borderColor}
          >
            <Flex justifyContent="space-between" alignItems="center" mb={3}>
              <Heading size="md">
                <Badge colorScheme={getStatusColor(goal?.status)} mr={2}>
                  {goal?.status || 'Unknown'}
                </Badge>
                {goal?.title || 'Untitled Goal'}
              </Heading>
              <Text fontSize="sm" color="gray.500">
                Created: {goal?.created_at ? new Date(goal.created_at).toLocaleString() : 'Unknown'}
              </Text>
            </Flex>
            
            <Text mb={4}>{goal?.description || 'No description available'}</Text>
            
            {/* Subtasks visualization */}
            <Box mb={4}>
              <Heading size="sm" mb={2}>Subtasks</Heading>
              {goal?.tasks && goal.tasks.length > 0 ? (
                <VStack spacing={3} align="stretch">
                  {goal.tasks.filter(task => task).map((task) => (
                    <Box 
                      key={task?.task_id || `task-${Math.random()}`} 
                      p={3} 
                      borderWidth="1px" 
                      borderRadius="md" 
                      borderLeftWidth="4px"
                      borderLeftColor={`${getStatusColor(task?.status)}.500`}
                    >
                      <Flex justifyContent="space-between" alignItems="center" mb={1}>
                        <Text fontWeight="bold">{task?.title || 'Untitled Task'}</Text>
                        <Badge colorScheme={getStatusColor(task?.status)}>
                          {task?.status || 'Unknown'}
                        </Badge>
                      </Flex>
                      
                      <Text fontSize="sm" mb={2}>{task?.description || 'No description'}</Text>
                      
                      <Flex gap={2} flexWrap="wrap" fontSize="xs">
                        <Badge colorScheme="purple">
                          Agent: {task?.assigned_agent || 'Unassigned'}
                        </Badge>
                        
                        {task?.started_at && (
                          <Text color="gray.500">
                            Started: {new Date(task.started_at).toLocaleString()}
                          </Text>
                        )}
                        
                        {task?.completed_at && (
                          <Text color="gray.500">
                            Completed: {new Date(task.completed_at).toLocaleString()}
                          </Text>
                        )}
                      </Flex>
                    </Box>
                  ))}
                </VStack>
              ) : (
                <Box 
                  textAlign="center" 
                  py={3} 
                  borderWidth="1px" 
                  borderRadius="md" 
                  borderStyle="dashed"
                  borderColor={borderColor}
                >
                  <Text color="gray.500">No subtasks found</Text>
                </Box>
              )}
            </Box>
            
            {/* Timeline visualization */}
            <Box>
              <Heading size="sm" mb={2}>Timeline</Heading>
              {goal?.tasks && goal.tasks.length > 0 ? (
                <VStack spacing={0} align="stretch" position="relative">
                  {goal.tasks
                    .filter(task => task?.created_at)
                    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
                    .map((task, index) => (
                      <Flex key={`timeline-${task?.task_id || index}`} mb={2}>
                        <Box 
                          w="12px" 
                          h="12px" 
                          borderRadius="full" 
                          bg={`${getStatusColor(task?.status)}.500`} 
                          mt={1}
                          mr={3}
                        />
                        <Box flex="1">
                          <Text fontWeight="medium">{task?.title || 'Untitled Task'}</Text>
                          <Flex fontSize="xs" color="gray.500">
                            <Text mr={2}>{task?.status || 'Unknown'}</Text>
                            <Text>{task?.created_at ? new Date(task.created_at).toLocaleString() : 'Unknown time'}</Text>
                          </Flex>
                        </Box>
                      </Flex>
                    ))}
                </VStack>
              ) : (
                <Box 
                  textAlign="center" 
                  py={3} 
                  borderWidth="1px" 
                  borderRadius="md" 
                  borderStyle="dashed"
                  borderColor={borderColor}
                >
                  <Text color="gray.500">No timeline data available</Text>
                </Box>
              )}
            </Box>
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

export default GoalLoopVisualization;
