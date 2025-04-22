import React from 'react';
import { 
  Box, 
  VStack,
  Heading,
  Text,
  Button,
  useToast
} from '@chakra-ui/react';
import MemoryQueryConsole from './MemoryQueryConsole';

/**
 * Test component for MemoryQueryConsole
 * 
 * This component demonstrates the usage of the MemoryQueryConsole
 * with various test queries and configurations.
 */
const MemoryQueryConsoleTest = () => {
  const toast = useToast();
  
  // Sample test queries
  const testQueries = [
    "Show me all reflections from SAGE in the last week",
    "Find all memory entries related to 'cognitive stability'",
    "Display loop executions with high drift index",
    "Show all agent delegations in project promethios-core",
    "Find all error events from yesterday"
  ];
  
  // Handle test query execution
  const runTestQuery = (query) => {
    toast({
      title: "Running test query",
      description: query,
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };
  
  return (
    <Box p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Memory Query Console - Test</Heading>
          <Text>This is a test component for the Memory Query Console. Try running some queries or use the test queries below.</Text>
        </Box>
        
        {/* Memory Query Console Component */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg" 
          boxShadow="md"
        >
          <Heading size="md" mb={4}>Live Component</Heading>
          <MemoryQueryConsole 
            projectId="test-project-123"
            initialQuery=""
            onResultsChange={(results) => console.log('Results changed:', results)}
          />
        </Box>
        
        {/* Test Queries */}
        <Box 
          p={5} 
          borderWidth="1px" 
          borderRadius="lg"
        >
          <Heading size="md" mb={4}>Test Queries</Heading>
          <Text mb={4}>Click any of these queries to test the component:</Text>
          
          <VStack spacing={2} align="stretch">
            {testQueries.map((query, index) => (
              <Button 
                key={index}
                variant="outline"
                justifyContent="flex-start"
                onClick={() => runTestQuery(query)}
              >
                {query}
              </Button>
            ))}
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default MemoryQueryConsoleTest;
