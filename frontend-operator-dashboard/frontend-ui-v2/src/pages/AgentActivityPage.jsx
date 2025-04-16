import React from 'react';
import { Box, Heading, SimpleGrid, useColorMode, VStack } from '@chakra-ui/react';
import AgentActivityPings from '../components/AgentActivityPings';
import '../styles/animations.css';

/**
 * AgentActivityPage Component
 *
 * Displays the real-time agent activity map
 */
const AgentActivityPage = () => {
  const { colorMode } = useColorMode();

  return (
    <Box p={4}>
      <Heading mb={6} size="lg">
        Agent Activity
      </Heading>

      <VStack spacing={6} align="stretch">
        <AgentActivityPings />

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
          {/* Additional activity visualizations can be added here in the future */}
        </SimpleGrid>
      </VStack>
    </Box>
  );
};

export default AgentActivityPage;
