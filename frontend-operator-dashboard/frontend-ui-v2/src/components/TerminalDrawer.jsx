import React from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  Flex,
  CloseButton,
  Divider
} from '@chakra-ui/react';

export default function TerminalDrawer({ open, onClose, payload, memory, logs }) {
  return (
    <Box
      position="fixed"
      top="0"
      right="0"
      h="100%"
      w="30rem"
      bg="black"
      color="green.400"
      p={4}
      boxShadow="lg"
      transform={open ? 'translateX(0)' : 'translateX(100%)'}
      transition="transform 0.3s ease"
      zIndex={50}
      overflowY="auto"
    >
      <CloseButton position="absolute" top={2} right={2} color="white" onClick={onClose} />
      <Heading size="md" mb={4}>🧠 Agent Debug View</Heading>

      <VStack spacing={6} align="stretch">
        <Box>
          <Text fontSize="sm" fontWeight="bold" borderBottom="1px" borderColor="green.700" mb={1}>
            🔁 Task Payload
          </Text>
          <Box 
            whiteSpace="pre-wrap" 
            fontSize="xs" 
            overflowX="auto" 
            bg="black" 
            p={2} 
            border="1px" 
            borderColor="green.700" 
            borderRadius="md"
          >
            {JSON.stringify(payload, null, 2) || '// No task submitted yet'}
          </Box>
        </Box>

        <Box>
          <Text fontSize="sm" fontWeight="bold" borderBottom="1px" borderColor="green.700" mb={1}>
            🧠 Memory Accessed
          </Text>
          <Box 
            whiteSpace="pre-wrap" 
            fontSize="xs" 
            overflowX="auto" 
            bg="black" 
            p={2} 
            border="1px" 
            borderColor="green.700" 
            borderRadius="md"
          >
            {memory || '// No memory log yet'}
          </Box>
        </Box>

        <Box>
          <Text fontSize="sm" fontWeight="bold" borderBottom="1px" borderColor="green.700" mb={1}>
            🧪 Reasoning & Logs
          </Text>
          <Box 
            whiteSpace="pre-wrap" 
            fontSize="xs" 
            overflowX="auto" 
            bg="black" 
            p={2} 
            border="1px" 
            borderColor="green.700" 
            borderRadius="md"
          >
            {logs || '// Agent has not returned internal reasoning yet'}
          </Box>
        </Box>
      </VStack>
    </Box>
  );
}
