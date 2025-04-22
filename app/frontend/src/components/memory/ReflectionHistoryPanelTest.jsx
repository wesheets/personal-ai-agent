import React, { useState } from 'react';
import { 
  Box, 
  VStack,
  Heading,
  Text,
  Button,
  HStack,
  Select,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useToast
} from '@chakra-ui/react';
import ReflectionHistoryPanel from './ReflectionHistoryPanel';

/**
 * Test component for ReflectionHistoryPanel
 * 
 * This component demonstrates the usage of the ReflectionHistoryPanel
 * with various test loop IDs and configurations.
 */
const ReflectionHistoryPanelTest = () => {
  const [selectedLoopId, setSelectedLoopId] = useState('loop-123');
  const [selectedNodeId, setSelectedNodeId] = useState('node-1');
  const toast = useToast();
  
  // Sample test loop IDs
  const testLoopIds = [
    'loop-123',
    'loop-456',
    'loop-789',
    'stability-check-20250422033800',
    'cognitive-rebuild-20250421'
  ];
  
  // Sample test node IDs
  const testNodeIds = [
    'node-1',
    'node-2',
    'node-3',
    'node-4',
    'node-5'
  ];
  
  // Handle loop ID selection
  const handleLoopIdChange = (e) => {
    setSelectedLoopId(e.target.value);
    toast({
      title: "Loop ID selected",
      description: `Viewing reflections for loop: ${e.target.value}`,
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };
  
  // Handle node ID selection
  const handleNodeIdChange = (e) => {
    setSelectedNodeId(e.target.value);
    toast({
      title: "Node ID selected",
      description: `Viewing reflections for node: ${e.target.value}`,
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };
  
  return (
    <Box p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Reflection History Panel - Test</Heading>
          <Text>This is a test component for the Reflection History Panel. Select a loop ID and node ID to view reflection history.</Text>
        </Box>
        
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>Loop-level Reflections</Tab>
            <Tab>Node-specific Reflections</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel>
              {/* Loop ID Selector */}
              <Box mb={4}>
                <HStack spacing={4}>
                  <Text fontWeight="bold">Select Loop ID:</Text>
                  <Select 
                    value={selectedLoopId} 
                    onChange={handleLoopIdChange}
                    width="300px"
                  >
                    {testLoopIds.map((loopId) => (
                      <option key={loopId} value={loopId}>{loopId}</option>
                    ))}
                  </Select>
                </HStack>
              </Box>
              
              {/* Reflection History Panel Component - Loop Level */}
              <Box 
                p={5} 
                borderWidth="1px" 
                borderRadius="lg" 
                boxShadow="md"
              >
                <Heading size="md" mb={4}>Loop-level Reflections</Heading>
                <ReflectionHistoryPanel 
                  loopId={selectedLoopId}
                  nodeId={null}
                />
              </Box>
            </TabPanel>
            
            <TabPanel>
              {/* Loop and Node ID Selectors */}
              <VStack spacing={4} align="start" mb={4}>
                <HStack spacing={4}>
                  <Text fontWeight="bold">Select Loop ID:</Text>
                  <Select 
                    value={selectedLoopId} 
                    onChange={handleLoopIdChange}
                    width="300px"
                  >
                    {testLoopIds.map((loopId) => (
                      <option key={loopId} value={loopId}>{loopId}</option>
                    ))}
                  </Select>
                </HStack>
                
                <HStack spacing={4}>
                  <Text fontWeight="bold">Select Node ID:</Text>
                  <Select 
                    value={selectedNodeId} 
                    onChange={handleNodeIdChange}
                    width="300px"
                  >
                    {testNodeIds.map((nodeId) => (
                      <option key={nodeId} value={nodeId}>{nodeId}</option>
                    ))}
                  </Select>
                </HStack>
              </VStack>
              
              {/* Reflection History Panel Component - Node Level */}
              <Box 
                p={5} 
                borderWidth="1px" 
                borderRadius="lg" 
                boxShadow="md"
              >
                <Heading size="md" mb={4}>Node-specific Reflections</Heading>
                <ReflectionHistoryPanel 
                  loopId={selectedLoopId}
                  nodeId={selectedNodeId}
                />
              </Box>
            </TabPanel>
          </TabPanels>
        </Tabs>
        
        {/* Test Instructions */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg"
        >
          <Heading size="md" mb={4}>Test Instructions</Heading>
          <VStack align="start" spacing={2}>
            <Text>1. Select different loop IDs to test loading different reflection histories</Text>
            <Text>2. Switch between loop-level and node-specific reflections</Text>
            <Text>3. Select different reflections to view their details</Text>
            <Text>4. Test the diff view functionality for comparing original plans with reflections</Text>
            <Text>5. Switch between the Reflections and Summary tabs</Text>
            <Text>6. Test the export functionality</Text>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default ReflectionHistoryPanelTest;
