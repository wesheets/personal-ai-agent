import React, { useState, useEffect, useRef } from 'react';
import isEqual from 'lodash.isequal';
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

const GoalLoopVisualization = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const prevGoalsRef = useRef([]);

  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchGoals = async () => {
      try {
        const data = await goalsService.getGoals();
        if (!isEqual(prevGoalsRef.current, data)) {
          setGoals(data);
          prevGoalsRef.current = JSON.parse(JSON.stringify(data));
        }
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch goals data');
        setLoading(false);
        if (process.env.NODE_ENV === 'development') {
          console.error('Error fetching goals:', err);
        }
      }
    };

    fetchGoals();
    const intervalId = setInterval(fetchGoals, 5000);
    return () => clearInterval(intervalId);
  }, []);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'green';
      case 'in_progress': return 'blue';
      case 'failed': return 'red';
      case 'pending': return 'yellow';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} minH="inherit">
          <Spinner size="xl" />
          <Text mt={4}>Loading goal data...</Text>
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
    <Box h="100%" minH="300px" overflow="hidden" display="flex" flexDir="column" justifyContent="flex-start">
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

            <Box>
              <Heading size="sm" mb={2}>Timeline</Heading>
              {goal.tasks && goal.tasks.length > 0 ? (
                <VStack spacing={0} align="stretch" position="relative">
                  {goal.tasks
                    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
                    .map((task) => (
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
    </Box>
  );
};

export default GoalLoopVisualization;
