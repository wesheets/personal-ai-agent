import React from 'react';
import { ChakraProvider, Box, VStack, Heading, Text } from '@chakra-ui/react';
import AgentChatConsole from './AgentChatConsole';

/**
 * Test component for AgentChatConsole
 * 
 * This component is used to test the AgentChatConsole in isolation
 * before integrating it with the main application.
 */
const AgentChatConsoleTest = () => {
  return (
    <ChakraProvider>
      <Box p={5} maxW="1200px" mx="auto">
        <VStack spacing={5} align="stretch">
          <Box>
            <Heading size="lg">AgentChatConsole Test</Heading>
            <Text>This is a test environment for the AgentChatConsole component.</Text>
          </Box>
          
          <AgentChatConsole projectId="test-project" />
        </VStack>
      </Box>
    </ChakraProvider>
  );
};

export default AgentChatConsoleTest;
