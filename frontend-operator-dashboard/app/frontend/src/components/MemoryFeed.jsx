import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  VStack,
  Text,
  Flex,
  Spinner,
  Badge,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import { memoryService } from '../services/api';
import isEqual from 'lodash/isEqual';

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
        if (memories.length === 0) {
          setLoading(true);
        }
        const data = await memoryService.getMemoryEntries();

        // Compare data before updating state to avoid unnecessary re-renders
        const dataChanged = !isEqual(data, memories);
        if (dataChanged) {
          setMemories(data);
        }

        if (loading) {
          setLoading(false);
        }
      } catch (err) {
        setError('Failed to fetch memory entries');
        setLoading(false);
        console.error('Error fetching memories:', err);
      }
    };

    // Initial fetch
    fetchMemories();

    // Set up polling for updates (every 5 seconds as requested)
    const intervalId = setInterval(fetchMemories, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Memoize the memories list to prevent unnecessary re-renders
  const memoizedMemories = useMemo(() => memories, [memories]);

  if (loading) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Flex direction="column" align="center">
          <Spinner size="xl" mb={4} />
          <Text>Loading memory entries...</Text>
        </Flex>
      </Box>
    );
  }

  if (error) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Flex direction="column" align="center">
          <Text fontSize="lg" color="red.500">
            {error}
          </Text>
          <Text mt={2}>Please try refreshing the page.</Text>
        </Flex>
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
      minH="240px"
    >
      <VStack spacing={4} align="stretch">
        <Text fontWeight="bold" fontSize="lg">
          Memory Feed
        </Text>

        {memoizedMemories.length === 0 ? (
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
            <Text color="gray.500">No memory entries to display</Text>
          </Box>
        ) : (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {memoizedMemories
              .filter((memory) => memory)
              .map((memory) => (
                <Box
                  key={memory?.id || `memory-${Math.random()}`}
                  p={3}
                  borderRadius="md"
                  borderWidth="1px"
                  borderColor={borderColor}
                >
                  <Flex justifyContent="space-between" alignItems="center" mb={2}>
                    <Text fontWeight="bold">{memory?.title || 'Memory Entry'}</Text>
                    <Text fontSize="xs" color="gray.500">
                      {memory?.timestamp
                        ? new Date(memory.timestamp).toLocaleString()
                        : 'Unknown time'}
                    </Text>
                  </Flex>

                  <Text whiteSpace="pre-wrap">{memory?.content || 'No content available'}</Text>

                  <Flex mt={2} flexWrap="wrap" gap={2}>
                    {memory?.agent_type && <Badge colorScheme="purple">{memory.agent_type}</Badge>}

                    {memory?.goal_id && <Badge colorScheme="blue">Goal: {memory.goal_id}</Badge>}

                    {memory?.tags &&
                      memory.tags.length > 0 &&
                      memory.tags.map((tag) => (
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
