import React from 'react';
import { 
  Box, 
  VStack,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel
} from '@chakra-ui/react';
import MemoryQueryConsole from './MemoryQueryConsole';
import LoopTraceViewer from './LoopTraceViewer';
import ReflectionHistoryPanel from './ReflectionHistoryPanel';

/**
 * Integration test component for Memory Query Console and Reflection Trace Viewer
 * 
 * This component demonstrates the integration of all three components:
 * - MemoryQueryConsole
 * - LoopTraceViewer
 * - ReflectionHistoryPanel
 */
const MemoryQueryIntegrationTest = () => {
  // State to track selected loop ID from query results
  const [selectedLoopId, setSelectedLoopId] = React.useState(null);
  // State to track selected node ID from loop trace
  const [selectedNodeId, setSelectedNodeId] = React.useState(null);
  // State to track query results
  const [queryResults, setQueryResults] = React.useState([]);
  
  // Handle query results change
  const handleQueryResultsChange = (results) => {
    setQueryResults(results);
    // Reset selected IDs when query changes
    setSelectedLoopId(null);
    setSelectedNodeId(null);
  };
  
  // Handle loop selection from query results
  const handleLoopSelection = (loopId) => {
    setSelectedLoopId(loopId);
    setSelectedNodeId(null); // Reset node selection
  };
  
  // Handle node selection from loop trace
  const handleNodeSelection = (nodeId) => {
    setSelectedNodeId(nodeId);
  };
  
  return (
    <Box p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Memory Query & Reflection Trace - Integration Test</Heading>
          <Text>This component demonstrates the integration of the Memory Query Console, Loop Trace Viewer, and Reflection History Panel.</Text>
        </Box>
        
        {/* Memory Query Console */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg" 
          boxShadow="md"
        >
          <Heading size="md" mb={4}>Memory Query Console</Heading>
          <MemoryQueryConsole 
            projectId="test-project-123"
            initialQuery=""
            onResultsChange={handleQueryResultsChange}
            onLoopSelect={handleLoopSelection}
          />
        </Box>
        
        {/* Conditional rendering based on selection */}
        {selectedLoopId ? (
          <Tabs variant="enclosed" colorScheme="blue">
            <TabList>
              <Tab>Loop Trace</Tab>
              <Tab>Reflection History</Tab>
            </TabList>
            
            <TabPanels>
              <TabPanel p={0} pt={4}>
                {/* Loop Trace Viewer */}
                <Box 
                  p={5} 
                  borderWidth="1px" 
                  borderRadius="lg" 
                  boxShadow="md"
                >
                  <Heading size="md" mb={4}>Loop Trace Viewer</Heading>
                  <LoopTraceViewer 
                    loopId={selectedLoopId}
                    projectId="test-project-123"
                    onNodeSelect={handleNodeSelection}
                  />
                </Box>
              </TabPanel>
              
              <TabPanel p={0} pt={4}>
                {/* Reflection History Panel */}
                <Box 
                  p={5} 
                  borderWidth="1px" 
                  borderRadius="lg" 
                  boxShadow="md"
                >
                  <Heading size="md" mb={4}>Reflection History</Heading>
                  <ReflectionHistoryPanel 
                    loopId={selectedLoopId}
                    nodeId={selectedNodeId}
                  />
                </Box>
              </TabPanel>
            </TabPanels>
          </Tabs>
        ) : (
          <Box 
            p={5} 
            borderWidth="1px" 
            borderRadius="lg" 
            borderStyle="dashed"
            textAlign="center"
          >
            <Text color="gray.500">Use the Memory Query Console to search for loops, then select a loop to view its trace and reflection history.</Text>
          </Box>
        )}
        
        {/* Integration Instructions */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg"
        >
          <Heading size="md" mb={4}>Integration Test Instructions</Heading>
          <VStack align="start" spacing={2}>
            <Text>1. Enter a query in the Memory Query Console to search for loops</Text>
            <Text>2. Select a loop from the results to view its trace</Text>
            <Text>3. Navigate between the Loop Trace and Reflection History tabs</Text>
            <Text>4. Select a node in the Loop Trace to filter the Reflection History</Text>
            <Text>5. Verify that all components update correctly based on selections</Text>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default MemoryQueryIntegrationTest;
