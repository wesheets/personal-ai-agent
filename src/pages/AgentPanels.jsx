import React, { useState } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Button,
  VStack,
  HStack,
  useColorMode,
  Card,
  CardBody,
  Text,
  Divider,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Spinner,
  useToast
} from '@chakra-ui/react';
import ApiService from '../api/ApiService';

// Generic Agent Panel component that can be used for Builder, Ops, and Research agents
const AgentPanel = ({ agentType, agentName, agentDescription }) => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  
  // State for form inputs
  const [taskName, setTaskName] = useState('');
  const [taskGoal, setTaskGoal] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  
  // State for task history
  const [taskHistory, setTaskHistory] = useState([]);
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Use the ApiService to delegate the task
      const result = await ApiService.delegateTask(agentType, taskName, taskGoal);
      
      // Set response from API
      setResponse(result);
      
      // Add to history (keeping only last 3)
      setTaskHistory(prev => {
        const newHistory = [
          {
            id: result.task_id || `task-${Date.now()}`,
            name: taskName,
            goal: taskGoal,
            timestamp: new Date().toISOString(),
            status: result.status || 'delegated'
          },
          ...prev
        ];
        
        // Keep only last 3
        return newHistory.slice(0, 3);
      });
      
      // Show success toast
      toast({
        title: 'Task delegated',
        description: `Task "${taskName}" has been delegated to ${agentName}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Reset form
      setTaskName('');
      setTaskGoal('');
    } catch (err) {
      console.error('Error delegating task:', err);
      setError('Failed to delegate task. Please try again.');
      
      // Show error toast
      toast({
        title: 'Error',
        description: 'Failed to delegate task. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      // Always reset submission state to prevent infinite spinner
      setIsSubmitting(false);
    }
  };
  
  return (
    <Box p={4}>
      <Heading mb={6} size="lg">{agentName ?? `${agentType} Agent`}</Heading>
      <Text mb={6} color="gray.500">{agentDescription ?? 'No description available'}</Text>
      
      <Card 
        bg={colorMode === 'light' ? 'white' : 'gray.700'} 
        boxShadow="md" 
        borderRadius="lg"
        mb={8}
      >
        <CardBody>
          <Heading size="md" mb={4}>Delegate Task</Heading>
          
          <form onSubmit={handleSubmit}>
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel>Task Name</FormLabel>
                <Input 
                  value={taskName}
                  onChange={(e) => setTaskName(e.target.value)}
                  placeholder="Enter a name for this task"
                />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>Task Goal</FormLabel>
                <Textarea 
                  value={taskGoal}
                  onChange={(e) => setTaskGoal(e.target.value)}
                  placeholder="Describe what you want the agent to accomplish"
                  rows={4}
                />
              </FormControl>
              
              <Button 
                type="submit" 
                colorScheme="blue" 
                isLoading={isSubmitting}
                loadingText="Submitting..."
                width="full"
              >
                Delegate to {agentName ?? `${agentType} Agent`}
              </Button>
            </VStack>
          </form>
          
          {error && (
            <Alert status="error" mt={4} borderRadius="md">
              <AlertIcon />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {response && (
            <Alert status="success" mt={4} borderRadius="md">
              <AlertIcon />
              <VStack align="start" spacing={1} width="full">
                <AlertTitle>Task Delegated</AlertTitle>
                <AlertDescription>
                  <Text>Task ID: {response?.task_id ?? 'Unknown'}</Text>
                  <Text>Status: {response?.status ?? 'Unknown'}</Text>
                  <Text>{response?.message ?? ''}</Text>
                </AlertDescription>
              </VStack>
            </Alert>
          )}
        </CardBody>
      </Card>
      
      {/* Task History */}
      {taskHistory.length > 0 && (
        <Card 
          bg={colorMode === 'light' ? 'white' : 'gray.700'} 
          boxShadow="md" 
          borderRadius="lg"
        >
          <CardBody>
            <Heading size="md" mb={4}>Recent Tasks</Heading>
            <VStack spacing={4} align="stretch">
              {taskHistory.map((task) => (
                <Box 
                  key={task?.id ?? Math.random()} 
                  p={4} 
                  borderRadius="md" 
                  bg={colorMode === 'light' ? 'gray.50' : 'gray.600'}
                >
                  <HStack justifyContent="space-between" mb={2}>
                    <Heading size="sm">{task?.name ?? 'Unnamed Task'}</Heading>
                    <Badge colorScheme={task?.status === 'delegated' ? 'green' : 'blue'}>
                      {task?.status ?? 'unknown'}
                    </Badge>
                  </HStack>
                  <Text noOfLines={2} mb={2}>{task?.goal ?? 'No description'}</Text>
                  <Text fontSize="xs" color="gray.500">
                    {new Date(task?.timestamp ?? Date.now()).toLocaleString()}
                  </Text>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}
    </Box>
  );
};

// Specific agent implementations
export const BuilderAgent = () => (
  <AgentPanel 
    agentType="builder" 
    agentName="Builder Agent" 
    agentDescription="Creates and manages development projects, builds applications, and implements features."
  />
);

export const OpsAgent = () => (
  <AgentPanel 
    agentType="ops" 
    agentName="Operations Agent" 
    agentDescription="Handles operations, infrastructure tasks, deployments, and system maintenance."
  />
);

export const ResearchAgent = () => (
  <AgentPanel 
    agentType="research" 
    agentName="Research Agent" 
    agentDescription="Conducts research, gathers information, and analyzes data from various sources."
  />
);
