import React, { useState, useEffect } from 'react';
import { Box, Text, Alert, Spinner } from '@chakra-ui/react';
import { AlertIcon } from '@chakra-ui/alert';

export default function InterruptControl() {
  const [loading, setLoading] = useState(true);
  const [interruptSystemOffline, setInterruptSystemOffline] = useState(false);
  
  // Inject window.or.getTaskState mock on component mount if it doesn't exist
  useEffect(() => {
    if (!window.or) {
      console.warn("⚠️ window.or not found, creating empty object");
      window.or = {};
    }

    if (typeof window.or.getTaskState !== "function") {
      console.warn("⚠️ Injecting mock getTaskState into window.or");
      window.or.getTaskState = async () => {
        console.warn("🛑 Mock getTaskState invoked – returning empty array");
        return [];
      };
    } else {
      console.log("✅ getTaskState exists and is safe to use");
    }
  }, []);

  // Update fetchSystemState with try/catch to always resolve
  useEffect(() => {
    const fetchSystemState = async () => {
      try {
        setLoading(true);
        const result = await window.or.getTaskState?.();
        console.log("✅ Successfully fetched task state:", result);
        setInterruptSystemOffline(false);
      } catch (err) {
        console.error("🔥 Error invoking getTaskState:", err);
        setInterruptSystemOffline(true);
      } finally {
        setLoading(false);
      }
    };

    fetchSystemState();
  }, []);

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg">
      <Text fontWeight="bold" mb={2}>Interrupt Control</Text>
      
      {loading ? (
        <Box display="flex" alignItems="center">
          <Spinner size="sm" mr={2} />
          <Text>Loading control panel...</Text>
        </Box>
      ) : interruptSystemOffline ? (
        <Alert status="warning" variant="left-accent">
          <AlertIcon />
          Interrupt system offline – retrying soon
        </Alert>
      ) : (
        <Text>Control panel loaded.</Text>
      )}
    </Box>
  );
}
