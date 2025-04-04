import React from 'react';
import { 
  Grid, 
  GridItem, 
  Box, 
  Heading, 
  Flex,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel
} from '@chakra-ui/react';
import AgentPanel from '../components/AgentPanel';
import ActivityFeed from '../components/ActivityFeed';
import StatusFeedback from '../components/StatusFeedback';

const AgentsPage = () => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>Agent Management</Heading>
      
      <Grid templateColumns="repeat(12, 1fr)" gap={6}>
        {/* Left column - Agent Panel */}
        <GridItem colSpan={{ base: 12, md: 6, lg: 4 }}>
          <AgentPanel />
        </GridItem>
        
        {/* Center column - Activity Feed */}
        <GridItem colSpan={{ base: 12, md: 6, lg: 4 }} height="70vh">
          <ActivityFeed />
        </GridItem>
        
        {/* Right column - Status Feedback */}
        <GridItem colSpan={{ base: 12, md: 12, lg: 4 }}>
          <Box 
            borderWidth="1px" 
            borderRadius="lg" 
            p={4} 
            shadow="md" 
            bg={bgColor} 
            borderColor={borderColor}
          >
            <Heading size="md" mb={4}>Agent Status</Heading>
            <StatusFeedback />
          </Box>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default AgentsPage;
