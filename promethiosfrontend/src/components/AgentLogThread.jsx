// /src/components/AgentLogThread.jsx
import React from "react";
import { Box, VStack, Text, Spinner } from "@chakra-ui/react";

const AgentLogThread = ({ logs, isLoading }) => {
  return (
    <Box flex="1" overflowY="auto" p={4}>
      <VStack align="start" spacing={3}>
        {logs.length === 0 && !isLoading && (
          <Text color="gray.500">No messages yet. Ask the agent something!</Text>
        )}
        {logs.map((log, index) => (
          <Box
            key={index}
            bg={log.type === "system" ? "gray.800" : "gray.700"}
            p={3}
            borderRadius="lg"
            width="100%"
          >
            <Text fontSize="sm" color="gray.400">
              {log.timestamp} — {log.sender}
            </Text>
            <Text mt={1}>{log.message}</Text>
          </Box>
        ))}
        {isLoading && (
          <Box pt={3}>
            <Spinner size="sm" mr={2} />
            <Text as="span">Agent is thinking...</Text>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default AgentLogThread;
