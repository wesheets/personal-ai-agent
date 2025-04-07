import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Text,
  Badge,
  Heading,
  Input,
  Select,
  Button,
  Textarea,
  FormControl,
  FormLabel,
  Divider,
  useColorMode,
  useToast,
  Spinner,
  Code
} from '@chakra-ui/react';
import { getVisibleAgents } from '../utils/agentUtils';

/**
 * AgentTestPanel Component
 * 
 * A UI component for testing HAL and Ash personas via the streaming route.
 * Allows users to select an agent, submit a task, and view the streaming response.
 */
const AgentTestPanel = () => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  const responseBoxRef = useRef(null);
  
  // State for form inputs
  const [agentId, setAgentId] = useState('hal9000');
  const [taskInput, setTaskInput] = useState('');
  const [taskId, setTaskId] = useState(`demo-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`);
  
  // State for response handling
  const [isLoading, setIsLoading] = useState(false);
  const [streamingProgress, setStreamingProgress] = useState([]);
  const [finalResponse, setFinalResponse] = useState(null);
  const [error, setError] = useState(null);
  
  // State for available agents
  const [availableAgents, setAvailableAgents] = useState([]);
  const [isLoadingAgents, setIsLoadingAgents] = useState(false);
  
  // Fetch available agents on component mount
  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    
    const fetchAgents = async () => {
      if (!isMounted) return;
      
      setIsLoadingAgents(true);
      try {
        // Use the centralized getVisibleAgents utility instead of direct fetch
        const visibleAgents = await getVisibleAgents();
        
        if (isMounted) {
          setAvailableAgents(visibleAgents);
        }
      } catch (err) {
        // Ignore abort errors as they're expected during cleanup
        if (err.name === 'AbortError') {
          return;
        }
        
        if (isMounted) {
          toast({
            title: 'Error fetching agents',
            description: err.message,
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
        }
      } finally {
        if (isMounted) {
          setIsLoadingAgents(false);
        }
      }
    };
    
    // Add a short delay before initial fetch
    const timeout = setTimeout(() => {
      if (isMounted) {
        fetchAgents();
      }
    }, 1000);
    
    return () => {
      isMounted = false;
      controller.abort(); // Abort any in-flight fetch
      clearTimeout(timeout);
    };
  }, [toast]);
  
  // Auto-scroll to bottom of response box when new content arrives
  useEffect(() => {
    let isMounted = true;
    
    if (isMounted && responseBoxRef.current) {
      responseBoxRef.current.scrollTop = responseBoxRef.current.scrollHeight;
    }
    
    return () => {
      isMounted = false;
    };
  }, [streamingProgress, finalResponse]);
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!agentId) {
      toast({
        title: 'Agent ID required',
        description: 'Please select or enter an agent ID',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    if (!taskInput) {
      toast({
        title: 'Task input required',
        description: 'Please enter a task input',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    // Prevent duplicate submissions
    if (isLoading) {
      return;
    }
    
    // Reset previous response data
    setIsLoading(true);
    setStreamingProgress([]);
    setFinalResponse(null);
    setError(null);
    
    // Set up failsafe timeout to reset loading state after 16 seconds
    const failsafeTimeout = setTimeout(() => {
      setIsLoading(false);
      setError({ message: 'Request timed out. The agent may still be processing your task in the background.' });
      toast({
        title: 'Request timeout',
        description: 'The request is taking longer than expected. The agent may still be processing your task.',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
    }, 16000);
    
    // Prepare request body
    const requestBody = {
      agent_id: agentId,
      task: {
        task_id: taskId,
        task_type: 'text',
        input: taskInput
      }
    };
    
    try {
      // Send request to streaming endpoint
      const response = await fetch('/api/agent/delegate-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`);
      }
      
      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            // Handle different types of streaming responses
            if (data.status === 'progress') {
              setStreamingProgress(prev => [...prev, data]);
            } else if (data.status === 'success') {
              setFinalResponse(data);
            } else if (data.status === 'error') {
              setError(data);
              toast({
                title: 'Error from server',
                description: data.message || 'Unknown error',
                status: 'error',
                duration: 5000,
                isClosable: true,
              });
            }
          } catch (parseError) {
            // Silently handle parse errors
          }
        }
      }
    } catch (err) {
      setError({ message: err.message });
      toast({
        title: 'Request failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      // Clear the failsafe timeout
      clearTimeout(failsafeTimeout);
      
      setIsLoading(false);
      // Generate new task ID for next request
      setTaskId(`demo-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`);
    }
  };
  
  // Find selected agent details
  const selectedAgent = finalResponse ? {
    name: finalResponse.agent,
    tone: finalResponse.tone,
    message: finalResponse.message
  } : availableAgents.find(agent => agent.id === agentId);
  
  // Get agent icon
  const getAgentIcon = (agentId) => {
    const agent = availableAgents.find(a => a.id === agentId);
    return agent?.icon || '';
  };
  
  return (
    <Card 
      variant="outline" 
      bg={colorMode === 'light' ? 'white' : 'gray.700'}
      borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
      boxShadow="md"
      borderRadius="md"
      overflow="hidden"
    >
      <CardHeader pb={2}>
        <Heading size="md">Agent Interaction Test Panel</Heading>
        <Text fontSize="sm" color={colorMode === 'light' ? 'gray.600' : 'gray.300'}>
          Test HAL and Ash personas via the streaming route
        </Text>
      </CardHeader>
      
      <CardBody>
        <VStack spacing={4} align="stretch">
          {/* Agent Selection and Task Input Form */}
          <form onSubmit={handleSubmit}>
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel htmlFor="agent-id">Agent ID</FormLabel>
                <Select 
                  id="agent-id"
                  value={agentId}
                  onChange={(e) => setAgentId(e.target.value)}
                  isDisabled={isLoading || isLoadingAgents}
                  placeholder={isLoadingAgents ? "Loading agents..." : "Select an agent"}
                >
                  {availableAgents.map(agent => (
                    <option key={agent.id} value={agent.id}>
                      {agent.icon} {agent.name} {agent.tone ? `(${agent.tone})` : ''}
                    </option>
                  ))}
                </Select>
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel htmlFor="task-input">Task Input</FormLabel>
                <Textarea
                  id="task-input"
                  value={taskInput}
                  onChange={(e) => setTaskInput(e.target.value)}
                  placeholder="Enter your task here..."
                  size="md"
                  rows={4}
                  isDisabled={isLoading}
                />
              </FormControl>
              
              <Button 
                type="submit" 
                colorScheme="blue" 
                isLoading={isLoading}
                loadingText="Submitting..."
                isDisabled={!agentId || !taskInput || isLoading}
              >
                Submit Task
              </Button>
            </VStack>
          </form>
          
          <Divider />
          
          {/* Response Display */}
          <Box>
            <Text fontWeight="medium" mb={2}>Response:</Text>
            <Box
              ref={responseBoxRef}
              border="1px"
              borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
              borderRadius="md"
              p={3}
              bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}
              height="300px"
              overflowY="auto"
            >
              {isLoading && streamingProgress.length === 0 ? (
                <VStack spacing={4} justify="center" height="100%">
                  <Spinner size="lg" />
                  <Text>Waiting for response...</Text>
                </VStack>
              ) : error ? (
                <Box color="red.500" p={2}>
                  <Text fontWeight="bold">Error:</Text>
                  <Text>{error.message}</Text>
                </Box>
              ) : finalResponse ? (
                <VStack align="stretch" spacing={3}>
                  <HStack>
                    <Badge colorScheme="green" fontSize="0.8em" px={2} py={1} borderRadius="full">
                      {getAgentIcon(agentId)} {finalResponse.agent}
                    </Badge>
                    {finalResponse.tone && (
                      <Badge colorScheme="purple" fontSize="0.8em" px={2} py={1} borderRadius="full">
                        {finalResponse.tone}
                      </Badge>
                    )}
                  </HStack>
                  <Text whiteSpace="pre-wrap">{finalResponse.message}</Text>
                </VStack>
              ) : streamingProgress.length > 0 ? (
                <VStack align="stretch" spacing={3}>
                  {streamingProgress.map((progress, index) => (
                    <Box key={index}>
                      {index === 0 && (
                        <HStack mb={2}>
                          <Badge colorScheme="blue" fontSize="0.8em" px={2} py={1} borderRadius="full">
                            {getAgentIcon(agentId)} {progress.agent || agentId}
                          </Badge>
                          {progress.tone && (
                            <Badge colorScheme="purple" fontSize="0.8em" px={2} py={1} borderRadius="full">
                              {progress.tone}
                            </Badge>
                          )}
                        </HStack>
                      )}
                      <Text whiteSpace="pre-wrap">{progress.content}</Text>
                    </Box>
                  ))}
                </VStack>
              ) : (
                <Text>Select an agent and submit a task to see the response</Text>
              )}
            </Box>
          </Box>
          
          {/* Debug Info */}
          <Box>
            <Heading size="xs" mb={2}>Debug Info:</Heading>
            <Code p={2} borderRadius="md" fontSize="xs" width="100%" overflowX="auto">
              Task ID: {taskId}
              <br />
              Selected Agent: {agentId}
              <br />
              Streaming from /api/agent/delegate-stream
            </Code>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AgentTestPanel;
