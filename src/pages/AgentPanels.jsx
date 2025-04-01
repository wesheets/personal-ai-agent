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
  Switch,
  IconButton,
  Flex,
  Tooltip
} from '@chakra-ui/react';
import ApiService from '../api/ApiService';

// Generic Agent Panel component that can be used for Builder, Ops, and Research agents
const AgentPanel = ({ agentType, agentName, agentDescription }) => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  const mountedRef = useRef(true);
  const failsafeTriggeredRef = useRef(false);
  const submissionStartTimeRef = useRef(null);
  
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
  const [submissionLifecycle, setSubmissionLifecycle] = useState({
    submitClick: null,
    apiCallStart: null,
    apiResponse: null,
    failsafeTrigger: null,
    spinnerResetCall: null,
    spinnerResetComplete: null
  });
  
  // Track render count for debugging
  useEffect(() => {
    setRenderCount(prev => prev + 1);
    setLastUpdated(new Date().toLocaleTimeString());
    
    // Cleanup function to track component unmounting
    return () => {
      console.log('⚠️ Component unmounting - setting mountedRef to false');
      mountedRef.current = false;
    };
  }, []);
  
  // ENHANCED: Failsafe timeout to force spinner reset after 8 seconds
  useEffect(() => {
    // Store reference to the timeouts so we can access them outside the cleanup function
    const timeoutRefs = {
      primary: null,
      secondary: null,
      tertiary: null
    };
    
    if (!isSubmitting) {
      // Reset the failsafe trigger when submission completes
      failsafeTriggeredRef.current = false;
      return;
    }
    
    // Log submission start time
    if (!submissionStartTimeRef.current) {
      submissionStartTimeRef.current = new Date();
    }
    
    console.log('⏱️ Starting failsafe timeout for spinner reset');
    addDebugLog('⏱️ Starting failsafe timeout (8s)');
    
    // Update submission lifecycle
    updateLifecycleState('submitClick', submissionStartTimeRef.current);
    
    // Primary failsafe - 8 seconds
    timeoutRefs.primary = setTimeout(() => {
      console.log('✅ Spinner should now stop (8s failsafe)');
      console.log('🔥 Failsafe reset triggered');
      console.warn('⏱️ Failsafe triggered: Forcing spinner reset after 8s');
      
      // Mark that failsafe was triggered
      failsafeTriggeredRef.current = true;
      
      // Update submission lifecycle
      updateLifecycleState('failsafeTrigger', new Date());
      
      // Only update state if component is still mounted
      if (mountedRef.current) {
        updateLifecycleState('spinnerResetCall', new Date());
        setIsSubmitting(false);
        updateLifecycleState('spinnerResetComplete', new Date());
        addDebugLog('⏱️ FAILSAFE: Forced spinner reset after 8s timeout');
        
        // Show toast notification about failsafe
        toast({
          title: 'Submission timeout',
          description: 'Task submission took too long. The form has been reset.',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      } else {
        console.log('⚠️ Component not mounted during 8s failsafe - cannot reset spinner');
      }
    }, 8000);
    
    // Secondary ultra-failsafe - 12 seconds (in case the first one fails)
    timeoutRefs.secondary = setTimeout(() => {
      if (mountedRef.current && isSubmitting) {
        console.log('✅ Spinner should now stop (12s ultra-failsafe)');
        console.log('🔥🔥 ULTRA-FAILSAFE: Last resort spinner reset triggered');
        
        // Update submission lifecycle
        updateLifecycleState('failsafeTrigger', new Date());
        updateLifecycleState('spinnerResetCall', new Date());
        
        // Force direct state update
        setIsSubmitting(false);
        
        updateLifecycleState('spinnerResetComplete', new Date());
        addDebugLog('🔥🔥 ULTRA-FAILSAFE: Last resort spinner reset at 12s');
      } else {
        console.log('⚠️ Component not mounted or not submitting during 12s failsafe');
      }
    }, 12000);
    
    // Tertiary nuclear-failsafe - 16 seconds (absolute last resort)
    timeoutRefs.tertiary = setTimeout(() => {
      console.log('✅ Spinner should now stop (16s nuclear-failsafe)');
      console.log('☢️☢️☢️ NUCLEAR-FAILSAFE: Emergency spinner reset triggered');
      
      // Try multiple approaches to reset the spinner
      try {
        // Direct DOM manipulation as absolute last resort
        const spinnerElements = document.querySelectorAll('[data-testid="spinner"]');
        if (spinnerElements.length > 0) {
          spinnerElements.forEach(el => {
            el.style.display = 'none';
          });
        }
        
        // Force React state update if component is still mounted
        if (mountedRef.current) {
          updateLifecycleState('failsafeTrigger', new Date());
          updateLifecycleState('spinnerResetCall', new Date());
          setIsSubmitting(false);
          updateLifecycleState('spinnerResetComplete', new Date());
        }
        
        addDebugLog('☢️☢️☢️ NUCLEAR-FAILSAFE: Emergency spinner reset at 16s');
      } catch (err) {
        console.error('Failed to apply nuclear failsafe:', err);
      }
    }, 16000);
    
    // Clean up all timeouts
    return () => {
      console.log('🧹 Cleaning up failsafe timeouts');
      clearTimeout(timeoutRefs.primary);
      clearTimeout(timeoutRefs.secondary);
      clearTimeout(timeoutRefs.tertiary);
    };
  }, [isSubmitting]); // Removed toast from dependencies to prevent re-triggering
  
  // Update submission lifecycle state
  const updateLifecycleState = (stage, timestamp) => {
    if (!mountedRef.current) return;
    
    console.log(`📊 Lifecycle: ${stage} at ${timestamp.toLocaleTimeString()}`);
    
    setSubmissionLifecycle(prev => ({
      ...prev,
      [stage]: timestamp
    }));
  };
  
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
    console.log('✅ Spinner should now stop (manual reset)');
    console.log('🚨 Manual spinner reset triggered');
    
    if (mountedRef.current) {
      updateLifecycleState('spinnerResetCall', new Date());
      setIsSubmitting(false);
      updateLifecycleState('spinnerResetComplete', new Date());
      addDebugLog('🚨 Manual spinner reset triggered by user');
      
      toast({
        title: 'Manual reset',
        description: 'Spinner has been manually reset',
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
    } else {
      console.log('⚠️ Component not mounted during manual reset - cannot reset spinner');
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Debug logging - added for spinner debugging
    console.log("✅ Submission started");
    
    // Reset submission tracking
    submissionStartTimeRef.current = new Date();
    
    // Update submission lifecycle
    updateLifecycleState('submitClick', submissionStartTimeRef.current);
    
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
        updateLifecycleState('apiCallStart', new Date());
        await new Promise(resolve => setTimeout(resolve, 500));
        result = { status: "success", message: "Fake success", task_id: `fake-${Date.now()}` };
        updateLifecycleState('apiResponse', new Date());
      } else {
        // Use the ApiService to delegate the task
        addDebugLog("📡 Calling ApiService.delegateTask()");
        updateLifecycleState('apiCallStart', new Date());
        console.log("🟡 Calling delegateTask");
        
        // TEMPORARY TEST: Replace actual API call with dummy Promise to isolate the issue
        // Comment out the actual API call and use a dummy Promise instead
        // result = await ApiService.delegateTask(agentType, taskName, taskGoal);
        
        // Dummy Promise that resolves immediately with a success status
        result = await Promise.resolve({ status: "ok", task_id: `test-${Date.now()}` });
        
        console.log("🟢 API call resolved");
        console.log("✅ API call result:", result);
        updateLifecycleState('apiResponse', new Date());
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
      console.log('✅ Spinner should now stop (finally block)');
      console.log('🛑 Spinner reset triggered in finally block');
      addDebugLog("🛑 Spinner reset triggered in finally block");
      
      // Update submission lifecycle
      updateLifecycleState('spinnerResetCall', new Date());
      
      // ENHANCED: Ensure spinner reset happens reliably
      if (mountedRef.current) {
        setIsSubmitting(false);
        console.log("✅ Spinner reset");
        updateLifecycleState('spinnerResetComplete', new Date());
        addDebugLog("✅ Spinner reset completed immediately");
        
        // Reset submission start time
        submissionStartTimeRef.current = null;
      } else {
        console.log("⚠️ Component unmounted before spinner reset");
      }
      
      // Use setTimeout as a backup to ensure this runs after React's current execution cycle
      setTimeout(() => {
        if (mountedRef.current && isSubmitting) {
          // Double-check we're still mounted and spinner is still active
          console.log('✅ Spinner should now stop (setTimeout callback)');
          setIsSubmitting(false);
          
          // Update submission lifecycle
          updateLifecycleState('spinnerResetComplete', new Date());
          
          console.log('✅ Spinner reset completed in setTimeout');
          addDebugLog("✅ Backup spinner reset completed in setTimeout");
        } else if (mountedRef.current) {
          console.log("✓ Spinner already reset before setTimeout executed");
        } else {
          console.log("⚠️ Component unmounted before spinner reset in setTimeout");
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
        
        {/* EMERGENCY KILL SWITCH - Always visible at the top */}
        {isSubmitting && (
          <Alert status="warning" mb={4} borderRadius="md">
            <AlertIcon />
            <AlertTitle mr={2}>Submission in progress</AlertTitle>
            <AlertDescription>
              Started at {submissionStartTimeRef.current?.toLocaleTimeString()}
            </AlertDescription>
            <Button 
              ml="auto" 
              colorScheme="red" 
              size="sm" 
              onClick={forceResetSpinner}
              leftIcon={<span>🚨</span>}
            >
              EMERGENCY STOP
            </Button>
          </Alert>
        )}
        
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
                size="sm" 
                colorScheme="red" 
                onClick={forceResetSpinner}
                isDisabled={!isSubmitting}
                leftIcon={<span>🚨</span>}
              >
                Force Reset Spinner
              </Button>
            </HStack>
            
            {/* Submission Lifecycle Display */}
            <Box mt={2} p={2} bg={colorMode === 'light' ? 'white' : 'gray.800'} borderRadius="md">
              <Heading size="xs" mb={1}>Submission Lifecycle:</Heading>
              <Text fontSize="xs" fontFamily="monospace">
                Submit Click: {submissionLifecycle.submitClick?.toLocaleTimeString() || 'N/A'}
              </Text>
              <Text fontSize="xs" fontFamily="monospace">
                API Call Start: {submissionLifecycle.apiCallStart?.toLocaleTimeString() || 'N/A'}
              </Text>
              <Text fontSize="xs" fontFamily="monospace">
                API Response: {submissionLifecycle.apiResponse?.toLocaleTimeString() || 'N/A'}
              </Text>
              <Text fontSize="xs" fontFamily="monospace">
                Failsafe Trigger: {submissionLifecycle.failsafeTrigger?.toLocaleTimeString() || 'N/A'}
              </Text>
              <Text fontSize="xs" fontFamily="monospace">
                Spinner Reset Call: {submissionLifecycle.spinnerResetCall?.toLocaleTimeString() || 'N/A'}
              </Text>
              <Text fontSize="xs" fontFamily="monospace">
                Spinner Reset Complete: {submissionLifecycle.spinnerResetComplete?.toLocaleTimeString() || 'N/A'}
              </Text>
            </Box>
            
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
          position="relative"
        >
          {/* Manual Kill Switch - Floating button */}
          {isSubmitting && (
            <Tooltip label="Emergency Stop" placement="top">
              <IconButton
                aria-label="Emergency Stop"
                icon={<span>🚨</span>}
                colorScheme="red"
                size="lg"
                position="absolute"
                top="-15px"
                right="-15px"
                borderRadius="full"
                onClick={forceResetSpinner}
                zIndex={10}
              />
            </Tooltip>
          )}
          
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
                    data-testid="task-name-input"
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel>Task Goal</FormLabel>
                  <Textarea 
                    value={taskGoal}
                    onChange={(e) => setTaskGoal(e.target.value)}
                    placeholder="Describe what you want the agent to accomplish"
                    rows={4}
                    data-testid="task-goal-input"
                  />
                </FormControl>
                
                <Button 
                  type="submit" 
                  colorScheme="blue" 
                  isLoading={isSubmitting}
                  loadingText="Submitting..."
                  width="full"
                  data-testid="submit-button"
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
              <Flex justify="space-between" align="center">
                <Heading size="xs" mb={2}>🛠️ Debug Panel</Heading>
                {isSubmitting && (
                  <Button 
                    size="xs" 
                    colorScheme="red" 
                    onClick={forceResetSpinner}
                    leftIcon={<span>🚨</span>}
                  >
                    Kill Spinner
                  </Button>
                )}
              </Flex>
              <Text fontSize="sm"><strong>isSubmitting:</strong> {isSubmitting.toString()}</Text>
              <Text fontSize="sm"><strong>taskName:</strong> {taskName}</Text>
              <Text fontSize="sm"><strong>agentType:</strong> {agentType}</Text>
              <Text fontSize="sm"><strong>last response:</strong> {response ? '✅ Received' : '❌ None'}</Text>
              <Text fontSize="sm"><strong>last error:</strong> {error || 'None'}</Text>
              <Text fontSize="sm"><strong>last updated:</strong> {lastUpdated}</Text>
              <Text fontSize="sm"><strong>failsafe triggered:</strong> {failsafeTriggeredRef.current.toString()}</Text>
              <Text fontSize="sm"><strong>component mounted:</strong> {mountedRef.current.toString()}</Text>
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
              {isSubmitting && (
                <Button 
                  mt={2} 
                  size="sm" 
                  colorScheme="red" 
                  onClick={forceResetSpinner}
                >
                  Force Reset Spinner
                </Button>
              )}
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
