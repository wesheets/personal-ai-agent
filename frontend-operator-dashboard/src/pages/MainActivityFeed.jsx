import React from 'react';
import { Box, Heading } from '@chakra-ui/react';
import ActivityFeedPanel from '../components/ActivityFeedPanel';

const MainActivityFeed = () => {
  return (
    <Box p={4}>
      <Heading mb={6} size="lg">
        Activity Feed
      </Heading>
      <ActivityFeedPanel />
    </Box>
  );
};

export default MainActivityFeed;
