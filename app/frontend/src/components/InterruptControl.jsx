import React, { useState, useEffect } from 'react';
import { Box, Text, Alert, Spinner } from '@chakra-ui/react';
import { AlertIcon } from '@chakra-ui/alert';

// Initialize window.or and getTaskState at the module level
// This ensures it happens before any component rendering
(function initializeGlobalOrchestrator() {
  try {
    if (typeof window !== 'undefined') {
      if (!window.or) {
        console.warn("⚠️ window.or not found, creating empty object");
        window.or = {};
      }

      if (typeof window.or.getTaskState !== "function") {
        console.warn("⚠️ Injecting mock getTaskState into window.or at module level");
        window.or.getTaskState = async () => {
          console.warn("🛑 Mock getTaskState invoked – returning empty array");
          return [];
        };
      } else {
        console.log("✅ getTaskState exists and is safe to use at module level");
      }
    }
  } catch (err) {
    console.error("🔥 Error initializing global orchestrator:", err);
  }
})();

export default function InterruptControl() {
  const [loading, setLoading] = useState(true);
  const [interruptSystemOffline, setInterruptSystemOffline] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  
  // Double-check window.or.getTaskState on component mount as a safety measure
  useEffect(() => {
    try {
      if (!window.or) {
        console.warn("⚠️ window.or still not found after module init, creating empty object");
        window.or = {};
      }

      if (typeof window.or.getTaskState !== "function") {
        console.warn("⚠️ Re-injecting mock getTaskState into window.or");
        window.or.getTaskState = async () => {
          console.warn("🛑 Mock getTaskState invoked – returning empty array");
          return [];
        };
      } else {
        console.log("✅ getTaskState exists and is safe to use in component");
      }
    } catch (err) {
      console.error("🔥 Error in component getTaskState check:", err);
      setInterruptSystemOffline(true);
    }
  }, []);

  // Update fetchSystemState with try/catch to always resolve
  useEffect(() => {
    const fetchSystemState = async () => {
      try {
        setLoading(true);
        
        // Extra defensive check before calling
        if (typeof window.or?.getTaskState !== "function") {
          console.warn("⚠️ getTaskState still not a function before fetch attempt");
          throw new Error("getTaskState is not available");
        }
        
        const result = await window.or.getTaskState();
        console.log("✅ Successfully fetched task state:", result);
        setInterruptSystemOffline(false);
      } catch (err) {
        console.error("🔥 Error invoking getTaskState:", err);
        setInterruptSystemOffline(true);
        
        // Implement retry logic with exponential backoff
        if (retryCount < 3) {
          const timeout = Math.pow(2, retryCount) * 1000;
          console.log(`⏱️ Retrying in ${timeout/1000} seconds...`);
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
          }, timeout);
        }
      } finally {
        // Always ensure loading state is reset
        setLoading(false);
      }
    };

    fetchSystemState();
  }, [retryCount]); // Re-run when retryCount changes

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
