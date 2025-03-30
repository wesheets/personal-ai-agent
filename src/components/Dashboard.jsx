import React, { useState, useEffect } from 'react';
import { Box, Grid, GridItem, Heading, Text, Container, VStack, Spinner } from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import { fetchGoals, fetchTaskState, fetchControlMode, fetchAgentStatus } from '../services/api';

// Component placeholders
const GoalLoopVisualization = () => (
  <Box p={4} borderWidth="1px" borderRadius="lg">
    <Heading size="md" mb={4}>Goal Loop Visualization</Heading>
    <Text>Visualization of the agent's goal loop and execution status</Text>
  </Box>
);

const MemoryViewer = () => (
  <Box p={4} borderWidth="1px" borderRadius="lg">
    <Heading size="md" mb={4}>Memory Viewer</Heading>
    <Text>View and search agent's memory and context</Text>
  </Box>
);

const InterruptControl = () => (
  <Box p={4} borderWidth="1px" borderRadius="lg">
    <Heading size="md" mb={4}>Interrupt Controls</Heading>
    <Text>Controls to interrupt or modify agent behavior</Text>
  </Box>
);

const StatusFeedback = () => (
  <Box p={4} borderWidth="1px" borderRadius="lg">
    <Heading size="md" mb={4}>Status Feedback</Heading>
    <Text>Real-time feedback on agent status and operations</Text>
  </Box>
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    goals: null,
    taskState: null,
    controlMode: null,
    agentStatus: null
  });
  
  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch data from all endpoints
        const [goals, taskState, controlMode, agentStatus] = await Promise.all([
          fetchGoals(),
          fetchTaskState(),
          fetchControlMode(),
          fetchAgentStatus()
        ]);
        
        setData({
          goals,
          taskState,
          controlMode,
          agentStatus
        });
        
        toast({
          title: "Connected to backend",
          description: "Successfully connected to the Personal AI Agent backend",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to connect to the backend API. Please check your connection.");
        
        toast({
          title: "Connection error",
          description: "Failed to connect to the backend API",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // Set up polling interval to refresh data
    const interval = setInterval(fetchData, 5000);
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, [toast]);

  if (loading && !data.goals) {
    return (
      <Container centerContent py={10}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Connecting to Personal AI Agent backend...</Text>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container centerContent py={10}>
        <VStack spacing={4}>
          <Heading color="red.500">Connection Error</Heading>
          <Text>{error}</Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={5}>
      <VStack spacing={8} align="stretch">
        <Box textAlign="center">
          <Heading as="h1" size="xl" mb={2}>Personal AI Agent System</Heading>
          <Text fontSize="lg" color="gray.600">
            Connected to: {import.meta.env.VITE_API_BASE_URL || 'https://personal-ai-agent-production.up.railway.app'}
          </Text>
        </Box>
        
        <Grid templateColumns="repeat(2, 1fr)" gap={6}>
          <GridItem>
            <GoalLoopVisualization />
          </GridItem>
          <GridItem>
            <MemoryViewer />
          </GridItem>
          <GridItem>
            <InterruptControl />
          </GridItem>
          <GridItem>
            <StatusFeedback />
          </GridItem>
        </Grid>
      </VStack>
    </Container>
  );
};

export default Dashboard;
