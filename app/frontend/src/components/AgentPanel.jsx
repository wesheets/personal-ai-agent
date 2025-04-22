import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Textarea, VStack, Heading, Text, useToast, Flex, Grid, GridItem } from '@chakra-ui/react';
import { controlService } from '../services/api';
import AgentCard from './AgentCard';

const AgentPanel = () => {
  const [taskInput, setTaskInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('builder');
  const [agentList, setAgentList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();
  const submitTimeoutRef = useRef(null);

  // Fetch agents from API
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        // Replace with actual API call when endpoint is available
        const response = await fetch('/api/agent/list');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch agents: ${response.status}`);
        }
        
        const data = await response.json();
        setAgentList(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching agents:', err);
        setError('Failed to load agents');
        
        // Fallback to hardcoded agents if API fails
        setAgentList(agents);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAgents();
  }, []);

  // Cleanup function to ensure we always reset state
  useEffect(() => {
    return () => {
      if (submitTimeoutRef.current) {
        clearTimeout(submitTimeoutRef.current);
      }
    };
  }, []);

  const handleSubmit = async () => {
    if (!taskInput.trim()) {
      toast({
        title: 'Empty task',
        description: 'Please enter a task description',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Force reset any previous submission state
    setIsSubmitting(true);
    
    // Set a hard timeout to reset the spinner regardless of what happens
    submitTimeoutRef.current = setTimeout(() => {
      console.warn('Force resetting submission state after timeout');
      setIsSubmitting(false);
    }, 15000);
    
    try {
      console.log(`Starting task delegation to ${selectedAgent}...`);
      
      // Add timeout to ensure the request doesn't hang indefinitely
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          console.warn('Request timeout reached');
          reject(new Error('Request timed out'));
        }, 10000);
      });
      
      // Race between the actual request and the timeout
      const result = await Promise.race([
        controlService.delegateTask(null, selectedAgent, taskInput),
        timeoutPromise
      ]);
      
      console.log('Task delegation successful:', result);
      
      toast({
        title: 'Task submitted',
        description: `Task delegated to ${selectedAgent} agent`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      setTaskInput('');
    } catch (error) {
      // Log detailed error information
      console.error('Error delegating task:', {
        message: error.message,
        stack: error.stack,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      
      toast({
        title: 'Submission failed',
        description: error.message === 'Request timed out' 
          ? 'Request timed out. The task may still be processing.' 
          : 'Failed to delegate task. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      // Clear the hard timeout
      if (submitTimeoutRef.current) {
        clearTimeout(submitTimeoutRef.current);
        submitTimeoutRef.current = null;
      }
      
      // Ensure spinner is always hidden after submission attempt
      console.log('Resetting submission state in finally block');
      setIsSubmitting(false);
      
      // Double-check that the state was reset after a small delay
      setTimeout(() => {
        if (isSubmitting) {
          console.warn('Submission state still true after finally block - forcing reset');
          setIsSubmitting(false);
        }
      }, 100);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <Box 
        borderWidth="1px" 
        borderRadius="lg" 
        p={4} 
        shadow="md" 
        bg="white" 
        _dark={{ bg: 'gray.700' }}
        minH="240px"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>Loading agents...</Text>
      </Box>
    );
  }

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      p={4} 
      shadow="md" 
      bg="white" 
      _dark={{ bg: 'gray.700' }}
      minH="240px"
      display="flex"
      flexDir="column"
      justifyContent="flex-start"
    >
      <VStack spacing={4} align="stretch">
        <Heading size="md">Agent Task Delegation</Heading>
        
        <Text fontSize="sm">Select an agent and describe your task</Text>
        
        {/* Agent cards grid */}
        <Grid 
          templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(4, 1fr)" }} 
          gap={4}
        >
          {agentList.map((agent) => (
            <GridItem key={agent.id}>
              <Box 
                onClick={() => setSelectedAgent(agent.id)}
                cursor="pointer"
                transition="all 0.2s"
              >
                <AgentCard
                  name={agent.name}
                  status={agent.status || 'idle'}
                  description={agent.description}
                  active={selectedAgent === agent.id}
                  color={agent.color}
                />
              </Box>
            </GridItem>
          ))}
        </Grid>
        
        <Textarea
          value={taskInput}
          onChange={(e) => setTaskInput(e.target.value)}
          placeholder="Describe your task here..."
          size="md"
          rows={5}
          resize="vertical"
        />
        
        <Button
          colorScheme="blue"
          onClick={handleSubmit}
          isLoading={isSubmitting}
          loadingText="Submitting"
          isDisabled={!taskInput.trim() || isSubmitting}
          width="full"
        >
          Delegate Task
        </Button>
      </VStack>
    </Box>
  );
};

// Fallback agent definitions if API fails
const agents = [
  { 
    id: 'builder', 
    name: 'Builder Agent', 
    color: 'blue',
    status: 'idle',
    description: 'Creates and modifies code, files, and configurations'
  },
  { 
    id: 'research', 
    name: 'Research Agent', 
    color: 'green',
    status: 'idle',
    description: 'Gathers information and performs analysis on topics'
  },
  { 
    id: 'memory', 
    name: 'Memory Agent', 
    color: 'purple',
    status: 'active',
    description: 'Manages and retrieves information from system memory'
  },
  { 
    id: 'ops', 
    name: 'Ops Agent', 
    color: 'orange',
    status: 'idle',
    description: 'Handles system operations and maintenance tasks'
  }
];

export default AgentPanel;
