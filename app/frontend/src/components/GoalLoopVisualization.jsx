import React, { useState, useEffect } from 'react';
<<<<<<< HEAD
=======
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
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)
import { goalsService } from '../services/api';

// Component for visualizing the goal loop with subtasks and agent assignments
const GoalLoopVisualization = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
<<<<<<< HEAD
=======
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)

  useEffect(() => {
    // Function to fetch goals data from the API
    const fetchGoals = async () => {
      try {
        setLoading(true);
        const data = await goalsService.getGoals();
        setGoals(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch goals data');
        setLoading(false);
        console.error('Error fetching goals:', err);
      }
    };

    // Initial fetch
    fetchGoals();

    // Set up polling for real-time updates (every 5 seconds)
    const intervalId = setInterval(fetchGoals, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color
  const getStatusColor = (status) => {
<<<<<<< HEAD
    switch (status.toLowerCase()) {
      case 'completed':
        return 'status-completed';
      case 'in_progress':
        return 'status-active';
      case 'failed':
        return 'status-error';
      case 'pending':
        return 'status-paused';
      default:
        return '';
=======
    switch (status?.toLowerCase()) {
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
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)
    }
  };

  if (loading) {
<<<<<<< HEAD
    return <div className="loading">Loading goal data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (goals.length === 0) {
    return <div className="empty-state">No active goals found</div>;
  }

  return (
    <div className="goal-visualization">
      {goals.map((goal) => (
        <div key={goal.goal_id} className="goal-container">
          <div className="goal-header">
            <h3>
              <span className={`status-indicator ${getStatusColor(goal.status)}`}></span>
              {goal.title}
            </h3>
            <div className="goal-meta">
              <span>Created: {new Date(goal.created_at).toLocaleString()}</span>
              <span>Status: {goal.status}</span>
            </div>
          </div>
          
          <div className="goal-description">{goal.description}</div>
          
          {/* Subtasks visualization */}
          <div className="subtasks">
            <h4>Subtasks</h4>
            {goal.tasks && goal.tasks.length > 0 ? (
              <div className="subtask-tree">
                {goal.tasks.map((task) => (
                  <div key={task.task_id} className="subtask-item">
                    <div className="subtask-header">
                      <span className={`status-indicator ${getStatusColor(task.status)}`}></span>
                      <span className="subtask-title">{task.title}</span>
                      <span className="subtask-agent">Agent: {task.assigned_agent || 'Unassigned'}</span>
                    </div>
                    <div className="subtask-details">
                      <div className="subtask-description">{task.description}</div>
                      <div className="subtask-meta">
                        <span>Status: {task.status}</span>
                        {task.started_at && <span>Started: {new Date(task.started_at).toLocaleString()}</span>}
                        {task.completed_at && <span>Completed: {new Date(task.completed_at).toLocaleString()}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">No subtasks found</div>
            )}
          </div>
          
          {/* Timeline visualization */}
          <div className="timeline">
            <h4>Timeline</h4>
            <div className="timeline-container">
              {goal.tasks && goal.tasks
                .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
                .map((task, index) => (
                  <div key={`timeline-${task.task_id}`} className="timeline-item">
                    <div className={`timeline-marker ${getStatusColor(task.status)}`}></div>
                    <div className="timeline-content">
                      <h5>{task.title}</h5>
                      <div className="timeline-meta">
                        <span>{task.status}</span>
                        <span>{new Date(task.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      ))}
    </div>
=======
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading goal data...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} color="red.500">
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
      >
        <Text color="gray.500">No active goals found</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      {goals.map((goal) => (
        <Box 
          key={goal.goal_id} 
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
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)
  );
};

export default GoalLoopVisualization;
