import React, { useState } from 'react';
import { Box, Button, Textarea, VStack, Heading, Text, useToast, Flex, Badge, Spinner } from '@chakra-ui/react';
import { controlService } from '../services/api';

const AgentPanel = () => {
  const [taskInput, setTaskInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('builder');
  const toast = useToast();

  const agents = [
    { id: 'builder', name: 'Builder Agent', color: 'blue' },
    { id: 'research', name: 'Research Agent', color: 'green' },
    { id: 'memory', name: 'Memory Agent', color: 'purple' },
    { id: 'ops', name: 'Ops Agent', color: 'orange' }
  ];

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

    setIsSubmitting(true);
    
    try {
      // Add timeout to ensure the request doesn't hang indefinitely
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timed out')), 10000);
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
      console.error('Error delegating task:', error);
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
      // Ensure spinner is always hidden after submission attempt
      setIsSubmitting(false);
    }
  };

  return (
    <Box borderWidth="1px" borderRadius="lg" p={4} shadow="md" bg="white" _dark={{ bg: 'gray.700' }}>
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

export default AgentPanel;
