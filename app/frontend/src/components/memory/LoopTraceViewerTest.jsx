import React, { useState } from 'react';
import { 
  Box, 
  VStack,
  Heading,
  Text,
  Button,
  HStack,
  Select,
  useToast
} from '@chakra-ui/react';
import LoopTraceViewer from './LoopTraceViewer';

/**
 * Test component for LoopTraceViewer
 * 
 * This component demonstrates the usage of the LoopTraceViewer
 * with various test loop IDs and configurations.
 */
const LoopTraceViewerTest = () => {
  const [selectedLoopId, setSelectedLoopId] = useState('loop-123');
  const toast = useToast();
  
  // Sample test loop IDs
  const testLoopIds = [
    'loop-123',
    'loop-456',
    'loop-789',
    'stability-check-20250422033800',
    'cognitive-rebuild-20250421'
  ];
  
  // Handle loop ID selection
  const handleLoopIdChange = (e) => {
    setSelectedLoopId(e.target.value);
    toast({
      title: "Loop ID selected",
      description: `Viewing trace for loop: ${e.target.value}`,
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };
  
  return (
    <Box p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Loop Trace Viewer - Test</Heading>
          <Text>This is a test component for the Loop Trace Viewer. Select a loop ID to view its execution trace.</Text>
        </Box>
        
        {/* Loop ID Selector */}
        <Box>
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
        
        {/* Loop Trace Viewer Component */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg" 
          boxShadow="md"
        >
          <Heading size="md" mb={4}>Live Component</Heading>
          <LoopTraceViewer 
            loopId={selectedLoopId}
            projectId="test-project-123"
          />
        </Box>
        
        {/* Test Instructions */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg"
        >
          <Heading size="md" mb={4}>Test Instructions</Heading>
          <VStack align="start" spacing={2}>
            <Text>1. Select different loop IDs from the dropdown to test loading different traces</Text>
            <Text>2. Try expanding and collapsing nodes in the tree view</Text>
            <Text>3. Switch between tree and timeline views</Text>
            <Text>4. Test the zoom in/out functionality</Text>
            <Text>5. Click on nodes to view their details in the side drawer</Text>
            <Text>6. Test the export functionality</Text>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default LoopTraceViewerTest;
