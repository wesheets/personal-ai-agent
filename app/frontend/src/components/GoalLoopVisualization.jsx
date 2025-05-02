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
  Alert,
  AlertIcon,
  Select
} from '@chakra-ui/react';
import isEqual from 'lodash.isequal';

// Component for visualizing the goal loop with subtasks and agent assignments
const GoalLoopVisualization = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSource, setDataSource] = useState('loop'); // 'loop' or 'memory'
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Add ref to store previous goals for comparison
  const prevGoalsRef = useRef(null);

  // Diagnostic DOM logging to detect component redraws
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("GoalLoopVisualization component rendered/redrawn");
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
        
        // Determine which API endpoint to use based on dataSource
        const endpoint = dataSource === 'loop' ? '/api/loop/plan' : '/api/memory/thread';
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Transform data based on source format
        const transformedData = dataSource === 'loop' 
          ? transformLoopData(data)
          : transformMemoryData(data);
        
        // Compare data before updating state to avoid unnecessary re-renders
        const dataChanged = !isEqual(prevGoalsRef.current, transformedData);
        if (dataChanged) {
          prevGoalsRef.current = transformedData;
          setGoals(transformedData);
        }
        
        if (loading) {
          setLoading(false);
        }
        
        setError(null);
      } catch (err) {
        console.error(`Error fetching data from ${dataSource} API:`, err);
        setError(`Failed to fetch data from ${dataSource === 'loop' ? 'loop plan' : 'memory thread'} API`);
        setLoading(false);
        
        // Fallback to mock data if in development
        if (process.env.NODE_ENV === "development") {
          setGoals(mockGoals);
        }
      }
    };

    // Initial fetch
    fetchGoals();

    // Set up polling for real-time updates (every 5 seconds as requested)
    const intervalId = setInterval(fetchGoals, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [dataSource]); // Re-run effect when dataSource changes

  // Transform loop data to goal format
  const transformLoopData = (data) => {
    // Handle missing or malformed data
    if (!data || !Array.isArray(data.plans)) {
      return [];
    }
    
    return data.plans.map(plan => ({
      goal_id: plan.plan_id || `plan-${Math.random()}`,
      title: plan.title || 'Untitled Plan',
      description: plan.description || 'No description available',
      status: plan.status || 'unknown',
      created_at: plan.created_at || new Date().toISOString(),
      tasks: Array.isArray(plan.steps) ? plan.steps.map(step => ({
        task_id: step.step_id || `step-${Math.random()}`,
        title: step.title || `Step ${step.step_number || '?'}`,
        description: step.description || 'No description',
        status: step.status || 'unknown',
        assigned_agent: step.agent || 'system',
        started_at: step.started_at,
        completed_at: step.completed_at,
        created_at: step.created_at || new Date().toISOString()
      })) : []
    }));
  };
  
  // Transform memory data to goal format
  const transformMemoryData = (data) => {
    // Handle missing or malformed data
    if (!data || !Array.isArray(data.threads)) {
      return [];
    }
    
    return data.threads.map(thread => ({
      goal_id: thread.thread_id || `thread-${Math.random()}`,
      title: thread.title || 'Untitled Thread',
      description: thread.summary || 'No summary available',
      status: thread.status || 'unknown',
      created_at: thread.created_at || new Date().toISOString(),
      tasks: Array.isArray(thread.messages) ? thread.messages.map(msg => ({
        task_id: msg.message_id || `msg-${Math.random()}`,
        title: msg.title || 'Message',
        description: msg.content || 'No content',
        status: msg.processed ? 'completed' : 'pending',
        assigned_agent: msg.agent || 'system',
        created_at: msg.timestamp || new Date().toISOString()
      })) : []
    }));
  };

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

  if (loading) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Flex direction="column" align="center">
          <Spinner size="xl" mb={4} />
          <Text>Loading goal data...</Text>
        </Flex>
      </Box>
    );
  }

  return (
    <Box>
      {/* Data source selector */}
      <Flex justifyContent="space-between" alignItems="center" mb={4}>
        <Heading size="md">Goal Loop Visualization</Heading>
        <Select 
          value={dataSource} 
          onChange={(e) => setDataSource(e.target.value)}
          width="auto"
          size="sm"
        >
          <option value="loop">Loop Plan Data</option>
          <option value="memory">Memory Thread Data</option>
        </Select>
      </Flex>
      
      {/* Error display */}
      {error && (
        <Alert status="error" mb={4} borderRadius="md">
          <AlertIcon />
          {error}
        </Alert>
      )}
      
      {/* Empty state */}
      {!error && memoizedGoals.length === 0 && (
        <Box 
          minH="200px"
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderWidth="1px" 
          borderRadius="md" 
          borderStyle="dashed"
          borderColor={borderColor}
        >
          <Text color="gray.500">No active goals found</Text>
        </Box>
      )}
      
      {/* Goals display */}
      <VStack spacing={6} align="stretch" minH="inherit">
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
      
      {/* Data source indicator */}
      <Text fontSize="xs" textAlign="right" mt={2} color="gray.500">
        Data source: {dataSource === 'loop' ? 'Loop Plan API' : 'Memory Thread API'}
      </Text>
    </Box>
  );
};

// Mock data for development and fallback
const mockGoals = [
  {
    goal_id: 'goal-1',
    title: 'Implement UI Components',
    description: 'Create and integrate all required UI components for the dashboard',
    status: 'in_progress',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    tasks: [
      {
        task_id: 'task-1',
        title: 'Design component mockups',
        description: 'Create mockups for all required components',
        status: 'completed',
        assigned_agent: 'designer',
        started_at: new Date(Date.now() - 86400000).toISOString(),
        completed_at: new Date(Date.now() - 43200000).toISOString(),
        created_at: new Date(Date.now() - 86400000).toISOString()
      },
      {
        task_id: 'task-2',
        title: 'Implement React components',
        description: 'Create React components based on the approved designs',
        status: 'in_progress',
        assigned_agent: 'developer',
        started_at: new Date(Date.now() - 43200000).toISOString(),
        created_at: new Date(Date.now() - 43200000).toISOString()
      },
      {
        task_id: 'task-3',
        title: 'Connect to backend APIs',
        description: 'Integrate components with backend data sources',
        status: 'pending',
        assigned_agent: 'developer',
        created_at: new Date(Date.now() - 21600000).toISOString()
      }
    ]
  },
  {
    goal_id: 'goal-2',
    title: 'Optimize Performance',
    description: 'Improve application performance and loading times',
    status: 'pending',
    created_at: new Date(Date.now() - 172800000).toISOString(),
    tasks: [
      {
        task_id: 'task-4',
        title: 'Audit current performance',
        description: 'Measure and document current performance metrics',
        status: 'pending',
        assigned_agent: 'analyst',
        created_at: new Date(Date.now() - 172800000).toISOString()
      },
      {
        task_id: 'task-5',
        title: 'Implement code splitting',
        description: 'Add code splitting to improve initial load time',
        status: 'pending',
        assigned_agent: 'developer',
        created_at: new Date(Date.now() - 172800000).toISOString()
      }
    ]
  }
];

export default GoalLoopVisualization;
