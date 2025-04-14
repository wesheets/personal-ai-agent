import React from 'react';
import { Box, Text, VStack, useColorModeValue } from '@chakra-ui/react';

const MemoryLog = ({ memory }) => {
  const bgColor = useColorModeValue('gray.100', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const tagBg = useColorModeValue('blue.100', 'blue.800');
  const tagColor = useColorModeValue('blue.800', 'blue.100');
  
  return (
    <Box 
      p={3} 
      bg={bgColor} 
      borderRadius="md" 
      boxShadow="sm"
    >
      <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.300')}>
        {memory.type.toUpperCase()} • {new Date(memory.timestamp).toLocaleString()}
      </Text>
      <Text mt={1} color={textColor}>{memory.content}</Text>
      {memory.tags && memory.tags.length > 0 && (
        <Box mt={2}>
          {memory.tags.map(tag => (
            <Text 
              key={tag} 
              as="span" 
              fontSize="xs" 
              bg={tagBg} 
              color={tagColor} 
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
  );
};

export default MemoryLog;
