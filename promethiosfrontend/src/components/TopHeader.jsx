// /src/components/TopHeader.jsx
import React from 'react';
import { Flex, Text, Box, Badge } from '@chakra-ui/react';

const TopHeader = ({ sessionId = 'fall-app-cycle', agentStatus = 'online' }) => {
  const statusColor =
    {
      online: 'green',
      thinking: 'yellow',
      offline: 'red'
    }[agentStatus] || 'gray';

  return (
    <Flex
      w="100%"
      h="60px"
      bg="gray.800"
      align="center"
      justify="space-between"
      px={6}
      borderBottom="1px solid #2D3748"
    >
      <Box>
        <Text fontSize="md" fontWeight="bold">
          Session: <Badge colorScheme="purple">{sessionId}</Badge>
        </Text>
      </Box>

      <Box>
        <Text fontSize="sm" color="gray.400">
          Agent Status: <Badge colorScheme={statusColor}>{agentStatus.toUpperCase()}</Badge>
        </Text>
      </Box>
    </Flex>
  );
};

export default TopHeader;
