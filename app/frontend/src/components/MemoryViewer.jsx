import React, { useState, useEffect, useMemo } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Input, 
  Select, 
  Button, 
  Flex, 
  Divider, 
  FormControl, 
  FormLabel, 
  Spinner,
  useColorModeValue
} from '@chakra-ui/react';
import { memoryService } from '../services/api';
import isEqual from 'lodash.isequal';

// Component for viewing memory entries with filtering capabilities
const MemoryViewer = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    goalId: '',
    agentType: '',
    startTimestamp: '',
    endTimestamp: ''
  });
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    // Function to fetch memory data from the API
    const fetchMemories = async () => {
      try {
        setLoading(true);
        
        // Build query parameters based on filters
        const params = {};
        if (filters.goalId) params.goal_id = filters.goalId;
        if (filters.agentType) params.agent_type = filters.agentType;
        if (filters.startTimestamp) params.start_timestamp = filters.startTimestamp;
        if (filters.endTimestamp) params.end_timestamp = filters.endTimestamp;
        
        const data = await memoryService.getMemoryEntries(params);
        
        // Compare data before updating state to avoid unnecessary re-renders
        const dataChanged = !isEqual(data, memories);
        if (dataChanged) {
          setMemories(data);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch memory data');
        setLoading(false);
        console.error('Error fetching memories:', err);
      }
    };

    // Initial fetch
    fetchMemories();
    
    // Set up polling for real-time updates (every 5 seconds as requested)
    const intervalId = setInterval(fetchMemories, 5000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [filters]);

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      goalId: '',
      agentType: '',
      startTimestamp: '',
      endTimestamp: ''
    });
  };

  // Memoize the memories list to prevent unnecessary re-renders
  const memoizedMemories = useMemo(() => memories, [memories]);

  if (loading) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Flex direction="column" align="center">
          <Spinner size="xl" mb={4} />
          <Text>Loading memory data...</Text>
        </Flex>
      </Box>
    );
  }

  if (error) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Text fontSize="lg" color="red.500">{error}</Text>
      </Box>
    );
  }

  return (
    <Box minH="inherit">
      {/* Filter controls */}
      <Box 
        mb={6} 
        p={4} 
        borderWidth="1px" 
        borderRadius="md" 
        bg={bgColor} 
        borderColor={borderColor}
      >
        <Text fontWeight="bold" mb={4}>Filter Memory Entries</Text>
        <Flex direction={{ base: "column", md: "row" }} gap={4} wrap="wrap">
          <FormControl flex="1">
            <FormLabel htmlFor="goalId">Goal ID:</FormLabel>
            <Input
              id="goalId"
              name="goalId"
              value={filters.goalId}
              onChange={handleFilterChange}
              placeholder="Filter by Goal ID"
              size="sm"
            />
          </FormControl>
          
          <FormControl flex="1">
            <FormLabel htmlFor="agentType">Agent Type:</FormLabel>
            <Select
              id="agentType"
              name="agentType"
              value={filters.agentType}
              onChange={handleFilterChange}
              size="sm"
            >
              <option value="">All Agents</option>
              <option value="builder">Builder</option>
              <option value="ops">Ops</option>
              <option value="research">Research</option>
              <option value="memory">Memory</option>
            </Select>
          </FormControl>
          
          <FormControl flex="1">
            <FormLabel htmlFor="startTimestamp">From:</FormLabel>
            <Input
              type="datetime-local"
              id="startTimestamp"
              name="startTimestamp"
              value={filters.startTimestamp}
              onChange={handleFilterChange}
              size="sm"
            />
          </FormControl>
          
          <FormControl flex="1">
            <FormLabel htmlFor="endTimestamp">To:</FormLabel>
            <Input
              type="datetime-local"
              id="endTimestamp"
              name="endTimestamp"
              value={filters.endTimestamp}
              onChange={handleFilterChange}
              size="sm"
            />
          </FormControl>
        </Flex>
        
        <Button 
          mt={4} 
          colorScheme="blue" 
          variant="outline" 
          size="sm" 
          onClick={resetFilters}
        >
          Reset Filters
        </Button>
      </Box>
      
      {/* Memory entries display */}
      <Box>
        {memoizedMemories.length > 0 ? (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {memoizedMemories.filter(memory => memory).map((memory) => (
              <Box 
                key={memory?.id || `memory-${Math.random()}`} 
                p={4} 
                borderWidth="1px" 
                borderRadius="md" 
                bg={bgColor} 
                borderColor={borderColor}
              >
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                  <Text fontWeight="bold">{memory?.title || 'Memory Entry'}</Text>
                  <Text fontSize="sm" color="gray.500">
                    {memory?.timestamp ? new Date(memory.timestamp).toLocaleString() : 'Unknown time'}
                  </Text>
                </Flex>
                
                <Text mb={3}>{memory?.content || 'No content available'}</Text>
                
                <Flex gap={2} flexWrap="wrap" fontSize="sm" color="gray.600">
                  <Text>Agent: {memory?.agent_type || 'Unknown'}</Text>
                  {memory?.goal_id && <Text>Goal: {memory.goal_id}</Text>}
                  {memory?.tags && memory.tags.length > 0 && (
                    <Text>Tags: {memory.tags.join(', ')}</Text>
                  )}
                </Flex>
              </Box>
            ))}
          </VStack>
        ) : (
          <Box 
            minH="inherit"
            display="flex"
            alignItems="center"
            justifyContent="center"
            borderWidth="1px" 
            borderRadius="md" 
            borderStyle="dashed"
            borderColor={borderColor}
          >
            <Text color="gray.500">No memory entries found</Text>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default MemoryViewer;
