import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Select,
  FormControl,
  FormLabel,
  useToast,
  Container,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Switch,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td
} from '@chakra-ui/react';
import { AutoRouterProvider, useAutoRouter } from '../../logic/AutoRerouter';

/**
 * Test component for AutoRerouter
 * 
 * This component demonstrates the AutoRerouter functionality
 * with sample loop data and interaction handlers.
 */
const AutoRerouterTest = () => {
  const [manualRerouteResult, setManualRerouteResult] = useState(null);
  const [monitoringEnabled, setMonitoringEnabled] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState('ASH');
  const [selectedLoop, setSelectedLoop] = useState('loop-123');
  const [failureCounts, setFailureCounts] = useState({
    'ASH': 2,
    'NOVA': 1,
    'SKEPTIC': 0
  });
  const toast = useToast();

  // Sample loops for testing
  const sampleLoops = [
    { id: 'loop-123', name: 'Data Processing Loop', agent: 'ASH' },
    { id: 'loop-456', name: 'Content Generation Loop', agent: 'NOVA' },
    { id: 'loop-789', name: 'Validation Loop', agent: 'SKEPTIC' }
  ];

  // Wrap the component content with AutoRouterProvider
  const TestContent = () => {
    // Use the AutoRouter context
    const autoRouter = useAutoRouter();
    
    // Update monitoring state when toggle changes
    useEffect(() => {
      if (autoRouter.isMonitoring !== monitoringEnabled) {
        autoRouter.toggleMonitoring();
      }
    }, [monitoringEnabled, autoRouter]);
    
    // Update failure counts in context
    useEffect(() => {
      // This is just for the test UI - in a real implementation,
      // the AutoRerouter would track these internally
      setFailureCounts(prevCounts => {
        const newCounts = {...prevCounts};
        Object.keys(autoRouter.agentFailureCounts).forEach(agent => {
          newCounts[agent] = autoRouter.agentFailureCounts[agent];
        });
        return newCounts;
      });
    }, [autoRouter.agentFailureCounts]);

    // Handle manual reroute
    const handleManualReroute = async () => {
      const loop = sampleLoops.find(l => l.id === selectedLoop);
      const originalAgent = loop ? loop.agent : selectedAgent;
      const fallbackAgent = getFallbackAgent(originalAgent);
      
      const success = await autoRouter.manualReroute(
        selectedLoop,
        originalAgent,
        fallbackAgent,
        'Manual reroute from test interface'
      );
      
      if (success) {
        setManualRerouteResult({
          loop_id: selectedLoop,
          original_agent: originalAgent,
          fallback_agent: fallbackAgent,
          timestamp: new Date().toISOString()
        });
        
        toast({
          title: 'Manual Reroute Successful',
          description: `Rerouted loop ${selectedLoop} from ${originalAgent} to ${fallbackAgent}`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        toast({
          title: 'Manual Reroute Failed',
          description: 'Failed to reroute the loop. Check console for details.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      }
    };

    // Handle increment failure count
    const handleIncrementFailure = () => {
      // In a real implementation, this would be tracked by the AutoRerouter
      // based on actual loop failures
      setFailureCounts(prev => ({
        ...prev,
        [selectedAgent]: (prev[selectedAgent] || 0) + 1
      }));
      
      // If we've reached the threshold, show a toast
      if ((failureCounts[selectedAgent] || 0) + 1 >= 3) {
        toast({
          title: 'Failure Threshold Reached',
          description: `${selectedAgent} has reached the failure threshold. Auto-rerouting will be triggered.`,
          status: 'warning',
          duration: 3000,
          isClosable: true,
        });
      }
    };

    // Handle clear failure count
    const handleClearFailure = () => {
      autoRouter.clearFailureCount(selectedAgent);
      
      toast({
        title: 'Failure Count Cleared',
        description: `Failure count for ${selectedAgent} has been reset to 0.`,
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
    };

    return (
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>Auto-Rerouter Test</Heading>
          <Text>
            This test component demonstrates the AutoRerouter functionality with sample loop data.
            You can simulate agent failures and trigger manual reroutes to see how the system behaves.
          </Text>
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Auto-Rerouter Controls</Heading>
          
          <FormControl display="flex" alignItems="center" mb={4}>
            <FormLabel htmlFor="monitoring-toggle" mb="0">
              Enable Auto-Rerouting:
            </FormLabel>
            <Switch
              id="monitoring-toggle"
              isChecked={monitoringEnabled}
              onChange={(e) => setMonitoringEnabled(e.target.checked)}
              colorScheme="green"
            />
          </FormControl>
          
          <Divider my={4} />
          
          <Heading size="sm" mb={3}>Agent Failure Simulation</Heading>
          
          <HStack mb={4}>
            <FormControl>
              <FormLabel>Select Agent</FormLabel>
              <Select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
              >
                <option value="ASH">ASH</option>
                <option value="NOVA">NOVA</option>
                <option value="SKEPTIC">SKEPTIC</option>
              </Select>
            </FormControl>
            
            <Box pt={8}>
              <Button
                colorScheme="red"
                variant="outline"
                onClick={handleIncrementFailure}
                mr={2}
              >
                Simulate Failure
              </Button>
              
              <Button
                colorScheme="blue"
                variant="outline"
                onClick={handleClearFailure}
              >
                Clear Failures
              </Button>
            </Box>
          </HStack>
          
          <Alert status="info" mb={4}>
            <AlertIcon />
            <Box>
              <AlertTitle>Current Failure Counts</AlertTitle>
              <AlertDescription>
                <HStack spacing={4} mt={2}>
                  <Badge colorScheme={failureCounts.ASH >= 3 ? 'red' : 'gray'}>
                    ASH: {failureCounts.ASH || 0}
                  </Badge>
                  <Badge colorScheme={failureCounts.NOVA >= 3 ? 'red' : 'gray'}>
                    NOVA: {failureCounts.NOVA || 0}
                  </Badge>
                  <Badge colorScheme={failureCounts.SKEPTIC >= 3 ? 'red' : 'gray'}>
                    SKEPTIC: {failureCounts.SKEPTIC || 0}
                  </Badge>
                </HStack>
                <Text mt={2} fontSize="sm">
                  When an agent reaches 3 failures, auto-rerouting will be triggered.
                </Text>
              </AlertDescription>
            </Box>
          </Alert>
          
          <Divider my={4} />
          
          <Heading size="sm" mb={3}>Manual Reroute</Heading>
          
          <HStack mb={4}>
            <FormControl>
              <FormLabel>Select Loop</FormLabel>
              <Select
                value={selectedLoop}
                onChange={(e) => setSelectedLoop(e.target.value)}
              >
                {sampleLoops.map(loop => (
                  <option key={loop.id} value={loop.id}>
                    {loop.name} ({loop.agent})
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <Box pt={8}>
              <Button
                colorScheme="purple"
                onClick={handleManualReroute}
              >
                Trigger Manual Reroute
              </Button>
            </Box>
          </HStack>
          
          {manualRerouteResult && (
            <Alert status="success" mb={4}>
              <AlertIcon />
              <Box>
                <AlertTitle>Manual Reroute Successful</AlertTitle>
                <AlertDescription>
                  <Text>Loop: <Code>{manualRerouteResult.loop_id}</Code></Text>
                  <Text>From: <Code>{manualRerouteResult.original_agent}</Code></Text>
                  <Text>To: <Code>{manualRerouteResult.fallback_agent}</Code></Text>
                  <Text>Time: <Code>{new Date(manualRerouteResult.timestamp).toLocaleString()}</Code></Text>
                </AlertDescription>
              </Box>
            </Alert>
          )}
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Recent Reroutes</Heading>
          
          {autoRouter.reroutes.length > 0 ? (
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Timestamp</Th>
                  <Th>Loop ID</Th>
                  <Th>From</Th>
                  <Th>To</Th>
                  <Th>Reason</Th>
                </Tr>
              </Thead>
              <Tbody>
                {autoRouter.getRecentReroutes(5).map((reroute, index) => (
                  <Tr key={index}>
                    <Td>{new Date(reroute.timestamp).toLocaleString()}</Td>
                    <Td>{reroute.loop_id}</Td>
                    <Td>{reroute.original_agent}</Td>
                    <Td>{reroute.fallback_agent}</Td>
                    <Td>{reroute.reason}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          ) : (
            <Text color="gray.500" textAlign="center" py={4}>
              No reroutes have occurred yet
            </Text>
          )}
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Component Notes</Heading>
          <VStack align="start" spacing={2}>
            <Text>• The AutoRerouter monitors loop scorecard values in real-time</Text>
            <Text>• Rerouting is triggered when:</Text>
            <Text ml={4}>- trust_delta falls below -0.5</Text>
            <Text ml={4}>- drift_score exceeds 0.7</Text>
            <Text ml={4}>- an agent has 3 or more recent failures</Text>
            <Text>• The system maintains a mapping of primary agents to fallback agents</Text>
            <Text>• All rerouting decisions are logged for future reference</Text>
            <Text>• The Operator is notified when rerouting occurs</Text>
          </VStack>
        </Box>
      </VStack>
    );
  };

  return (
    <Container maxW="container.xl" py={8}>
      <AutoRouterProvider>
        <TestContent />
      </AutoRouterProvider>
    </Container>
  );
};

// Helper function to get fallback agent
const getFallbackAgent = (agentId) => {
  const AGENT_FALLBACKS = {
    'ASH': 'SAGE',
    'NOVA': 'SAGE',
    'SKEPTIC': 'PHILOSOPHER',
    'DEFAULT': 'SAGE'
  };
  
  return AGENT_FALLBACKS[agentId] || AGENT_FALLBACKS.DEFAULT;
};

export default AutoRerouterTest;
