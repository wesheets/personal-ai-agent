import React from 'react';
import { 
  Box, 
  Heading, 
  Text, 
  VStack, 
  Container, 
  Divider,
  useColorMode 
} from '@chakra-ui/react';
import AgentTestPanel from '../components/AgentTestPanel';
import ErrorBoundary from '../components/ErrorBoundary';

export default function AgentListPage() {
  const { colorMode } = useColorMode();
  
  return (
    <Container maxW="container.lg" py={4}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="lg" mb={2}>Agent Directory</Heading>
          <Text color={colorMode === 'light' ? 'gray.600' : 'gray.300'}>
            View and interact with available agent personalities
          </Text>
        </Box>
        
        <Divider />
        
        <ErrorBoundary>
          <AgentTestPanel />
        </ErrorBoundary>
      </VStack>
    </Container>
  );
}
