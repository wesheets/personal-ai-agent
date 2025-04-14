import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Textarea, VStack, Heading, Text, useToast, Flex, Badge } from '@chakra-ui/react';
import { controlService } from '../services/api';

const AgentPanel = () => {
  const [taskInput, setTaskInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('builder');
  const toast = useToast();
  const submitTimeoutRef = useRef(null);

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
        
        <Flex wrap="wrap" gap={2}>
          {agents.map((agent) => (
            <Badge
              key={agent.id}
              px={3}
              py={1}
              borderRadius="full"
              colorScheme={agent.color}
              cursor="pointer"
              onClick={() => setSelectedAgent(agent.id)}
              bg={selectedAgent === agent.id ? `${agent.color}.500` : `${agent.color}.100`}
              color={selectedAgent === agent.id ? 'white' : `${agent.color}.800`}
              _dark={{
                bg: selectedAgent === agent.id ? `${agent.color}.500` : `${agent.color}.900`,
                color: selectedAgent === agent.id ? 'white' : `${agent.color}.200`
              }}
            >
              {agent.name}
            </Badge>
          ))}
        </Flex>
        
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

// Agent definitions
const agents = [
  { id: 'builder', name: 'Builder Agent', color: 'blue' },
  { id: 'research', name: 'Research Agent', color: 'green' },
  { id: 'memory', name: 'Memory Agent', color: 'purple' },
  { id: 'ops', name: 'Ops Agent', color: 'orange' }
];

export default AgentPanel;
