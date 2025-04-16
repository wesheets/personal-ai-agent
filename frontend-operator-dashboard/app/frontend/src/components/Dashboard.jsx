import React, { useEffect } from 'react';
import {
  Grid,
  GridItem,
  Box,
  Heading,
  Flex,
  SimpleGrid,
  useColorModeValue
} from '@chakra-ui/react';
import GoalLoopVisualization from './GoalLoopVisualization';
import MemoryViewer from './MemoryViewer';
import InterruptControl from './InterruptControl';
import StatusFeedback from './StatusFeedback';
import AgentPanel from './AgentPanel';
import ActivityFeed from './ActivityFeed';

const Dashboard = () => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Diagnostic DOM logging to detect component redraws
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Dashboard component rendered/redrawn');
    }
  });

  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>
        Dashboard
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
        {/* Left column - Agent Panel and Activity Feed */}
        <GridItem>
          <Flex direction="column" gap={6}>
            <AgentPanel />

            <Box
              borderWidth="1px"
              borderRadius="lg"
              p={4}
              shadow="md"
              bg={bgColor}
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>
                Goal Loop Visualization
              </Heading>
              <Box
                h="100%"
                minH="300px"
                overflow="hidden"
                w="full"
                display="flex"
                flexDir="column"
                justifyContent="flex-start"
              >
                <GoalLoopVisualization />
              </Box>
            </Box>
          </Flex>
        </GridItem>

        {/* Center column - Activity Feed */}
        <GridItem>
          <ActivityFeed />
        </GridItem>

        {/* Right column - Memory Viewer, Interrupt Control, Status Feedback */}
        <GridItem>
          <Flex direction="column" gap={6}>
            <Box
              borderWidth="1px"
              borderRadius="lg"
              p={4}
              shadow="md"
              bg={bgColor}
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>
                Memory Viewer
              </Heading>
              <Box
                h="100%"
                minH="300px"
                overflow="hidden"
                w="full"
                display="flex"
                flexDir="column"
                justifyContent="flex-start"
              >
                <MemoryViewer />
              </Box>
            </Box>

            <Box
              borderWidth="1px"
              borderRadius="lg"
              p={4}
              shadow="md"
              bg={bgColor}
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>
                Interrupt Control
              </Heading>
              <Box
                h="100%"
                minH="300px"
                overflow="hidden"
                w="full"
                display="flex"
                flexDir="column"
                justifyContent="flex-start"
              >
                <InterruptControl />
              </Box>
            </Box>

            <Box
              borderWidth="1px"
              borderRadius="lg"
              p={4}
              shadow="md"
              bg={bgColor}
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>
                Status Feedback
              </Heading>
              <Box
                h="100%"
                minH="300px"
                overflow="hidden"
                w="full"
                display="flex"
                flexDir="column"
                justifyContent="flex-start"
              >
                <StatusFeedback />
              </Box>
            </Box>
          </Flex>
        </GridItem>
      </SimpleGrid>
    </Box>
  );
};

export default Dashboard;
