// /src/components/AgentError.jsx
import React from "react";
import { Box, Text, Alert, AlertIcon, Button } from "@chakra-ui/react";

const AgentError = ({ errorMessage = "Something went wrong.", onRetry }) => {
  return (
    <Box p={4}>
      <Alert status="error" borderRadius="md" mb={4}>
        <AlertIcon />
        <Text fontSize="sm">{errorMessage}</Text>
      </Alert>
      {onRetry && (
        <Button size="sm" colorScheme="red" onClick={onRetry}>
          Retry
        </Button>
      )}
    </Box>
  );
};

export default AgentError;
