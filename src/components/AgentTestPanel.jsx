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
        const response = await fetch('/api/agents', {
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch agents: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        
        if (isMounted) {
          // Filter to include both system and persona type agents
          // No filtering - show all agents including HAL and ASH
          const visibleAgents = data;
          setAvailableAgents(visibleAgents);
          console.log("Loaded agents:", visibleAgents);
          console.debug(`Loaded ${visibleAgents.length} agents (all types)`);
        }
      } catch (err) {
        // Ignore abort errors as they're expected during cleanup
        if (err.name === 'AbortError') {
          console.debug("AgentTestPanel - Fetch aborted during cleanup");
          return;
        }
        
        console.error('Error fetching agents:', err);
        
        if (isMounted) {
          toast({
            title: 'Error fetching agents',
            description: err.message,
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          // Fallback to default agents if API fails
          setAvailableAgents([
            { id: 'hal9000', name: 'HAL 9000', icon: '🔴', tone: 'calm' },
            { id: 'ash-xenomorph', name: 'Ash', icon: '🧬', tone: 'clinical' }
          ]);
          console.log("Using fallback agents: HAL and ASH");
        }
      } finally {
        if (isMounted) {
          setIsLoadingAgents(false);
        }
      }
    };
    
    // Add a 3 second delay before initial fetch
    const timeout = setTimeout(() => {
      if (isMounted) {
        fetchAgents();
      }
    }, 3000);
    
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
      console.debug('Submission already in progress, ignoring duplicate request');
      return;
    }
    
    // Reset previous response data
    setIsLoading(true);
    setStreamingProgress([]);
    setFinalResponse(null);
    setError(null);
    
    // Set up failsafe timeout to reset loading state after 16 seconds
    const failsafeTimeout = setTimeout(() => {
      console.warn('⏱️ Failsafe triggered: Forcing loading reset after 16s');
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
            console.error('Error parsing JSON from stream:', parseError, line);
          }
        }
      }
    } catch (err) {
      console.error('Error sending request:', err);
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
                  placeholder="Enter your task prompt here..."
                  isDisabled={isLoading}
                  rows={3}
                />
              </FormControl>
              
              <FormControl>
                <FormLabel htmlFor="task-id">Task ID</FormLabel>
                <Input 
                  id="task-id"
                  value={taskId}
                  onChange={(e) => setTaskId(e.target.value)}
                  placeholder="Task ID (auto-generated)"
                  isDisabled={isLoading}
                  size="sm"
                />
              </FormControl>
              
              <Button 
                type="submit" 
                colorScheme="blue" 
                isLoading={isLoading}
                loadingText="Sending..."
                isDisabled={!agentId || !taskInput || isLoading}
                width="full"
              >
                Send Task
              </Button>
            </VStack>
          </form>
          
          <Divider />
          
          {/* Response Display Section */}
          <Box>
            <Text fontWeight="bold" mb={2}>Response:</Text>
            
            {/* Streaming Progress */}
            {streamingProgress.length > 0 && (
              <Box 
                mb={4} 
                p={2} 
                bg={colorMode === 'light' ? 'gray.100' : 'gray.800'}
                borderRadius="md"
                fontSize="sm"
              >
                <Text fontWeight="bold" mb={2}>Progress:</Text>
                {streamingProgress.map((progress, index) => (
                  <Text key={index} fontSize="xs">
                    {progress.stage}: {progress.message} 
                    {progress.progress && ` (${Math.round(progress.progress)}%)`}
                  </Text>
                ))}
              </Box>
            )}
            
            {/* Final Response */}
            {finalResponse && (
              <Box 
                ref={responseBoxRef}
                p={4} 
                bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}
                borderRadius="md"
                borderWidth="1px"
                borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                maxHeight="300px"
                overflowY="auto"
              >
                <VStack align="stretch" spacing={3}>
                  <HStack>
                    <Text fontWeight="bold">Agent:</Text>
                    <Text>
                      {getAgentIcon(agentId)} {finalResponse.agent}
                    </Text>
                  </HStack>
                  
                  <HStack>
                    <Text fontWeight="bold">Tone:</Text>
                    <Badge colorScheme={
                      finalResponse.tone === 'calm' ? 'blue' : 
                      finalResponse.tone === 'clinical' ? 'purple' :
                      'gray'
                    }>
                      {finalResponse.tone}
                    </Badge>
                  </HStack>
                  
                  <Box>
                    <Text fontWeight="bold" mb={1}>Message:</Text>
                    <Box 
                      p={3} 
                      bg={colorMode === 'light' ? 'white' : 'gray.700'}
                      borderRadius="md"
                      borderWidth="1px"
                      borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                    >
                      <Text>{finalResponse.message}</Text>
                    </Box>
                  </Box>
                  
                  <Box>
                    <Text fontWeight="bold" mb={1}>Raw Response:</Text>
                    <Code 
                      p={2} 
                      borderRadius="md" 
                      width="100%" 
                      fontSize="xs"
                      whiteSpace="pre-wrap"
                      overflowX="auto"
                    >
                      {JSON.stringify(finalResponse, null, 2)}
                    </Code>
                  </Box>
                </VStack>
              </Box>
            )}
            
            {/* Loading Indicator */}
            {isLoading && !finalResponse && (
              <Box textAlign="center" py={4}>
                <Spinner size="md" />
                <Text mt={2}>Waiting for response...</Text>
              </Box>
            )}
            
            {/* Error Display */}
            {error && (
              <Box 
                p={3} 
                bg="red.50" 
                color="red.800" 
                borderRadius="md"
                borderWidth="1px"
                borderColor="red.200"
              >
                <Text fontWeight="bold">Error:</Text>
                <Text>{error.message}</Text>
                {error.error && (
                  <Text fontSize="sm" mt={1}>
                    {error.error}
                  </Text>
                )}
              </Box>
            )}
            
            {/* Empty State */}
            {!isLoading && !finalResponse && !error && streamingProgress.length === 0 && (
              <Box 
                p={4} 
                textAlign="center" 
                color={colorMode === 'light' ? 'gray.500' : 'gray.400'}
                bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}
                borderRadius="md"
              >
                <Text>Select an agent and submit a task to see the response</Text>
              </Box>
            )}
          </Box>
        </VStack>
      </CardBody>
      
      <CardFooter pt={0} justifyContent="flex-end">
        <Text fontSize="xs" color={colorMode === 'light' ? 'gray.500' : 'gray.400'}>
          Streaming from /api/agent/delegate-stream
        </Text>
      </CardFooter>
    </Card>
  );
};

export default AgentTestPanel;
