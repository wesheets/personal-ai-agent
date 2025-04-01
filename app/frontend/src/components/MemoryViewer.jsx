import React, { useState, useEffect } from 'react';
<<<<<<< HEAD
=======
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
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)
import { memoryService } from '../services/api';

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
<<<<<<< HEAD
=======
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)

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
        setMemories(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch memory data');
        setLoading(false);
        console.error('Error fetching memories:', err);
      }
    };

    // Initial fetch
    fetchMemories();
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

  if (loading) {
<<<<<<< HEAD
    return <div className="loading">Loading memory data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="memory-viewer">
      {/* Filter controls */}
      <div className="memory-filters">
        <div className="filter-group">
          <label htmlFor="goalId">Goal ID:</label>
          <input
            type="text"
            id="goalId"
            name="goalId"
            value={filters.goalId}
            onChange={handleFilterChange}
            placeholder="Filter by Goal ID"
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="agentType">Agent Type:</label>
          <select
            id="agentType"
            name="agentType"
            value={filters.agentType}
            onChange={handleFilterChange}
          >
            <option value="">All Agents</option>
            <option value="builder">Builder</option>
            <option value="ops">Ops</option>
            <option value="research">Research</option>
            <option value="memory">Memory</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="startTimestamp">From:</label>
          <input
            type="datetime-local"
            id="startTimestamp"
            name="startTimestamp"
            value={filters.startTimestamp}
            onChange={handleFilterChange}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="endTimestamp">To:</label>
          <input
            type="datetime-local"
            id="endTimestamp"
            name="endTimestamp"
            value={filters.endTimestamp}
            onChange={handleFilterChange}
          />
        </div>
        
        <button className="btn btn-secondary" onClick={resetFilters}>
          Reset Filters
        </button>
      </div>
      
      {/* Memory entries display */}
      <div className="memory-entries">
        {memories.length > 0 ? (
          <div className="memory-list">
            {memories.map((memory) => (
              <div key={memory.id} className="memory-item">
                <div className="memory-header">
                  <h4>{memory.title || 'Memory Entry'}</h4>
                  <span className="memory-timestamp">
                    {new Date(memory.timestamp).toLocaleString()}
                  </span>
                </div>
                
                <div className="memory-content">
                  <p>{memory.content}</p>
                </div>
                
                <div className="memory-metadata">
                  <span className="memory-agent">Agent: {memory.agent_type || 'Unknown'}</span>
                  {memory.goal_id && <span className="memory-goal">Goal: {memory.goal_id}</span>}
                  {memory.tags && memory.tags.length > 0 && (
                    <div className="memory-tags">
                      Tags: {memory.tags.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">No memory entries found</div>
        )}
      </div>
    </div>
=======
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading memory data...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} color="red.500">
        <Text fontSize="lg">{error}</Text>
      </Box>
    );
  }

  return (
    <Box>
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
        {memories.length > 0 ? (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {memories.map((memory) => (
              <Box 
                key={memory.id} 
                p={4} 
                borderWidth="1px" 
                borderRadius="md" 
                bg={bgColor} 
                borderColor={borderColor}
              >
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                  <Text fontWeight="bold">{memory.title || 'Memory Entry'}</Text>
                  <Text fontSize="sm" color="gray.500">
                    {new Date(memory.timestamp).toLocaleString()}
                  </Text>
                </Flex>
                
                <Text mb={3}>{memory.content}</Text>
                
                <Flex gap={2} flexWrap="wrap" fontSize="sm" color="gray.600">
                  <Text>Agent: {memory.agent_type || 'Unknown'}</Text>
                  {memory.goal_id && <Text>Goal: {memory.goal_id}</Text>}
                  {memory.tags && memory.tags.length > 0 && (
                    <Text>Tags: {memory.tags.join(', ')}</Text>
                  )}
                </Flex>
              </Box>
            ))}
          </VStack>
        ) : (
          <Box 
            textAlign="center" 
            py={10} 
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
>>>>>>> 3f081ad (Restore original UI components and implement missing ones with Chakra UI)
  );
};

export default MemoryViewer;
