import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  Spinner, 
  Badge, 
  Divider, 
  useColorModeValue,
  Heading
} from '@chakra-ui/react';
import { goalsService } from '../services/api';

// Component for visualizing the goal loop with subtasks and agent assignments
const GoalLoopVisualization = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

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
        const dataChanged = JSON.stringify(data) !== JSON.stringify(goals);
        if (dataChanged) {
          setGoals(data);
        }
        
        if (loading) {
          setLoading(false);
        }
      } catch (err) {
        setError('Failed to fetch goals data');
        setLoading(false);
        console.error('Error fetching goals:', err);
      }
    };

    // Initial fetch
    fetchGoals();

    // Set up polling for real-time updates (keep at 5 seconds as it's already reasonable)
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

  if (loading) {
    return (
      <Box textAlign="center" py={10} minH="200px" display="flex" flexDirection="column" justifyContent="center">
        <Spinner size="xl" mx="auto" />
        <Text mt={4}>Loading goal data...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} minH="200px" display="flex" flexDirection="column" justifyContent="center" color="red.500">
        <Text fontSize="lg">{error}</Text>
      </Box>
    );
  }

  if (goals.length === 0) {
    return (
      <Box 
        textAlign="center" 
        py={10} 
        borderWidth="1px" 
        borderRadius="md" 
        borderStyle="dashed"
        borderColor={borderColor}
        minH="200px"
        display="flex"
        flexDirection="column"
        justifyContent="center"
      >
        <Text color="gray.500">No active goals found</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch" minH="200px">
      {goals.filter(goal => goal).map((goal) => (
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
              <Badge colorScheme={getStatusColor(goal.status)} mr={2}>
                {goal.status}
              </Badge>
              {goal.title}
            </Heading>
            <Text fontSize="sm" color="gray.500">
              Created: {new Date(goal.created_at).toLocaleString()}
            </Text>
          </Flex>
          
          <Text mb={4}>{goal.description}</Text>
          
          {/* Subtasks visualization */}
          <Box mb={4}>
            <Heading size="sm" mb={2}>Subtasks</Heading>
            {goal.tasks && goal.tasks.length > 0 ? (
              <VStack spacing={3} align="stretch">
                {goal.tasks.map((task) => (
                  <Box 
                    key={task.task_id} 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    borderLeftWidth="4px"
                    borderLeftColor={`${getStatusColor(task.status)}.500`}
                  >
                    <Flex justifyContent="space-between" alignItems="center" mb={1}>
                      <Text fontWeight="bold">{task.title}</Text>
                      <Badge colorScheme={getStatusColor(task.status)}>
                        {task.status}
                      </Badge>
                    </Flex>
                    
                    <Text fontSize="sm" mb={2}>{task.description}</Text>
                    
                    <Flex gap={2} flexWrap="wrap" fontSize="xs">
                      <Badge colorScheme="purple">
                        Agent: {task.assigned_agent || 'Unassigned'}
                      </Badge>
                      
                      {task.started_at && (
                        <Text color="gray.500">
                          Started: {new Date(task.started_at).toLocaleString()}
                        </Text>
                      )}
                      
                      {task.completed_at && (
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
            {goal.tasks && goal.tasks.length > 0 ? (
              <VStack spacing={0} align="stretch" position="relative">
                {goal.tasks
                  .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
                  .map((task, index) => (
                    <Flex key={`timeline-${task.task_id}`} mb={2}>
                      <Box 
                        w="12px" 
                        h="12px" 
                        borderRadius="full" 
                        bg={`${getStatusColor(task.status)}.500`} 
                        mt={1}
                        mr={3}
                      />
                      <Box flex="1">
                        <Text fontWeight="medium">{task.title}</Text>
                        <Flex fontSize="xs" color="gray.500">
                          <Text mr={2}>{task.status}</Text>
                          <Text>{new Date(task.created_at).toLocaleString()}</Text>
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

export default GoalLoopVisualization;
