// /src/components/AgentTyping.jsx
import React from 'react';
import { Flex, Text, Spinner } from '@chakra-ui/react';

const AgentTyping = ({ agentName = 'HAL' }) => {
  return (
    <Flex align="center" gap={2} py={4}>
      <Spinner size="sm" color="green.400" />
      <Text fontSize="sm" color="gray.400">
        {agentName} is thinking...
      </Text>
    </Flex>
  );
};

export default AgentTyping;
