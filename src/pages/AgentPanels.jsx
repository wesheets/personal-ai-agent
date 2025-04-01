import React, { useState, useEffect, useRef } from 'react';
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
  useToast,
  Code,
  Switch
} from '@chakra-ui/react';
import ApiService from '../api/ApiService';

// Generic Agent Panel component that can be used for Builder, Ops, and Research agents
const AgentPanel = ({ agentType, agentName, agentDescription }) => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  const mountedRef = useRef(true);
  
  // State for form inputs
  const [taskName, setTaskName] = useState('');
  const [taskGoal, setTaskGoal] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  
  // State for task history
  const [taskHistory, setTaskHistory] = useState([]);
  
  // Debug state
  const [renderCount, setRenderCount] = useState(0);
  const [useSimulatedResponse, setUseSimulatedResponse] = useState(false);
  const [debugLogs, setDebugLogs] = useState([]);
  
  // Track render count for debugging
  useEffect(() => {
    setRenderCount(prev => prev + 1);
    
    // Cleanup function to track component unmounting
    return () => {
      mountedRef.current = false;
    };
  }, []);
  
  // Add debug log
  const addDebugLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugLogs(prev => [...prev.slice(-9), `${timestamp}: ${message}`]);
    console.log(`[${timestamp}] ${message}`);
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    addDebugLog("🌀 Submitting task...");
    addDebugLog(`Payload: ${JSON.stringify({ agentType, taskName, taskGoal })}`);
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      let result;
      
      if (useSimulatedResponse) {
        addDebugLog("🔄 Using simulated response");
        await new Promise(resolve => setTimeout(resolve, 500));
        result = { status: "success", message: "Fake success", task_id: `fake-${Date.now()}` };
      } else {
        // Use the ApiService to delegate the task
        addDebugLog("📡 Calling ApiService.delegateTask()");
        result = await ApiService.delegateTask(agentType, taskName, taskGoal);
      }
      
      addDebugLog(`✅ Delegate response: ${JSON.stringify(result)}`);
      
      // Check if component is still mounted
      if (!mountedRef.current) {
        addDebugLog("⚠️ Component unmounted before state update");
        return;
      }
      
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
      
      // Reset form
      setTaskName('');
      setTaskGoal('');
      
      // Show success toast - uncommented for testing
      toast({
        title: 'Task delegated',
        description: `Task "${taskName}" has been delegated to ${agentName}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      addDebugLog(`❌ Error delegating task: ${err.message}`);
      console.error('Error delegating task:', err);
      
      // Check if component is still mounted
      if (!mountedRef.current) {
        addDebugLog("⚠️ Component unmounted before error state update");
        return;
      }
      
      setError(`Failed to delegate task: ${err.message}`);
      
      // Show error toast - uncommented for testing
      toast({
        title: 'Error',
        description: `Failed to delegate task: ${err.message}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      // Always reset submission state to prevent infinite spinner
      addDebugLog("🛑 Spinner reset triggered");
      
      // Use setTimeout to ensure this runs after React's current execution cycle
      setTimeout(() => {
        if (mountedRef.current) {
          setIsSubmitting(false);
          addDebugLog("✅ Spinner reset completed");
        } else {
          addDebugLog("⚠️ Component unmounted before spinner reset");
        }
      }, 0);
    }
  };
  
  return (
    <Box p={4}>
      <Heading mb={6} size="lg">{agentName ?? `${agentType} Agent`}</Heading>
      <Text mb={6} color="gray.500">{agentDescription ?? 'No description available'}</Text>
      
      {/* Debug State Display */}
      <Card 
        bg={colorMode === 'light' ? 'yellow.50' : 'yellow.900'} 
        boxShadow="md" 
        borderRadius="lg"
        mb={4}
        p={3}
      >
        <Heading size="sm" mb={2}>Debug State</Heading>
        <HStack mb={2}>
          <Text>Spinner State: <Code>{isSubmitting.toString()}</Code></Text>
          <Text>Error State: <Code>{error ? "Error" : "null"}</Code></Text>
          <Text>Response: <Code>{response ? "Present" : "null"}</Code></Text>
          <Text>Render Count: <Code>{renderCount}</Code></Text>
        </HStack>
        <HStack mb={2}>
          <Text>Use Simulated Response:</Text>
          <Switch 
            isChecked={useSimulatedResponse} 
            onChange={() => setUseSimulatedResponse(!useSimulatedResponse)}
            colorScheme="green"
          />
        </HStack>
        <Box mt={2} maxH="150px" overflowY="auto" bg={colorMode === 'light' ? 'gray.50' : 'gray.700'} p={2} borderRadius="md">
          <Heading size="xs" mb={1}>Debug Logs:</Heading>
          {debugLogs.map((log, index) => (
            <Text key={index} fontSize="xs" fontFamily="monospace">{log}</Text>
          ))}
        </Box>
      </Card>
      
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
