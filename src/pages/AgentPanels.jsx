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
  Tooltip,
  Progress
} from '@chakra-ui/react';
import { FiRefreshCw, FiInfo, FiAlertCircle, FiCheckCircle, FiXCircle } from 'react-icons/fi';
import ApiService from '../api/ApiService';
import { AgentDebugFeedback } from '../components';
import DEBUG_MODE from '../config/debug';

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
  
  // State for debug info
  const [debugVisible, setDebugVisible] = useState(DEBUG_MODE);
  const [debugLogs, setDebugLogs] = useState([]);
  const [renderCount, setRenderCount] = useState(0);
  const [lastUpdated, setLastUpdated] = useState('');
  const [submissionLifecycle, setSubmissionLifecycle] = useState({});
  
  // State for simulated response (for development)
  const [useSimulatedResponse, setUseSimulatedResponse] = useState(DEBUG_MODE);
  
  // State for streaming response
  const [streamingProgress, setStreamingProgress] = useState([]);
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  const [currentProgress, setCurrentProgress] = useState(0);
  
  // Track render count for debugging
  useEffect(() => {
    setRenderCount(prev => prev + 1);
    setLastUpdated(new Date().toLocaleTimeString());
    
    console.debug(`Loaded: AgentPanel (${agentType}) ✅`);
    
    // Cleanup function to track component unmounting
    return () => {
      console.log('⚠️ Component unmounting - setting mountedRef to false');
      mountedRef.current = false;
    };
  }, [agentType]);
  
  // ENHANCED: Failsafe timeout to force spinner reset after 8 seconds
  useEffect(() => {
    // Only set up failsafe timeouts if not in debug mode
    if (DEBUG_MODE) {
      return;
    }
    
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
    
    setSubmissionLifecycle(prev => ({
      ...prev,
      [stage]: timestamp
    }));
  };
  
  // Add a debug log entry
  const addDebugLog = (message) => {
    if (!mountedRef.current) return;
    
    const timestamp = new Date().toLocaleTimeString();
    setDebugLogs(prev => [
      {
        id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
        timestamp,
        message
      },
      ...prev.slice(0, 49) // Keep only the 50 most recent logs
    ]);
  };
  
  // Handle form submission with debounce
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Prevent rapid consecutive submissions
    if (isSubmitting) {
      addDebugLog('⚠️ Submission already in progress, ignoring duplicate request');
      return;
    }
    
    // Validate form
    if (!taskName.trim() || !taskGoal.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please provide both a task name and goal.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    
    // Reset state
    setIsSubmitting(true);
    setResponse(null);
    setError(null);
    submissionStartTimeRef.current = new Date();
    
    // Update submission lifecycle
    updateLifecycleState('submitClick', submissionStartTimeRef.current);
    addDebugLog(`🚀 Submitting task to ${agentType} agent`);
    
    try {
      // Prepare request payload
      const payload = {
        agent_id: agentType,
        task_name: taskName,
        task_goal: taskGoal,
        use_streaming: streamingEnabled
      };
      
      // Log request details
      console.log('📤 Sending request:', payload);
      addDebugLog(`📤 Sending request to ${agentType} agent`);
      
      // Update submission lifecycle
      updateLifecycleState('apiCallStart', new Date());
      
      // Use simulated response in debug mode if enabled
      if (useSimulatedResponse) {
        addDebugLog('🧪 Using simulated response (debug mode)');
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate streaming updates if enabled
        if (streamingEnabled) {
          simulateStreamingUpdates();
        }
        
        // Simulate final response
        const simulatedResponse = {
          success: true,
          message: 'Task processed successfully (simulated)',
          result: `I've analyzed your request for "${taskName}" and here's my response:\n\n1. First, I'll need to gather information about ${taskGoal}\n2. Then, I'll create a structured approach\n3. Finally, I'll deliver the results in your preferred format.\n\nPlease let me know if you need any clarification or have additional requirements.`,
          task_id: `sim-${Date.now()}`
        };
        
        // Only update state if component is still mounted
        if (mountedRef.current) {
          updateLifecycleState('apiResponse', new Date());
          setResponse(simulatedResponse);
          
          // Add to task history
          setTaskHistory(prev => [
            {
              id: simulatedResponse.task_id,
              name: taskName,
              goal: taskGoal,
              timestamp: new Date().toISOString(),
              result: simulatedResponse.result
            },
            ...prev.slice(0, 9) // Keep only the 10 most recent tasks
          ]);
          
          // Reset form
          setTaskName('');
          setTaskGoal('');
        }
      } else {
        // Make actual API call
        const endpoint = streamingEnabled ? 'delegate-stream' : 'delegate';
        const apiResponse = await ApiService.delegateTask(endpoint, payload);
        
        // Update submission lifecycle
        updateLifecycleState('apiResponse', new Date());
        addDebugLog(`✅ Received response from ${agentType} agent`);
        
        // Only update state if component is still mounted
        if (mountedRef.current) {
          setResponse(apiResponse);
          
          // Add to task history
          setTaskHistory(prev => [
            {
              id: apiResponse.task_id || `task-${Date.now()}`,
              name: taskName,
              goal: taskGoal,
              timestamp: new Date().toISOString(),
              result: apiResponse.result || apiResponse.message
            },
            ...prev.slice(0, 9) // Keep only the 10 most recent tasks
          ]);
          
          // Reset form
          setTaskName('');
          setTaskGoal('');
        }
      }
    } catch (err) {
      console.error('Error submitting task:', err);
      
      // Only update state if component is still mounted
      if (mountedRef.current) {
        // Determine error type for better user feedback
        let errorMessage = 'Failed to submit task. Please try again.';
        let errorType = 'Unknown Error';
        
        if (err.message && err.message.includes('timeout')) {
          errorType = 'Timeout Error';
          errorMessage = 'Request timed out. The server took too long to respond.';
        } else if (err.message && err.message.includes('network')) {
          errorType = 'Network Error';
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (err.response && err.response.status === 403) {
          errorType = 'Access Denied';
          errorMessage = 'You do not have permission to perform this action.';
        } else if (err.response && err.response.status === 404) {
          errorType = 'Invalid Agent';
          errorMessage = `Agent "${agentType}" not found or not available.`;
        }
        
        setError({
          type: errorType,
          message: errorMessage,
          details: err.message || 'No additional details available',
          timestamp: new Date().toISOString()
        });
        
        addDebugLog(`❌ Error: ${errorType} - ${errorMessage}`);
        
        toast({
          title: errorType,
          description: errorMessage,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    } finally {
      // Only update state if component is still mounted and failsafe wasn't triggered
      if (mountedRef.current && !failsafeTriggeredRef.current) {
        updateLifecycleState('spinnerResetCall', new Date());
        setIsSubmitting(false);
        updateLifecycleState('spinnerResetComplete', new Date());
        addDebugLog('✅ Form submission complete');
      } else if (!mountedRef.current) {
        console.log('⚠️ Component not mounted during submission completion - cannot update state');
      } else {
        console.log('⚠️ Failsafe already triggered - skipping normal completion flow');
      }
    }
  };
  
  // Simulate streaming updates for development
  const simulateStreamingUpdates = () => {
    const updates = [
      { stage: 'init', message: 'Initializing task processing', progress: 10 },
      { stage: 'planning', message: 'Planning approach', progress: 25 },
      { stage: 'processing', message: 'Processing task data', progress: 50 },
      { stage: 'analyzing', message: 'Analyzing results', progress: 75 },
      { stage: 'finalizing', message: 'Finalizing response', progress: 90 }
    ];
    
    let index = 0;
    
    const interval = setInterval(() => {
      if (index < updates.length && mountedRef.current) {
        setStreamingProgress(prev => [...prev, updates[index]]);
        setCurrentProgress(updates[index].progress);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 500);
  };
  
  // Add a manual refresh button in DevMode
  const ManualRefreshButton = () => {
    if (!DEBUG_MODE) return null;
    
    return (
      <Box mt={4} p={3} borderWidth="1px" borderRadius="md" bg={colorMode === 'light' ? 'gray.50' : 'gray.700'}>
        <Heading size="sm" mb={2}>DevMode Controls</Heading>
        <HStack spacing={4}>
          <Button 
            size="sm" 
            leftIcon={<FiRefreshCw />}
            colorScheme="blue"
            onClick={() => {
              toast({
                title: 'Manual Refresh',
                description: 'Refreshing agent data...',
                status: 'info',
                duration: 2000,
              });
              // Refresh agent data here
              addDebugLog('🔄 Manual refresh triggered');
            }}
          >
            Refresh Agents
          </Button>
          <Button 
            size="sm" 
            colorScheme="purple"
            onClick={() => {
              setUseSimulatedResponse(!useSimulatedResponse);
              addDebugLog(`🧪 Simulated responses ${!useSimulatedResponse ? 'enabled' : 'disabled'}`);
            }}
          >
            {useSimulatedResponse ? 'Use Real API' : 'Use Simulated API'}
          </Button>
          <Button 
            size="sm" 
            colorScheme="red"
            onClick={() => {
              setDebugVisible(!debugVisible);
            }}
          >
            {debugVisible ? 'Hide Debug' : 'Show Debug'}
          </Button>
        </HStack>
      </Box>
    );
  };
  
  // Render error display with improved details
  const ErrorDisplay = () => {
    if (!error) return null;
    
    return (
      <Alert status="error" variant="left-accent" mt={4} borderRadius="md">
        <AlertIcon />
        <Box flex="1">
          <AlertTitle>{error.type || 'Error'}</AlertTitle>
          <AlertDescription display="block">
            {error.message}
            {DEBUG_MODE && error.details && (
              <Code mt={2} p={2} display="block" fontSize="xs">
                {error.details}
              </Code>
            )}
            <Text fontSize="xs" mt={1} color="gray.500">
              {new Date(error.timestamp).toLocaleTimeString()}
            </Text>
          </AlertDescription>
        </Box>
      </Alert>
    );
  };
  
  // Render response display with improved formatting
  const ResponseDisplay = () => {
    if (!response) {
      if (isSubmitting) {
        return (
          <Box mt={4} p={4} borderWidth="1px" borderRadius="md" bg={colorMode === 'light' ? 'gray.50' : 'gray.700'}>
            <Text mb={2}>Processing your request...</Text>
            {streamingEnabled ? (
              <>
                <Progress value={currentProgress} size="sm" colorScheme="blue" mb={2} />
                <VStack align="stretch" spacing={1} mt={2}>
                  {streamingProgress.map((progress, index) => (
                    <Text key={index} fontSize="xs">
                      <Badge colorScheme="blue" mr={1}>{progress.stage}</Badge>
                      {progress.message}
                    </Text>
                  ))}
                </VStack>
              </>
            ) : (
              <Spinner size="md" />
            )}
          </Box>
        );
      }
      return (
        <Box mt={4} p={4} borderWidth="1px" borderRadius="md" bg={colorMode === 'light' ? 'gray.50' : 'gray.700'}>
          <Text color="gray.500">Agent has not responded yet</Text>
        </Box>
      );
    }
    
    return (
      <Card mt={4} variant="outline">
        <CardBody>
          <Heading size="sm" mb={2}>Response</Heading>
          <Text whiteSpace="pre-wrap">{response.result || response.message}</Text>
        </CardBody>
      </Card>
    );
  };
  
  return (
    <Box p={4}>
      <Heading size="md" mb={2}>{agentName}</Heading>
      <Text mb={4}>{agentDescription}</Text>
      
      {/* Manual Refresh Button (DevMode only) */}
      <ManualRefreshButton />
      
      <form onSubmit={handleSubmit}>
        <VStack spacing={4} align="stretch">
          <FormControl isRequired>
            <FormLabel>Task Name</FormLabel>
            <Input 
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              placeholder="Enter a short, descriptive name for this task"
              disabled={isSubmitting}
            />
          </FormControl>
          
          <FormControl isRequired>
            <FormLabel>Task Goal</FormLabel>
            <Textarea 
              value={taskGoal}
              onChange={(e) => setTaskGoal(e.target.value)}
              placeholder="Describe what you want the agent to accomplish"
              rows={4}
              disabled={isSubmitting}
            />
          </FormControl>
          
          <HStack>
            <Button 
              type="submit" 
              colorScheme="blue" 
              isLoading={isSubmitting}
              loadingText="Submitting"
              width="full"
            >
              Submit Task
            </Button>
          </HStack>
        </VStack>
      </form>
      
      {/* Error Display */}
      <ErrorDisplay />
      
      {/* Response Display */}
      <ResponseDisplay />
      
      {/* Debug Information */}
      {debugVisible && (
        <AgentDebugFeedback 
          logs={debugLogs}
          renderCount={renderCount}
          lastUpdated={lastUpdated}
          submissionLifecycle={submissionLifecycle}
        />
      )}
    </Box>
  );
};

export default AgentPanel;
