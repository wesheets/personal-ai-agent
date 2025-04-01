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
  const failsafeTriggeredRef = useRef(false);
  
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
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());
  const [debugVisible, setDebugVisible] = useState(true);
  
  // Track render count for debugging
  useEffect(() => {
    setRenderCount(prev => prev + 1);
    setLastUpdated(new Date().toLocaleTimeString());
    
    // Cleanup function to track component unmounting
    return () => {
      mountedRef.current = false;
    };
  }, []);
  
  // ENHANCED: Failsafe timeout to force spinner reset after 8 seconds
  useEffect(() => {
    if (!isSubmitting) {
      // Reset the failsafe trigger when submission completes
      failsafeTriggeredRef.current = false;
      return;
    }
    
    console.log('⏱️ Starting failsafe timeout for spinner reset');
    addDebugLog('⏱️ Starting failsafe timeout (8s)');
    
    // Primary failsafe - 8 seconds
    const timeout = setTimeout(() => {
      console.log('🔥 Failsafe reset triggered');
      console.warn('⏱️ Failsafe triggered: Forcing spinner reset after 8s');
      
      // Mark that failsafe was triggered
      failsafeTriggeredRef.current = true;
      
      // Only update state if component is still mounted
      if (mountedRef.current) {
        setIsSubmitting(false);
        addDebugLog('⏱️ FAILSAFE: Forced spinner reset after 8s timeout');
        
        // Show toast notification about failsafe
        toast({
          title: 'Submission timeout',
          description: 'Task submission took too long. The form has been reset.',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
    }, 8000);
    
    // Secondary ultra-failsafe - 12 seconds (in case the first one fails)
    const ultraFailsafe = setTimeout(() => {
      if (mountedRef.current && isSubmitting) {
        console.log('🔥🔥 ULTRA-FAILSAFE: Last resort spinner reset triggered');
        setIsSubmitting(false);
        addDebugLog('🔥🔥 ULTRA-FAILSAFE: Last resort spinner reset at 12s');
      }
    }, 12000);
    
    // Clean up both timeouts
    return () => {
      clearTimeout(timeout);
      clearTimeout(ultraFailsafe);
    };
  }, [isSubmitting, toast]);
  
  // Add debug log
  const addDebugLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    
    // Only update state if component is still mounted
    if (mountedRef.current) {
      setDebugLogs(prev => [...prev.slice(-9), `${timestamp}: ${message}`]);
      setLastUpdated(timestamp);
    }
    
    // Always log to console
    console.log(`[${timestamp}] ${message}`);
  };
  
  // Force reset spinner state (emergency function)
  const forceResetSpinner = () => {
    console.log('🚨 Manual spinner reset triggered');
    if (mountedRef.current) {
      setIsSubmitting(false);
      addDebugLog('🚨 Manual spinner reset triggered by user');
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 Submitting task:', { taskName, agentType, taskGoal });
    addDebugLog("🌀 Submitting task...");
    addDebugLog(`Payload: ${JSON.stringify({ agentType, taskName, taskGoal })}`);
    
    // Reset failsafe trigger flag
    failsafeTriggeredRef.current = false;
    
    // Set submitting state
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
        console.log('✅ Submission complete:', result);
      }
      
      addDebugLog(`✅ Delegate response: ${JSON.stringify(result)}`);
      
      // Check if component is still mounted
      if (!mountedRef.current) {
        addDebugLog("⚠️ Component unmounted before state update");
        return;
      }
      
      // Check if failsafe was already triggered
      if (failsafeTriggeredRef.current) {
        addDebugLog("⚠️ Failsafe already triggered, skipping success state updates");
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
      console.error('❌ Error delegating task:', err);
      addDebugLog(`❌ Error delegating task: ${err.message}`);
      
      // Check if component is still mounted
      if (!mountedRef.current) {
        addDebugLog("⚠️ Component unmounted before error state update");
        return;
      }
      
      // Check if failsafe was already triggered
      if (failsafeTriggeredRef.current) {
        addDebugLog("⚠️ Failsafe already triggered, skipping error state updates");
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
      console.log('🛑 Spinner reset triggered');
      addDebugLog("🛑 Spinner reset triggered in finally block");
      
      // Use setTimeout to ensure this runs after React's current execution cycle
      setTimeout(() => {
        if (mountedRef.current) {
          // Double-check we're still mounted
          setIsSubmitting(false);
          console.log('✅ Spinner reset completed');
          addDebugLog("✅ Spinner reset completed");
        } else {
          console.log("⚠️ Component unmounted before spinner reset");
        }
      }, 0);
    }
  };
  
  // Error boundary for the entire component
  try {
    return (
      <Box p={4}>
        <Heading mb={6} size="lg">{agentName ?? `${agentType} Agent`}</Heading>
        <Text mb={6} color="gray.500">{agentDescription ?? 'No description available'}</Text>
        
        {/* Debug State Display - Force visible */}
        {debugVisible && (
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
              <Button 
                size="xs" 
                colorScheme="red" 
                onClick={forceResetSpinner}
                isDisabled={!isSubmitting}
              >
                Force Reset Spinner
              </Button>
            </HStack>
            <Box mt={2} maxH="150px" overflowY="auto" bg={colorMode === 'light' ? 'gray.50' : 'gray.700'} p={2} borderRadius="md">
              <Heading size="xs" mb={1}>Debug Logs:</Heading>
              {debugLogs.map((log, index) => (
                <Text key={index} fontSize="xs" fontFamily="monospace">{log}</Text>
              ))}
            </Box>
          </Card>
        )}
        
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
            
            {/* Additional Debug Panel - Force visible */}
            <Box mt={4} p={2} borderTopWidth="1px" borderColor="gray.300">
              <Heading size="xs" mb={2}>🛠️ Debug Panel</Heading>
              <Text fontSize="sm"><strong>isSubmitting:</strong> {isSubmitting.toString()}</Text>
              <Text fontSize="sm"><strong>taskName:</strong> {taskName}</Text>
              <Text fontSize="sm"><strong>agentType:</strong> {agentType}</Text>
              <Text fontSize="sm"><strong>last response:</strong> {response ? '✅ Received' : '❌ None'}</Text>
              <Text fontSize="sm"><strong>last error:</strong> {error || 'None'}</Text>
              <Text fontSize="sm"><strong>last updated:</strong> {lastUpdated}</Text>
              <Text fontSize="sm"><strong>failsafe triggered:</strong> {failsafeTriggeredRef.current.toString()}</Text>
            </Box>
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
  } catch (error) {
    // Fallback UI if the component crashes
    console.error('AgentPanel render error:', error);
    return (
      <Box p={4}>
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          <VStack align="start">
            <AlertTitle>Component Error</AlertTitle>
            <AlertDescription>
              <Text>The agent panel encountered an error.</Text>
              <Text fontSize="sm">{error.message}</Text>
              <Button 
                mt={2} 
                size="sm" 
                onClick={() => window.location.reload()}
              >
                Reload Page
              </Button>
            </AlertDescription>
          </VStack>
        </Alert>
      </Box>
    );
  }
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
