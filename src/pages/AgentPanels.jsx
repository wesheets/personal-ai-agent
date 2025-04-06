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
import { getVisibleAgents } from '../utils/agentUtils';

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
        console.log('🧪 Using simulated response (debug mode)');
        addDebugLog('🧪 Using simulated response (debug mode)');
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate streaming progress if enabled
        if (streamingEnabled) {
          const progressSteps = [
            'Analyzing task requirements...',
            'Searching for relevant information...',
            'Generating solution approach...',
            'Implementing solution...',
            'Finalizing response...'
          ];
          
          for (let i = 0; i < progressSteps.length; i++) {
            if (!mountedRef.current) break; // Stop if component unmounted
            
            // Simulate progress update
            const progressUpdate = {
              status: 'progress',
              content: progressSteps[i],
              progress: (i + 1) / progressSteps.length,
              timestamp: new Date().toISOString()
            };
            
            setStreamingProgress(prev => [...prev, progressUpdate]);
            setCurrentProgress((i + 1) / progressSteps.length * 100);
            
            // Wait before next update
            await new Promise(resolve => setTimeout(resolve, 800));
          }
        }
        
        // Simulate final response
        const simulatedResponse = {
          status: 'success',
          message: `Task "${taskName}" has been processed by the ${agentName || agentType} agent.\n\nGoal: ${taskGoal}\n\nThis is a simulated response for development purposes. In production, this would contain the actual agent response.`,
          task_id: `task-${Date.now()}`,
          agent: agentName || agentType,
          timestamp: new Date().toISOString()
        };
        
        // Update state with simulated response
        setResponse(simulatedResponse);
        addDebugLog('✅ Received simulated response');
        
        // Add to task history
        setTaskHistory(prev => [
          {
            id: simulatedResponse.task_id,
            name: taskName,
            goal: taskGoal,
            timestamp: simulatedResponse.timestamp,
            status: 'completed',
            response: simulatedResponse.message
          },
          ...prev.slice(0, 9) // Keep only the 10 most recent tasks
        ]);
      } else {
        // Use real API call
        let apiResponse;
        
        if (streamingEnabled) {
          // Use streaming API
          apiResponse = await ApiService.delegateTaskStreaming(
            agentType,
            taskName,
            taskGoal,
            (progressData) => {
              // Handle progress updates
              if (mountedRef.current) {
                setStreamingProgress(prev => [...prev, progressData]);
                if (progressData.progress) {
                  setCurrentProgress(progressData.progress * 100);
                }
              }
            },
            (completeData) => {
              // Handle completion
              if (mountedRef.current) {
                setResponse(completeData);
                addDebugLog('✅ Received final response');
                
                // Add to task history
                setTaskHistory(prev => [
                  {
                    id: completeData.task_id || `task-${Date.now()}`,
                    name: taskName,
                    goal: taskGoal,
                    timestamp: completeData.timestamp || new Date().toISOString(),
                    status: 'completed',
                    response: completeData.message
                  },
                  ...prev.slice(0, 9) // Keep only the 10 most recent tasks
                ]);
              }
            },
            (errorData) => {
              // Handle errors
              if (mountedRef.current) {
                setError(errorData);
                addDebugLog(`❌ Error: ${errorData.message}`);
                
                toast({
                  title: 'Error',
                  description: errorData.message || 'An error occurred while processing your request.',
                  status: 'error',
                  duration: 5000,
                  isClosable: true,
                });
              }
            }
          );
        } else {
          // Use non-streaming API
          apiResponse = await ApiService.delegateTask(agentType, taskName, taskGoal);
          
          // Update state with API response
          setResponse(apiResponse);
          addDebugLog('✅ Received API response');
          
          // Add to task history
          setTaskHistory(prev => [
            {
              id: apiResponse.task_id || `task-${Date.now()}`,
              name: taskName,
              goal: taskGoal,
              timestamp: apiResponse.timestamp || new Date().toISOString(),
              status: 'completed',
              response: apiResponse.message || 'Task completed successfully.'
            },
            ...prev.slice(0, 9) // Keep only the 10 most recent tasks
          ]);
        }
      }
      
      // Update submission lifecycle
      updateLifecycleState('apiCallComplete', new Date());
      
      // Reset form after successful submission
      setTaskName('');
      setTaskGoal('');
    } catch (err) {
      console.error('Error submitting task:', err);
      
      // Update submission lifecycle
      updateLifecycleState('apiCallError', new Date());
      
      // Set error state
      setError({
        message: err.message || 'An error occurred while processing your request.'
      });
      
      addDebugLog(`❌ Error: ${err.message}`);
      
      // Show error toast
      toast({
        title: 'Error',
        description: err.message || 'An error occurred while processing your request.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      // Reset submission state
      if (mountedRef.current) {
        setIsSubmitting(false);
        setCurrentProgress(0);
        updateLifecycleState('submissionComplete', new Date());
      }
    }
  };
  
  // Render the component
  return (
    <Box p={4}>
      <Heading mb={6} size="lg">{agentName || `${agentType} Agent`}</Heading>
      
      {agentDescription && (
        <Text mb={6} color={colorMode === 'light' ? 'gray.600' : 'gray.300'}>
          {agentDescription}
        </Text>
      )}
      
      <Card 
        variant="outline" 
        bg={colorMode === 'light' ? 'white' : 'gray.700'}
        boxShadow="md"
        borderRadius="lg"
        mb={6}
      >
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
              
              <HStack justifyContent="space-between">
                <FormControl display="flex" alignItems="center" width="auto">
                  <FormLabel htmlFor="streaming-toggle" mb="0" mr={2}>
                    Streaming
                  </FormLabel>
                  <Switch
                    id="streaming-toggle"
                    isChecked={streamingEnabled}
                    onChange={(e) => setStreamingEnabled(e.target.checked)}
                    colorScheme="blue"
                    isDisabled={isSubmitting}
                  />
                </FormControl>
                
                {DEBUG_MODE && (
                  <FormControl display="flex" alignItems="center" width="auto">
                    <FormLabel htmlFor="simulate-toggle" mb="0" mr={2}>
                      Simulate
                    </FormLabel>
                    <Switch
                      id="simulate-toggle"
                      isChecked={useSimulatedResponse}
                      onChange={(e) => setUseSimulatedResponse(e.target.checked)}
                      colorScheme="purple"
                      isDisabled={isSubmitting}
                    />
                  </FormControl>
                )}
                
                <Button
                  type="submit"
                  colorScheme="blue"
                  isLoading={isSubmitting}
                  loadingText="Submitting..."
                  rightIcon={<FiRefreshCw />}
                >
                  Submit Task
                </Button>
              </HStack>
            </VStack>
          </form>
        </CardBody>
      </Card>
      
      {/* Progress indicator for streaming responses */}
      {isSubmitting && streamingEnabled && (
        <Box mb={6}>
          <HStack mb={2}>
            <Text fontWeight="medium">Processing task</Text>
            <Spinner size="sm" />
          </HStack>
          <Progress value={currentProgress} size="sm" colorScheme="blue" borderRadius="full" />
        </Box>
      )}
      
      {/* Response display */}
      {(response || streamingProgress.length > 0 || error) && (
        <Card 
          variant="outline" 
          bg={colorMode === 'light' ? 'white' : 'gray.700'}
          boxShadow="md"
          borderRadius="lg"
          mb={6}
        >
          <CardBody>
            <Heading size="md" mb={4}>Response</Heading>
            
            {error ? (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error.message}</AlertDescription>
                </Box>
              </Alert>
            ) : response ? (
              <Box>
                <HStack mb={2}>
                  <Badge colorScheme="green">
                    {response.agent || agentType}
                  </Badge>
                  {response.timestamp && (
                    <Text fontSize="xs" color="gray.500">
                      {new Date(response.timestamp).toLocaleString()}
                    </Text>
                  )}
                </HStack>
                <Text whiteSpace="pre-wrap">{response.message}</Text>
              </Box>
            ) : streamingProgress.length > 0 ? (
              <VStack align="stretch" spacing={3}>
                {streamingProgress.map((progress, index) => (
                  <Box key={index}>
                    <Text whiteSpace="pre-wrap">{progress.content}</Text>
                  </Box>
                ))}
              </VStack>
            ) : null}
          </CardBody>
        </Card>
      )}
      
      {/* Task History */}
      {taskHistory.length > 0 && (
        <Card 
          variant="outline" 
          bg={colorMode === 'light' ? 'white' : 'gray.700'}
          boxShadow="md"
          borderRadius="lg"
          mb={6}
        >
          <CardBody>
            <Heading size="md" mb={4}>Recent Tasks</Heading>
            
            <VStack spacing={3} align="stretch" divider={<Divider />}>
              {taskHistory.map(task => (
                <Box key={task.id}>
                  <HStack mb={1} justifyContent="space-between">
                    <Heading size="sm">{task.name}</Heading>
                    <Badge colorScheme={task.status === 'completed' ? 'green' : 'yellow'}>
                      {task.status}
                    </Badge>
                  </HStack>
                  <Text fontSize="sm" color="gray.500" mb={2}>
                    {new Date(task.timestamp).toLocaleString()}
                  </Text>
                  <Text noOfLines={2} fontSize="sm">{task.goal}</Text>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}
      
      {/* Debug Panel (only visible in debug mode) */}
      {DEBUG_MODE && (
        <Box mb={6}>
          <HStack mb={2}>
            <Heading size="md">Debug Info</Heading>
            <IconButton
              icon={debugVisible ? <FiXCircle /> : <FiInfo />}
              size="sm"
              variant="ghost"
              onClick={() => setDebugVisible(!debugVisible)}
              aria-label={debugVisible ? "Hide debug info" : "Show debug info"}
            />
          </HStack>
          
          {debugVisible && (
            <Card 
              variant="outline" 
              bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}
              boxShadow="sm"
              borderRadius="lg"
            >
              <CardBody>
                <AgentDebugFeedback
                  agentType={agentType}
                  renderCount={renderCount}
                  lastUpdated={lastUpdated}
                  submissionLifecycle={submissionLifecycle}
                  debugLogs={debugLogs}
                />
              </CardBody>
            </Card>
          )}
        </Box>
      )}
    </Box>
  );
};

// Specific agent implementations
export const BuilderAgent = () => (
  <AgentPanel
    agentType="builder"
    agentName="Builder Agent"
    agentDescription="The Builder Agent helps create and modify code, components, and other technical artifacts."
  />
);

export const OpsAgent = () => (
  <AgentPanel
    agentType="ops"
    agentName="Operations Agent"
    agentDescription="The Operations Agent helps with deployment, monitoring, and maintenance tasks."
  />
);

export const ResearchAgent = () => (
  <AgentPanel
    agentType="research"
    agentName="Research Agent"
    agentDescription="The Research Agent helps gather information, analyze data, and provide insights."
  />
);

export default {
  BuilderAgent,
  OpsAgent,
  ResearchAgent
};
