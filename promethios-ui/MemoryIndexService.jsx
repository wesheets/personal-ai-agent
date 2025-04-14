import React, { useState, useEffect } from 'react';
import { Box, Flex, VStack, Text, useColorModeValue, Heading, Badge, Divider } from '@chakra-ui/react';

/**
 * MemoryIndexService component
 * Handles indexing and retrieval of memory logs scoped by user_id and agent_id
 */
const MemoryIndexService = ({ agentId, userId }) => {
  const [memoryIndex, setMemoryIndex] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.800');
  
  // Load memory index when component mounts or when agentId/userId changes
  useEffect(() => {
    if (agentId && userId) {
      loadMemoryIndex();
    }
  }, [agentId, userId]);
  
  const loadMemoryIndex = async () => {
    setLoading(true);
    
    try {
      // In a real implementation, this would fetch memory index from the API
      // const response = await fetch(`/api/memory/index?agent_id=${agentId}&user_id=${userId}`);
      // if (!response.ok) {
      //   throw new Error('Failed to load memory index');
      // }
      // const data = await response.json();
      // setMemoryIndex(data.index);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock memory index data
      const mockMemoryIndex = [
        {
          id: 'idx-1',
          type: 'conversation',
          topic: 'Quantum Computing',
          relevance: 0.95,
          lastAccessed: new Date(Date.now() - 1 * 60 * 60000),
          entryCount: 5
        },
        {
          id: 'idx-2',
          type: 'document',
          topic: 'Neural Networks Research Paper',
          relevance: 0.87,
          lastAccessed: new Date(Date.now() - 2 * 24 * 60 * 60000),
          entryCount: 1
        },
        {
          id: 'idx-3',
          type: 'conversation',
          topic: 'Machine Learning Algorithms',
          relevance: 0.82,
          lastAccessed: new Date(Date.now() - 5 * 24 * 60 * 60000),
          entryCount: 8
        }
      ];
      
      setMemoryIndex(mockMemoryIndex);
    } catch (error) {
      console.error('Error loading memory index:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const formatLastAccessed = (date) => {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    }
  };
  
  return (
    <Box>
      <Heading as="h3" size="md" mb={4}>Memory Index</Heading>
      
      {loading ? (
        <Text>Loading memory index...</Text>
      ) : memoryIndex.length === 0 ? (
        <Text>No memory index found for this agent</Text>
      ) : (
        <VStack spacing={4} align="stretch">
          {memoryIndex.map(item => (
            <Box
              key={item.id}
              p={4}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              bg={bgColor}
            >
              <Flex justify="space-between" align="center" mb={2}>
                <Heading as="h4" size="sm">{item.topic}</Heading>
                <Badge colorScheme={item.type === 'conversation' ? 'blue' : 'green'}>
                  {item.type}
                </Badge>
              </Flex>
              
              <Divider my={2} />
              
              <Flex justify="space-between" fontSize="sm">
                <Text>Relevance: {(item.relevance * 100).toFixed(0)}%</Text>
                <Text>{item.entryCount} entries</Text>
                <Text>Last accessed: {formatLastAccessed(item.lastAccessed)}</Text>
              </Flex>
            </Box>
          ))}
        </VStack>
      )}
    </Box>
  );
};

export default MemoryIndexService;
