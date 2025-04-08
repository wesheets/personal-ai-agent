import React from 'react';
import { Box, Text, VStack } from '@chakra-ui/react';

export default function MemoryFeed({ memories }) {
  if (!memories || memories.length === 0) {
    return null;
  }
  
  return (
    <VStack spacing={3} align="stretch">
      {memories.map(memory => (
        <Box 
          key={memory.id} 
          p={3} 
          bg="gray.700" 
          borderRadius="md" 
          boxShadow="sm"
        >
          <Text fontSize="sm" color="gray.300">
            {memory.type.toUpperCase()} • {new Date(memory.timestamp).toLocaleString()}
          </Text>
          <Text mt={1}>{memory.content}</Text>
          {memory.tags && memory.tags.length > 0 && (
            <Box mt={2}>
              {memory.tags.map(tag => (
                <Text 
                  key={tag} 
                  as="span" 
                  fontSize="xs" 
                  bg="blue.800" 
                  color="blue.100" 
                  px={2} 
                  py={1} 
                  borderRadius="full" 
                  mr={1}
                >
                  #{tag}
                </Text>
              ))}
            </Box>
          )}
        </Box>
      ))}
    </VStack>
  );
}
