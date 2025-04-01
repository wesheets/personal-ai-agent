import React from 'react';
import { 
  Grid, 
  GridItem, 
  Box, 
  Heading, 
  Flex,
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

  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>Dashboard</Heading>
      
      <Grid templateColumns="repeat(12, 1fr)" gap={6}>
        {/* Left column - Agent Panel and Activity Feed */}
        <GridItem colSpan={{ base: 12, md: 6, lg: 4 }}>
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
              <Heading size="md" mb={4}>Goal Loop Visualization</Heading>
              <GoalLoopVisualization />
            </Box>
          </Flex>
        </GridItem>
        
        {/* Center column - Activity Feed */}
        <GridItem colSpan={{ base: 12, md: 6, lg: 4 }} height="70vh">
          <ActivityFeed />
        </GridItem>
        
        {/* Right column - Memory Viewer, Interrupt Control, Status Feedback */}
        <GridItem colSpan={{ base: 12, md: 12, lg: 4 }}>
          <Flex direction="column" gap={6}>
            <Box 
              borderWidth="1px" 
              borderRadius="lg" 
              p={4} 
              shadow="md" 
              bg={bgColor} 
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>Memory Viewer</Heading>
              <MemoryViewer />
            </Box>
            
            <Box 
              borderWidth="1px" 
              borderRadius="lg" 
              p={4} 
              shadow="md" 
              bg={bgColor} 
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>Interrupt Control</Heading>
              <InterruptControl />
            </Box>
            
            <Box 
              borderWidth="1px" 
              borderRadius="lg" 
              p={4} 
              shadow="md" 
              bg={bgColor} 
              borderColor={borderColor}
            >
              <Heading size="md" mb={4}>Status Feedback</Heading>
              <StatusFeedback />
            </Box>
          </Flex>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default Dashboard;
