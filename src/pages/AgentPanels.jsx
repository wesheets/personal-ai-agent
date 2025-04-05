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
import ApiService from '../api/ApiService';
import { AgentDebugFeedback } from '../components';

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

  // Streaming state
  const [streamingProgress, setStreamingProgress] = useState([]);
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  const [currentProgress, setCurrentProgress] = useState(0);
  
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
    
    // Reset previous response, error, and streaming progress
    setResponse(null);
    setError(null);
    setStreamingProgress([]);
    setCurrentProgress(0);
    
    // Validate inputs
    if (!taskName.trim() || !taskGoal.trim()) {
      setError('Please fill in all required fields');
      return;
    }
    
    // Set submitting state
    setIsSubmitting(true);
    addDebugLog('🚀 Form submission started');
    
    try {
      // Update submission lifecycle
      updateLifecycleState('apiCallStart', new Date());
      
      // Use simulated response for testing if enabled
      if (useSimulatedResponse) {
        addDebugLog('🧪 Using simulated response (3s delay)');
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Simulate API response
        const simulatedResponse = {
          success: true,
          message: 'Task submitted successfully (SIMULATED)',
          taskId: `sim-${Date.now()}`,
          status: 'pending'
        };
        
        // Update submission lifecycle
        updateLifecycleState('apiResponse', new Date());
        
        // Update state with simulated response
        setResponse(simulatedResponse);
        addDebugLog('✅ Simulated response received');
        
        // Add to task history
        setTaskHistory(prev => [
          {
            id: simulatedResponse.taskId,
            name: taskName,
            goal: taskGoal,
            status: 'pending',
            timestamp: new Date()
          },
          ...prev
        ]);
        
        // Reset form
        setTaskName('');
        setTaskGoal('');
      } else if (streamingEnabled) {
        // Use streaming API
        addDebugLog('📡 Sending streaming API request');
        
        try {
          // Handle progress updates
          const handleProgress = (progressData) => {
            if (!mountedRef.current) return;
            
            addDebugLog(`🔄 Progress: ${progressData.stage} - ${progressData.message}`);
            setStreamingProgress(prev => [...prev, progressData]);
            
            // Update progress percentage if available
            if (progressData.progress) {
              setCurrentProgress(progressData.progress);
            }
          };
          
          // Handle completion
          const handleComplete = (completeData) => {
            if (!mountedRef.current) return;
            
            addDebugLog(`✅ Complete: ${completeData.agent} - ${completeData.message}`);
            setResponse(completeData);
            
            // Add to task history
            setTaskHistory(prev => [
              {
                id: `task-${Date.now()}`,
                name: taskName,
                goal: taskGoal,
                status: 'completed',
                timestamp: new Date(),
                agent: completeData.agent,
                tone: completeData.tone,
                message: completeData.message
              },
              ...prev
            ]);
            
            // Reset form
            setTaskName('');
            setTaskGoal('');
            
            // Update submission lifecycle
            updateLifecycleState('apiResponse', new Date());
          };
          
          // Handle errors
          const handleError = (errorData) => {
            if (!mountedRef.current) return;
            
            addDebugLog(`❌ Error: ${errorData.message}`);
            setError(errorData.message || 'An error occurred during streaming');
            
            // Update submission lifecycle
            updateLifecycleState('apiResponse', new Date());
          };
          
          // Call streaming API
          await ApiService.delegateTaskStreaming(
            agentType,
            taskName,
            taskGoal,
            handleProgress,
            handleComplete,
            handleError
          );
        } catch (streamingError) {
          console.error('Error in streaming task:', streamingError);
          setError(streamingError.message || 'An error occurred during streaming');
          addDebugLog(`❌ Streaming error: ${streamingError.message}`);
          
          // Update submission lifecycle
          updateLifecycleState('apiResponse', new Date());
        }
      } else {
        // Make regular API call
        addDebugLog('📡 Sending regular API request');
        
        const apiResponse = await ApiService.delegateTask(
          agentType,
          taskName,
          taskGoal
        );
        
        // Update submission lifecycle
        updateLifecycleState('apiResponse', new Date());
        
        // Update state with API response
        setResponse(apiResponse);
        addDebugLog('✅ API response received');
        
        // Add to task history if successful
        if (apiResponse.success) {
          setTaskHistory(prev => [
            {
              id: apiResponse.taskId,
              name: taskName,
              goal: taskGoal,
              status: apiResponse.status || 'pending',
              timestamp: new Date()
            },
            ...prev
          ]);
          
          // Reset form on success
          setTaskName('');
          setTaskGoal('');
        }
      }
    } catch (err) {
      console.error('Error submitting task:', err);
      
      // Update submission lifecycle
      updateLifecycleState('apiResponse', new Date());
      
      // Set error state
      setError(err.message || 'An error occurred while submitting the task');
      addDebugLog('❌ Error: ' + (err.message || 'Unknown error'));
    } finally {
      // Use setTimeout to ensure state updates don't conflict
      setTimeout(() => {
        // Only update state if component is still mounted
        if (mountedRef.current) {
          // Reset submitting state
          setIsSubmitting(false);
          addDebugLog('✅ Form submission completed');
          console.log("✓ Spinner should now stop (normal flow)");
          console.log("✓ Spinner reset in finally block");
          
          // Update submission lifecycle
          updateLifecycleState('spinnerResetCall', new Date());
          updateLifecycleState('spinnerResetComplete', new Date());
        } else if (failsafeTriggeredRef.current) {
          console.log("✓ Spinner already reset before setTimeout executed");
        } else {
          console.log("⚠️ Component unmounted before spinner reset in setTimeout");
        }
      }, 0);
    }
  };

  // Get color scheme based on agent tone
  const getToneColorScheme = (tone) => {
    switch(tone?.toLowerCase()) {
      case 'calm':
        return 'blue';
      case 'clinical':
        return 'purple';
      case 'decisive':
        return 'green';
      case 'direct':
        return 'orange';
      default:
        return 'gray';
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
        
        {/* Replace the inline debug card with the AgentDebugFeedback component */}
        <AgentDebugFeedback 
          agentType={agentType}
          isVisible={debugVisible}
          debugLogs={debugLogs}
          lifecycleEvents={submissionLifecycle}
          performanceMetrics={{
            'Spinner State': isSubmitting.toString(),
            'Error State': error ? "Error" : "null",
            'Response': response ? "Present" : "null",
            'Render Count': renderCount.toString(),
            'Simulated Response': useSimulatedResponse ? "Enabled" : "Disabled",
            'Streaming': streamingEnabled ? "Enabled" : "Disabled"
          }}
          onClearLogs={() => setDebugLogs([])}
          onToggleVisibility={() => setDebugVisible(!debugVisible)}
        />
        
        {/* Task submission form */}
        <Card mb={6} variant="outline">
          <CardBody>
            <form onSubmit={handleSubmit}>
              <VStack spacing={4} align="stretch">
                <FormControl isRequired>
                  <FormLabel>Task Name</FormLabel>
                  <Input
                    value={taskName}
                    onChange={(e) => setTaskName(e.target.value)}
                    placeholder="Enter a name for this task"
                    isDisabled={isSubmitting}
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel>Task Goal</FormLabel>
                  <Textarea
                    value={taskGoal}
                    onChange={(e) => setTaskGoal(e.target.value)}
                    placeholder="Describe what you want the agent to accomplish"
                    rows={4}
                    isDisabled={isSubmitting}
                  />
                </FormControl>

                <HStack>
                  <FormControl display="flex" alignItems="center">
                    <FormLabel htmlFor="streaming-toggle" mb="0" fontSize="sm">
                      Use Streaming API
                    </FormLabel>
                    <Switch 
                      id="streaming-toggle" 
                      isChecked={streamingEnabled}
                      onChange={() => setStreamingEnabled(!streamingEnabled)}
                      colorScheme="blue"
                      isDisabled={isSubmitting}
                    />
                  </FormControl>

                  <FormControl display="flex" alignItems="center">
                    <FormLabel htmlFor="simulated-toggle" mb="0" fontSize="sm">
                      Simulated Response (Debug)
                    </FormLabel>
                    <Switch 
                      id="simulated-toggle" 
                      isChecked={useSimulatedResponse}
                      onChange={() => setUseSimulatedResponse(!useSimulatedResponse)}
                      colorScheme="purple"
                      isDisabled={isSubmitting || streamingEnabled}
                    />
                  </FormControl>
                </HStack>
                
                {error && (
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {/* Streaming Progress Display */}
                {streamingEnabled && streamingProgress.length > 0 && (
                  <Box mt={2} p={3} borderWidth="1px" borderRadius="md" bg={colorMode === 'light' ? 'gray.50' : 'gray.700'}>
                    <Text fontWeight="bold" mb={2}>Processing Task:</Text>
                    <Progress 
                      value={currentProgress} 
                      size="sm" 
                      colorScheme="blue" 
                      mb={3}
                      hasStripe
                      isAnimated
                    />
                    <VStack align="start" spacing={1}>
                      {streamingProgress.map((progress, index) => (
                        <Text key={index} fontSize="sm">
                          {progress.stage}: {progress.message}
                          {progress.progress && ` (${Math.round(progress.progress)}%)`}
                        </Text>
                      ))}
                    </VStack>
                  </Box>
                )}
                
                {/* Persona-based Response Display */}
                {response && response.status === 'success' && (
                  <Box 
                    mt={2} 
                    p={4} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    bg={colorMode === 'light' ? 'gray.50' : 'gray.700'}
                    borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                  >
                    <VStack align="stretch" spacing={3}>
                      <HStack>
                        <Text fontWeight="bold">Agent:</Text>
                        <Text>{response.agent}</Text>
                      </HStack>
                      
                      <HStack>
                        <Text fontWeight="bold">Tone:</Text>
                        <Badge colorScheme={getToneColorScheme(response.tone)}>
                          {response.tone}
                        </Badge>
                      </HStack>
                      
                      <Box>
                        <Text fontWeight="bold" mb={1}>Response:</Text>
                        <Box 
                          p={3} 
                          bg={colorMode === 'light' ? 'white' : 'gray.800'}
                          borderRadius="md"
                          borderWidth="1px"
                          borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                        >
                          <Text>{response.message}</Text>
                        </Box>
                      </Box>
                    </VStack>
                  </Box>
                )}
                
                <Button
                  type="submit"
                  colorScheme="blue"
                  isLoading={isSubmitting}
                  loadingText="Submitting..."
                  data-testid="spinner"
                >
                  Submit Task
                </Button>
              </VStack>
            </form>
          </CardBody>
        </Card>
        
        {/* Task history section */}
        <Card variant="outline">
          <CardBody>
            <Heading size="md" mb={4}>Task History</Heading>
            
            {taskHistory.length === 0 ? (
              <Text color="gray.500">No tasks submitted yet</Text>
            ) : (
              <VStack spacing={3} align="stretch">
                {taskHistory.map((task, index) => (
                  <Box key={task.id || index} p={3} borderWidth="1px" borderRadius="md">
                    <HStack justifyContent="space-between">
                      <Heading size="sm">{task.name}</Heading>
                      <Badge colorScheme={task.status === 'completed' ? 'green' : 'blue'}>
                        {task.status}
                      </Badge>
                    </HStack>
                    <Text mt={2} fontSize="sm" color="gray.600">{task.goal}</Text>
                    
                    {/* Persona details in history if available */}
                    {task.agent && (
                      <HStack mt={2} spacing={2}>
                        <Badge size="sm">Agent: {task.agent}</Badge>
                        {task.tone && (
                          <Badge colorScheme={getToneColorScheme(task.tone)} size="sm">
                            {task.tone}
                          </Badge>
                        )}
                      </HStack>
                    )}
                    
                    {task.message && (
                      <Text mt={1} fontSize="sm" fontStyle="italic">
                        "{task.message}"
                      </Text>
                    )}
                    
                    <Text mt={1} fontSize="xs" color="gray.500">
                      Submitted: {task.timestamp.toLocaleString()}
                    </Text>
                  </Box>
                ))}
              </VStack>
            )}
          </CardBody>
        </Card>
      </Box>
    );
  } catch (error) {
    console.error('Render error in AgentPanel:', error);
    
    // Fallback UI in case of render errors
    return (
      <Box p={4}>
        <Alert status="error" variant="solid">
          <AlertIcon />
          <AlertTitle mr={2}>Rendering Error</AlertTitle>
          <AlertDescription>
            An error occurred while rendering the agent panel. Please try refreshing the page.
          </AlertDescription>
        </Alert>
        
        <Card mt={4} bg="red.50" color="red.800">
          <CardBody>
            <Heading size="md" mb={2}>Error Details</Heading>
            <Code p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
              {error.toString()}
              {error.stack}
            </Code>
          </CardBody>
        </Card>
      </Box>
    );
  }
};

// Builder Agent Component
export const BuilderAgent = () => (
  <AgentPanel
    agentType="builder"
    agentName="Builder Agent"
    agentDescription="The Builder Agent helps you create and implement solutions. It excels at coding, design, and technical implementation tasks."
  />
);

// Ops Agent Component
export const OpsAgent = () => (
  <AgentPanel
    agentType="ops"
    agentName="Operations Agent"
    agentDescription="The Operations Agent helps you manage and optimize systems. It excels at monitoring, maintenance, and operational tasks."
  />
);

// Research Agent Component
export const ResearchAgent = () => (
  <AgentPanel
    agentType="research"
    agentName="Research Agent"
    agentDescription="The Research Agent helps you gather and analyze information. It excels at finding data, summarizing content, and providing insights."
  />
);

export default {
  BuilderAgent,
  OpsAgent,
  ResearchAgent
};
