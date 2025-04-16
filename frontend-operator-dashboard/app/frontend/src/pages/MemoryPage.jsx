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
import MemoryViewer from '../components/MemoryViewer';
import MemoryFeed from '../components/MemoryFeed';
import MemoryUpload from '../components/MemoryUpload';
import AgentPanel from '../components/AgentPanel';
import ActivityFeed from '../components/ActivityFeed';

const MemoryPage = () => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>
        Memory Management
      </Heading>

      <Grid templateColumns="repeat(12, 1fr)" gap={6}>
        {/* Left column - Memory Browser and Upload */}
        <GridItem colSpan={{ base: 12, md: 6, lg: 8 }}>
          <Box
            borderWidth="1px"
            borderRadius="lg"
            shadow="md"
            bg={bgColor}
            borderColor={borderColor}
            mb={6}
          >
            <Tabs isFitted variant="enclosed">
              <TabList>
                <Tab>Browse Memory</Tab>
                <Tab>Upload Memory</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <MemoryViewer />
                </TabPanel>
                <TabPanel>
                  <MemoryUpload />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        </GridItem>

        {/* Right column - Memory Feed */}
        <GridItem colSpan={{ base: 12, md: 6, lg: 4 }} height="70vh">
          <MemoryFeed />
        </GridItem>
      </Grid>
    </Box>
  );
};

export default MemoryPage;
