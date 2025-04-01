import React, { useState, useEffect } from 'react';
import { Box, VStack, Text, Flex, Spinner, Badge, Divider, useColorModeValue } from '@chakra-ui/react';
import { memoryService } from '../services/api';

const MemoryFeed = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    // Function to fetch memory entries
    const fetchMemories = async () => {
      try {
        setLoading(true);
        const data = await memoryService.getMemoryEntries();
        setMemories(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch memory entries');
        setLoading(false);
        console.error('Error fetching memories:', err);
      }
    };

    // Initial fetch
    fetchMemories();

    // Set up polling for updates (every 30 seconds)
    const intervalId = setInterval(fetchMemories, 30000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading memory entries...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} color="red.500">
        <Text fontSize="lg">{error}</Text>
        <Text mt={2}>Please try refreshing the page.</Text>
      </Box>
    );
  }

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      p={4} 
      shadow="md" 
      bg={bgColor} 
      borderColor={borderColor}
      height="100%"
      overflowY="auto"
    >
      <VStack spacing={4} align="stretch">
        <Text fontWeight="bold" fontSize="lg">Memory Feed</Text>
        
        {memories.length === 0 ? (
          <Text textAlign="center" py={10} color="gray.500">
            No memory entries to display
          </Text>
        ) : (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {memories.map((memory) => (
              <Box 
                key={memory.id} 
                p={3} 
                borderRadius="md" 
                borderWidth="1px"
                borderColor={borderColor}
              >
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                  <Text fontWeight="bold">{memory.title || 'Memory Entry'}</Text>
                  <Text fontSize="xs" color="gray.500">
                    {new Date(memory.timestamp).toLocaleString()}
                  </Text>
                </Flex>
                
                <Text whiteSpace="pre-wrap">{memory.content}</Text>
                
                <Flex mt={2} flexWrap="wrap" gap={2}>
                  {memory.agent_type && (
                    <Badge colorScheme="purple">
                      {memory.agent_type}
                    </Badge>
                  )}
                  
                  {memory.goal_id && (
                    <Badge colorScheme="blue">
                      Goal: {memory.goal_id}
                    </Badge>
                  )}
                  
                  {memory.tags && memory.tags.length > 0 && memory.tags.map((tag) => (
                    <Badge key={tag} colorScheme="green">
                      {tag}
                    </Badge>
                  ))}
                </Flex>
              </Box>
            ))}
          </VStack>
        )}
      </VStack>
    </Box>
  );
};

export default MemoryFeed;
