import React from 'react';
import { 
  Box, 
  Text, 
  useColorModeValue
} from '@chakra-ui/react';

// This is a simplified test component
const ThreadTester: React.FC = () => {
  return (
    <Box p={4} bg={useColorModeValue('gray.50', 'gray.900')}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Thread Tester Component
      </Text>
      <Text>
        This component is for testing purposes only. It contains mock data and handlers
        to test the threaded conversation architecture.
      </Text>
    </Box>
  );
};

export default ThreadTester;
